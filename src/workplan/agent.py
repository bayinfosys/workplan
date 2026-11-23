"""define-tasks and produce-patch: an agent's work in a worktree.

workplan owns the worktree for every agent:

1. git worktree add --detach <tmp> <base>, where base is the
   workplan's definition branch, else HEAD
2. copy workplans/ from this tree, so uncommitted edits are seen
3. run agent.setup in the worktree
4. render the prompt and run the adapter in the worktree
5. bring the result back:
   produce-patch  the diff outside workplans/ becomes output.patch,
                  and COMMIT_MSG is copied out
   define-tasks   new task directories under workplans/<id>/ are
                  copied back, listed in WORKPLAN.md and committed
6. remove the worktree
"""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from workplan import git, plans, templates
from workplan.agents import ADAPTERS
from workplan.git import Fail
from workplan.state import commit_for

EXCLUDE = f":(exclude){plans.ROOT}/"
TASK_FILES = ("TASK.md", "BREAKDOWN.md", "NOTES.md")
FILE_LIMIT = 64 * 1024
CONTEXT_LIMIT = 256 * 1024
PATHLIKE = re.compile(r"[\w.-]+(?:/[\w.-]+)*\.\w+|[\w.-]+(?:/[\w.-]+)+")


# ---------------------------------------------------------------------------
# context
# ---------------------------------------------------------------------------

def named_files(texts: list[str], root: Path) -> list[Path]:
    """Files outside workplans/ that the plan's text names and the tree holds."""
    found: list[Path] = []
    for text in texts:
        for token in PATHLIKE.findall(text):
            path = Path(token[2:] if token.startswith("./") else token)
            if not path.parts or path.parts[0] in (plans.ROOT.name, ".git"):
                continue
            full = root / path
            if (path not in found and full.is_file()
                    and full.resolve().is_relative_to(root.resolve())
                    and full.stat().st_size <= FILE_LIMIT):
                found.append(path)
    return found


def context(files: list[Path], workdir: Path, embed: bool) -> str:
    """The prompt's $context: file contents for an agent without tools,
    a list of paths for one with tools."""
    files = [p for p in files if (workdir / p).is_file()]
    if not embed:
        return "\n".join(f"- {p}" for p in files)

    texts = [(workdir / p).read_text(errors="replace") for p in files]
    blocks, size = [], 0
    for path in [*files, *named_files(texts, workdir)]:
        text = (workdir / path).read_text(errors="replace")
        if size + len(text) > CONTEXT_LIMIT:
            blocks.append(f"===== {path} (left out: context limit) =====")
            continue
        size += len(text)
        blocks.append(f"===== {path} =====\n{text.rstrip()}\n")
    return "\n".join(blocks)


# ---------------------------------------------------------------------------
# the worktree
# ---------------------------------------------------------------------------

def adapter_for(cfg: dict):
    name = cfg["agent"]["name"]
    if name not in ADAPTERS:
        raise Fail(f"agent {name}: one of {', '.join(ADAPTERS)}")
    return name, ADAPTERS[name]


def in_worktree(wid: str, cfg: dict, work: Callable[[Path], dict]) -> dict:
    """Run work(workdir) in a fresh worktree of the workplan's branch."""
    branch = plans.branch_of(wid)
    base = branch if git.ref_exists(f"refs/heads/{branch}") else "HEAD"
    workdir = Path(tempfile.mkdtemp(prefix="workplan-"))
    git.run("worktree", "add", "--detach", str(workdir), base)
    try:
        shutil.copytree(plans.ROOT, workdir / plans.ROOT, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("output.patch", "COMMIT_MSG"))
        if setup := cfg["agent"]["setup"]:
            result = subprocess.run(setup, shell=True, cwd=workdir, capture_output=True,
                                    text=True)
            if result.returncode != 0:
                raise Fail(f"agent.setup failed: {(result.stderr or result.stdout).strip()[-800:]}")
        result = work(workdir)
    finally:
        git.ok("worktree", "remove", "--force", str(workdir))
        shutil.rmtree(workdir, ignore_errors=True)
        git.ok("worktree", "prune")
    result["base"] = base
    return result


# ---------------------------------------------------------------------------
# produce-patch
# ---------------------------------------------------------------------------

def produce_patch(task: str, cfg: dict) -> dict:
    tid = plans.task_id(task)
    wid = tid.split("/")[0]
    directory = plans.ROOT / tid
    if not (directory / "TASK.md").is_file():
        raise Fail(f"{directory}/TASK.md: not found")
    if commit := commit_for(tid, "HEAD"):
        raise Fail(f"{tid} is committed: {commit}")
    name, adapter = adapter_for(cfg)
    files = [plans.ROOT / "PRINCIPLES.md", plans.plan_path(wid),
             *(directory / f for f in TASK_FILES)]

    def work(workdir: Path) -> dict:
        prompt = templates.render(
            "prompts", "produce-patch-none.md" if name == "none" else "produce-patch.md",
            id=tid, workplan=wid, commit_msg=str(directory / "COMMIT_MSG"),
            context=context(files, workdir, embed=name == "none"),
        )
        report = adapter(workdir, prompt, cfg, "produce-patch", tid)
        git.run("add", "-A", "--", ".", EXCLUDE, cwd=workdir)
        patch = git.run("diff", "--cached", "--binary", "--", ".", EXCLUDE, cwd=workdir,
                        strip=False)
        if not patch.strip():
            raise Fail(f"the agent made no change outside {plans.ROOT}/\n{report.strip()[-800:]}")
        message, note = commit_message(workdir / directory / "COMMIT_MSG", tid)
        return {"patch": patch, "commit_msg": message, "note": note, "report": report.strip()}

    result = in_worktree(wid, cfg, work)
    (directory / "output.patch").write_text(result.pop("patch"))
    (directory / "COMMIT_MSG").write_text(result["commit_msg"] + "\n")
    result.update(task=tid, agent=name, patch=str(directory / "output.patch"))
    return result


def commit_message(path: Path, tid: str) -> tuple[str, str]:
    """The agent's COMMIT_MSG, or the task id and title when it wrote
    none or one in another form."""
    if path.is_file():
        lines = path.read_text().strip().splitlines()
        if len(lines) == 1 and lines[0].startswith(f"{tid} "):
            return lines[0], ""
    title = plans.task_title(tid) or "change"
    return f"{tid} {title}", "COMMIT_MSG was missing or malformed; written from TASK.md's title"


# ---------------------------------------------------------------------------
# define-tasks
# ---------------------------------------------------------------------------

def define_tasks(arg: str | None, cfg: dict) -> dict:
    """The agent writes the workplan's tasks. New task directories are
    copied back and listed in WORKPLAN.md; existing ones are left alone.
    WORKPLAN.md and the new tasks are committed together."""
    wid = plans.workplan_id(arg)
    branch = plans.branch_of(wid)
    plan_file = _need_plan(wid)
    if git.branch() != branch:
        raise Fail(f"define-tasks commits on {branch}; switch to it first")
    name, adapter = adapter_for(cfg)

    existing = set(plans.task_dirs(wid))
    files = [plans.ROOT / "PRINCIPLES.md", plan_file,
             *(plans.ROOT / wid / n / f for n in sorted(existing) for f in TASK_FILES)]

    def work(workdir: Path) -> dict:
        prompt = templates.render(
            "prompts", "define-tasks-none.md" if name == "none" else "define-tasks.md",
            id=wid, next=plans.next_number(wid),
            task_template=templates.text("documents", "TASK.md"),
            breakdown_template=templates.text("documents", "BREAKDOWN.md"),
            context=context(files, workdir, embed=name == "none"),
        )
        report = adapter(workdir, prompt, cfg, "define-tasks", wid)
        base = workdir / plans.ROOT / wid
        new = sorted(p.name for p in base.iterdir()
                     if p.is_dir() and plans.NNNN.fullmatch(p.name)
                     and p.name not in existing and (p / "TASK.md").is_file())
        copied = {n: {f: (base / n / f).read_text() for f in TASK_FILES
                      if (base / n / f).is_file()} for n in new}
        return {"copied": copied, "report": report.strip()}

    result = in_worktree(wid, cfg, work)
    copied = result.pop("copied")
    if not copied:
        raise Fail(f"the agent wrote no new task under {plans.ROOT / wid}/\n{result['report'][-800:]}")

    tasks, dropped = plans.listed(wid)
    for nnnn, documents in copied.items():
        for filename, text in documents.items():
            path = plans.ROOT / wid / nnnn / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        if nnnn not in tasks and nnnn not in dropped:
            plans.add_task_line(wid, f"{nnnn}  {plans.task_title(f'{wid}/{nnnn}')}")

    paths = [str(plan_file), *(str(plans.ROOT / wid / n) for n in copied)]
    git.run("add", "--", *paths)
    git.run("commit", "-q", "-m", f"{wid} define tasks", "--", *paths)
    result.update(workplan=wid, agent=name, tasks=[f"{wid}/{n}" for n in copied],
                  commit=git.run("log", "-1", "--format=%h %s"))
    return result


def _need_plan(wid: str) -> Path:
    path = plans.plan_path(wid)
    if not path.is_file():
        raise Fail(f"{path}: not found")
    return path
