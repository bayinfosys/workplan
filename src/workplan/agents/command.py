"""An agent run as a command in the worktree.

The argv comes from agent.command, else the preset. A "{prompt}"
argument is replaced by the prompt; with none, the prompt goes on stdin.
WORKPLAN_ACTION and WORKPLAN_TARGET are set in its environment, and for
produce-patch, WORKPLAN_COMMIT_MSG.
"""

import os
import subprocess
from pathlib import Path

from workplan import plans
from workplan.git import Fail

PRESETS = {
    "claude-code": ["claude", "-p", "--allowedTools", "Read,Edit,Write,Glob,Grep,Bash"],
    "codex": ["codex", "exec", "--sandbox", "workspace-write", "{prompt}"],
}


def run(workdir: Path, prompt: str, cfg: dict, action: str, target: str,
        preset: str | None = None) -> str:
    argv = list(cfg["agent"]["command"]) or list(PRESETS.get(preset or "", []))
    if not argv:
        raise Fail("agent.command is empty")

    stdin = prompt
    if "{prompt}" in argv:
        argv = [prompt if a == "{prompt}" else a for a in argv]
        stdin = None

    env = {**os.environ, "WORKPLAN_ACTION": action, "WORKPLAN_TARGET": target}
    if action == "produce-patch":
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
