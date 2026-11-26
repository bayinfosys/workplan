# Workplan 2026-11-26-protocol: protocol

## Goal

PROTOCOL.md defines the protocol: the files, their formats, the
states, the branches, and each protocol command as the git commands it
performs, in order, for anyone implementing the process or proposing a
change to it. SPEC.md is removed. README.md is the usage, and
separates the protocol commands from the supporting commands, which
read git but change nothing in the protocol. PRINCIPLES.md guides
development.

## Context

- SPEC.md: sections 1 to 13; formats and rules, with "By hand" blocks
  in sections 1, 4, 5, 6, 7, 9 (merge, changelog), 10, 11 and 12
- README.md: the command table, in three groups; links SPEC.md in its
  introduction, the modes, the sequence paragraph, Routing and
  Development
- workplans/PRINCIPLES.md: "SPEC.md gives the step, and a change to a
  step changes SPEC.md in the same task"
- tests/test_by_hand.py: compares each command with a by-hand script;
  its docstring names SPEC.md
- src/workplan/commands.py: the registry
- src/workplan/templates/project/README.md and pyproject.toml's
  Specification URL: link SPEC.md

## Findings

- SPEC.md mixes the protocol (files, states, git steps) with the
  library's own features (routing, agents, templates of prompts)
- several commands have no git steps written down: edit, task edit,
  task drop, task gen, patch add, patch drop
- the commands fall into two kinds: protocol commands, which change
  the repository in the protocol's terms (init, new, edit, merge, task
  add, gen, edit, drop, patch add, gen, apply, accept, reject, drop),
  and supporting commands, which read git or run the library (list,
  show, status, task show, patch show, changelog, route, install,
  serve)

## Decisions

1. PROTOCOL.md, in order: the layout and identifiers; the documents
   and their formats, the trailer block included; the states, as git
   reads; the branches; then each protocol command, in README's order,
   as its `wp` form, a sentence, and a bash block of git commands with
   arguments and comments aligned, after a preamble naming the
   variables ($w, $n, $t, $b, $master). An editor or agent step is a
   comment line; for task gen and patch gen the protocol fixes the
   files produced, and the worktree is how the library does it.
2. Merge's preconditions, the review questions and working together
   are protocol: they go into PROTOCOL.md.
3. Routing, agents, prompt templates and the changelog are the
   library's: they go into README.md, which already describes most of
   them.
4. SPEC.md is deleted; nothing links it.
5. README.md's command table lists the protocol commands first, then
   the supporting commands, each group saying which it is; protocol
   rows link their PROTOCOL.md section.
6. PRINCIPLES.md: PROTOCOL.md defines the protocol; a change to a
   protocol command's git steps or to a format changes PROTOCOL.md in
   the same task.
7. A test checks that every protocol command in the registry has a
   section in PROTOCOL.md.
8. The project template's README and pyproject.toml link PROTOCOL.md.

## Tasks

0000  Mark the protocol commands in the registry
0001  PROTOCOL.md: files, formats, states and branches
0002  PROTOCOL.md: each protocol command as git commands
0003  README.md: protocol and supporting commands, and the library's features
0004  Remove SPEC.md

## Dropped
