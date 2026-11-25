# Workplan 2026-11-25-command-commits: command commits

## Goal

Every workplan command that changes a document commits it, on the
checked-out branch; and PRINCIPLES.md holds the two rules this follows.

## Context

- src/workplan/ops.py: `plan` (add-workplan), `add_task`,
  `save_document` and `edit_document` (edit-workplan, edit-task, and
  the board's Save) write files and commit nothing; `drop_task` commits
  WORKPLAN.md alone with `git commit -- <path>`
- src/workplan/agent.py: `add_tasks` (add-task --reply) writes tasks
  and commits nothing; `gen_task` commits WORKPLAN.md and the new tasks
  as `<id> define tasks`
- src/workplan/commands.py: `cmd_add_task` opens the editor on TASK.md
  after `ops.add_task`
- workplans/PRINCIPLES.md
- README.md: the walkthrough, the command table and the paragraph on
  the editor; SPEC.md section 4: add-task and its by-hand block
- tests: test_cycle, test_fixes, test_manual and test_by_hand assert
  that these commands leave their files uncommitted

## Findings

- add-workplan, add-task, add-task --reply, edit-workplan and
  edit-task leave their change for the maintainer to commit, while
  gen-task, accept-patch, drop-task and merge-workplan commit; the by
  hand path needed git where the agent path did not, seen in
  2026-11-25-follow-ups
- the maintainer's decisions of 2026-11-25: workplan commands always
  commit their changes; commands edit the checked-out branch only

## Decisions

1. A command that changes a document commits that document alone, with
   `git commit -- <paths>`, so other staged changes stay staged.
2. The messages: add-workplan `<id> workplan`; add-task
   `<id> add <nnnn>`; add-task --reply `<id> define tasks`, as gen-task;
   edit-workplan and edit-task `<id> edit <document>`, where document
   is WORKPLAN.md or `<nnnn>/<name>`. No message starts with a task id
   and a space, so none reads as a task's commit.
3. An edit that changes nothing commits nothing, and says so.
4. add-task commits after the editor closes on TASK.md.
5. The board's Save commits, as edit-task does.
6. PRINCIPLES.md: a command that changes a document commits it;
   commands write to the checked-out branch only, and add-workplan and
   merge-workplan are the commands that change branches.

## Tasks

0000  Commands commit the documents they change

## Dropped
