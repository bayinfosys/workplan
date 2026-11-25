# Task lines follow one another in WORKPLAN.md

`add_task_line` adds a task line straight after the last line of the
section, with no blank line between task entries.

Effects:

- gen-task, add-task, add-task --reply and drop-task leave the Tasks
  and Dropped sections with one task entry per line, continuation
  lines included, and a blank line only after the heading and before
  the next heading
- reading WORKPLAN.md is unchanged: a section with blank lines between
  its entries reads as before

Depends on none.
