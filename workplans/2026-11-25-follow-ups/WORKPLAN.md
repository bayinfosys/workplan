# Workplan 2026-11-25-follow-ups: follow-ups

## Goal

Full auto runs from the hooks; merge-workplan leaves no local branch
behind; workplan writes nothing under .git but the hooks; init gives a
new project BACKLOG.md and a dispatch script; SPEC.md describes
BACKLOG.md and its items, and says committing task files before work is
optional; and the departures of 2026-11-24-command-interface are
recorded in its tasks' NOTES.md.

## Context

- src/workplan/ops.py: `HOOK`, the script `install` writes to
  .git/hooks/post-commit and post-merge; `plan` drafts WORKPLAN.md in
  .git/workplan/; `merge` drafts the squash message there, and its
  result lists `git branch -D` as a next step; `init` writes README.md,
  PRINCIPLES.md and config.toml from templates/project/
- src/workplan/git.py: `git_path`, used for those drafts and for the
  hooks directory
- src/workplan/templates/project/config.toml: `[route] dispatch = ""`
- src/workplan/route.py: `dispatch` runs route.dispatch with the action
  and its targets; the actions gen-task and gen-patch are command names
- SPEC.md: section 1, the layout; section 3, the documents; section 5,
  the steps, where step 2 commits the task files
- workplans/BACKLOG.md: one `## ` heading per item, in order of
  priority
- workplans/2026-11-24-command-interface/0004 to 0007: the tasks whose
  departures are listed in the backlog item this workplan came from
- tests/test_fixes.py: the install and merge tests

## Findings

- git runs hooks with GIT_INDEX_FILE and the author variables set; the
  hook passes them on to workplan, whose git commands in a worktree
  then use the main index and fail, out of sight in the background, so
  full auto never runs
- merge-workplan leaves the local definition branch, and prints the
  command that deletes it
- add-workplan and merge-workplan write their drafts under .git, which
  belongs to git
- a new project gets no BACKLOG.md and no dispatch script, so neither
  the queue of work nor full auto is ready after init
- SPEC.md says nothing of BACKLOG.md, and its step 2 reads as if task
  files must be committed before work starts
- the departures of 2026-11-24-command-interface are recorded only in
  conversation

## Decisions

1. The hooks clear GIT_INDEX_FILE, GIT_DIR, GIT_WORK_TREE, GIT_PREFIX
   and the GIT_AUTHOR_ and GIT_COMMITTER_ variables before running
   workplan.
2. merge-workplan deletes the local definition branch once the squash
   commit is made. Deleting the remote branch stays with the
   maintainer, as pushing does.
3. workplan writes under .git only the hooks, which git reads from
   nowhere else. The drafts go to the system's temporary directory.
4. init writes workplans/BACKLOG.md and workplans/dispatch.sh from
   templates; config.toml names dispatch.sh in a commented line.
5. BACKLOG.md is part of the protocol: a `## ` heading per item, with
   free text under it; order is priority; an item chosen for work
   becomes a workplan and leaves BACKLOG.md in the workplan's first
   commit.
6. The departures are recorded as NOTES.md in the tasks they belong
   to, committed on this workplan's branch.

## Tasks

0000  Clear git's hook variables before running workplan

0001  Delete the local definition branch in merge-workplan

0002  Write editor drafts in the temporary directory

0003  init writes BACKLOG.md and dispatch.sh

0004  Describe BACKLOG.md in SPEC.md, and the task commit as optional

0005  Record the departures of 2026-11-24-command-interface in NOTES.md

## Dropped
