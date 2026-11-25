# Workplan 2026-11-25-task-lines: task lines

## Goal

Task lines that workplan adds to WORKPLAN.md follow one another, as in
SPEC.md section 3.

## Context

- src/workplan/plans.py: `add_task_line`, used by add-task, gen-task,
  add-task --reply and, through `move_task_line`, drop-task
- SPEC.md section 3: the task line format, lines one after another
- tests/test_cycle.py and tests/test_drop.py: assertions on the text
  of the Tasks and Dropped sections

## Findings

- `add_task_line` puts a blank line before each task line it adds, so
  a section reads with a blank line between tasks; seen in
  2026-11-25-follow-ups

## Decisions

1. A task line added to a section follows the last line of the section
   with no blank line; the section keeps a blank line after its heading
   and before the next heading.

## Tasks

0000  Task lines follow one another in WORKPLAN.md

## Dropped
