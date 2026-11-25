# Breakdown

1. Add src/workplan/templates/project/BACKLOG.md: a `# Backlog`
   heading and a paragraph saying each `## ` heading is an item, in
   order of priority.
2. Add src/workplan/templates/project/dispatch.sh: a /bin/sh script
   taking `<action> <target>...`, with a case for gen-task, gen-patch
   and review; review reads `workplan status --json` with python3 and
   runs gen-patch for each task in the state `stale`.
3. In `init` in src/workplan/ops.py, add BACKLOG.md and dispatch.sh
   to the names written, and set the executable bits on dispatch.sh.
4. In src/workplan/templates/project/config.toml, add a commented line
   under `dispatch = ""`: `# dispatch = "workplans/dispatch.sh"`.
5. In SPEC.md section 1, add dispatch.sh to the layout with a
   one-line description, and add it to the by-hand init block.
6. In README.md, update the `init` row of the command table, and name
   dispatch.sh in the Configuration and Routing sections.
7. In tests/test_by_hand.py's test_init, add the two files to the
   by-hand script; in tests/test_fixes.py, check dispatch.sh is
   executable after init.
