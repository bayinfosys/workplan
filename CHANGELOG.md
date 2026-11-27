# Changelog

## v0.3.0 (2026-11-27)

### Breaking

- SPEC.md is removed; the protocol is in PROTOCOL.md (protocol, 2026-11-26-protocol/0004)
- the config key master is now parent, and WORKPLAN_MASTER is now WORKPLAN_PARENT (launch, 2026-11-27-launch/0000)

### Added

- TASK.md ends with a trailer block (change kinds, 2026-11-26-change-kinds/0001)
- The squash message carries breaking changes (change kinds, 2026-11-26-change-kinds/0002)
- wp changelog (change kinds, 2026-11-26-change-kinds/0003)
- wp publish (publish, 2026-11-27-publish/0000)

### Fixed

- The parent branch is the config key parent, written by init (launch, 2026-11-27-launch/0000)
- With no agent, the failure says how to go on (launch, 2026-11-27-launch/0001)

### Changed

- Read a task's trailer block with git (change kinds, 2026-11-26-change-kinds/0000)
- Trailer blocks for the tasks since v0.1.0 (change kinds, 2026-11-26-change-kinds/0004)
- README and PRINCIPLES.md on sequence and git; release and provenance in the backlog (sequence, 2026-11-26-sequence/0000)
- Mark the protocol commands in the registry (protocol, 2026-11-26-protocol/0000)
- PROTOCOL.md: files, formats, states and branches (protocol, 2026-11-26-protocol/0001)
- PROTOCOL.md: each protocol command as git commands (protocol, 2026-11-26-protocol/0002)
- README.md: protocol and supporting commands, and the library's features (protocol, 2026-11-26-protocol/0003)
- Remove SPEC.md (protocol, 2026-11-26-protocol/0004)
- README.md for a new user (launch, 2026-11-27-launch/0002)
- PROTOCOL.md: glossary, version and the parent branch (launch, 2026-11-27-launch/0003)

## v0.2.0 (2026-11-26)

### Breaking

- the commands are named verb-noun: plan is now add-workplan, define-tasks gen-task, produce-patch gen-patch, apply apply-patch, diff show-patch, accept accept-patch, reject reject-patch and merge merge-workplan; status is kept (command interface, 2026-11-24-command-interface/0001)
- the route actions and WORKPLAN_ACTION define-tasks and produce-patch are now gen-task and gen-patch, and the prompt templates are renamed to match (command interface, 2026-11-24-command-interface/0004)
- the commands are noun then verb, with the workplan's as top-level verbs: add-task is now task add, show-patch patch show, add-workplan new, merge-workplan merge, and so on for every command but init, install, serve, route and status (command groups, 2026-11-25-command-groups/0000)
- the route actions and WORKPLAN_ACTION gen-task and gen-patch are now task-gen and patch-gen, and the prompt templates are renamed to match (command groups, 2026-11-25-command-groups/0001)

### Added

- Read workplans held on other branches (serve, 2026-11-24-serve/0000)
- Write documents of the editable workplan, and merge with a given message (serve, 2026-11-24-serve/0001)
- Serve the operations over HTTP on 127.0.0.1 (serve, 2026-11-24-serve/0002)
- The board page (serve, 2026-11-24-serve/0003)
- add-task: a task from its templates (command interface, 2026-11-24-command-interface/0005)
- Manual mode: prompts and pasted replies (command interface, 2026-11-24-command-interface/0006)
- drop-task and drop-patch (command interface, 2026-11-24-command-interface/0007)
- Delete the local definition branch in merge-workplan (follow-ups, 2026-11-25-follow-ups/0001)
- init writes BACKLOG.md and dispatch.sh (follow-ups, 2026-11-25-follow-ups/0003)
- show-patch heads the diff with the task, its commit and its dependencies (review patch, 2026-11-25-review-patch/0000)
- A patch is the diff from the worktree as the agent receives it (workplan patches, 2026-11-25-workplan-patches/0000)
- Commands commit the documents they change (command commits, 2026-11-25-command-commits/0000)
- new takes a whole WORKPLAN.md with --reply (intake, 2026-11-26-intake/0000)
- merge runs test.command before squashing (test command, 2026-11-26-test-command/0000)
- merge says it is running test.command (merge progress, 2026-11-26-merge-progress/0000)

### Fixed

- Clear git's hook variables before running workplan (follow-ups, 2026-11-25-follow-ups/0000)
- Write editor drafts in the temporary directory (follow-ups, 2026-11-25-follow-ups/0002)
- Fences in a reply open and close at the start of a line (reply fences, 2026-11-25-reply-fences/0000)
- Task lines follow one another in WORKPLAN.md (task lines, 2026-11-25-task-lines/0000)
- patch add refuses a reply whose commit line names another task (reply task, 2026-11-26-reply-task/0000)
- patch accept refuses a task WORKPLAN.md does not list (intake, 2026-11-26-intake/0001)

### Changed

- The command registry (command interface, 2026-11-24-command-interface/0000)
- The commands, named verb-noun, on the CLI (command interface, 2026-11-24-command-interface/0001)
- The API from the registry (command interface, 2026-11-24-command-interface/0002)
- The page through api.js (command interface, 2026-11-24-command-interface/0003)
- Route actions and agent actions named for the commands (command interface, 2026-11-24-command-interface/0004)
- Describe BACKLOG.md in SPEC.md, and the task commit as optional (follow-ups, 2026-11-25-follow-ups/0004)
- Record the departures of 2026-11-24-command-interface in NOTES.md (follow-ups, 2026-11-25-follow-ups/0005)
- The CLI takes the new names (command groups, 2026-11-25-command-groups/0000)
- Route actions named task-gen and patch-gen (command groups, 2026-11-25-command-groups/0001)
- README.md in the new names (command groups, 2026-11-25-command-groups/0002)
- SPEC.md and PRINCIPLES.md in the new names (command groups, 2026-11-25-command-groups/0003)
- The last old names in comments, and the commands that commit in README.md (old names, 2026-11-26-old-names/0000)
- PRINCIPLES.md, SPEC.md and README.md on the tests; the backlog item (test command, 2026-11-26-test-command/0001)

## v0.1.0 (2026-11-23)

First release, extracted from marigold's tasks/ process (task.py at
89cb0be).

- `workplans/` directory, `workplan` command with `wp` as a short name,
  `WORKPLAN_` variables
- the flow: `init`, `plan`, `define-tasks`, `produce-patch`, `apply`,
  `diff`, `accept`, `reject`, `merge`; the commands commit what they
  complete, so no step needs `git add`
- `plan` opens the editor git uses, on WORKPLAN.md rendered from its
  template; `-m` writes the goal and skips it
- `define-tasks` and `produce-patch` run an agent (`none`, `command`,
  `claude-code`, `codex`) in a worktree owned by workplan
- `accept` commits the patch with the task's directory and WORKPLAN.md,
  and refuses on master
- `merge` renders the message from the SQUASH_COMMIT_MSG template and
  opens the editor; it requires the branch to contain master and
  restores the tree on failure
- workplan branches are `workplan/<id>/definition`
- `status` with layout problems and `--json`; the `dropped` state
- `route` with the rules or an OpenAI-compatible classifier; action
  names match the commands; `install` writes hooks into .git/hooks
- SPEC.md with a "By hand" block for each step
