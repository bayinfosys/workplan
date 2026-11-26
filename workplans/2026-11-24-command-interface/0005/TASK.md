# add-task: a task from its templates

`add-task TITLE [--depend N]` writes the next task's TASK.md and
BREAKDOWN.md from their templates, adds its line to WORKPLAN.md, and
opens the editor on TASK.md; `-m TEXT` writes the change and skips the
editor. Nothing is committed: accept-patch carries the files.

Effects:

- `wp add-task "Say goodbye" --depend 0000` creates the next task
  directory on the editable workplan
- over HTTP, POST /api/workplan/{id}/task takes the title, the
  dependencies and the text
- the page has a New task button, which asks for the title and the
  dependencies and opens the new task's panel in its editor
- README.md and SPEC.md section 4 name `add-task` as the way to write
  a task by hand

Depends: 0003
Change: feat
Audience: users
