"""A task's state, derived from git history and the files alone."""

from pathlib import Path

from workplan import git, plans
from workplan.git import Fail

STATES = (
    "merged", "complete", "dropped", "testing", "development",
    "waiting", "stale", "refinement", "unspecified", "unknown",
)


def master_ref(master: str) -> str:
    """Master, locally if it exists there, else on origin."""
    for ref in (master, f"origin/{master}"):
        if git.ref_exists(ref):
            return ref
    raise Fail(f"no branch {master}, locally or on origin")


def commit_for(tid: str, ref: str) -> str:
    """The latest commit in ref's history with a line starting with the
    task id: the task's commit, or the squash that lists it."""
    pattern = "^(\\+ )?" + tid.replace(".", "\\.") + " "
    return git.run("log", ref, "-E", f"--grep={pattern}", "--format=%h %s", "-n", "1")


def patch_applied(patch: Path) -> bool:
    """True when the index or the tree already holds the patch."""
    return (git.ok("apply", "--cached", "-R", "--check", str(patch))
            or git.ok("apply", "-R", "--check", str(patch)))


def state(tid: str, master: str, seen: frozenset = frozenset()) -> tuple[str, str]:
    """A task's state and its detail: the commit, or the tasks waited on.
    The first state in STATES that holds is the state."""
    for ref, name in ((master_ref(master), "merged"), ("HEAD", "complete")):
        if commit := commit_for(tid, ref):
            return name, commit

    wid, nnnn = tid.split("/")
    tasks, dropped = plans.listed(wid)
    if nnnn in dropped:
        return "dropped", ""

    directory = plans.ROOT / tid
    patch = directory / "output.patch"
    if patch.is_file():
        if patch_applied(patch):
            return "testing", ""
        if git.ok("apply", "--check", str(patch)):
            return "development", ""
        pending = [
            dep for dep in plans.depends_on(tid)
            if dep not in seen
            and state(dep, master, seen | {tid})[0] not in ("merged", "complete")
        ]
        if pending:
            return "waiting", "on " + ", ".join(pending)
        return "stale", ""

    if (directory / "TASK.md").is_file():
        return "refinement", ""
    if nnnn in tasks:
        return "unspecified", ""
    return "unknown", ""


def problems(tid: str) -> list[str]:
    """Layout problems in a task's files."""
    wid, nnnn = tid.split("/")
    directory = plans.ROOT / tid
    tasks, dropped = plans.listed(wid)
    found = []

    if directory.is_dir() and nnnn not in tasks and nnnn not in dropped:
        found.append("WORKPLAN.md does not list this task")

    task = directory / "TASK.md"
    if task.is_file():
        text = task.read_text()
        if not plans.TITLE.search(text):
            found.append("TASK.md has no '# ' title")
        if not plans.DEPENDS.search(text):
            found.append("TASK.md has no 'Depends on' line")
        known = set(tasks) | set(plans.task_dirs(wid))
        for dep in plans.depends_on(tid):
            n = dep.split("/")[1]
            if n == nnnn:
                found.append("TASK.md depends on itself")
            elif n not in known:
                found.append(f"TASK.md depends on {dep}, which the workplan does not hold")

    msg = directory / "COMMIT_MSG"
    if msg.is_file():
        lines = msg.read_text().strip().splitlines()
        if len(lines) != 1 or not lines[0].startswith(f"{tid} "):
            found.append(f"COMMIT_MSG is not one line starting '{tid} '")

    return found
