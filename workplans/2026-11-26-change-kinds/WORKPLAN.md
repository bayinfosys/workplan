# Workplan 2026-11-26-change-kinds: change kinds

## Goal

Each task says what kind of change it makes, for whom, and whether it
breaks anything, in git trailer lines at the end of TASK.md; and
`wp changelog` writes a changelog between two tags or commits from the
squash commits and those lines, with no agent needed.

## Context

- src/workplan/templates/documents/TASK.md: ends with "Depends on $depends."
- src/workplan/plans.py: DEPENDS, `depends_of` and `depends_on` read the "Depends on" line; the states and the board use them
- src/workplan/templates/prompts/task-gen.md and task-gen-none.md: tell the agent how to write "Depends on"
- src/workplan/ops.py: `add_task` renders TASK.md; `squash_message` renders SQUASH_COMMIT_MSG with $id, $title, $goal, $tasks and $path
- every squash commit on master ends with `Workplan: <path>`; the workplan's directory, with each TASK.md, is on master from then on
- tags: v0.1.0 at 6fdf863
- SPEC.md section 3 (TASK.md and its example), section 4 (templates and their values), section 9 (merging); README.md

## Findings

- the squash commits give a changelog its entries: one per workplan, with a title, a goal written as an outcome, and the task subjects; commits with no Workplan trailer drop out
- they do not give the kind of each change, its audience, or whether it breaks anything; command-groups renamed every command and nothing marks it as breaking
- a workplan mixes kinds: follow-ups held a fix, a change, an addition and documentation, so the kind belongs to each task
- git's trailer syntax, `Key: value` lines as the last paragraph, can be found with grep and read with `git interpret-trailers --parse`. We should rely on `git` commands wherever possible.

## Decisions

1. TASK.md ends with a trailer block: one `Key: value` line each, as its last paragraph. The keys:
   - `Depends:` task numbers, or none; replaces the "Depends on" sentence, which is still read
   - `Change:` feat, fix, docs, refactor, test or chore
   - `Audience:` users, developers or internal
   - `Breaking:` what breaks, in a sentence; absent when nothing does
   - `Refs:` and `Fixes:`, optional: a link or issue, and the task or commit a fix repairs
   Values are hints: tools read the first word of Change and Audience when it is one of the words above, and leave anything else to a reader or a model.
2. The TASK.md template writes the block, with Depends filled and the others as placeholders; the task-gen prompts ask for it.
3. The squash message adds a `BREAKING CHANGE: <text>` line for each task with Breaking, as Conventional Commits expects, through a `$breaking` value in SQUASH_COMMIT_MSG.
4. `wp changelog [FROM] [TO]`: FROM defaults to the latest tag reachable
   from TO, and TO to HEAD. It lists each squash commit in the range,
   oldest first, reads the TASK.md trailers of its workplan at TO, and
   prints Markdown: a heading with TO's tag or "Unreleased", breaking
   changes first, then the tasks under Added (feat), Fixed (fix) and
   Changed (refactor, docs, test, chore), each with its workplan; tasks
   with no Change under Other. `--audience NAME` keeps the tasks for
   that audience and those with none. The command changes nothing in the history.
5. `changelog` is a top-level command, with a GET route.
6. The tasks of the workplans since v0.1.0 get trailer blocks, so the first changelog, v0.1.0 to now, is grouped.
7. Provenance, the Co-authored-by, Suggested-by and Reported-by lines
   collected into the squash message, and the agent named on each task
   commit, is a workplan of its own, after this one.

## Tasks

0000  Read a task's trailer block with git
0001  TASK.md ends with a trailer block
0002  The squash message carries breaking changes
0003  wp changelog
0004  Trailer blocks for the tasks since v0.1.0

## Dropped
