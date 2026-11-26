# Breakdown

1. In `plan` in src/workplan/ops.py, take `text`: when given, check its
   heading's id against the new id before branching, and write it in
   place of the rendered template.
2. In `cmd_new_workplan` in src/workplan/commands.py, add the `reply`
   flag; read it with `read_reply`; refuse it with `-m`.
3. In README.md, add `--reply FILE` to the `new` row and a sentence to
   the paragraph on `new`.
4. In tests/test_cycle.py, test a reply from a file and from standard
   input, a reply for another id, and `-m` with `--reply`.
