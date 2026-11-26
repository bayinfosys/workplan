# Breakdown

1. In `parse_patch` in src/workplan/agent.py, find the diff first, then
   search the text before it for the first line, stripped as now, that
   starts with `<workplan id>/<nnnn> `; return it with the diff.
2. In `use_patch`, when that line's task id is not the task's, return
   the error before applying anything.
3. In tests/test_manual.py, add tests: a reply naming another task is
   refused and leaves no output.patch; a reply whose diff holds a line
   starting with the task's id, and no commit line, gets COMMIT_MSG from
   the title.
