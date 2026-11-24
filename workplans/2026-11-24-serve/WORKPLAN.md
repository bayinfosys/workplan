# Workplan 2026-11-24-serve: serve

## Goal

`workplan serve` opens a local web page that shows every workplan as a
board of task states and runs the whole flow from the browser: plan,
editing WORKPLAN.md and the task files, define-tasks, produce-patch,
apply, diff, accept, reject and merge. Workplans held on other
branches are shown read-only, read from their definition branches.

## Context

- src/workplan/ops.py: the operations, each returning data;
  `status` reads a workplan from the working tree only; `merge` opens
  the editor on the squash message, or with edit=False commits the
  rendered template
- src/workplan/plans.py: ids, documents, templates and states, read
  from files under workplans/; `title` and `goal` take paths
- src/workplan/agent.py: `define_tasks` and `produce_patch`, each
  minutes long with a real agent
- src/workplan/cli.py: argparse; formats what the operations return
- pyproject.toml: package-data holds templates/*/* only
- tests/support.py: `Repo`, `scripted_agent`, `agent_env`, `planned`
- README.md: commands, configuration, agents; TODO.md lists serve
  first under Next
- the design, agreed in discussion: bound to 127.0.0.1; a token printed
  at startup on every API request; standard library only; page files
  in src/workplan/web/; Markdown rendered by a renderer of our own;
  one operation at a time; the page refreshes from status every few
  seconds; plan and merge included; other workplans read-only

## Findings

- a workplan on another branch is invisible to `status`, though its
  files are on its definition branch (0000)
- nothing writes a document but an editor, and `merge` takes its
  message only from the editor or the template (0001)
- there is no server (0002)
- there is no page (0003)

## Decisions

1. A workplan is editable only when its definition branch is checked
   out; every other workplan is read-only.
2. Workplans on other branches are read from local definition
   branches first, then from origin's.
3. The server answers only requests whose Host is 127.0.0.1 or
   localhost on its port and that carry the token, so another site in
   the browser can neither read nor write.
4. Writes are confined to WORKPLAN.md and the task files of the
   editable workplan; commits still happen only through define-tasks,
   accept, plan's branch and merge.
5. The server holds no state of its own beyond the token and the lock.
6. No JavaScript dependencies: the page's Markdown and diff rendering
   are our own.

## Tasks

0000  Read workplans held on other branches

0001  Write documents of the editable workplan, and merge with a given message

0002  Serve the operations over HTTP on 127.0.0.1

0003  The board page

## Dropped
