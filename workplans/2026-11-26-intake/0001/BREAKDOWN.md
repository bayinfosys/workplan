# Breakdown

1. In `accept` in src/workplan/ops.py, after the branch check, refuse a
   task whose number is not in the Tasks list from `plans.listed`.
2. In tests/test_fixes.py, test a task directory with a patch and no
   line: the refusal, and the tree and HEAD unchanged.
