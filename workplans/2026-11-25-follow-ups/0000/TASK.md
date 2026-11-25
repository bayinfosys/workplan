# Clear git's hook variables before running workplan

The post-commit and post-merge hooks that `install` writes unset
GIT_INDEX_FILE, GIT_DIR, GIT_WORK_TREE, GIT_PREFIX, GIT_AUTHOR_NAME,
GIT_AUTHOR_EMAIL, GIT_AUTHOR_DATE, GIT_COMMITTER_NAME,
GIT_COMMITTER_EMAIL and GIT_COMMITTER_DATE before they run
`workplan route --dispatch HEAD`.

Effects:

- a commit on a workplan branch with `route.dispatch` set runs the
  dispatch command, and git commands it runs in a worktree use that
  worktree's index
- hooks written by an earlier `install` are replaced by the next
  `install`, as they carry the mark
- README.md's Routing section says the hooks clear git's variables

Depends on none.
