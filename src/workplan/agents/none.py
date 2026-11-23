"""No agent: completions from an OpenAI-compatible endpoint.

produce-patch  the reply holds the commit message line and a unified
               diff, applied in the worktree with git apply
define-tasks   the reply holds files, each after a line
               '===== workplans/<id>/<nnnn>/<NAME>.md =====',
               written into the worktree

When the reply cannot be used, the error goes back to the model, up to
agent.attempts times.
"""

import re
import subprocess
from pathlib import Path

from workplan import llm, plans
from workplan.git import Fail

FENCE = re.compile(r"```(?:diff|patch)?[ \t]*\n(.*?)```", re.S)
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


def run(workdir: Path, prompt: str, cfg: dict, action: str, target: str) -> str:
    agent = cfg["agent"]
    messages = [{"role": "user", "content": prompt}]
    attempts = max(1, int(agent["attempts"]))
    use = use_patch if action == "produce-patch" else use_files
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
