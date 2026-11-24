# Breakdown

1. ops.py: `add_task(wid, title, depends, text)`: checks the workplan
   is editable and each dependency exists; renders TASK.md and
   BREAKDOWN.md; adds the task line; returns the task id.
2. commands.py: `cmd_add_task`, with the editor on TASK.md when no
   text is given on the CLI.
3. web: api.js `addTask`; a New task dialog; the panel opens on the
   new task in its editor.
4. tests: the files and the task line; a missing dependency; a
   read-only workplan.
5. README.md, SPEC.md section 4.
