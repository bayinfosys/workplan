# Read workplans held on other branches

`status` and a new `workplans` operation find workplans on local and
origin definition branches, as well as in the working tree, and read
their documents with git; a workplan read from a branch carries its
committed states only, and is not editable.

Effects:

- `wp status <id>` shows a workplan held only on another branch, with
  `merged`, `complete`, `dropped`, `refinement` or `unspecified` per task
- `ops.workplans` lists every workplan with its source (the tree or a
  ref), its branch, and whether it is current and editable
- `ops.document` reads WORKPLAN.md or a task file from either source
- `status --json` gives each workplan's source and whether it is
  editable

Depends on none.
