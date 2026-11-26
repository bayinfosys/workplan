# Workplan 2026-11-26-sequence: sequence

## Goal

README.md and PRINCIPLES.md state what the library adds over the
by-hand steps: it runs each step's git operations in order, and it
reads and changes the repository through git commands only. Release
and provenance enter the backlog.

## Context

- README.md: "Manual, semi-automatic, full auto"
- workplans/PRINCIPLES.md
- workplans/BACKLOG.md: items in priority order

## Findings

- each step is several git operations in a fixed order; README does
  not say the commands exist to keep that order
- state is read with git (log, show, interpret-trailers, describe);
  no principle records it

## Decisions

1. README: a paragraph after the three modes: steps can be done by
   hand; the library ensures the order of their git operations.
2. PRINCIPLES.md: the library ensures the order of git operations
   within a step; the repository is read and changed through git
   commands only; a command exists where order matters.
3. BACKLOG.md: Release, then Provenance, at the top.

## Tasks

0000  README and PRINCIPLES.md on sequence and git; release and provenance in the backlog

## Dropped
