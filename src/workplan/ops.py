"""The protocol's operations. Each returns data and prints nothing;
the CLI formats it as text and the web server as JSON.

A workplan is read from the working tree when it is there, else from
its definition branch; it is editable only while that branch is
checked out.
"""

import datetime
import re
import stat
import subprocess
import tempfile
from pathlib import Path

from workplan import git, plans
from workplan.git import Fail
from workplan.plans import commit_for, master_ref, patch_applied, state

PROJECT_FILES = ("README.md", "PRINCIPLES.md", "BACKLOG.md", "config.toml", "dispatch.sh")

GITIGNORE = (
    "workplans/*/*/output.patch",
    "workplans/*/*/COMMIT_MSG",
)

DOCUMENT = re.compile(r"WORKPLAN\.md|\d{4}/(?:TASK|BREAKDOWN|NOTES)\.md")

CHANGE_PLACEHOLDER = "<The change, in a sentence or two.>"
GOAL_PLACEHOLDER = "<What is true when this workplan reaches master, in a few sentences.>"

HOOK_MARK = "# installed by workplan"
HOOK = f"""#!/bin/sh
{HOOK_MARK}
command -v workplan >/dev/null 2>&1 || exit 0
unset GIT_INDEX_FILE GIT_DIR GIT_WORK_TREE GIT_PREFIX GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL \\
    GIT_AUTHOR_DATE GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL GIT_COMMITTER_DATE
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

def commit_paths(paths: list[str], message: str) -> str | None:
    """Commit the paths alone, whatever else is staged; None when they
    hold no change."""
    git.run("add", "--", *paths)
    if git.ok("diff", "--cached", "--quiet", "--", *paths):
        return None
    git.run("commit", "-q", "-m", message, "--", *paths)
    return git.run("log", "-1", "--format=%h %s")


def init() -> list[str]:
    """Create workplans/ with its README, principles, backlog, config and
    dispatch script, add the working files to .gitignore, and commit
    them. Existing files are left alone."""
    done, paths = [], []
    for name in PROJECT_FILES:
        path = plans.ROOT / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(plans.template_text("project", name))
            if name == "dispatch.sh":
                path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
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


def plan(name: str, master: str, goal: str | None = None, today: str | None = None,
         text: str | None = None) -> dict:
    """A new workplan: WORKPLAN.md from its template, or the text given,
    committed as '<id> workplan' on a new branch from master. With
    neither a goal nor a text, the editor opens on the rendered template,
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

    rendered = plans.render("documents", "WORKPLAN.md", id=wid,
                                title=name.replace("-", " "),
                                goal=" ".join(goal.split()) if goal else GOAL_PLACEHOLDER)
    if text is not None:
        if m := re.search(r"^# Workplan (\S+):", text, re.M):
            if m[1] != wid:
                raise Fail(f"the WORKPLAN.md is for {m[1]}, not {wid}")
        text = text if text.endswith("\n") else text + "\n"
    elif goal:
        text = rendered
    else:
        with tempfile.TemporaryDirectory(prefix="workplan-") as tmp:
            draft = Path(tmp) / "WORKPLAN.md"
            draft.write_text(rendered)
            git.edit(draft)
            text = draft.read_text()
        if not text.strip() or text == rendered:
            raise Fail("WORKPLAN.md unchanged; no workplan created")

    git.run("switch", "-q", "-c", branch, start)
    path = plans.plan_path(wid)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return {"workplan": wid, "branch": branch, "created": str(path),
            "commit": commit_paths([str(path)], f"{wid} workplan")}


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
    }


def editable(wid: str) -> bool:
    return git.branch() == plans.branch_of(wid)


def ref_status(wid: str, ref: str, master: str) -> dict:
    """A workplan's committed states, read from a branch: its WORKPLAN.md,
    its task directories, and the histories of master and the branch."""
    text = plans.read_ref(ref, plans.plan_path(wid))
    parts = plans.sections(text)
    tasks = plans.TASK_LINE.findall(parts.get("tasks", ""))
    dropped = plans.TASK_LINE.findall(parts.get("dropped", ""))
    listing = git.run("ls-tree", "--name-only", ref, f"{plans.ROOT}/{wid}/").splitlines()
    dirs = [Path(p).name for p in listing if plans.NNNN.fullmatch(Path(p).name)]
    merged_in = master_ref(master)

    rows = []
    for n in sorted(set(tasks) | set(dropped) | set(dirs)):
        tid = f"{wid}/{n}"
        task = plans.read_ref(ref, plans.ROOT / tid / "TASK.md")
        name, detail = "unknown", ""
        if commit := commit_for(tid, merged_in):
            name, detail = "merged", commit
        elif commit := commit_for(tid, ref):
            name, detail = "complete", commit
        elif n in dropped:
            name = "dropped"
        elif task:
            name = "refinement"
        elif n in tasks:
            name = "unspecified"
        rows.append({"id": tid, "state": name, "detail": detail,
                     "title": plans.title_of(task), "depends": plans.depends_of(task, wid)})

    return {
        "workplan": wid,
        "title": plans.workplan_title_of(text),
        "goal": plans.goal_of(text),
        "branch": plans.branch_of(wid),
        "source": ref,
        "editable": False,
        "tasks": rows,
    }


def status(arg: str | None, master: str) -> dict:
    if arg and ("/" in arg or plans.NNNN.fullmatch(arg)):
        tid = plans.task_id(arg)
        return {"workplan": tid.split("/")[0], "tasks": [task_status(tid, master)]}
    wid = arg or plans.current_workplan()
    if not (plans.ROOT / wid).is_dir() and (ref := plans.branches().get(wid)):
        return ref_status(wid, ref, master)
    wid = plans.workplan_id(wid)
    return {
        "workplan": wid,
        "title": plans.workplan_title(wid),
        "goal": plans.goal(wid),
        "branch": plans.branch_of(wid),
        "source": "tree",
        "editable": editable(wid),
        "tasks": [task_status(tid, master) for tid in plans.workplan_tasks(wid)],
    }


def workplans() -> list[dict]:
    """Every workplan: those in the working tree, then those held only
    on a definition branch."""
    match = plans.BRANCH.match(git.branch() + "/")
    current = match[1] if match else None
    rows = [{"id": wid, "title": plans.workplan_title(wid), "source": "tree",
             "branch": plans.branch_of(wid), "current": wid == current,
             "editable": editable(wid)} for wid in plans.workplans()]
    held = {row["id"] for row in rows}
    for wid, ref in plans.branches().items():
        if wid not in held:
            text = plans.read_ref(ref, plans.plan_path(wid))
            rows.append({"id": wid, "title": plans.workplan_title_of(text), "source": ref,
                         "branch": plans.branch_of(wid), "current": False, "editable": False})
    return sorted(rows, key=lambda row: row["id"])


def document(wid: str, name: str) -> dict:
    """WORKPLAN.md or a task file, from the tree or the workplan's branch."""
    if not plans.ID.fullmatch(wid) or not DOCUMENT.fullmatch(name):
        raise Fail(f"{wid}/{name}: not a workplan document")
    path = plans.ROOT / wid / name
    if (plans.ROOT / wid).is_dir():
        return {"text": path.read_text() if path.is_file() else "", "editable": editable(wid)}
    if ref := plans.branches().get(wid):
        return {"text": plans.read_ref(ref, path), "editable": False}
    raise Fail(f"workplan {wid} not found")


def save_document(wid: str, name: str, text: str) -> dict:
    """Write WORKPLAN.md or a task file of the editable workplan, and
    commit it as '<id> edit <name>'."""
    if not plans.ID.fullmatch(wid) or not DOCUMENT.fullmatch(name):
        raise Fail(f"{wid}/{name}: not a workplan document")
    if not editable(wid):
        raise Fail(f"{wid} is editable only on {plans.branch_of(wid)}")
    path = plans.ROOT / wid / name
    if not path.parent.is_dir():
        raise Fail(f"{path.parent}: no such task")
    path.write_text(text if not text or text.endswith("\n") else text + "\n")
    return {"saved": str(path), "commit": commit_paths([str(path)], f"{wid} edit {name}")}


def add_task(wid: str, title: str, depends: list[str] | None = None,
             change: str | None = None, edit: bool = False) -> dict:
    """The next task of the editable workplan: TASK.md and BREAKDOWN.md
    from their templates, and its line in WORKPLAN.md; with edit, the
    editor opens on TASK.md. All are committed as '<id> add <nnnn>'."""
    if not editable(wid):
        raise Fail(f"{wid} is editable only on {plans.branch_of(wid)}")
    if not plans.plan_path(wid).is_file():
        raise Fail(f"{plans.plan_path(wid)}: not found")
    title = " ".join((title or "").split())
    if not title:
        raise Fail("a task needs a title")

    tasks, dropped = plans.listed(wid)
    known = set(tasks) | set(dropped) | set(plans.task_dirs(wid))
    numbers = []
    for dep in depends or []:
        n = dep.split("/")[-1]
        if not plans.NNNN.fullmatch(n) or n not in known:
            raise Fail(f"{dep}: no such task in {wid}")
        numbers.append(n)

    nnnn = plans.next_number(wid)
    tid = f"{wid}/{nnnn}"
    directory = plans.ROOT / tid
    directory.mkdir(parents=True)
    values = {"id": tid, "title": title}
    (directory / "TASK.md").write_text(plans.render(
        "documents", "TASK.md", **values, depends=", ".join(numbers) or "none",
        change=" ".join(change.split()) if change else CHANGE_PLACEHOLDER))
    (directory / "BREAKDOWN.md").write_text(plans.render("documents", "BREAKDOWN.md", **values))
    plans.add_task_line(wid, f"{nnnn}  {title}")
    if edit:
        git.edit(directory / "TASK.md")
    return {"task": tid, "created": [str(directory / "TASK.md"), str(directory / "BREAKDOWN.md")],
            "listed": str(plans.plan_path(wid)),
            "commit": commit_paths([str(directory), str(plans.plan_path(wid))],
                                   f"{wid} add {nnnn}")}


def drop_task(task: str, master: str) -> dict:
    """Move a task from Tasks to Dropped in WORKPLAN.md, and commit
    WORKPLAN.md as '<id> drop <nnnn>'."""
    tid = plans.task_id(task)
    wid, nnnn = tid.split("/")
    if not editable(wid):
        raise Fail(f"{wid} is editable only on {plans.branch_of(wid)}")
    name, detail = state(tid, master)
    if name in ("merged", "complete"):
        raise Fail(f"{tid} is {name}: {detail}")
    if name == "dropped":
        raise Fail(f"{tid} is dropped already")
    plans.move_task_line(wid, nnnn, "dropped")
    path = str(plans.plan_path(wid))
    git.run("commit", "-q", "-m", f"{wid} drop {nnnn}", "--", path)
    return {"task": tid, "commit": git.run("log", "-1", "--format=%h %s")}


def edit_document(wid: str, name: str) -> dict:
    """Open WORKPLAN.md or a task file of the editable workplan in the
    editor git uses, and commit it as '<id> edit <name>'."""
    if not plans.ID.fullmatch(wid) or not DOCUMENT.fullmatch(name):
        raise Fail(f"{wid}/{name}: not a workplan document")
    if not editable(wid):
        raise Fail(f"{wid} is editable only on {plans.branch_of(wid)}")
    path = plans.ROOT / wid / name
    if not path.parent.is_dir():
        raise Fail(f"{path.parent}: no such task")
    existed = path.exists()
    git.edit(path)
    if not existed and path.exists() and not path.read_text().strip():
        path.unlink()
    if not path.exists():
        return {"saved": str(path), "commit": None}
    return {"saved": str(path), "commit": commit_paths([str(path)], f"{wid} edit {name}")}


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


def review(task: str, master: str) -> dict:
    """What a review of a patch needs: the task, its state, its commit
    message, its dependencies and their states, the stat and the diff."""
    tid, patch = _patch(task)
    msg = plans.ROOT / tid / "COMMIT_MSG"
    name, detail = state(tid, master)
    return {
        "task": tid,
        "state": name,
        "title": plans.task_title(tid),
        "commit_msg": msg.read_text().strip() if msg.is_file() else None,
        "depends": [{"id": d, "state": state(d, master)[0]} for d in plans.depends_on(tid)],
        "stat": git.run("apply", "--stat", str(patch), strip=False),
        "text": diff(task),
    }


def accept(task: str, master: str) -> str:
    """Apply the patch if needed, and commit it with COMMIT_MSG, together
    with the task's directory and WORKPLAN.md."""
    tid, patch = _patch(task)
    wid = tid.split("/")[0]
    msg = _need(plans.ROOT / tid / "COMMIT_MSG")

    if git.branch() == master:
        raise Fail(f"HEAD is {master}; patch accept commits on the workplan branch")
    if tid.split("/")[1] not in plans.listed(wid)[0]:
        raise Fail(f"{tid} is not listed in WORKPLAN.md; add its line under ## Tasks")
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


def drop_patch(task: str) -> dict:
    """Delete an unapplied patch and its COMMIT_MSG."""
    tid, patch = _patch(task)
    if patch_applied(patch):
        raise Fail(f"{patch}: applied; patch reject takes it out first")
    removed = [str(patch)]
    patch.unlink()
    msg = plans.ROOT / tid / "COMMIT_MSG"
    if msg.exists():
        msg.unlink()
        removed.append(str(msg))
    return {"task": tid, "removed": removed}


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
    return plans.render(
        "documents", "SQUASH_COMMIT_MSG",
        id=wid,
        title=plans.workplan_title(wid),
        goal=plans.goal(wid),
        tasks="\n".join(subjects),
        path=str(plans.plan_path(wid)),
    )


def ready_to_merge(wid: str, master: str) -> str:
    """The workplan's branch, once every check before a merge passes."""
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
    return branch


def merge_message(arg: str | None, master: str) -> str:
    """The message merge would open in the editor."""
    wid = plans.workplan_id(arg)
    return squash_message(wid, master, ready_to_merge(wid, master))


def merge(arg: str | None, master: str, edit: bool = True, message: str | None = None,
          test_command: str = "") -> dict:
    """Squash workplan/<id>/definition into master. The message is the
    one given, or the SQUASH_COMMIT_MSG template rendered and opened in
    the editor, as git commit does.

    Every listed task must be committed or dropped, and the branch must
    contain master. With a test command, it runs first in the working
    tree, with the branch checked out, and must pass. On any failure,
    master and the tree are restored; on success, the local branch is
    deleted.
    """
    wid = plans.workplan_id(arg)
    branch = ready_to_merge(wid, master)
    if test_command:
        run_tests(test_command, branch)

    text = message if message is not None else squash_message(wid, master, branch)

    previous = git.branch()
    with tempfile.TemporaryDirectory(prefix="workplan-") as tmp:
        draft = Path(tmp) / "SQUASH_COMMIT_MSG"
        draft.write_text(text)
        git.run("switch", "-q", master)
        try:
            git.run("merge", "--squash", branch)
            if edit and message is None:
                git.interactive("commit", "-q", "-e", "-F", str(draft))
            else:
                git.run("commit", "-q", "-F", str(draft))
        except Fail:
            git.ok("reset", "--merge")
            git.ok("switch", "-q", previous)
            raise
    git.run("branch", "-q", "-D", branch)

    return {
        "workplan": wid,
        "commit": git.run("log", "-1", "--format=%h %s"),
        "tested": test_command or None,
        "next": [f"git push origin {master}", f"git push origin --delete {branch}"],
    }


def run_tests(command: str, branch: str) -> None:
    """Run test.command in the working tree with the branch checked out;
    fail with the end of its output when it fails."""
    if git.branch() != branch:
        raise Fail(f"switch to {branch} to run test.command")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise Fail(f"test.command failed (exit {result.returncode}): {command}\n"
                   f"{output[-3000:]}\nnothing merged")


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
