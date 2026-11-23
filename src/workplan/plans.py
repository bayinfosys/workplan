"""Workplans and tasks on disk: ids, discovery and the documents' formats.

Paths are relative to the repository root; the CLI runs from there.
"""

import re
from pathlib import Path

from workplan import git
from workplan.git import Fail

ROOT = Path("workplans")

ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")     # a workplan id
DATED = re.compile(r"\d{4}-\d{2}-\d{2}")            # a dated id starts so
NNNN = re.compile(r"\d{4}")                         # a task number
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")      # the name in a new id

TASK_LINE = re.compile(r"^(\d{4})\s", re.M)         # a task line in WORKPLAN.md
DEPENDS = re.compile(r"^Depends on (.+)$", re.M)    # the dependency line in TASK.md
TITLE = re.compile(r"^# (.+)$", re.M)               # the title line of a document
BRANCH = re.compile(r"^workplan/([^/]+)/")          # a workplan's branches
HEADING = re.compile(r"^## (.+)$", re.M)


def branch_of(wid: str) -> str:
    return f"workplan/{wid}/definition"


def plan_path(wid: str) -> Path:
    return ROOT / wid / "WORKPLAN.md"


def sections(text: str) -> dict[str, str]:
    """The text under each '## ' heading, keyed by the lower-cased heading."""
    found: dict[str, str] = {}
    matches = list(HEADING.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        found[m[1].strip().lower()] = text[m.end():end]
    return found


def workplans() -> list[str]:
    if not ROOT.is_dir():
        return []
    return sorted(p.name for p in ROOT.iterdir() if p.is_dir() and ID.fullmatch(p.name)
                  and p.name != "templates")


def current_workplan() -> str:
    """The current branch's workplan, else the newest dated workplan,
    else the only workplan."""
    branch = git.branch()
    if m := BRANCH.match(branch + "/"):
        return m[1]
    names = workplans()
    dated = [n for n in names if DATED.match(n)]
    if dated:
        return dated[-1]
    if len(names) == 1:
        return names[0]
    raise Fail(f"no workplan for branch {branch}; name one")


def workplan_id(arg: str | None) -> str:
    wid = arg or current_workplan()
    if not ID.fullmatch(wid) or not (ROOT / wid).is_dir():
        raise Fail(f"workplan {wid} does not exist under {ROOT}/")
    return wid


def task_id(arg: str) -> str:
    """ID/NNNN as given, or NNNN in the current workplan."""
    tid = arg if "/" in arg else f"{current_workplan()}/{arg}"
    parts = tid.split("/")
    if len(parts) != 2 or not ID.fullmatch(parts[0]) or not NNNN.fullmatch(parts[1]):
        raise Fail(f"{arg}: a task id is <workplan>/<nnnn>, or <nnnn>")
    return tid


def listed(wid: str) -> tuple[list[str], list[str]]:
    """The task numbers WORKPLAN.md lists under Tasks and under Dropped."""
    path = plan_path(wid)
    if not path.is_file():
        return [], []
    parts = sections(path.read_text())
    return (TASK_LINE.findall(parts.get("tasks", "")),
            TASK_LINE.findall(parts.get("dropped", "")))


def task_dirs(wid: str) -> list[str]:
    base = ROOT / wid
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and NNNN.fullmatch(p.name))


def workplan_tasks(wid: str) -> list[str]:
    """Every task WORKPLAN.md lists or workplans/<wid>/ holds."""
    tasks, dropped = listed(wid)
    return [f"{wid}/{n}" for n in sorted(set(tasks) | set(dropped) | set(task_dirs(wid)))]


def next_number(wid: str) -> str:
    tasks, dropped = listed(wid)
    numbers = [int(n) for n in [*tasks, *dropped, *task_dirs(wid)]]
    return f"{max(numbers) + 1 if numbers else 0:04d}"


def depends_on(tid: str) -> list[str]:
    """The tasks named on TASK.md's 'Depends on' line, in the same workplan."""
    path = ROOT / tid / "TASK.md"
    if not path.is_file():
        return []
    wid = tid.split("/")[0]
    return [f"{wid}/{n}" for line in DEPENDS.findall(path.read_text())
            for n in NNNN.findall(line)]


def title(path: Path) -> str:
    if not path.is_file():
        return ""
    m = TITLE.search(path.read_text())
    return m[1].strip() if m else ""


def task_title(tid: str) -> str:
    return title(ROOT / tid / "TASK.md")


def goal(wid: str) -> str:
    """The text of WORKPLAN.md's Goal section."""
    path = plan_path(wid)
    if not path.is_file():
        return ""
    return sections(path.read_text()).get("goal", "").strip()


def workplan_title(wid: str) -> str:
    """The title in WORKPLAN.md's first line, '# Workplan <id>: <title>'."""
    text = title(plan_path(wid))
    return text.split(": ", 1)[1].strip() if ": " in text else text


def add_task_line(wid: str, line: str) -> None:
    """Add a task line at the end of WORKPLAN.md's Tasks section."""
    path = plan_path(wid)
    text = path.read_text()
    matches = list(HEADING.finditer(text))
    tasks = next((i for i, m in enumerate(matches) if m[1].strip().lower() == "tasks"), None)
    if tasks is None:
        raise Fail(f"{path}: no '## Tasks' section")
    end = matches[tasks + 1].start() if tasks + 1 < len(matches) else len(text)
    body = text[matches[tasks].end():end].strip("\n")
    body = f"{body}\n\n{line}" if body else line
    result = text[:matches[tasks].end()] + "\n\n" + body + "\n\n" + text[end:].lstrip("\n")
    path.write_text(result.rstrip("\n") + "\n")
