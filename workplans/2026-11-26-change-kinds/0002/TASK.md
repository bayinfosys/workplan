# The squash message carries breaking changes

`squash_message` collects the Breaking trailer of each committed task
of the workplan, and SQUASH_COMMIT_MSG puts one
`BREAKING-CHANGE: <text>` line for each above the Workplan trailer.
Conventional Commits takes BREAKING-CHANGE as the same token as
BREAKING CHANGE, and the hyphen keeps the line a git trailer, which a
space would not.

Effects:

- `wp merge --show` for a workplan with a task whose TASK.md has
  `Breaking: X` shows `BREAKING-CHANGE: X` in the trailer paragraph,
  before `Workplan:`, one line per such task, in task order
- with no Breaking trailer, the message is as now
- `git log -1 --format='%(trailers:key=BREAKING-CHANGE,valueonly)'`
  reads the lines after the merge
- SPEC.md section 4 lists `$breaking`; section 9 shows it in the
  example and in the by-hand block

Depends: 0000
Change: feat
Audience: users
