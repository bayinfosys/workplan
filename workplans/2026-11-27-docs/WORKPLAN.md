# Workplan 2026-11-27-docs: docs

## Goal

GETTING_STARTED.md takes a new user from install to a merged
workplan; README.md is an overview that links it and PROTOCOL.md.
These, with CHANGELOG.md, are the documents the website publishes.
PRINCIPLES.md gains a short Code section for agents, and the backlog
gains the Review page.

## Context

- README.md: 469 lines; Install, Try it on this repository, the three
  modes, the walkthrough, Commands, Manual mode with a chat, Changelog,
  Configuration, Agents, Routing, Serve, Templates, Development,
  Removing workplan
- PROTOCOL.md, CHANGELOG.md
- workplans/PRINCIPLES.md: read by agents in the patch-gen prompt
- workplans/BACKLOG.md: Page polish, Review agent

## Findings

- README.md mixes the first steps with the reference, so a new user
  reads 469 lines to find them
- the website at workplan.bayis.co.uk is built from README.md,
  GETTING_STARTED.md, PROTOCOL.md and CHANGELOG.md on master; each must
  read on its own, with links between them by file name
- agent patches carry narrating comments, docstrings that restate
  names and checks for cases that cannot happen; PRINCIPLES.md does not
  say not to

## Decisions

1. GETTING_STARTED.md: install; try it on this repository; a first
   workplan without an agent (new, task add, patch gen --prompt with a
   chat, patch add, patch accept, merge, publish); then with an agent.
   Short, and every command runs as written.
2. README.md keeps the opening, the two points, Install, Commands,
   Configuration, Development, Removing workplan and Licence, and links
   GETTING_STARTED.md and PROTOCOL.md. The walkthrough and the
   first-steps sections move to GETTING_STARTED.md; Manual mode,
   Changelog, Agents, Routing, Serve and Templates stay, as reference.
3. PRINCIPLES.md: a Code section of a few lines, for agents.
4. BACKLOG.md: Review page replaces Page polish and Review agent.

## Tasks

0000  GETTING_STARTED.md, and README.md as overview and reference
0001  A Code section in PRINCIPLES.md, for agents
0002  The Review page in the backlog

## Dropped
