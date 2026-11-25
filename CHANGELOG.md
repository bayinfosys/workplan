# Changelog

## 0.1.0 (unreleased)

First release, extracted from marigold's tasks/ process (task.py at
89cb0be).

- `workplans/` directory, `workplan` command with `wp` as a short name,
  `WORKPLAN_` variables
- the flow: `init`, `plan`, `define-tasks`, `produce-patch`, `apply`,
  `diff`, `accept`, `reject`, `merge`; the commands commit what they
  complete, so no step needs `git add`
- `plan` opens the editor git uses, on WORKPLAN.md rendered from its
  template; `-m` writes the goal and skips it
- `define-tasks` and `produce-patch` run an agent (`none`, `command`,
  `claude-code`, `codex`) in a worktree owned by workplan
- `accept` commits the patch with the task's directory and WORKPLAN.md,
  and refuses on master
- `merge` renders the message from the SQUASH_COMMIT_MSG template and
  opens the editor; it requires the branch to contain master and
  restores the tree on failure
- workplan branches are `workplan/<id>/definition`
- `status` with layout problems and `--json`; the `dropped` state
- `route` with the rules or an OpenAI-compatible classifier; action
  names match the commands; `install` writes hooks into .git/hooks
- SPEC.md with a "By hand" block for each step
