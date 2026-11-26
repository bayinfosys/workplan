# wp changelog

`wp changelog [FROM] [TO]` prints a changelog in Markdown from the
squash commits between two tags or commits and the trailer blocks of
their tasks, as WORKPLAN.md's decision 4 says, using git for each step.

Effects:

- TO defaults to HEAD; FROM to the latest tag reachable from TO's
  parent, from `git describe --tags --abbrev=0`; with no tag, the
  first commit
- the heading is the tag at TO, from `git tag --points-at`, or
  "Unreleased", with TO's commit date
- the squash commits in FROM..TO are those with a Workplan trailer,
  read with `git log --format` and `%(trailers:key=Workplan)`, oldest
  first
- for each, the trailer blocks of its tasks are read at TO with `git
  show TO:<path>` and `plans.trailers`; a task listed under Dropped
  is left out
- sections, each left out when empty: Breaking, then Added (feat),
  Fixed (fix), Changed (refactor, docs, test, chore) and Other (no
  Change, or another word); each line is the task's title, with its
  workplan's title and id
- `--audience NAME` keeps tasks with that audience and those with none
- `--json` gives the same as data; `GET /api/changelog` takes `from`,
  `to` and `audience`
- nothing is written: no file, no commit, no ref
- README.md has the command's row and a short section; SPEC.md has a
  section with the by-hand form: git log with the Workplan trailer,
  then git show and git interpret-trailers for each task

Depends: 0000
Change: feat
Audience: users
