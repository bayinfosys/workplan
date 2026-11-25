# Workplan 2026-11-25-review-patch: review patch

## Goal

`workplan show-patch` gives what a review of a patch needs in the
terminal: the task, its state, its commit message, the tasks it
depends on and their states, the files it changes, and the diff.

## Context

- src/workplan/commands.py: `cmd_show_patch` returns `{"text": diff}`
  and renders the text; `cmd_show_task` gathers a task's state from
  `ops.status`
- src/workplan/ops.py: `diff`, the staged change when the patch is
  applied, else output.patch
- src/workplan/plans.py: `depends_on`
- src/workplan/cli.py: show-patch output goes through the pager
- src/workplan/web/app.js: the board reads `text` from show-patch

## Findings

- show-patch prints the diff alone; the state, the commit message and
  the dependencies each take another command

## Decisions

1. show-patch gains a header; no new command, as PRINCIPLES.md asks
   for an existing command in preference to a new one.
2. The result keeps `text`, the diff, so the board is unchanged.

## Tasks

0000  show-patch heads the diff with the task, its commit and its dependencies

## Dropped
