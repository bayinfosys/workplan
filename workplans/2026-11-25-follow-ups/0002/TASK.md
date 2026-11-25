# Write editor drafts in the temporary directory

add-workplan and merge-workplan write their editor drafts, WORKPLAN.md
and SQUASH_COMMIT_MSG, in a directory from `tempfile` that is removed
once the command finishes. Nothing in workplan writes under .git apart
from `install`.

Effects:

- `wp add-workplan NAME` with no goal and `wp merge-workplan` with
  no message leave no .git/workplan directory
- the editor opens on a file named WORKPLAN.md or SQUASH_COMMIT_MSG,
  as now
- `git_path` is used only by `install`

Depends on 0001.
