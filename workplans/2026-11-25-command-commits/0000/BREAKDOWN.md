# Breakdown

1. In src/workplan/ops.py, add `commit_paths(paths, message)`: stage
   the paths, return None when they hold no change, else commit them
   alone and return `%h %s`.
2. Call it from `plan`, `save_document`, `edit_document` and
   `add_task`; move the editor on TASK.md into `add_task` behind an
   `edit` argument, so the commit follows it.
3. In src/workplan/agent.py, call it from `add_tasks`.
4. In src/workplan/commands.py, add `committed(result)` and use it in
   the renderers of the five commands; update their help.
5. Add the two rules to workplans/PRINCIPLES.md.
6. Update README.md's walkthrough, command table and the paragraph on
   the editor, and SPEC.md section 4 and its by-hand block.
7. Update the tests that expect these commands to leave files
   uncommitted; check the commit messages and that an unchanged edit
   commits nothing.
