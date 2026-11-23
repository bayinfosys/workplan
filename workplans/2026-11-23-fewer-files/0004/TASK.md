# Move the agent adapters into agent.py

The `none` and `command` adapters, the presets and `ADAPTERS` move
from agents/ into agent.py, and agents/ is deleted.

Effects:

- agent.py holds the worktree, define-tasks, produce-patch and the
  adapters
- the adapters' interface, run(workdir, prompt, cfg, action, target),
  and the agent names are unchanged

Depends on none.
