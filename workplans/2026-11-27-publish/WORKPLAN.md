# Workplan 2026-11-27-publish: publish

## Goal

`wp publish` pushes the parent branch after a merge, then deletes the
workplan's branches on the remote, in that order. `wp merge && wp
publish` completes a workplan.

## Context

- src/workplan/ops.py: `merge` ends with the next steps `git push
  origin <parent>` and `git push origin --delete <branch>`
- src/workplan/config.py: DEFAULTS and OVERRIDES; config.toml
  templates
- src/workplan/route.py: the action `complete`, for a commit on the
  parent branch with a Workplan trailer
- src/workplan/templates/project/dispatch.sh: no case for `complete`
- PROTOCOL.md: section 5, Working together, the preamble, the command
  sections; README.md: the walkthrough, the command table,
  configuration
- tests/test_clones.py: two clones and a bare origin

## Findings

- every merge is followed by the same two pushes, in an order that
  matters: deleting the remote branches before the parent is pushed
  leaves the work only in the local clone

## Decisions

1. `wp publish [ID]`: ID defaults to the workplan of HEAD's Workplan
   trailer. It refuses unless the parent branch is checked out, the
   workplan's squash commit is on it, and its local definition branch
   is gone.
2. It pushes the parent branch to the remote; when that fails it stops
   and deletes nothing. Then it deletes every `workplan/<id>/*` branch
   on the remote.
3. The remote is the config key `remote`, `origin` by default, with
   WORKPLAN_REMOTE.
4. `publish` is a protocol command. PROTOCOL.md says it is the only
   command that pushes to a pre-existing remote branch, and that it
   may fail.
5. dispatch.sh has a commented case: `complete` runs `workplan
   publish`.
6. merge's next step names `workplan publish`.

## Tasks

0000  wp publish

## Dropped
