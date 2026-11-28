# BACKLOG.md in the item format, with the current candidates

workplans/BACKLOG.md holds the candidate workplans as they stand after
v0.3.0, each in the item format of PROTOCOL.md section 3, in the
current command names.

Effects:

- the preamble is the init template's
- every item has a goal paragraph, `- ` lines for the tasks in view,
  and a Depends trailer where it depends on another item
- release: `wp release VERSION`, as the current Release item, with
  PROTOCOL.md's by-hand block in place of SPEC's; changelog --all;
  the release workflow writes the GitHub release notes with changelog
- provenance: as the current Provenance item
- item-commands: `item list` and `item show` over BACKLOG.md, with
  `--json` for the board and the site; `new --item NAME` fills
  WORKPLAN.md from the item and removes it from BACKLOG.md in the
  workplan's first commit; items are added, edited and removed by
  hand, one edit and one commit each; a Backlog column on the board;
  README.md and PROTOCOL.md describe the chain from item to patch
- gen-workplan: `new NAME --gen`, the agent writes WORKPLAN.md, a
  fourth source beside the editor, `-m` and `--reply`; combines with
  `--item`; a Start with the agent button on the board; its route;
  Depends: gen-prompts
- gen-prompts: the prompts for `new --gen`, `task gen` and
  `patch gen` at their three scopes, in the current command names,
  with PROTOCOL.md in place of SPEC
- prompt-log: as the current prompt-log item, in the current command
  names
- review-page, workplan-order, hosted-board, unwind: as the current
  items, in the current command names (`wp list` for list-workplan,
  `patch gen` for gen-patch), with PROTOCOL.md in place of SPEC
- self-hosted-loop: Real agents and Internal agent as one item; the
  goal is an AI-assisted code loop with no hosted model, the none
  agent and the internal tool loop against marigold, a self-hosted
  model layer; tasks: the internal tool loop (read, list, grep, edit
  and an allowlisted command, every path confined to the worktree);
  the none agent and the loop tried against marigold and a hosted
  endpoint; the claude-code and codex presets tried; what each needs
  recorded in README.md
- examples: a demo repository and a script that runs one workplan
  from `wp new` to `wp publish` with a scripted agent, against a
  local bare remote; run by the test suite
- animation: the examples run recorded with VHS for README.md and the
  site; Depends: examples
- current-workplan: off a workplan branch, commands that write need
  an explicit id; commands that read keep the fallback to the newest
  dated workplan
- program-name: `--help` and the usage line print the name the
  command was run as, `wp` or `workplan`
- no item names SPEC, gen-task, gen-patch, list-workplan or
  examples/demo.tape; every item's trailer block, if any, parses with
  `git interpret-trailers --parse`

Depends: 0004
Change: docs
Audience: internal
