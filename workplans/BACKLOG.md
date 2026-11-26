# Backlog

Each item is a candidate workplan: a heading, then what it is for and
the tasks already in view. Items are in order of priority. An item
chosen for work becomes a workplan, and leaves this file in that
workplan's first commit.

## Release

Changelog, commit and tag, in order.

- release VERSION: changelog from the latest tag to HEAD, headed
  VERSION, prepended to CHANGELOG.md; committed as "release VERSION";
  that commit tagged VERSION; refuses unless on master with a clean
  tree and VERSION unused
- pushing the tag stays with the maintainer
- changelog --all: a section per tag, newest first
- the release workflow writes the GitHub release notes with changelog
- README's sequence paragraph names release; SPEC by-hand block

## Provenance

Who did what, collected into the squash message from git.

- Co-authored-by from the task commits' authors
- Suggested-by from the author of the `<id> workplan` commit
- Reported-by from the author of the commit that added the backlog
  item, once items are linked to workplans
- the agent and model named on each task commit; COMMIT_MSG takes
  trailers after its first line
- Signed-off-by left to the maintainer: it certifies the DCO

## Item commands

Items as the fourth noun: an item on the backlog becomes a workplan, a
workplan becomes tasks, a task becomes a patch. Written in the noun
and verb form of 2026-11-25-command-groups.

- item list, item show, item add, item edit and item drop over the
  `## ` headings of BACKLOG.md; an item's name is its heading as a
  slug, "Item commands" as item-commands
- item add, item edit and item drop commit BACKLOG.md, as the other
  commands commit what they change
- they edit BACKLOG.md on the checked-out branch, and no other
- new --item NAME fills the WORKPLAN.md template from the
  item, names the workplan after it, and removes the item from
  BACKLOG.md in the workplan's first commit
- a Backlog column on the board: a card per item, opening its text,
  with Start
- README and SPEC describe the chain from item to patch

## gen-workplan

The agent expands an item into WORKPLAN.md, as gen-task expands a
workplan into tasks: goal, context, findings and decisions, from the
item and the current state of the project.

- gen NAME, a top-level verb as new is, with --prompt for a chat,
  and its route
- the item leaves BACKLOG.md in the workplan's first commit, as with
  new --item
- a Start with the agent button beside Start in the Backlog view

## gen-prompts

The three gen- commands work at three scopes, and each needs its own
prompt, context and permissions.

- gen-workplan: the whole project (README, SPEC, PRINCIPLES.md, the
  item, recent history, past workplans, the code); explores and writes
  WORKPLAN.md; read-only
- gen-task: WORKPLAN.md and the files it names; writes task files;
  read-only
- gen-patch: one task and its files; edits, builds, runs the tests and
  repeats; write and shell
- the context each prompt is built from, gathered in steps a reader
  can follow
- the claude-code and codex presets get read-only permissions for
  gen-workplan and gen-task, and write and shell for gen-patch

## prompt-log

Each gen- run, by agent or by --prompt, writes its rendered prompt,
its context and the agent's reply to workplans/logs/, for debugging.

- one file per run: <time>-<action>-<target>.md
- `logs` joins `templates` as a name no workplan may take: a list of
  reserved names in plans.py
- whether the logs are ignored by git

## Page polish

- click a rendered document to edit it in place: a flat text box with
  Save and Cancel
- mark a task's uncommitted document changes on its card and its tabs,
  worked out from git, as the states are
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

## Unwind

Step back through a workplan's task commits to the last that passes
test.command, and send the failure to the task after it.

- test each task commit, newest first, in a worktree; reset to the
  last that passes, with --keep
- the failure goes into the next task's NOTES.md; its patch is
  dropped, so patch gen writes it again with the notes in its prompt;
  the later tasks are accepted again from their saved patches
- refuse when document commits follow the last passing commit
- the route sends a NOTES.md change to patch-gen, for full auto
- the by-hand steps in SPEC; a how-to with a demo workplan of eight
  tasks and a regression in the fifth
