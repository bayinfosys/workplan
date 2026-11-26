# The workplan protocol

Version 0.1

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

Every step can be carried out by hand with git and an editor; the
`workplan` command is support. Each section below ends with its step
by hand.

## 1. Repository layout

```
src/                    your project code
tests/                  your test code
workplans/              the workplan state
  README.md             points here
  PRINCIPLES.md         principles for the project
  BACKLOG.md            candidate workplans, in order of priority
  config.toml           settings for the workplan command
  dispatch.sh           the steps the workplan command's hooks run after each commit
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
definitions and review: taste, personas, constraints. `config.toml`
configures the `workplan` command and has no meaning in the protocol,
as does `dispatch.sh`, the script `route.dispatch` can name.

Working files ignored by git:

```
workplans/*/*/output.patch
workplans/*/*/COMMIT_MSG
```

By hand:

```bash
mkdir -p workplans
$EDITOR workplans/README.md workplans/PRINCIPLES.md workplans/BACKLOG.md
printf '%s\n' 'workplans/*/*/output.patch' 'workplans/*/*/COMMIT_MSG' >> .gitignore
git add workplans .gitignore
git commit -m "workplan init"
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

## 4. Templates

Every document has a template, and so does the squash commit message.
Templates use substitution only: `$name` is replaced, `$$` is a literal
`$`. A project overrides a template by placing a file of the same name
in `workplans/templates/<kind>/`; the kinds are `documents`, `prompts`
and `project`.

| Template | Values |
|---|---|
| documents/WORKPLAN.md | `$id`, `$title`, `$goal` |
| documents/TASK.md | `$id`, `$title`, `$depends`, `$change` |
| documents/BREAKDOWN.md | `$id`, `$title` |
| documents/NOTES.md | `$id`, `$title` |
| documents/SQUASH_COMMIT_MSG | `$id`, `$title`, `$goal`, `$tasks`, `$breaking`, `$path` |
| prompts/task-gen.md | `$id`, `$next`, `$context`, `$task_template`, `$breakdown_template` |
| prompts/task-gen-none.md | as task-gen.md |
| prompts/patch-gen.md | `$id`, `$workplan`, `$context`, `$commit_msg` |
| prompts/patch-gen-none.md | as patch-gen.md |
| prompts/route.md | `$branch`, `$parents`, `$subject`, `$workplan`, `$paths` |

Text in angle brackets in a template is for the author to replace.

`workplan task add TITLE [--depend N] [-m CHANGE]` writes a new task
this way, adds its line to WORKPLAN.md, and commits them as
`<id> add <nnnn>`.

By hand, a new task:

```bash
n=0003; w=workplans/2026-11-24-one-package
mkdir $w/$n
cp <templates>/documents/TASK.md <templates>/documents/BREAKDOWN.md $w/$n/
$EDITOR $w/$n/TASK.md $w/$n/BREAKDOWN.md     # replace $title, $depends, $change
$EDITOR $w/WORKPLAN.md                      # add "0003  <title>" under Tasks
git add $w/$n $w/WORKPLAN.md
git commit -m "${w#workplans/} add $n" -- $w/$n $w/WORKPLAN.md
```

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
4. Review the workplan as a whole (section 12).
5. Squash-merge to master (section 9).

The maintainer authors every commit. AI assistants do not commit.

Testing is the maintainer's: after applying a patch, after committing
a task, before merging or after. The protocol does not record it.

By hand, steps 1 and 2:

```bash
w=2026-11-24-one-package
git switch -c workplan/$w/definition master
mkdir -p workplans/$w
cp <templates>/documents/WORKPLAN.md workplans/$w/
$EDITOR workplans/$w/WORKPLAN.md             # replace $id, $title, $goal
$EDITOR workplans/BACKLOG.md                  # remove the item
git add workplans/$w workplans/BACKLOG.md
git commit -m "$w workplan"
# write the tasks (section 4), then, to share them before work starts:
git add workplans/$w
git commit -m "$w define tasks"
```

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
(section 11).

By hand:

```bash
w=2026-11-24-one-package; t=workplans/$w/0003
git apply --check $t/output.patch
git apply --index $t/output.patch                  # apply
git diff --cached                                  # read
git apply --index -R $t/output.patch               # reject
git add $t workplans/$w/WORKPLAN.md                # accept
git commit -F $t/COMMIT_MSG
```

## 7. States

A task's state comes from git history and the files; there are no
marker files. The first state that holds is the state:

| State | Holds when |
|---|---|
| `merged` | a commit on master has a line starting with the task id and a space |
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

By hand:

```bash
t=2026-11-24-one-package/0003
git log master -E --grep="^$t " --format='%h %s' -n 1      # merged
git log HEAD   -E --grep="^$t " --format='%h %s' -n 1      # complete
git apply -R --check workplans/$t/output.patch             # testing
git apply    --check workplans/$t/output.patch             # development
```

## 8. Branches

| Branch | Holds | From | Into |
|---|---|---|---|
| `master` | integrated, tested code; one commit per workplan | -- | -- |
| `workplan/<id>/definition` | the workplan's files and one commit per task | master | master, squashed |
| `workplan/<id>/task/<nnnn>` | one task, branched from the definition branch | `workplan/<id>/definition` | `workplan/<id>/definition` |

Git stores a branch name as a path, so no branch name can be the
leading path of another; the workplan branch ends in `definition` for
that reason.

```bash
git branch -r --list 'origin/workplan/*/definition'   # open workplans
git branch -r --list 'origin/workplan/<id>/*'         # one workplan and its tasks
```

Task branches are needed only when several people work on the same
workplan at once. The name of `master` is configurable.

## 9. Merging

A workplan is squash-merged into master when every task it lists is
committed on the branch or dropped, the branch contains master, and
the project's tests pass on the branch. Until then the definition
branch is the workplan's own, and may be rewritten, by a reset to an
earlier task for instance; once merged, master holds its record.

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

Every task id then reaches master's history, where its state reads
`merged`. The workplan's directory stays on master as the record of
the work. Tagging the branch before deleting it is the maintainer's
choice.

By hand:

```bash
w=2026-11-24-one-package; b=workplan/$w/definition
git merge-base --is-ancestor master $b || echo "rebase $b onto master first"
git switch $b && <the project's test command> || echo "the tests fail; merge nothing"
{ echo "$w <title>"; echo; echo "<goal>"; echo
  git log --reverse --format=%s master..$b | grep "^$w/[0-9]\{4\} "; echo
  for t in workplans/$w/[0-9][0-9][0-9][0-9]/TASK.md; do
    git interpret-trailers --parse "$t" | sed -n 's/^Breaking: /BREAKING-CHANGE: /p'; done
  echo "Workplan: workplans/$w/WORKPLAN.md"; } > /tmp/msg
git switch master
git merge --squash $b
git commit -e -F /tmp/msg
git branch -D $b
git push origin master
git push origin --delete $b
```

`git log --format='%h %s %(trailers:key=Workplan,valueonly)'` lists
the workplan behind each commit on master.

## 10. Routing

After a commit, the next step follows from what the commit changed.
The targets come from the commit; the action is the first in this
table that has targets:

| Action | When | Targets |
|---|---|---|
| `complete` | a commit on master with a `Workplan:` trailer | the workplan |
| `review` | code changed in a commit whose subject is a task id | the task |
| `patch-gen` | TASK.md or BREAKDOWN.md changed | each task |
| `task-gen` | WORKPLAN.md changed | the workplan |
| `none` | anything else, such as a change to the protocol's files | -- |

A task's commit, which also carries its files and WORKPLAN.md, leads
to `review`; the commit that defines the tasks leads to
`patch-gen`. A `post-commit` hook can run each step automatically.

By hand:

```bash
git show --name-only --format='%s%n%(trailers:key=Workplan)' HEAD
```

## 11. Agents

An agent is anything that defines a workplan's tasks, or turns a
task's files into output.patch and COMMIT_MSG. The agent works in a
separate worktree at the head of the workplan branch, so the
maintainer's tree is untouched:

1. `git worktree add --detach <tmp> workplan/<id>/definition`
2. copy `workplans/` into the worktree, so uncommitted edits are seen
3. run any setup the project needs in the worktree, then stage the
   worktree and keep its tree as the base
4. run the agent in the worktree
5. bring the result back:
   - to define tasks: copy the new task directories back, list them in
     WORKPLAN.md, and commit WORKPLAN.md with them
   - to produce a patch: stage everything but output.patch and
     COMMIT_MSG, save the diff from the base as output.patch, and copy
     COMMIT_MSG out
6. `git worktree remove --force <tmp>`

By hand, producing a patch:

```bash
w=2026-11-24-one-package; t=$w/0003
git worktree add --detach /tmp/wt workplan/$w/definition
cp -r workplans /tmp/wt/
git -C /tmp/wt add -A && base=$(git -C /tmp/wt write-tree)
( cd /tmp/wt && <agent, or edit by hand> )
x=":(exclude)workplans/*/*/output.patch"; y=":(exclude)workplans/*/*/COMMIT_MSG"
git -C /tmp/wt add -A -- . "$x" "$y"
git -C /tmp/wt diff --cached --binary $base -- . "$x" "$y" > workplans/$t/output.patch
cp /tmp/wt/workplans/$t/COMMIT_MSG workplans/$t/
git worktree remove --force /tmp/wt
```

Pasting the rendered prompt and the files into a chat, and saving the
reply's diff as output.patch, is the same step.

## 12. Review

The review reads WORKPLAN.md, the task files and the diff of the
workplan's commits, without the discussion that produced them, and
answers:

- does the diff reach the workplan's goal?
- does the diff hold to PRINCIPLES.md?
- does the diff contain changes that no task accounts for?

By hand:

```bash
git diff master...workplan/2026-11-24-one-package/definition    # the whole workplan
git log -p --reverse master..workplan/2026-11-24-one-package/definition   # task by task
```

## 13. Working together

- Fetch before starting work: `git fetch --prune`.
- Each workplan has one owner. When master moves while a workplan is
  open, the owner rebases its branch onto master and pushes; task
  branches rebase onto the workplan branch the same way.
- Tasks whose files do not overlap may run in parallel on task
  branches; tasks that share files run in sequence.
- Pushing a task branch claims the task. The first push stands.
- Suggested settings: `git config pull.rebase true`,
  `git config rebase.autoStash true`, `git config fetch.prune true`.
