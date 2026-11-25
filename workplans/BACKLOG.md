# Backlog

Each item is a candidate workplan: a heading, then what it is for and
the tasks already in view. Items are in order of priority. An item
chosen for work becomes a workplan, and leaves this file in that
workplan's first commit.

## Follow-ups from command-interface

The gaps found during 2026-11-24-command-interface, and the fixes found
before it.

- the post-commit and post-merge hooks pass git's `GIT_INDEX_FILE` and
  author variables on to workplan, so its worktree commands fail in the
  background; the hooks clear them
- merge-workplan deletes the local definition branch after the squash
- SPEC section 5: committing the task files before work starts is
  optional, since accept-patch carries them
- init writes a dispatch.sh, commented out in config.toml, so full auto
  is one setting away
- the departures from 2026-11-24-command-interface's tasks recorded in
  their NOTES.md: 0004 renamed the agent functions; 0005 added `$change`
  to the TASK.md template; 0006 reads a reply as a file on the CLI and
  as text over HTTP, keeps git's diff of an applied reply, and shares
  the agent's prompt and capture code; 0007 depends on 0006 as well as
  0003

## Backlog items

BACKLOG.md as the queue of work, and a fourth noun: an item on the
backlog becomes a workplan, a workplan becomes tasks, a task becomes a
patch.

- list-item, show-item, add-item, edit-item and drop-item over the
  `## ` headings of BACKLOG.md; an item's name comes from its heading
- add-workplan --item NAME fills the WORKPLAN.md template from the
  item, and the item leaves BACKLOG.md in the workplan's first commit
- gen-workplan NAME: the agent writes WORKPLAN.md from the item, as
  gen-task writes tasks from a workplan
- a Backlog view in the page: a card per item, opening its text, with
  Start
- README and SPEC describe the backlog and the chain from item to patch

## Page polish

- mark a task's uncommitted document changes on its card and its tabs,
  worked out from git, as the states are
- click a rendered document to edit it in place
- the task panel's actions in `development`: seven buttons in one row
- the open panel covers the header's buttons

## Workplan order

Several workplans can share a date, and the date says nothing about the
order they reached master. Master's history holds that order: one
squash commit per workplan, with its Workplan trailer. list-workplan
and the page could list workplans in that order.

## Real agents

Try the claude-code and codex presets on a real repository, and the
none agent against marigold and a hosted endpoint. Record what each
needs in README.md.

## Review agent

An agent step for the `review` action: what it reads, and where its
notes go.

## Internal agent

A tool loop over chat completions: read, list, grep, edit and an
allowlisted command, with every path confined to the worktree.

## Animation

Render examples/demo.tape with VHS for the README and the website.

## Hosted board

- a GitHub Action builds the board from `status --json` and publishes
  it to Pages
- writes from the hosted board go through pull requests to
  `workplan/<id>/task/<nnnn>`, with a fine-grained token, then OAuth
  through a token-exchange proxy
- the agent in GitHub Actions: a read-only job returns its result as an
  artefact, and a separate job opens the pull request
