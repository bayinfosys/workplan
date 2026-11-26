# Route actions named task-gen and patch-gen

Two route actions are renamed, everywhere an action name is used:

| Before | After |
|---|---|
| `gen-task` | `task-gen` |
| `gen-patch` | `patch-gen` |
| `complete`, `review`, `none` | unchanged |
| templates/prompts/gen-task.md | templates/prompts/task-gen.md |
| templates/prompts/gen-task-none.md | templates/prompts/task-gen-none.md |
| templates/prompts/gen-patch.md | templates/prompts/patch-gen.md |
| templates/prompts/gen-patch-none.md | templates/prompts/patch-gen-none.md |

Effects:

- `wp route` prints `patch-gen <task>...` and `task-gen <workplan>`
  where it printed gen-patch and gen-task, and `--dispatch` passes the
  After names to route.dispatch
- the classifier is asked for, and accepts, the After names
- an agent sees WORKPLAN_ACTION=task-gen or patch-gen
- the prompt templates are read by their After names, from the package
  and from a project's own templates/prompts/
- dispatch.sh runs `workplan task gen` for task-gen, and `workplan
  patch gen` for patch-gen and for each stale task on review;
  config.toml's comment names the After actions
- the agent module's docstring and comments use the After names

Depends: 0000
Change: refactor
Audience: developers
Breaking: the route actions and WORKPLAN_ACTION gen-task and gen-patch are now task-gen and patch-gen, and the prompt templates are renamed to match
