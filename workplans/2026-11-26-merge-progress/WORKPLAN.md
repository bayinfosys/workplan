# Workplan 2026-11-26-merge-progress: merge progress

## Goal

`wp merge` says it is running test.command before the tests start, so
the wait that follows reads as the tests running.

## Context

- src/workplan/ops.py: `merge` calls `run_tests` after `ready_to_merge`;
  the tests run with their output captured, and nothing is printed
  until they finish
- src/workplan/commands.py: `cmd_merge_workplan`; `ctx.interactive` is
  true on the CLI and false over HTTP
- PRINCIPLES.md: operations return data; the CLI and the web server
  format it

## Findings

- this repository's suite takes about a minute, and `wp merge` prints
  nothing in that time

## Decisions

1. `merge` takes an optional callback, called with the command just
   before the tests run; the operation itself prints nothing.
2. On the CLI the callback writes "running test.command: <command>" to
   stderr; over HTTP there is none.

## Tasks

0000  merge says it is running test.command

## Dropped
