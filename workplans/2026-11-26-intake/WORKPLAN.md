# Workplan 2026-11-26-intake: intake

## Goal

A workplan can start from a whole WORKPLAN.md, with no placeholder
goal, and `patch accept` takes only tasks that WORKPLAN.md lists.

## Context

- src/workplan/ops.py: `plan` renders WORKPLAN.md from its template with
  a goal, or opens the editor on it, then branches and commits; `accept`
  checks the branch, COMMIT_MSG and the task's state
- src/workplan/commands.py: `cmd_new_workplan`, with `-m`; `read_reply`
  reads a reply from a file or standard input on the CLI, and takes the
  text over HTTP, as `task add --reply` and `patch add` do
- src/workplan/plans.py: `listed`, the task numbers under Tasks and
  Dropped
- README.md: the command table and the paragraph on `new`

## Findings

- a WORKPLAN.md written elsewhere, by a chat or another person, goes in
  through `wp new NAME -m x` and an edit, so a commit with the goal "x"
  comes first; on 2026-11-26 two workplans reached master with "x" as
  their goal
- `patch accept` committed a task that WORKPLAN.md did not list: the
  task directory and its patch were enough

## Decisions

1. `wp new NAME --reply FILE` takes a whole WORKPLAN.md, from a file or
   standard input on the CLI and as text over HTTP, and commits it as
   `<id> workplan`. `--reply` and `-m` are not given together.
2. A reply whose heading names another workplan id is refused, with
   both ids in the error.
3. `patch accept` refuses a task that is not listed under Tasks in
   WORKPLAN.md, and says to add its line; writing the files by hand
   stays possible, with the line added by hand as well.

## Tasks

0000  new takes a whole WORKPLAN.md with --reply
0001  patch accept refuses a task WORKPLAN.md does not list

## Dropped
