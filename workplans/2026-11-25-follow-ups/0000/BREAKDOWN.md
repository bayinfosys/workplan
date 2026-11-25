# Breakdown

1. In src/workplan/ops.py, add a line to `HOOK` after the
   `command -v` line that unsets the ten variables.
2. In tests/test_fixes.py, add a test that runs `install`, then runs
   .git/hooks/post-commit with GIT_INDEX_FILE set to a path outside
   the repository and `WORKPLAN_ROUTE_DISPATCH` set to a command that
   writes its arguments and `$GIT_INDEX_FILE` to a file, waits for
   the file, and checks the route was dispatched with GIT_INDEX_FILE
   empty.
3. In README.md's Routing section, add a sentence after the
   description of `workplan install`: the hooks clear the variables
   git sets for hooks, so that commands run by dispatch work in their
   own worktrees.
