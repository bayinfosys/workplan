# Trailer blocks for the tasks since v0.1.0

Each task of the fourteen workplans merged since v0.1.0 gets a trailer
block, so `wp changelog v0.1.0` groups them. The "Depends on"
sentence of each becomes its Depends trailer.

Effects:

- every TASK.md under these workplans ends with Depends, Change and
  Audience trailers, and Breaking where the task broke something:
  2026-11-24-serve, 2026-11-24-command-interface,
  2026-11-25-follow-ups, 2026-11-25-review-patch,
  2026-11-25-reply-fences, 2026-11-25-task-lines,
  2026-11-25-workplan-patches, 2026-11-25-command-commits,
  2026-11-25-command-groups, 2026-11-26-reply-task,
  2026-11-26-old-names, 2026-11-26-intake, 2026-11-26-test-command,
  2026-11-26-merge-progress
- each task's dependencies are unchanged, as `wp status` for each
  workplan shows
- the renaming tasks of command-interface and command-groups carry
  Breaking lines naming the old and new command names
- `wp changelog v0.1.0` puts no task of these workplans under Other
- the rest of each TASK.md is unchanged

Depends: 0000, 0003
Change: docs
Audience: internal
