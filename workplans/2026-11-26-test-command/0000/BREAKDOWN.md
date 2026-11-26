# Breakdown

1. In src/workplan/config.py, add `"test": {"command": ""}` to DEFAULTS
   and WORKPLAN_TEST_COMMAND to OVERRIDES.
2. In `merge` in src/workplan/ops.py, take `test_command`; after
   `ready_to_merge`, when it is set, refuse unless the branch is
   checked out, run it with `shell=True`, and fail with the end of its
   output when it exits non-zero; add `tested` to the result.
3. In src/workplan/commands.py, pass `ctx.cfg["test"]["command"]`, and
   print the passed line in `render_merge`.
4. Add the `[test]` section to the project template's config.toml and
   to workplans/config.toml.
5. In README.md, add the row to the configuration table and the test
   to the merge row.
6. In tests/test_fixes.py, test a passing command, a failing one
   (nothing merged, branch still checked out, output shown), merge from
   another branch, and an empty command.
