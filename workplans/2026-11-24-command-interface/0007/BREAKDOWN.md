# Breakdown

1. plans.py: `move_task_line(wid, nnnn, section)`.
2. ops.py: `drop_task` and `drop_patch`, with their checks; drop_task
   commits WORKPLAN.md alone.
3. commands.py: `cmd_drop_task`, `cmd_drop_patch`.
4. web: api.js functions; the buttons, each behind a confirm dialog.
5. tests: both commands and their refusals; merge with a dropped task.
6. README.md.
