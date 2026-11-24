# Workplan 2026-11-24-command-interface: command interface

## Goal

Every workplan command is declared once, as a function named for its
verb and noun, and that declaration gives both its CLI subcommand and
its HTTP method and route. The commands are `verb-noun` over three
nouns, `workplan`, `task` and `patch`, with `wp status` kept for
`list-task`. The page calls the API through one small `api.js`. New
commands give manual mode in the terminal and the page: adding a task
by hand, adding a patch from a pasted reply, printing the agent's
prompt, and dropping a task or a patch.

## Context

- src/workplan/cli.py: argparse, 13 subcommands mapped by hand to
  ops.py and agent.py; formats results as text
- src/workplan/serve.py: http.server, 5 read routes and `/api/run`
  mapped by hand to the same functions; the token and Host checks, the
  write lock
- src/workplan/web/app.js: calls `/api/workplans`, `/api/status`,
  `/api/document`, `/api/diff`, `/api/merge-message` and `/api/run`
- src/workplan/ops.py and src/workplan/agent.py: the operations, each
  returning data
- src/workplan/route.py: actions `define-tasks` and `produce-patch`
  are named for the commands that carry them out
- src/workplan/agent.py: the `none` adapter's reply parsing
  (`parse_patch`, `parse_files`) and the prompt templates
- tests/: drive the CLI by name through `Repo.wp`; test_serve.py
  drives the API by route
- README.md and SPEC.md sections 5 to 11 name the commands
- https://pypi.org/project/cliapi/: one registry of command functions
  giving argparse and FastAPI; its conventions are followed here
  without its dependency on FastAPI

## Findings

- every command is declared twice, in cli.py and serve.py, and the
  page names a third set of routes (0000, 0001, 0002, 0003)
- the command names mix nouns, verbs and protocol terms: `plan`,
  `define-tasks`, `produce-patch`, `apply`, `diff`, `accept`, `merge`
  (0001, 0004)
- no command adds a task by hand, takes a pasted reply as a patch, or
  prints the prompt an agent would get, so manual mode needs files
  written by hand (0005, 0006)
- dropping a task or a patch means editing WORKPLAN.md or deleting
  files by hand (0007)

## Decisions

1. Commands are `verb-noun`. The nouns are `workplan`, `task` and
   `patch`, singular throughout.
2. Each verb has one meaning and one HTTP method:

   | Verb | Means | HTTP |
   |---|---|---|
   | list | every item of a kind | GET on the collection |
   | show | one item | GET on the item |
   | add | you supply it: a template, or a pasted reply | POST on the collection |
   | gen | the agent produces it | POST on .../gen |
   | edit | change its document | PUT on the item |
   | drop | close or remove it | DELETE on the item |
   | apply, accept, reject, merge | the protocol's state changes | POST on .../verb |

3. The commands, with the names they replace:

   | Command | Replaces |
   |---|---|
   | list-workplan | page only |
   | show-workplan [ID] | status ID |
   | add-workplan NAME [-m GOAL] | plan |
   | edit-workplan [ID] | page save |
   | merge-workplan [ID] | merge |
   | list-task [ID], and status | status |
   | show-task NNNN | status ID/NNNN |
   | add-task TITLE [--depend N] | new |
   | gen-task [ID] [--prompt] | define-tasks |
   | edit-task NNNN [--doc NAME] | page save |
   | drop-task NNNN | WORKPLAN.md by hand |
   | show-patch NNNN | diff |
   | add-patch NNNN [FILE] | new |
   | gen-patch NNNN [--prompt] | produce-patch |
   | apply-patch, accept-patch, reject-patch NNNN | apply, accept, reject |
   | drop-patch NNNN | rm by hand |

   `init`, `route`, `install` and `serve` keep their names; `init`,
   `install` and `serve` are CLI only.
4. `status` stays, as a second name for `list-task`. Every other old
   name is removed, with no aliases.
5. The registry is part of workplan and uses the standard library only.
   A command is a function `cmd_<verb>_<noun>` with keyword-only
   parameters; the declaration marks which are positional on the CLI
   and which are path segments over HTTP. Results are data: the CLI
   renders them as text, HTTP as JSON. A step that needs the editor
   runs on the CLI only; over HTTP the text is sent instead.
6. Routes:

   | Route | Commands |
   |---|---|
   | /api/workplan | list, add |
   | /api/workplan/{id} | show, edit |
   | /api/workplan/{id}/merge | merge |
   | /api/workplan/{id}/task | list, add |
   | /api/workplan/{id}/task/gen | gen |
   | /api/task/{id}/{nnnn} | show, drop |
   | /api/task/{id}/{nnnn}/{doc} | edit |
   | /api/task/{id}/{nnnn}/patch | show, add, drop |
   | /api/task/{id}/{nnnn}/patch/{verb} | gen, apply, accept, reject |
   | /api/route | route |

7. The token and Host checks, and the lock on writes, apply to every
   route through the registry's HTTP side.
8. Route actions take the command names: `gen-task` and `gen-patch`;
   `complete`, `review` and `none` are unchanged.
9. `add-patch` reads a reply in the form the `none` agent asks for: the
   commit message line and a unified diff. `--prompt` prints the prompt
   the `none` agent would send, with the files' contents, ready to paste
   into a chat.
10. The renames come first; the new commands, and the page's buttons
    for them, follow as later tasks.

## Tasks

0000  The command registry

0001  The commands, named verb-noun, on the CLI

0002  The API from the registry

0003  The page through api.js

0004  Route actions named for the commands

0005  add-task: a task from its templates

0006  Manual mode: prompts and pasted replies

0007  drop-task and drop-patch

## Dropped
