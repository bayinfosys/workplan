# Workplan 2026-11-27-launch: launch

## Goal

A new user can install workplan, point it at a repository whose parent
branch has any name, find out what to do without an agent, and try it
on this repository's own history. README.md states what the project
is for, and how to remove it; PROTOCOL.md has a glossary and a version
policy.

## Context

- src/workplan/config.py: DEFAULTS `"master": "master"`, overridden by
  WORKPLAN_MASTER; src/workplan/commands.py: `Context(cfg,
  cfg["master"], ...)`; route.py reads `cfg["master"]`
- src/workplan/templates/project/config.toml and workplans/config.toml:
  `master = "master"`
- src/workplan/ops.py: `init`; src/workplan/llm.py or agent.py: the
  "no model configured" failure
- README.md: Install, the walkthrough, "examples/demo.sh runs this
  cycle", Development; PROTOCOL.md: the introduction, section 5, the
  preamble's `$master`
- CHANGELOG.md: the hand-written 0.1.0 section
- tags: v0.2.0 is on c6515ce, a commit of the change-kinds definition
  branch, not on master

## Findings

- in a repository whose branch is `main`, `wp new` fails: "no branch
  master, locally or on origin"
- with no agent configured, `task gen` and `patch gen` fail with "no
  model configured" and no way on
- README.md names examples/demo.sh, which is not in the repository
- this repository holds nineteen workplans since v0.1.0, readable with
  `wp list`, `wp serve` and `wp changelog`
- PROTOCOL.md section 5 says testing is not recorded and assistants do
  not commit; merge runs test.command, and commands commit
- v0.2.0 was tagged on c6515ce, on the change-kinds definition branch,
  so master does not contain it: `git describe` on master finds
  v0.1.0, and the package built from master is versioned 0.1.1.devN
- PyPI's 0.2.0 was built from c6515ce: its README and its
  Specification URL link SPEC.md, which master no longer has

## Decisions

1. The parent branch is the config key `parent`, with
   WORKPLAN_PARENT; `init` writes the branch checked out when it runs.
   README.md and PROTOCOL.md say "parent branch", and PROTOCOL.md's
   blocks use `$parent`. The code's own names stay as they are.
2. No interactive setup. With no agent, the failure names the three
   ways on: `agent.name` claude-code or codex; `llm.api_base` for the
   none agent; `--prompt` with a chat, then `task add --reply` or
   `patch add`.
3. README.md:
   - after the opening, two points: git as state, and a protocol, not
     a service
   - "Try it on this repository": clone it, install, `wp list`,
     `wp serve`, `wp changelog v0.1.0`
   - the examples/demo.sh line is removed
   - a line under Install: Linux, with git and Python 3.11
   - "Removing workplan": the hooks, the .gitignore lines, workplans/,
     and the package
4. PROTOCOL.md: a glossary of workplan, task, patch, state and parent
   branch at the top; a version line: 0.x, pre-1.0, changed without
   compatibility until 1.0, versioned with the package's minor
   version; section 5 corrected.
5. CHANGELOG.md: a section for v0.1.0 to master, from `wp changelog`,
   above the hand-written 0.1.0 section, headed as the next release.
6. The next release, v0.3.0, is tagged on master, by Release; v0.2.0
   stays where it is, as published. PROTOCOL.md's version is then 0.3.

## Tasks

0000  The parent branch is the config key parent, written by init
0001  With no agent, the failure says how to go on
0002  README.md for a new user
0003  PROTOCOL.md: glossary, version and the parent branch

## Dropped
