# Workplan 2026-11-25-command-groups: command groups

## Goal

The CLI takes a noun, then a verb, for tasks and patches: `wp task add`,
`wp patch show 0000`. A workplan's commands are top-level verbs:
`wp new`, `wp list`, `wp show`, `wp edit` and `wp merge`; with init,
install, serve, route and status. The route actions and the agent's
environment use the same words. The HTTP routes are unchanged.

## Context

- src/workplan/registry.py: `Registry.command` names a command
  `<verb>-<noun>` from its function `cmd_<verb>_<noun>`, and `http_of`
  gives its route from the same verb and noun; `parser` builds one
  argparse subcommand per command, with its aliases; `get` finds a
  command by name or alias; `call` names the command in its errors
- src/workplan/commands.py: the commands; `status` is an alias of
  list-task
- src/workplan/cli.py: `PAGED`, the command names whose output goes
  through the pager
- command names in the code's messages: ops.py (accept, drop_patch,
  merge and others), agent.py, route.py, serve.py, the web page's
  hints and dialogs, and the templates (prompts, dispatch.sh,
  README.md of a project)
- src/workplan/route.py: ACTIONS, with `gen-task` and `gen-patch`;
  templates/prompts/route.md lists the actions for the classifier
- src/workplan/agent.py: WORKPLAN_ACTION is `gen-task` or `gen-patch`;
  the prompt templates gen-task.md, gen-task-none.md, gen-patch.md and
  gen-patch-none.md are named for the actions
- templates/project/dispatch.sh: a case for each action
- tests/support.py: the scripted agent's case on WORKPLAN_ACTION
- README.md: the walkthrough, the command table and every example;
  SPEC.md: command names next to each by-hand block;
  workplans/PRINCIPLES.md names add-workplan and merge-workplan
- tests: every test runs commands by name; test_registry tests the
  naming and the routes

## Findings

- commands read verb first, `add-task`, while their HTTP routes are
  grouped by resource, `/api/workplan/{workplan}/task`
- a noun first groups a resource's commands in the help, as
  `wp task --help`, and gives the noun to come, item, its own group
- a workplan noun would read `workplan workplan merge`; the workplan is
  what the tool is named for, and new and merge are the commands that
  change branches
- there are no users and no agents built on the current names, so
  nothing needs the old names kept

## Decisions

1. The CLI form is `wp <noun> <verb> [arguments]` for the nouns task
   and patch; the registry takes both words from the function name, as
   now.
2. The workplan's commands are top-level verbs: `new NAME` (was
   add-workplan), `list`, `show [ID]`, `edit [ID]` and `merge [ID]`.
   `new` replaces add for the workplan alone, as it starts a branch.
3. Functions with no noun are top-level as well: init, install, serve
   and route.
4. `wp status` stays, as a top-level alias of `task list`; it is the
   one alias.
5. The old names go, with no aliases.
6. A command's name in messages and errors is its CLI form:
   `task add`, `merge`.
7. The route actions become complete, review, `patch-gen`, `task-gen`
   and none: one word each, the CLI's words in order. WORKPLAN_ACTION
   takes the same values; the prompt templates are renamed to match,
   patch-gen.md and task-gen.md; dispatch.sh maps `task-gen` to
   `workplan task gen` and `patch-gen` to `workplan patch gen`.
8. The HTTP routes stay as they are: /api/workplan for the workplan's
   commands, whatever their CLI names.
9. README.md, SPEC.md, PRINCIPLES.md, the templates, the web page and
   the tests use the new names throughout.

## Tasks

0000  The CLI takes the new names
0001  Route actions named task-gen and patch-gen
0002  README.md in the new names
0003  SPEC.md and PRINCIPLES.md in the new names

## Dropped
