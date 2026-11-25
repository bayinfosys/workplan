# Breakdown

1. In `plan` in src/workplan/ops.py, create the draft inside a
   `tempfile.TemporaryDirectory()` and read it back before the
   directory is removed.
2. In `merge`, write the squash message draft inside a
   `tempfile.TemporaryDirectory()` that spans the merge and the
   commit, including the failure path.
3. In tests/test_fixes.py, after add-workplan through a scripted
   editor and after merge-workplan, check that .git/workplan does not
   exist.
