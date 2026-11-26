# Breakdown

1. In `squash_message` in src/workplan/ops.py, read each listed,
   committed task's Breaking trailer with `plans.trailer`, and pass
   `breaking`: the lines, each ending in a newline, or empty.
2. In src/workplan/templates/documents/SQUASH_COMMIT_MSG, put
   `$breaking` at the start of the Workplan line, so the lines join
   the trailer paragraph.
3. Update SPEC.md sections 4 and 9.
4. In tests/test_fixes.py, check the message with and without a
   Breaking trailer.
