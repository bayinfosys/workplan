# Breakdown

1. In src/workplan/ops.py, add `review(task, master)`, returning the
   task's id, state, title, COMMIT_MSG or None, its dependencies with
   their states, the stat of output.patch, and the diff from `diff`.
2. In src/workplan/commands.py, have `cmd_show_patch` return
   `ops.review`, and add `render_patch`, which prints the header lines
   and the diff.
3. In README.md, update the show-patch line of the walkthrough and its
   row in the command table.
4. In tests/test_manual.py or a test module of its own, check the
   header lines for a task with a dependency, and `--json`.
