# Notes 2026-11-24-command-interface/0005: add-task: a task from its templates

Did the patch change anything TASK.md does not state?

Yes. The TASK.md template gained the value `$change`, in place of the
line `<The change, in a sentence or two.>`, so that `add-task -m TEXT`
writes the change through the template. With no text, `$change` is
filled with that same line. SPEC.md section 4 lists the new value.
