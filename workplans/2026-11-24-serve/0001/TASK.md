# Write documents of the editable workplan, and merge with a given message

`save_document` writes WORKPLAN.md or a task file of the editable
workplan, and nothing else; `merge` takes a message in place of the
editor, and `merge_message` returns the rendered template for editing
elsewhere.

Effects:

- `ops.save_document(wid, name, text)` writes only when the
  workplan's definition branch is checked out and name is one of the
  four document names; it commits nothing
- `ops.merge(id, master, message=...)` commits with that message and
  opens no editor
- `ops.merge_message(id, master)` returns the message `merge` would
  open in the editor

Depends on 0000.
