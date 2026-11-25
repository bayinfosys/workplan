"""gen-task and gen-patch: an agent's work in a worktree.

workplan owns the worktree for every agent:

1. git worktree add --detach <tmp> <base>, where base is the
   workplan's definition branch, else HEAD
2. copy workplans/ from this tree, so uncommitted edits are seen
3. run agent.setup in the worktree
4. render the prompt and run the adapter in the worktree
5. bring the result back:
   gen-patch  the diff outside workplans/ becomes output.patch, and
              COMMIT_MSG is copied out
   gen-task   new task directories under workplans/<id>/ are copied
              back, listed in WORKPLAN.md and committed
6. remove the worktree

An adapter is run(workdir, prompt, cfg, action, target) -> str, where
action is gen-task (target: a workplan id) or gen-patch
(target: a task id). It changes files in workdir and returns the
agent's final message:

gen-patch  edit files outside workplans/; write the commit message to
           workplans/<task id>/COMMIT_MSG
gen-task   write workplans/<id>/<nnnn>/TASK.md and BREAKDOWN.md for
           each new task

none     completions from an OpenAI-compatible endpoint: the reply
         holds a unified diff and the commit message line, or task
         files each after a line '===== <path> ====='; a reply that
         cannot be used goes back with the error, up to agent.attempts
         times
command  agent.command, else a preset, run in the worktree; a
         "{prompt}" argument is replaced by the prompt, else it goes on
         stdin; WORKPLAN_ACTION, WORKPLAN_TARGET and, for
         gen-patch, WORKPLAN_COMMIT_MSG are set in its environment
"""

import os
import re
import shutil
import subprocess
import tempfile
from functools import partial
from pathlib import Path
from typing import Callable

from workplan import git, llm, ops, plans
from workplan.git import Fail
from workplan.plans import commit_for

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


def in_worktree(wid: str, cfg: dict, work: Callable[[Path], dict], setup: bool = True) -> dict:
    """Run work(workdir) in a fresh worktree of the workplan's branch."""
    branch = plans.branch_of(wid)
    base = branch if git.ref_exists(f"refs/heads/{branch}") else "HEAD"
    workdir = Path(tempfile.mkdtemp(prefix="workplan-"))
    git.run("worktree", "add", "--detach", str(workdir), base)
    try:
        shutil.copytree(plans.ROOT, workdir / plans.ROOT, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("output.patch", "COMMIT_MSG"))
        if setup and (command := cfg["agent"]["setup"]):
            result = subprocess.run(command, shell=True, cwd=workdir, capture_output=True,
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
# prompts
# ---------------------------------------------------------------------------

def patch_prompt(tid: str, embed: bool, root: Path) -> str:
    """The gen-patch prompt: with the files' contents for an agent
    without tools, with their paths for one with tools."""
    wid = tid.split("/")[0]
    directory = plans.ROOT / tid
    files = [plans.ROOT / "PRINCIPLES.md", plans.plan_path(wid),
             *(directory / f for f in TASK_FILES)]
    return plans.render(
        "prompts", "gen-patch-none.md" if embed else "gen-patch.md",
        id=tid, workplan=wid, commit_msg=str(directory / "COMMIT_MSG"),
        context=context(files, root, embed=embed),
    )


def task_prompt(wid: str, embed: bool, root: Path) -> str:
    """The gen-task prompt, in the same two forms."""
    files = [plans.ROOT / "PRINCIPLES.md", plans.plan_path(wid),
             *(plans.ROOT / wid / n / f for n in plans.task_dirs(wid) for f in TASK_FILES)]
    return plans.render(
        "prompts", "gen-task-none.md" if embed else "gen-task.md",
        id=wid, next=plans.next_number(wid),
        task_template=plans.template_text("documents", "TASK.md"),
        breakdown_template=plans.template_text("documents", "BREAKDOWN.md"),
        context=context(files, root, embed=embed),
    )


def prompt(action: str, target: str | None) -> dict:
    """The prompt the none agent would send, from this tree, to paste
    into a chat. Nothing changes."""
    if action == "gen-patch":
        tid = plans.task_id(target)
        if not (plans.ROOT / tid / "TASK.md").is_file():
            raise Fail(f"{plans.ROOT / tid}/TASK.md: not found")
        return {"prompt": patch_prompt(tid, True, Path.cwd())}
    wid = plans.workplan_id(target)
    _need_plan(wid)
    return {"prompt": task_prompt(wid, True, Path.cwd())}


# ---------------------------------------------------------------------------
# gen-patch and add-patch
# ---------------------------------------------------------------------------

def patch_task(task: str) -> str:
    tid = plans.task_id(task)
    if not (plans.ROOT / tid / "TASK.md").is_file():
        raise Fail(f"{plans.ROOT / tid}/TASK.md: not found")
    if commit := commit_for(tid, "HEAD"):
        raise Fail(f"{tid} is committed: {commit}")
    return tid


def capture(workdir: Path, tid: str, report: str) -> dict:
    """The worktree's change outside workplans/, and its commit message."""
    git.run("add", "-A", "--", ".", EXCLUDE, cwd=workdir)
    patch = git.run("diff", "--cached", "--binary", "--", ".", EXCLUDE, cwd=workdir, strip=False)
    if not patch.strip():
        raise Fail(f"no change outside {plans.ROOT}/\n{report.strip()[-800:]}")
    message, note = commit_message(workdir / plans.ROOT / tid / "COMMIT_MSG", tid)
    return {"patch": patch, "commit_msg": message, "note": note, "report": report.strip()}


def keep_patch(tid: str, result: dict) -> dict:
    directory = plans.ROOT / tid
    (directory / "output.patch").write_text(result.pop("patch"))
    (directory / "COMMIT_MSG").write_text(result["commit_msg"] + "\n")
    result.update(task=tid, patch=str(directory / "output.patch"))
    return result


def gen_patch(task: str, cfg: dict) -> dict:
    tid = patch_task(task)
    name, adapter = adapter_for(cfg)

    def work(workdir: Path) -> dict:
        report = adapter(workdir, patch_prompt(tid, name == "none", workdir), cfg, "gen-patch", tid)
        return capture(workdir, tid, report)

    result = keep_patch(tid, in_worktree(tid.split("/")[0], cfg, work))
    result["agent"] = name
    return result


def add_patch(task: str, reply: str, cfg: dict) -> dict:
    """A reply in the none agent's form, pasted from a chat: its diff is
    applied in a worktree of the branch head, and kept as output.patch
    with its commit message."""
    tid = patch_task(task)

    def work(workdir: Path) -> dict:
        if error := use_patch(reply, workdir, tid):
            raise Fail(f"the reply cannot be used: {error}")
        return capture(workdir, tid, "")

    result = keep_patch(tid, in_worktree(tid.split("/")[0], cfg, work, setup=False))
    result["agent"] = "a pasted reply"
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
# gen-task and add-task with a reply
# ---------------------------------------------------------------------------

def keep_tasks(wid: str, documents: dict[str, dict[str, str]]) -> list[str]:
    """Write new task directories and list them in WORKPLAN.md; a task
    directory that exists is left alone."""
    existing = set(plans.task_dirs(wid))
    tasks, dropped = plans.listed(wid)
    kept = []
    for nnnn, files in sorted(documents.items()):
        if nnnn in existing or "TASK.md" not in files:
            continue
        for filename, text in files.items():
            path = plans.ROOT / wid / nnnn / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        if nnnn not in tasks and nnnn not in dropped:
            plans.add_task_line(wid, f"{nnnn}  {plans.task_title(f'{wid}/{nnnn}')}")
        kept.append(f"{wid}/{nnnn}")
    return kept


def gen_task(arg: str | None, cfg: dict) -> dict:
    """The agent writes the workplan's tasks. New task directories are
    copied back and listed in WORKPLAN.md; existing ones are left alone.
    WORKPLAN.md and the new tasks are committed together."""
    wid = plans.workplan_id(arg)
    branch = plans.branch_of(wid)
    plan_file = _need_plan(wid)
    if git.branch() != branch:
        raise Fail(f"gen-task commits on {branch}; switch to it first")
    name, adapter = adapter_for(cfg)
    existing = set(plans.task_dirs(wid))

    def work(workdir: Path) -> dict:
        report = adapter(workdir, task_prompt(wid, name == "none", workdir), cfg, "gen-task", wid)
        base = workdir / plans.ROOT / wid
        new = sorted(p.name for p in base.iterdir()
                     if p.is_dir() and plans.NNNN.fullmatch(p.name) and p.name not in existing)
        copied = {n: {f: (base / n / f).read_text() for f in TASK_FILES
                      if (base / n / f).is_file()} for n in new}
        return {"copied": copied, "report": report.strip()}

    result = in_worktree(wid, cfg, work)
    tids = keep_tasks(wid, result.pop("copied"))
    if not tids:
        raise Fail(f"the agent wrote no new task under {plans.ROOT / wid}/\n{result['report'][-800:]}")

    paths = [str(plan_file), *(str(plans.ROOT / tid) for tid in tids)]
    git.run("add", "--", *paths)
    git.run("commit", "-q", "-m", f"{wid} define tasks", "--", *paths)
    result.update(workplan=wid, agent=name, tasks=tids,
                  commit=git.run("log", "-1", "--format=%h %s"))
    return result


def add_tasks(wid: str, reply: str) -> dict:
    """A gen-task reply in the none agent's form, pasted from a chat: its
    new tasks are written and listed, as gen-task writes them. Nothing is
    committed."""
    if not ops.editable(wid):
        raise Fail(f"{wid} is editable only on {plans.branch_of(wid)}")
    _need_plan(wid)
    documents: dict[str, dict[str, str]] = {}
    for path, text in parse_files(reply, wid).items():
        nnnn, filename = path.split("/")[-2:]
        documents.setdefault(nnnn, {})[filename] = text
    tids = keep_tasks(wid, documents)
    if not tids:
        raise Fail(f"the reply holds no new task; each starts with a line "
                   f"'===== {plans.ROOT}/{wid}/<nnnn>/TASK.md ====='")
    return {"workplan": wid, "tasks": tids}


def _need_plan(wid: str) -> Path:
    path = plans.plan_path(wid)
    if not path.is_file():
        raise Fail(f"{path}: not found")
    return path

# ---------------------------------------------------------------------------
# adapters
# ---------------------------------------------------------------------------

FENCE = re.compile(r"^```(?:diff|patch)?[ \t]*\n(.*?)^```", re.S | re.M)
FILE_HEADER = re.compile(r"^=====\s*(\S+)\s*=====\s*$", re.M)


def parse_patch(reply: str, tid: str) -> tuple[str, str]:
    """The commit message line and the diff in a reply."""
    message = ""
    for line in reply.splitlines():
        line = line.strip().strip("`")
        line = re.sub(r"^(COMMIT_MSG|Commit message)\s*:\s*", "", line, flags=re.I)
        if line.startswith(f"{tid} "):
            message = line
            break

    patch = ""
    for block in FENCE.findall(reply):
        if re.search(r"^(diff --git|--- )", block, re.M):
            patch = block
            break
    if not patch:
        m = re.search(r"^(diff --git|--- )", reply, re.M)
        patch = reply[m.start():] if m else ""
    if patch and not patch.endswith("\n"):
        patch += "\n"
    return message, patch


def parse_files(reply: str, wid: str) -> dict[str, str]:
    """Task files in a reply, keyed by path; other paths are ignored."""
    allowed = re.compile(rf"^{re.escape(str(plans.ROOT))}/{re.escape(wid)}/\d{{4}}/"
                         r"(TASK|BREAKDOWN|NOTES)\.md$")
    parts = FILE_HEADER.split(reply)
    files = {}
    for path, body in zip(parts[1::2], parts[2::2]):
        if allowed.match(path):
            body = re.sub(r"^\s*```[a-z]*\n|\n```\s*$", "", body.strip("\n"))
            files[path] = body.strip("\n") + "\n"
    return files


def use_patch(reply: str, workdir: Path, tid: str) -> str:
    """Apply the reply's diff; return an error, or empty on success."""
    message, patch = parse_patch(reply, tid)
    if not patch:
        return "the reply holds no unified diff"
    result = subprocess.run(["git", "apply", "--recount", "--whitespace=nowarn", "-"],
                            cwd=workdir, input=patch, capture_output=True, text=True)
    if result.returncode != 0:
        return f"the diff did not apply: {result.stderr.strip()}"
    if message:
        path = workdir / plans.ROOT / tid / "COMMIT_MSG"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(message + "\n")
    return ""


def use_files(reply: str, workdir: Path, wid: str) -> str:
    """Write the reply's task files; return an error, or empty on success."""
    files = parse_files(reply, wid)
    if not any(path.endswith("/TASK.md") for path in files):
        return ("the reply holds no TASK.md under a "
                f"'===== {plans.ROOT}/{wid}/<nnnn>/TASK.md =====' line")
    for path, text in files.items():
        full = workdir / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(text)
    return ""


def run_none(workdir: Path, prompt: str, cfg: dict, action: str, target: str) -> str:
    agent = cfg["agent"]
    messages = [{"role": "user", "content": prompt}]
    attempts = max(1, int(agent["attempts"]))
    use = use_patch if action == "gen-patch" else use_files
    error = ""

    for _ in range(attempts):
        reply = llm.chat(cfg, agent["model"], messages, float(agent["timeout"]))
        error = use(reply, workdir, target)
        if not error:
            return reply
        messages += [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": f"That reply could not be used: {error}\n"
                                        "Reply again, in full, in the form asked for."},
        ]

    raise Fail(f"no usable reply after {attempts} attempts: {error}")


PRESETS = {
    "claude-code": ["claude", "-p", "--allowedTools", "Read,Edit,Write,Glob,Grep,Bash"],
    "codex": ["codex", "exec", "--sandbox", "workspace-write", "{prompt}"],
}


def run_command(workdir: Path, prompt: str, cfg: dict, action: str, target: str,
                preset: str | None = None) -> str:
    argv = list(cfg["agent"]["command"]) or list(PRESETS.get(preset or "", []))
    if not argv:
        raise Fail("agent.command is empty")

    stdin = prompt
    if "{prompt}" in argv:
        argv = [prompt if a == "{prompt}" else a for a in argv]
        stdin = None

    env = {**os.environ, "WORKPLAN_ACTION": action, "WORKPLAN_TARGET": target}
    if action == "gen-patch":
        env["WORKPLAN_COMMIT_MSG"] = str(plans.ROOT / target / "COMMIT_MSG")
    try:
        result = subprocess.run(argv, cwd=workdir, input=stdin, capture_output=True, text=True,
                                env=env, timeout=float(cfg["agent"]["timeout"]))
    except FileNotFoundError as e:
        raise Fail(f"agent command not found: {argv[0]}") from e
    except subprocess.TimeoutExpired as e:
        raise Fail(f"agent timed out after {cfg['agent']['timeout']}s") from e

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-800:]
        raise Fail(f"agent exited {result.returncode}: {detail}")
    return result.stdout


ADAPTERS = {
    "none": run_none,
    "command": run_command,
    "claude-code": partial(run_command, preset="claude-code"),
    "codex": partial(run_command, preset="codex"),
}
