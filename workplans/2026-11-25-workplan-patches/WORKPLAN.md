# Workplan 2026-11-25-workplan-patches: workplan patches

## Goal

A patch can change files under workplans/, such as another task's
NOTES.md or PRINCIPLES.md, whether it comes from gen-patch or from
add-patch.

## Context

- src/workplan/agent.py: `in_worktree` copies workplans/ into the
  worktree, so uncommitted documents are seen, then runs agent.setup;
  `capture` stages and diffs everything outside workplans/ (`EXCLUDE`);
  the module docstring describes the steps
- src/workplan/ops.py: `GITIGNORE`, the working files output.patch and
  COMMIT_MSG
- src/workplan/templates/prompts/gen-patch.md: tells the agent to
  change nothing under workplans/ but the commit message file
- README.md, Agents; SPEC.md section 11, the steps and the by-hand
  block
- tests/test_by_hand.py: test_gen_patch runs the by-hand block

## Findings

- workplans/ is left out of the diff because the worktree holds the
  copy of workplans/ from the maintainer's tree, whose uncommitted
  documents would otherwise show as part of the change
- so a patch cannot change any file under workplans/: 0005 of
  2026-11-25-follow-ups, which wrote NOTES.md files, went by hand

## Decisions

1. The worktree as the agent receives it, after the copy and
   agent.setup, is staged and kept as a tree with `git write-tree`;
   the patch is the diff from that tree, over the whole repository.
2. output.patch and COMMIT_MSG under workplans/ are left out of the
   diff by pathspec, as well as by .gitignore.
3. The gen-patch prompt lets the agent change files under workplans/
   where TASK.md says so.

## Tasks

0000  A patch is the diff from the worktree as the agent receives it

## Dropped
