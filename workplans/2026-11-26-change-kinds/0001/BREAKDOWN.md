# Breakdown

1. Replace the last line of src/workplan/templates/documents/TASK.md
   with the trailer block.
2. In `add_task` in src/workplan/ops.py, render `$depends` as the
   Depends value: numbers joined by ", ", or none.
3. Update the two task-gen prompts.
4. Update SPEC.md section 3, its example and the states table; and
   README.md.
5. Update the tests that read the template's last line, and check
   that a task written by `task add` parses with `plans.trailers`.
