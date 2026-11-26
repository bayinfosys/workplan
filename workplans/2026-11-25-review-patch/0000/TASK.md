# show-patch heads the diff with the task, its commit and its dependencies

show-patch prints a header before the diff: the task's id, state and
title; its COMMIT_MSG; each task it depends on with that task's state;
and the files the patch changes, as `git apply --stat` gives them.

Effects:

- `workplan show-patch 0000` prints the header, a blank line, then the
  diff, through the pager as now
- the result adds `task`, `state`, `title`, `commit_msg`, `depends`
  and `stat` to `text`; `--json` and the HTTP route return them
- a task with no COMMIT_MSG shows `(none)` in its place
- README.md's walkthrough and command table describe the header

Depends: none
Change: feat
Audience: users
