# Workplan 2026-11-26-reply-task: reply task

## Goal

`patch add` refuses a reply whose commit message line names another
task, so a reply saved under the wrong name cannot be accepted as the
wrong task.

## Context

- src/workplan/agent.py: `parse_patch` takes the first line, anywhere
  in the reply, that starts with the task's id as the commit message,
  and the diff from the first fenced block holding one, else from the
  first diff header; `use_patch` applies the diff and writes COMMIT_MSG;
  `commit_message` falls back to TASK.md's title when COMMIT_MSG is
  missing, with a note
- `patch add` and the none agent's `patch gen` both go through
  `use_patch`; for the none agent, an error goes back to the model with
  a retry
- tests/test_manual.py: the patch add tests

## Findings

- on 2026-11-26, the reply for command-groups/0003 was saved as the
  reply for 0000; `patch add 0000` found no line for 0000, wrote
  COMMIT_MSG from 0000's title with a note, and applied 0003's diff,
  which `patch accept 0000` committed as 0000
- the commit message line is searched for through the whole reply,
  diff included, so a context line of a diff that starts with a task
  id could be taken for it

## Decisions

1. The commit message line is looked for in the reply before its diff
   alone.
2. When the first line there that starts with a task id of this
   workplan names another task, the reply is refused, with both ids in
   the error, and nothing is written.

## Tasks

0000  patch add refuses a reply whose commit line names another task

## Dropped
