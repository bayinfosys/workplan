# init writes BACKLOG.md and dispatch.sh

`init` writes workplans/BACKLOG.md and workplans/dispatch.sh from new
project templates, with the other project files. dispatch.sh is
executable and runs `workplan gen-task` for gen-task, `workplan
gen-patch` for each target of gen-patch in parallel, and gen-patch
again for each stale task on review. config.toml names it in a
commented `dispatch` line.

Effects:

- `wp init` in a new repository creates and commits BACKLOG.md and
  dispatch.sh, and leaves existing ones alone
- setting `route.dispatch = "workplans/dispatch.sh"` and running
  `wp install` gives full auto
- templates/project/BACKLOG.md holds the file's heading and a sentence
  on the form of an item, and no items
- SPEC.md section 1's layout lists dispatch.sh as a file of the
  workplan command, and its by-hand init block matches what init
  writes
- README.md's command table, Configuration and Routing sections name
  both files

Depends on 0000.
