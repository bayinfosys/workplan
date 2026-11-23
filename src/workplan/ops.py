"""The protocol's operations. Each returns data and prints nothing;
the CLI formats it as text and a web server could send it as JSON."""

import datetime
import re
import stat
from pathlib import Path

from workplan import git, plans, templates
from workplan.git import Fail
from workplan.state import commit_for, master_ref, patch_applied, problems, state

GITIGNORE = (
    "workplans/*/*/output.patch",
    "workplans/*/*/COMMIT_MSG",
)

GOAL_PLACEHOLDER = "<What is true when this workplan reaches master, in a few sentences.>"

HOOK_MARK = "# installed by workplan"
HOOK = f"""#!/bin/sh
{HOOK_MARK}
command -v workplan >/dev/null 2>&1 || exit 0
( workplan route --dispatch HEAD >/dev/null 2>&1 & )
"""
HOOKS = ("post-commit", "post-merge")


def _need(path: Path) -> Path:
    if not path.is_file():
        raise Fail(f"{path}: not found")
    return path


# ---------------------------------------------------------------------------
# init and plan
# ---------------------------------------------------------------------------

def init() -> list[str]:
    """Create workplans/ with its README, principles and config, add the
    working files to .gitignore, and commit them. Existing files are
    left alone."""
    done, paths = [], []
    for name in ("README.md", "PRINCIPLES.md", "config.toml"):
        path = plans.ROOT / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(templates.render("project", name))
            done.append(f"created {path}")
            paths.append(str(path))

    ignore = Path(".gitignore")
    lines = ignore.read_text().splitlines() if ignore.is_file() else []
    missing = [line for line in GITIGNORE if line not in lines]
    if missing:
        text = ignore.read_text() if ignore.is_file() else ""
        if text and not text.endswith("\n"):
            text += "\n"
        ignore.write_text(text + "\n".join(missing) + "\n")
        done.append("added to .gitignore: " + ", ".join(missing))
        paths.append(str(ignore))

    if paths:
        git.run("add", "--", *paths)
        git.run("commit", "-q", "-m", "workplan init", "--", *paths)
        done.append("committed: " + git.run("log", "-1", "--format=%h %s"))
    return done


def plan(name: str, master: str, goal: str | None = None, today: str | None = None) -> dict:
    """A new workplan: WORKPLAN.md from its template, on a new branch
    from master. With no goal, the editor opens on the rendered template,
    as git commit does; leaving it unchanged creates nothing."""
    if not plans.NAME.fullmatch(name):
        raise Fail(f"{name}: a workplan name is lower-case words joined by '-'")
    wid = f"{today or datetime.date.today().isoformat()}-{name}"
    branch = plans.branch_of(wid)
    if (plans.ROOT / wid).exists():
        raise Fail(f"workplan {wid} exists")
    if git.ref_exists(f"refs/heads/{branch}"):
        raise Fail(f"branch {branch} exists")
    start = master_ref(master)

    rendered = templates.render("documents", "WORKPLAN.md", id=wid,
                                title=name.replace("-", " "),
                                goal=" ".join(goal.split()) if goal else GOAL_PLACEHOLDER)
    if goal:
        text = rendered
    else:
        draft = git.git_path("workplan") / "WORKPLAN.md"
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_text(rendered)
        git.edit(draft)
        text = draft.read_text()
        if not text.strip() or text == rendered:
            raise Fail("WORKPLAN.md unchanged; no workplan created")

    git.run("switch", "-q", "-c", branch, start)
    path = plans.plan_path(wid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return {"workplan": wid, "branch": branch, "created": str(path)}


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def task_status(tid: str, master: str) -> dict:
    name, detail = state(tid, master)
    return {
        "id": tid,
        "state": name,
        "detail": detail,
        "title": plans.task_title(tid),
        "depends": plans.depends_on(tid),
        "problems": problems(tid),
    }


def status(arg: str | None, master: str) -> dict:
    if arg and ("/" in arg or plans.NNNN.fullmatch(arg)):
        tid = plans.task_id(arg)
        return {"workplan": tid.split("/")[0], "tasks": [task_status(tid, master)]}
    wid = plans.workplan_id(arg)
    return {
        "workplan": wid,
        "title": plans.workplan_title(wid),
        "goal": plans.goal(wid),
        "branch": plans.branch_of(wid),
        "tasks": [task_status(tid, master) for tid in plans.workplan_tasks(wid)],
    }


# ---------------------------------------------------------------------------
# the patch loop
# ---------------------------------------------------------------------------

def _patch(task: str) -> tuple[str, Path]:
    tid = plans.task_id(task)
    return tid, _need(plans.ROOT / tid / "output.patch")


def apply(task: str) -> str:
    """Stage the patch in the tree and the index; return its stat."""
    _, patch = _patch(task)
    if patch_applied(patch):
        raise Fail(f"{patch}: already applied")
    git.run("apply", "--index", str(patch))
    return git.run("diff", "--cached", "--stat")


def diff(task: str) -> str:
    """The staged change when applied, else the patch itself."""
    _, patch = _patch(task)
    if patch_applied(patch):
        return git.run("diff", "--cached", strip=False)
    return patch.read_text()


def accept(task: str, master: str) -> str:
    """Apply the patch if needed, and commit it with COMMIT_MSG, together
    with the task's directory and WORKPLAN.md."""
    tid, patch = _patch(task)
    wid = tid.split("/")[0]
    msg = _need(plans.ROOT / tid / "COMMIT_MSG")

    if git.branch() == master:
        raise Fail(f"HEAD is {master}; accept commits on the workplan branch")
    lines = msg.read_text().strip().splitlines()
    if len(lines) != 1 or not lines[0].startswith(f"{tid} "):
        raise Fail(f"{msg}: one line, starting '{tid} '")
    name, commit = state(tid, master)
    if name in ("merged", "complete"):
        raise Fail(f"{tid} is {name}: {commit}")

    if not patch_applied(patch):
        git.run("apply", "--index", str(patch))
    git.run("add", "--", str(plans.ROOT / tid), str(plans.plan_path(wid)))
    git.run("commit", "-q", "-F", str(msg))
    return git.run("log", "-1", "--format=%h %s")


def reject(task: str) -> str:
    """Take an applied, uncommitted patch back out of the tree and index."""
    _, patch = _patch(task)
    if not patch_applied(patch):
        raise Fail(f"{patch}: not applied")
    if not git.ok("apply", "--index", "-R", "--check", str(patch)):
        raise Fail(f"{patch}: the tree has edits to the patch's files; restore them first")
    git.run("apply", "--index", "-R", str(patch))
    return f"{patch}: rejected"


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------

def squash_message(wid: str, master: str, branch: str) -> str:
    subjects = [
        s for s in git.run("log", "--reverse", "--format=%s", f"{master}..{branch}").splitlines()
        if re.match(rf"{re.escape(wid)}/\d{{4}} ", s)
    ]
    if not subjects:
        raise Fail(f"no task commits on {branch} beyond {master}")
    return templates.render(
        "documents", "SQUASH_COMMIT_MSG",
        id=wid,
        title=plans.workplan_title(wid),
        goal=plans.goal(wid),
        tasks="\n".join(subjects),
        path=str(plans.plan_path(wid)),
    )


def merge(arg: str | None, master: str, edit: bool = True) -> dict:
    """Squash workplan/<id>/definition into master, with the message
    rendered from the SQUASH_COMMIT_MSG template and opened in the
    editor, as git commit does.

    Every listed task must be committed or dropped, and the branch must
    contain master. On any failure, master and the tree are restored.
    """
    wid = plans.workplan_id(arg)
    branch = plans.branch_of(wid)

    if not git.ref_exists(f"refs/heads/{branch}"):
        raise Fail(f"branch {branch} does not exist")
    if not git.ref_exists(f"refs/heads/{master}"):
        raise Fail(f"no local branch {master}")
    if not git.clean():
        raise Fail("the tree has uncommitted changes")
    if not git.is_ancestor(master, branch):
        raise Fail(f"{branch} does not contain {master}; rebase it onto {master} first")

    _, dropped = plans.listed(wid)
    open_tasks = [
        tid for tid in plans.workplan_tasks(wid)
        if tid.split("/")[1] not in dropped
        and not (commit_for(tid, branch) or commit_for(tid, master))
    ]
    if open_tasks:
        raise Fail(f"not committed on {branch}: " + ", ".join(open_tasks))

    draft = git.git_path("workplan") / "SQUASH_COMMIT_MSG"
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(squash_message(wid, master, branch))

    previous = git.branch()
    git.run("switch", "-q", master)
    try:
        git.run("merge", "--squash", branch)
        if edit:
            git.interactive("commit", "-q", "-e", "-F", str(draft))
        else:
            git.run("commit", "-q", "-F", str(draft))
    except Fail:
        git.ok("reset", "--merge")
        git.ok("switch", "-q", previous)
        raise

    return {
        "workplan": wid,
        "commit": git.run("log", "-1", "--format=%h %s"),
        "next": [f"git push origin {master}", f"git push origin --delete {branch}",
                 f"git branch -D {branch}"],
    }


# ---------------------------------------------------------------------------
# hooks
# ---------------------------------------------------------------------------

def install() -> list[str]:
    """Write post-commit and post-merge hooks that run `workplan route`.
    A hook not written by workplan is left in place."""
    hooks = git.git_path("hooks")
    hooks.mkdir(parents=True, exist_ok=True)
    done = []
    for name in HOOKS:
        path = hooks / name
        if path.exists() and HOOK_MARK not in path.read_text():
            done.append(f"skipped {path}: an existing hook; add `workplan route --dispatch HEAD` to it")
            continue
        path.write_text(HOOK)
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        done.append(f"wrote {path}")
    return done
