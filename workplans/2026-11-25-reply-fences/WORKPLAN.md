# Workplan 2026-11-25-reply-fences: reply fences

## Goal

add-patch and the none agent take a reply whose diff changes a
Markdown file with code blocks in it.

## Context

- src/workplan/agent.py: `FENCE`, the pattern for a fenced block in a
  reply; `parse_patch`, which takes the first fenced block holding a
  diff, else the reply from its first diff header
- src/workplan/templates/prompts/gen-patch-none.md: asks for the diff
  in a fenced block
- tests/test_manual.py: the add-patch tests

## Findings

- `FENCE` ends a block at the first three backticks anywhere in the
  reply, so a diff with a context or added line of three backticks is
  cut there and does not apply
- with no fence, the same pattern finds a block that starts and ends
  on such lines inside the diff, and takes it for the patch
- found while applying 2026-11-25-follow-ups, whose patches to README.md
  and SPEC.md went by hand for this reason

## Decisions

1. A fence opens and closes only at the start of a line. Every line of
   a diff's body starts with a space, `+`, `-` or a backslash, so no
   line inside a diff can open or close a fence.

## Tasks

0000  Fences in a reply open and close at the start of a line

## Dropped
