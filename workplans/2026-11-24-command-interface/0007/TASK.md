# drop-task and drop-patch

`drop-task NNNN` moves the task's line from `## Tasks` to `## Dropped`
and commits WORKPLAN.md as `<id> drop <nnnn>`. `drop-patch NNNN`
deletes the task's output.patch and COMMIT_MSG.

Effects:

- a dropped task reads `dropped` in status and no longer blocks
  merge-workplan
- drop-task refuses a task that is committed; drop-patch refuses a
  patch that is applied
- the page's panel has Drop task and Drop patch, each asking first
- README.md lists both

Depends: 0003
Change: feat
Audience: users
