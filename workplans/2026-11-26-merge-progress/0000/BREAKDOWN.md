# Breakdown

1. In `merge` in src/workplan/ops.py, add `on_test: Callable[[str],
   None] | None = None`, and call it before `run_tests`.
2. In `cmd_merge_workplan` in src/workplan/commands.py, pass a function
   writing the line to stderr when `ctx.interactive`.
3. In tests/test_fixes.py, check the line on stderr for a passing merge,
   and its absence for a merge refused before the tests.
