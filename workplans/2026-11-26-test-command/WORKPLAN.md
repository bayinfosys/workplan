# Workplan 2026-11-26-test-command: test command

## Goal

A project names its test command once, in config.toml, and `wp merge`
runs it on the workplan's branch before squashing, refusing to merge
when it fails. This repository's own tests run that way, and README.md
says how to run them.

## Context

- src/workplan/config.py: DEFAULTS and OVERRIDES, the WORKPLAN_
  variables
- src/workplan/templates/project/config.toml and workplans/config.toml:
  every key, with comments
- src/workplan/ops.py: `merge` checks the workplan with
  `ready_to_merge`, then switches to master and squashes
- src/workplan/commands.py: `cmd_merge_workplan` and `render_merge`;
  `Context.cfg`
- src/workplan/agent.py: agent.setup, a shell command, is run with
  `shell=True` and its output shown on failure
- .github/workflows/test.yml: `python -m unittest discover -s tests -v`
- README.md: configuration and the merge row; SPEC.md section 9,
  merging, with its by-hand block; workplans/PRINCIPLES.md
- workplans/BACKLOG.md: the Test command item

## Findings

- nothing runs the tests before a merge; the maintainer has to
  remember the command, and README.md does not give it
- unwind, on the backlog, needs the same command to tell a passing task
  commit from a failing one

## Decisions

1. One key, `test.command`, a shell command, with WORKPLAN_TEST_COMMAND
   to override it; empty by default. Unwind will use the same key.
2. `wp merge` runs it, when set, in the working tree with the
   workplan's branch checked out, before switching to master; when it
   fails, nothing is merged and the end of its output is shown. With
   another branch checked out, merge refuses while a command is set.
3. There is no flag to skip it: `WORKPLAN_TEST_COMMAND= wp merge` runs
   none. `merge --show` runs nothing.
4. The result says the command passed; the board's Merge runs it too.
5. This repository sets `test.command` to its unittest command.
6. PRINCIPLES.md: each accepted task leaves the test suite passing;
   tasks may add to it; the suite exists before the workplan.
7. SPEC.md: the tests run before the squash, in the by-hand block too;
   the definition branch may be rewritten until it is merged.
8. The Test command item leaves BACKLOG.md.

## Tasks

0000  merge runs test.command before squashing
0001  PRINCIPLES.md, SPEC.md and README.md on the tests; the backlog item

## Dropped
