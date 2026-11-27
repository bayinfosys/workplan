# The workplan protocol

Version 0.3. The protocol is pre-1.0: until 1.0 it changes without
compatibility between versions. Its version follows the minor version
of the `workplan` package.

A `WORKPLAN.md` is a unit of work stored in the git repository of a
project. Each workplan is broken down into a series of tasks, each
stored in a sub-directory with a `TASK.md` describing the task and a
`BREAKDOWN.md` breaking the task down into simple steps. A human, LLM
or agent can then take this context from the shared repository,
implement the change and produce a `.patch` file with a `COMMIT_MSG`.
The patch is committed to the repository, together with the task's
files, and shared with remotes; the `.patch` file itself is not
committed.

As a result, the workplan is decomposed into manageable chunks,
converted to a series of simple changes, and committed back with the
task definitions. This allows review of the workplan's goals, the task
definitions, the changes and their outcomes separately, or as a single
review before merging.

Finally, all the tasks of a workplan are squash-merged into the parent
branch, with each task's `COMMIT_MSG` in the log message.

All state is in files and git history. There is no central server and
no co-ordination outside standard git processes.

This document defines the files, their formats, the states and the
branches, then gives each protocol command as the git commands it
performs. The `workplan` command, `wp`, implements it; its usage is in
README.md.

| Term | Meaning |
|---|---|
| workplan | one goal, its tasks, and the branch that holds them until merged |
| task | one change: TASK.md, BREAKDOWN.md, and one commit when accepted |
| patch | a task's change as output.patch and COMMIT_MSG, before it is committed |
| state | where a task stands, read from its files and the git history |
| parent branch | the branch workplans start from and merge into: master, main or another |

## 1. Repository layout

```
src/                    your project code
tests/                  your test code
workplans/              the workplan state
  README.md             points here
  PRINCIPLES.md         principles for the project
  BACKLOG.md            candidate workplans, in order of priority
  templates/            optional overrides of the templates
  <id>/                 one workplan
    WORKPLAN.md         the goal, context, decisions and tasks
    <nnnn>/             one task in this workplan
      TASK.md           the task
      BREAKDOWN.md      the task broken down into simple steps
      NOTES.md          optional notes on the task, its breakdown or implementation
      output.patch      the change, uncommitted
      COMMIT_MSG        the change's one-line commit message, uncommitted
```

`PRINCIPLES.md` holds project-level guidance for workplans, task
definitions and review: taste, personas, constraints. An
implementation may keep files of its own under `workplans/`, such as
the `workplan` command's config.toml; they have no meaning in the
protocol.

Working files ignored by git:

```
workplans/*/*/output.patch
workplans/*/*/COMMIT_MSG
```

## 2. Identifiers

A workplan id is the date the workplan was started and a name, such as
`2026-11-24-one-package`: letters, digits, `.`, `_` and `-`, with no
`/`. A date alone is a valid id.

A task number is four digits, `0000` upwards, in the order the tasks'
changes are applied to the repository. A task id is
`<workplan id>/<nnnn>`, such as `2026-11-24-one-package/0002`.

## 3. Documents

Each document starts from a template (section 4).

### BACKLOG.md

The work not yet started. Each `## ` heading is an item: a candidate
workplan, named by its heading, with free text under it on what it is
for and the tasks already in view. The order of the headings is the
order of priority.

```markdown
# Backlog

## Item commands

Items as the fourth noun: an item becomes a workplan, a workplan
becomes tasks, a task becomes a patch.

## Animation

Render examples/demo.tape for the README.
```

An item chosen for work becomes a workplan, and leaves BACKLOG.md in
the workplan's first commit.

### WORKPLAN.md

The goal, the context needed to work in the code, the findings that
make the work necessary, the decisions, and the tasks in order. It is
the current accepted plan and is edited as the plan changes.

```markdown
# Workplan <id>: <title>

## Goal
## Context
## Findings
## Decisions
## Tasks
## Dropped
```

A task line under `## Tasks` or `## Dropped` starts with the task
number at the start of the line, followed by whitespace and a
description; continuation lines are indented:

```
0003  Read handler settings from the resolved ModelSettings and
      remove set_model_config_env
```

A task listed under `## Dropped` is closed without a commit.

### TASK.md

One change and its effects. The first line is the title. The last
paragraph is a block of git trailers, one `Key: value` line each:

```markdown
# <title>

<the change>

Effects:

- <what holds once the change is applied>

Depends: 0000, 0002
Change: feat
Audience: users
Breaking: wp add-task is now wp task add
```

| Key | Value |
|---|---|
| `Depends` | the tasks it depends on, by number, or `none` |
| `Change` | `feat`, `fix`, `docs`, `refactor`, `test` or `chore` |
| `Audience` | `users`, `developers` or `internal` |
| `Breaking` | what the change breaks, in a sentence; left out when nothing breaks |
| `Refs`, `Fixes` | optional: a link or issue; the task or commit a fix repairs |

The values are hints: tools read the first word of `Change` and
`Audience` when it is one of the words above, and leave anything else
to a reader or a model. Older tasks end with a sentence, "Depends on
0000, 0002.", which is read when there is no `Depends` trailer. By
hand, `git interpret-trailers --parse TASK.md` prints the block, and
`grep '^Change:' workplans/<id>/*/TASK.md` lists the kinds.

A task changes the project: its code, its documentation or its build.
It needs no further decisions before work starts.

### BREAKDOWN.md

The steps that make the change, numbered, in order.

### NOTES.md

Review questions about the task and their answers.

### output.patch

The change, as `git diff` output, built against the head of the
workplan branch and applied with `git apply`. A patch that fails
`git apply --check` is produced again, not merged by hand.

### COMMIT_MSG

The task's commit message: one line, the task id, a space, and what
the change does:

```
2026-11-24-one-package/0002 Install the CLI with pipx or uv tool
```

A change that needs a second line to describe is two tasks.

## 4. Document templates

Every document has a template, and so does the squash commit message.
Templates use substitution only: `$name` is replaced, `$$` is a literal
`$`. A project overrides a template by placing a file of the same name
in `workplans/templates/documents/`.

| Template | Values |
|---|---|
| documents/WORKPLAN.md | `$id`, `$title`, `$goal` |
| documents/TASK.md | `$id`, `$title`, `$depends`, `$change` |
| documents/BREAKDOWN.md | `$id`, `$title` |
| documents/NOTES.md | `$id`, `$title` |
| documents/SQUASH_COMMIT_MSG | `$id`, `$title`, `$goal`, `$tasks`, `$breaking`, `$path` |

Text in angle brackets in a template is for the author to replace.

## 5. Steps

1. Plan: choose an item from BACKLOG.md, write WORKPLAN.md from it on
   a new workplan branch, and remove the item from BACKLOG.md in the
   same commit.
2. Define the tasks: write each task's TASK.md and BREAKDOWN.md, and
   list them in WORKPLAN.md. Commit WORKPLAN.md with the tasks before
   work starts, to share and review them; or leave them uncommitted,
   and each task's files are committed with its patch in step 3.
   Refine the tasks, in discussion or in NOTES.md, until they are
   accepted.
3. For each task in order: confirm the tasks it depends on are
   committed; run the patch loop (section 6) until the diff is right;
   commit it with COMMIT_MSG, together with the task's directory and
   WORKPLAN.md; push.
4. Review the workplan as a whole (section 10).
5. Squash-merge to the parent branch (section 9), then publish: push
   the parent branch and delete the workplan's branches on the remote.

The maintainer authors every commit, through the commands or by hand;
agents write files and do not commit.

The project's tests run before the squash merge, and the maintainer
may run them at any step before. Each accepted task leaves them
passing.

## 6. The patch loop

1. Produce output.patch and COMMIT_MSG from TASK.md and BREAKDOWN.md,
   against the head of the workplan branch.
2. Apply the patch to the tree and the index, and read the diff.
3. If the diff is wrong, take it back out, adjust TASK.md or
   BREAKDOWN.md, and produce it again.
4. When the diff is right, commit it with COMMIT_MSG, together with the
   task's directory and WORKPLAN.md.

A change the patch would need outside its task, such as an
architectural change, a refactoring or an unrelated fix, is raised for
a later workplan, not put into the patch.

The patch can come from any source: a person, a chat, or an agent
(the `patch gen` command).

## 7. States

A task's state comes from git history and the files; there are no
marker files. The first state that holds is the state:

| State | Holds when |
|---|---|
| `merged` | a commit on the parent branch has a line starting with the task id and a space |
| `complete` | a commit on the current branch has that line |
| `dropped` | WORKPLAN.md lists the task under `## Dropped` |
| `testing` | output.patch is in the index or the tree, uncommitted |
| `development` | output.patch exists and would apply |
| `waiting` | output.patch does not apply, and a task named by its `Depends` trailer is not committed |
| `stale` | output.patch does not apply, and every task it depends on is committed: produce it again |
| `refinement` | TASK.md exists, with no patch |
| `unspecified` | WORKPLAN.md lists the task, with no directory |
| `unknown` | neither WORKPLAN.md nor the directory knows the task |

Patches are working files, so `testing`, `development`, `waiting` and
`stale` are states of one clone. Every clone sees `merged`,
`complete`, `dropped`, `refinement` and `unspecified`.

Read with git:

```bash
t=2026-11-24-one-package/0003
git log $parent -E --grep="^$t " --format='%h %s' -n 1     # merged
git log HEAD   -E --grep="^$t " --format='%h %s' -n 1      # complete
git apply -R --check workplans/$t/output.patch             # testing
git apply    --check workplans/$t/output.patch             # development
```

## 8. Branches

| Branch | Holds | From | Into |
|---|---|---|---|
| parent, such as `master` | integrated, tested code; one commit per workplan | -- | -- |
| `workplan/<id>/definition` | the workplan's files and one commit per task | parent | parent, squashed |
| `workplan/<id>/task/<nnnn>` | one task, branched from the definition branch | `workplan/<id>/definition` | `workplan/<id>/definition` |

Git stores a branch name as a path, so no branch name can be the
leading path of another; the workplan branch ends in `definition` for
that reason.

```bash
git branch -r --list 'origin/workplan/*/definition'   # open workplans
git branch -r --list 'origin/workplan/<id>/*'         # one workplan and its tasks
```

Task branches are needed only when several people work on the same
workplan at once. The parent branch is named in the configuration:
master, main or another.

## 9. Merging

A workplan is squash-merged into the parent branch when every task it
lists is committed on the branch or dropped, the branch contains the
parent, and
the project's tests pass on the branch. Until then the definition
branch is the workplan's own, and may be rewritten, by a reset to an
earlier task for instance; once merged, the parent holds its record.

The message is rendered from the SQUASH_COMMIT_MSG template: the
workplan id and title, the goal, the task commit subjects in order,
a `BREAKING-CHANGE:` trailer for each task with a `Breaking` trailer,
and a trailer naming the workplan. Conventional Commits reads
`BREAKING-CHANGE` as `BREAKING CHANGE`; the hyphen keeps it a git
trailer. The maintainer edits the message before the commit:

```
2026-11-24-one-package One import package

pip install bayis-marigold puts one import package, marigold, and the
marigold command into an environment.

2026-11-24-one-package/0000 Move the packages under marigold
2026-11-24-one-package/0001 Name each module by its path under marigold
2026-11-24-one-package/0002 Install the CLI with pipx or uv tool

BREAKING-CHANGE: the packages bayis and marigold_cli are now marigold
Workplan: workplans/2026-11-24-one-package/WORKPLAN.md
```

Every task id then reaches the parent's history, where its state reads
`merged`. The workplan's directory stays on the parent as the record of
the work. Tagging the branch before deleting it is the maintainer's
choice.

`git log --format='%h %s %(trailers:key=Workplan,valueonly)'` lists
the workplan behind each commit on the parent branch.

## 10. Review

The review reads WORKPLAN.md, the task files and the diff of the
workplan's commits, without the discussion that produced them, and
answers:

- does the diff reach the workplan's goal?
- does the diff hold to PRINCIPLES.md?
- does the diff contain changes that no task accounts for?

Read with git:

```bash
git diff $parent...workplan/2026-11-24-one-package/definition    # the whole workplan
git log -p --reverse $parent..workplan/2026-11-24-one-package/definition   # task by task
```

## 11. Working together

- Fetch before starting work: `git fetch --prune`.
- Each workplan has one owner. When the parent moves while a workplan
  is open, the owner rebases its branch onto it and pushes; task
  branches rebase onto the workplan branch the same way.
- Tasks whose files do not overlap may run in parallel on task
  branches; tasks that share files run in sequence.
- Pushing a task branch claims the task. The first push stands.
- After the merge, `wp publish` pushes the parent branch, then deletes
  the workplan's branches on the remote.
- Suggested settings: `git config pull.rebase true`,
  `git config rebase.autoStash true`, `git config fetch.prune true`.

## 12. Protocol commands

Each protocol command of the `workplan` command, `wp`, is given below
as the git commands it performs, in order. A line starting with `#`
is a step for an editor, a person or an agent. The supporting
commands, which read git or run the library and change nothing in the
protocol, are in README.md.

The blocks use these variables:

```bash
w=2026-11-24-one-package                          # workplan id
n=0003                                            # task number
t=workplans/$w/$n                                 # task directory
b=workplan/$w/definition                          # workplan branch
parent=master                                     # parent branch: master, main, ...
remote=origin                                     # the remote publish pushes to
T=<templates>/documents                           # document templates
```

## wp init

Create workplans/ and ignore the working files. The `workplan` command
also writes its own config.toml and dispatch.sh there.

```bash
mkdir -p workplans
# write README.md, PRINCIPLES.md and BACKLOG.md in workplans/
printf '%s\n' 'workplans/*/*/output.patch' 'workplans/*/*/COMMIT_MSG' >> .gitignore
git add        workplans .gitignore
git commit     -m "workplan init" -- workplans .gitignore
```

## wp new

A workplan on a new branch from the parent branch. `--reply FILE` gives the whole
WORKPLAN.md in place of the template.

```bash
git switch     -c $b $parent
mkdir -p workplans/$w
cp $T/WORKPLAN.md workplans/$w/
$EDITOR workplans/$w/WORKPLAN.md                  # replace $id, $title, $goal
# from a BACKLOG.md item: remove it there, and add BACKLOG.md below
git add        workplans/$w/WORKPLAN.md
git commit     -m "$w workplan" -- workplans/$w/WORKPLAN.md
```

## wp edit

Edit WORKPLAN.md, with the workplan's branch checked out.

```bash
$EDITOR workplans/$w/WORKPLAN.md
git add        workplans/$w/WORKPLAN.md
git commit     -m "$w edit WORKPLAN.md" -- workplans/$w/WORKPLAN.md
```

## wp merge

Squash the workplan into the parent branch once every listed task is
committed or dropped, the branch contains the parent and the tests
pass (section 9). Nothing is pushed; `wp publish` does that.

```bash
git merge-base --is-ancestor $parent $b           # else rebase $b onto $parent
git switch     $b
<the project's test command>                      # stop if it fails
{ echo "$w <title>"; echo; echo "<goal>"; echo
  git log --reverse --format=%s $parent..$b | grep "^$w/[0-9]\{4\} "; echo
  for f in workplans/$w/[0-9][0-9][0-9][0-9]/TASK.md; do
    git interpret-trailers --parse "$f" | sed -n 's/^Breaking: /BREAKING-CHANGE: /p'
  done; echo "Workplan: workplans/$w/WORKPLAN.md"; } > /tmp/msg
git switch     $parent
git merge      --squash $b
git commit     -e -F /tmp/msg                     # on failure: reset --merge, switch $b
git branch     -D $b
```

## wp publish

Push the parent branch, then delete the workplan's branches on the
remote. This is the only command which pushes to a pre-existing remote
branch. It may fail: when the remote's parent branch has moved on, the
push is refused, and nothing is deleted.

```bash
# with $parent checked out, the merge on it, and $b deleted
git push       $remote $parent                    # stop here if refused
git ls-remote  --heads $remote "refs/heads/workplan/$w/*"
git push       $remote --delete workplan/$w/definition   # and each workplan/$w/task/*
```

## wp task add

The next task from its templates, listed in WORKPLAN.md. `--reply
FILE` writes the tasks in a reply and commits them as
`$w define tasks`.

```bash
mkdir $t
cp $T/TASK.md $T/BREAKDOWN.md $t/
$EDITOR $t/TASK.md $t/BREAKDOWN.md                # replace $title, $change, $depends
$EDITOR workplans/$w/WORKPLAN.md                  # add "$n  <title>" under ## Tasks
git add        $t workplans/$w/WORKPLAN.md
git commit     -m "$w add $n" -- $t workplans/$w/WORKPLAN.md
```

## wp task gen

New tasks written from WORKPLAN.md by any author, with the workplan's
branch checked out. The `workplan` command runs an agent in a worktree
(README.md, Agents); the protocol fixes the files it leaves.

```bash
# write TASK.md and BREAKDOWN.md in workplans/$w/<nnnn>/ for each new task
$EDITOR workplans/$w/WORKPLAN.md                  # list each under ## Tasks
git add        workplans/$w
git commit     -m "$w define tasks" -- workplans/$w
```

## wp task edit

Edit a task's TASK.md, BREAKDOWN.md or NOTES.md.

```bash
$EDITOR $t/TASK.md                                # or BREAKDOWN.md, NOTES.md
git add        $t/TASK.md
git commit     -m "$w edit $n/TASK.md" -- $t/TASK.md
```

## wp task drop

Close a task without a commit of its own.

```bash
$EDITOR workplans/$w/WORKPLAN.md                  # move its line to ## Dropped
git commit     -m "$w drop $n" -- workplans/$w/WORKPLAN.md
```

## wp patch add

A reply from a chat or a person, holding a commit message line and a
diff, becomes the task's patch. The `workplan` command applies the
diff in a worktree and keeps the diff git produces there.

```bash
# save the reply's diff as $t/output.patch        # against the head of $b
echo "$w/$n <what the change does>" > $t/COMMIT_MSG
git apply      --check $t/output.patch
```

## wp patch gen

A patch produced from TASK.md and BREAKDOWN.md by any author. The
`workplan` command runs an agent in a worktree (README.md, Agents);
the protocol fixes the files it leaves.

```bash
# write $t/output.patch and $t/COMMIT_MSG         # against the head of $b
git apply      --check $t/output.patch
```

## wp patch apply

Stage the patch for review.

```bash
git apply      --index $t/output.patch
git diff       --cached                           # read it; run the tests
```

## wp patch accept

Commit the patch with the task's files. Refused on the parent branch,
for a task not listed under ## Tasks, and when COMMIT_MSG is not one
line starting with the task id.

```bash
git apply      --index $t/output.patch            # unless applied already
git add        $t workplans/$w/WORKPLAN.md
git commit     -F $t/COMMIT_MSG
```

## wp patch reject

Take an applied, uncommitted patch back out.

```bash
# when the check fails, restore the edited files first
git apply      --index -R --check $t/output.patch
git apply      --index -R $t/output.patch
```

## wp patch drop

Delete an unapplied patch and its commit message.

```bash
git apply      -R --check $t/output.patch         # succeeds if applied: reject
rm $t/output.patch $t/COMMIT_MSG
```
