# Route actions and agent actions named for the commands

The route actions `define-tasks` and `produce-patch` become `gen-task`
and `gen-patch`, so a dispatch script can run `workplan <action>
<target>` for both. The agents' actions, given in `WORKPLAN_ACTION`,
and the prompt templates take the same names.

Effects:

- `workplan route` prints `complete`, `review`, `gen-patch`,
  `gen-task` or `none`, with its targets
- the classifier's prompt names the same actions
- a `command` agent receives `WORKPLAN_ACTION` as `gen-task` or
  `gen-patch`
- the prompt templates are prompts/gen-task.md, gen-task-none.md,
  gen-patch.md and gen-patch-none.md
- SPEC.md sections 4 and 10, and README.md's Agents and Routing
  sections, use the names

Depends on 0001.
