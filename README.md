# workplan

Plan and record development work in git, for agent-driven and
AI-assisted development.

A workplan breaks one goal into tasks. Each task is one commit; the
workplan reaches master as one squash commit listing every task. The
plans and the task definitions are Markdown files in `workplans/`, and
every task's state comes from git history. Any clone holds the whole
record, and every step can be done by hand with git and an editor:
[SPEC.md](SPEC.md) describes the steps.

An agent, such as Claude Code, Codex, or a model behind any
OpenAI-compatible endpoint, defines the tasks and produces each task's
patch in a separate worktree. The maintainer reads each diff and
accepts or rejects it.

## Install

```bash
pipx install workplan
```

Python 3.11 or later and git. No other dependencies.

`wp` is installed as a short name for `workplan`. WP-CLI, the WordPress
command line, also installs `wp`; where both are installed, use
`workplan`.

## Manual, semi-automatic, full auto

Run it on full auto for the real vibe coding experience, or manual for the good old days.

- **Manual:** git and an editor. [SPEC.md](SPEC.md) gives every step by hand; the `workplan` command is optional.
- **Semi-automatic:** run each command; Agents define tasks and produce patches; you read the diffs and accept or reject.
- **Full auto:** `workplan install` adds hooks that route each commit
  to its next step, and `route.dispatch` runs `task gen` and
  `patch gen` as soon as they are due. Accepting each patch and
  merging stay with you.

## A workplan from start to finish

```bash
workplan init                      # create workplans/ and commit it
$EDITOR workplans/BACKLOG.md       # the work not yet started: one ## heading per item
workplan new greeting              # branch workplan/<date>-greeting/definition;
                                   # the editor opens on WORKPLAN.md: goal, context, findings;
                                   # it is committed
workplan task gen                  # the agent writes the tasks; WORKPLAN.md and the
                                   # tasks are committed
git push                           # share the plan

workplan patch gen 0000            # the agent writes output.patch and COMMIT_MSG
workplan patch apply 0000          # stage it
workplan patch show 0000           # the task, its commit, its dependencies and the diff:
                                   # read it, test it
workplan patch accept 0000         # commit it with the task's files; or: patch reject
workplan status

workplan merge                     # squash into master; the editor opens on the message;
                                   # the local definition branch is deleted
```

The commands that complete a step or change a document commit it:
`init`, `new`, `edit`, `task add`, `task gen`, `task edit`,
`task drop`, `patch accept` and `merge`. `patch apply` stages a patch
for review and commits nothing. Pushing is the maintainer's.

The workplan's commands are verbs on their own: `new`, `list`, `show`,
`edit` and `merge`; `new` and `merge` are the two that change branches.
Tasks and patches take a noun, then a verb: `task add`, `patch show`.
`list` and `show` read; `add` is you supplying something; `gen` is the
agent producing it; `edit` changes a document; `apply`, `accept`,
`reject` and `merge` are the protocol's steps. `status` is a second
name for `task list`.

To write tasks yourself in place of `task gen`, use
`task add "Say goodbye" --depend 0000` for each.

`new` opens the editor git uses for commit messages, on WORKPLAN.md
rendered from its template; closing it unchanged creates nothing.
`new greeting -m "app.txt says goodbye"` writes the goal and skips the
editor. `new greeting --reply WORKPLAN.md` takes a whole WORKPLAN.md,
written by a chat or by hand; its heading must name the new id. `edit` and `task edit` open the editor the same way on an
existing document.

Every command that changes a document commits it, on the checked-out
branch and with nothing else that is staged: `new` as `<id> workplan`,
`task add` as `<id> add <nnnn>`, `task add --reply` as
`<id> define tasks`, and `edit` and `task edit` as
`<id> edit <document>`. An edit that changes nothing commits nothing.

Every command also runs as `wp`: `wp new greeting`, `wp task add`,
`wp patch show 0000`.

`examples/demo.sh` runs this cycle in a temporary repository with a
scripted agent.

## Commands

The workplan, and the commands with no noun:

| Command | Does |
|---|---|
| `init` | create `workplans/` with README, PRINCIPLES.md, BACKLOG.md, config.toml and dispatch.sh; add the working files to .gitignore; commit |
| `list` | every workplan, in the tree or on another branch, and whether it is editable |
| `show [ID]` | the workplan's goal and its tasks' states |
| `new NAME [-m GOAL \| --reply FILE]` | `workplans/<date>-NAME/WORKPLAN.md` from its template, or the whole file given, on a new branch from master; commit |
| `edit [ID]` | WORKPLAN.md in the editor; commit |
| `merge [ID] [-m MESSAGE] [--show]` | run `test.command` and stop if it fails; squash the workplan into master, with the message from its template; `--show` prints the message |
| `status [ID]` | `task list` |
| `route [REV] [--dispatch]` | the next step after a commit |
| `install` | post-commit and post-merge hooks that run `route --dispatch` |
| `serve [--port N]` | the board in a local web page, on 127.0.0.1 |

Tasks:

| Command | Does |
|---|---|
| `task list [ID]` | each task's state; a workplan held only on another branch shows its committed states |
| `task show NNNN` | the task's state and TASK.md |
| `task add TITLE [--depend N] [-m CHANGE]` | the next task's TASK.md and BREAKDOWN.md from their templates, and its line in WORKPLAN.md; the editor opens on TASK.md; commit |
| `task add --reply FILE` | the new tasks in a `task gen` reply from a chat; `-` reads standard input; commit |
| `task gen [ID] [--prompt]` | the agent writes each new task's TASK.md and BREAKDOWN.md; they are listed in WORKPLAN.md and committed with it; `--prompt` prints the prompt for a chat |
| `task edit NNNN [--doc NAME]` | TASK.md, BREAKDOWN.md or NOTES.md in the editor; commit |
| `task drop NNNN` | move the task to `## Dropped` in WORKPLAN.md and commit WORKPLAN.md |

Patches:

| Command | Does |
|---|---|
| `patch show NNNN` | the task, its state, COMMIT_MSG, its dependencies and their states, the files changed; then the staged change if applied, else output.patch |
| `patch gen NNNN [--prompt]` | the agent writes output.patch and COMMIT_MSG; `--prompt` prints the prompt for a chat |
| `patch add NNNN [FILE]` | a reply from a chat, with its commit message line and diff, becomes output.patch and COMMIT_MSG; standard input when FILE is left out |
| `patch apply NNNN` | stage the patch in the tree and the index |
| `patch accept NNNN` | commit the patch with COMMIT_MSG, together with the task's directory and WORKPLAN.md |
| `patch reject NNNN` | take an applied patch back out |
| `patch drop NNNN` | delete an unapplied output.patch and its COMMIT_MSG |

A task is `ID/NNNN`, or `NNNN` in the current branch's workplan. Every
command takes `--json` to print its result as JSON.

## Manual mode with a chat

With no agent configured, any chat can do the agent's work. `--prompt`
prints the prompt the `none` agent would send, with the files it
names; paste it into a chat, and paste the reply back:

```bash
workplan task gen --prompt          # paste into a chat
workplan task add --reply reply.txt # its new tasks; - reads standard input
workplan patch gen 0000 --prompt
workplan patch add 0000 reply.txt   # its diff and commit message line
```

`patch add` applies the reply's diff to the head of the workplan's
branch in a separate worktree, and refuses a reply with no diff or one
that does not apply. In the page, Copy prompt and Paste reply do the
same, beside Gen tasks and Gen patch.

## Configuration

`workplans/config.toml`; `workplan init` writes it with every key, and
writes `workplans/dispatch.sh` for `route.dispatch`.
Environment variables override it, and API keys come from the
environment only.

| Key | Variable | Default |
|---|---|---|
| `master` | `WORKPLAN_MASTER` | `master` |
| `llm.api_base` | `WORKPLAN_API_BASE` | `http://localhost:8000/v1` |
| `llm.api_key_env` | | `WORKPLAN_API_KEY` |
| `llm.params` | | `{}`, added to each request body |
| `route.classifier` | `WORKPLAN_ROUTE_CLASSIFIER` | `rules` |
| `route.model` | `WORKPLAN_ROUTE_MODEL` | |
| `route.dispatch` | `WORKPLAN_ROUTE_DISPATCH` | |
| `agent.name` | `WORKPLAN_AGENT` | `none` |
| `agent.model` | `WORKPLAN_AGENT_MODEL` | |
| `agent.setup` | `WORKPLAN_AGENT_SETUP` | |
| `agent.command` | `WORKPLAN_AGENT_COMMAND` | `[]` |
| `agent.attempts`, `agent.timeout` | | `3`, `1800` |
| `test.command` | `WORKPLAN_TEST_COMMAND` | |

## Agents

`task gen` and `patch gen` create a worktree at the head of
the workplan branch, copy `workplans/` into it, run `agent.setup`, stage the worktree and keep
its tree as the base, then run the agent. The worktree is removed afterwards; the maintainer's own
tree is never touched.

- `task gen`: the new task directories the agent wrote under
  `workplans/<id>/` are copied back; existing tasks are left alone.
- `patch gen`: the worktree's diff from the base, output.patch and
  COMMIT_MSG left out, becomes output.patch; it can change files under
  `workplans/`, and the documents copied in are not part of it.

| `agent.name` | Runs |
|---|---|
| `none` | completions from `llm.api_base`; the plan files and the files they name go in the prompt; the reply holds the task files or a diff, retried with the error up to `agent.attempts` times |
| `claude-code` | `claude -p --allowedTools Read,Edit,Write,Glob,Grep,Bash`, prompt on stdin |
| `codex` | `codex exec --sandbox workspace-write <prompt>` |
| `command` | `agent.command`; a `{prompt}` argument is replaced by the prompt, else it goes on stdin |

`claude-code` and `codex` are presets of `command`; setting
`agent.command` replaces the preset's arguments. Agents with a shell
build the code and run its checks in the worktree. Containers, ports
and other host resources are shared with the host, so integration runs
stay with the maintainer.

A `command` agent receives `WORKPLAN_ACTION` (`task-gen` or
`patch-gen`) and `WORKPLAN_TARGET` (the workplan or task id) in its
environment, and for `patch-gen`, `WORKPLAN_COMMIT_MSG`: the path
to write the commit message to. When it writes none, COMMIT_MSG is the
task id and TASK.md's title.

### Examples

Claude Code, with the project's dependencies installed first:

```toml
[agent]
name = "claude-code"
setup = "uv sync"
```

Codex:

```toml
[agent]
name = "codex"
```

A model behind an OpenAI-compatible endpoint, with no agent:

```toml
[llm]
api_base = "https://api.anthropic.com/v1"     # or https://api.openai.com/v1
api_key_env = "ANTHROPIC_API_KEY"             # or OPENAI_API_KEY

[agent]
name = "none"
model = "<model name>"
```

A local model, through [marigold](https://marigold.run) or Ollama:

```toml
[llm]
api_base = "http://localhost:8000/v1"         # Ollama: http://localhost:11434/v1

[agent]
name = "none"
model = "<model name>"
```

## Routing

`workplan route` reads a commit and prints the next step: `complete`,
`review`, `patch-gen`, `task-gen` or `none`, with its targets.
The rules are in SPEC.md, section 10. With `route.classifier = "llm"`,
a model chooses the action from the prompt in
`templates/prompts/route.md`; the targets still come from the commit,
and an answer that is not an action with targets falls back to the
rules. stderr shows both choices:

```
$ workplan route
route: llm chose patch-gen; the rules chose patch-gen
patch-gen 2026-11-24-greeting/0000
```

`workplan install` adds hooks that run `workplan route --dispatch` in
the background after each commit. `--dispatch` runs `route.dispatch`
with the action and its targets. `workplan init` writes a dispatch
script, `workplans/dispatch.sh`: for `task-gen` it runs
`workplan task gen`, for `patch-gen` it runs `workplan patch gen` for
each target in parallel, and on `review` it produces each stale patch
again. Set
`route.dispatch = "workplans/dispatch.sh"` and run `workplan install`
for full auto.
The hooks clear the variables git sets for hooks, such as
`GIT_INDEX_FILE`, so that the commands a dispatch script runs work in
their own worktrees.

## Serve

```bash
workplan serve                     # http://127.0.0.1:8765/?token=...
```

`serve` starts a web server on 127.0.0.1 and prints its address, with
a token made at startup. The page runs the same operations as the
commands, so the whole flow can run from the browser, for instance
over a screen share while a team refines the tasks. A workplan is
editable while its definition branch is checked out; workplans on
other branches are shown read-only, read from their branches.

The page shows the workplan's title, branch and goal, and a board with
a column for each state. A card opens the task's TASK.md, BREAKDOWN.md,
NOTES.md and patch, rendered, with Edit and Save; its buttons are the
steps its state allows: Gen patch, Apply, Accept, Reject. The
header holds Gen tasks and Merge, and the merge message opens in a
text box. New workplan asks for a name and a goal. The selector lists
every workplan, those on other branches marked read-only. The page
refreshes every five seconds, so commits made in a terminal appear on
their own.

The page and the commands share one API: every command but `init`,
`install` and `serve` has a route, given by its verb and noun.
`task list` is `GET /api/workplan/{id}/task`, `patch accept` is
`POST /api/task/{id}/{nnnn}/patch/accept`, and so on; registry.py
holds the rule.

Every request must name 127.0.0.1 or localhost as its host, and every
API request must carry the token, so another site open in the browser
can neither read nor change anything. Operations that change the
repository run one at a time. The server keeps no state of its own:
everything it shows comes from the files and git.

## Templates

Documents, prompts and the squash commit message are rendered from
templates with `string.Template`: `$name` is replaced and nothing else
happens. To change one, copy it from `src/workplan/templates/<kind>/`
into `workplans/templates/<kind>/` and edit the copy; the rest keep the
package's version.

## Development

```bash
python -m unittest discover -s tests
```

workplans/config.toml sets this as `test.command`, so `wp merge` runs
it, quietly, before squashing a workplan into master.

The tests build temporary repositories, compare each command with its
"By hand" block in SPEC.md, rehearse two clones sharing one origin, and
run the `none` agent and the classifier against a local fake endpoint.

The version comes from git tags through setuptools-scm. A release is a
`vX.Y.Z` tag on master:

```bash
git tag v0.1.0
git push origin v0.1.0
```

`.github/workflows/release.yaml` builds the package on every push to
master; on a tag it publishes the package to PyPI and creates the
GitHub release. It runs in the `release` environment and needs the
repository secret `PYPI_API_TOKEN`.

## Licence

MIT. See [LICENSE](LICENSE).
