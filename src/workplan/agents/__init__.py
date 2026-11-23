"""Agent adapters.

An adapter is run(workdir, prompt, cfg, action, target) -> str, where
action is define-tasks (target: a workplan id) or produce-patch
(target: a task id). It changes files in workdir and returns the
agent's final message; agent.py does everything around it.

produce-patch  edit files outside workplans/; write the commit message
               to workplans/<task id>/COMMIT_MSG
define-tasks   write workplans/<id>/<nnnn>/TASK.md and BREAKDOWN.md
               for each new task
"""

from functools import partial

from workplan.agents import command, none

ADAPTERS = {
    "none": none.run,
    "command": command.run,
    "claude-code": partial(command.run, preset="claude-code"),
    "codex": partial(command.run, preset="codex"),
}
