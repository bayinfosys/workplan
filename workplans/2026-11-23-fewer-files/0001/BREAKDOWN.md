# Breakdown

1. state.py: delete `problems`.
2. ops.py: drop the `problems` import and the field in `task_status`.
3. cli.py: drop the loop over problems in `print_status`.
4. tests/test_cycle.py: delete `test_problems`.
5. README.md: the commands table's `status` row and any other mention
   of layout problems.
