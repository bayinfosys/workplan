# Workplan 2026-11-26-old-names: old names

## Goal

No comment or sentence in the repository names a command by its old
name, and README.md says which commands commit.

## Context

- tests/test_drop.py: its docstring names drop-task and drop-patch
- tests/test_cycle.py: a section comment names add-task
- README.md, after the walkthrough: "The commands commit what they
  complete: `init`, `task gen`, `patch accept` and `merge`."; the
  paragraph after the editor lists what each document command commits

## Findings

- 2026-11-25-command-groups/0000 renamed the commands the tests run,
  and left two comments with the old names
- since 2026-11-25-command-commits, new, task add, task edit and edit
  commit as well; the README sentence lists four commands

## Decisions

1. The README sentence lists every command that commits, and says
   patch apply stages a patch for review and commits nothing.

## Tasks

0000  The last old names in comments, and the commands that commit in README.md

## Dropped
