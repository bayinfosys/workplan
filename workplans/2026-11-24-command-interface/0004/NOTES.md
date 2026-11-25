# Notes 2026-11-24-command-interface/0004: Route actions and agent actions named for the commands

Did the patch change anything TASK.md does not state?

Yes. The agent module's functions were renamed with the actions:
`define_tasks` became `gen_task` and `produce_patch` became
`gen_patch`, so that each command calls the function of its own name.
TASK.md names the route actions, `WORKPLAN_ACTION`, the prompt
templates and the documentation, and not the functions.
