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
  to its next step, and `route.dispatch` runs `define-tasks` and
  `produce-patch` as soon as they are due. Accepting each patch and
  merging stay with you.

## A workplan from start to finish

```bash
workplan init                      # create workplans/ and commit it
workplan plan greeting             # branch workplan/<date>-greeting/definition;
                                   # the editor opens on WORKPLAN.md: goal, context, findings
workplan define-tasks              # the agent writes the tasks; WORKPLAN.md and the
                                   # tasks are committed
git push                           # share the plan

workplan produce-patch 0000        # the agent writes output.patch and COMMIT_MSG
workplan apply 0000                # stage it
workplan diff 0000                 # read it, test it
workplan accept 0000               # commit it with the task's files; or: workplan reject 0000
workplan status

workplan merge                     # squash into master; the editor opens on the message
```

The commands commit what they complete: `init`, `define-tasks`,
`accept` and `merge`. Pushing is the maintainer's.

`plan` opens the editor git uses for commit messages, on WORKPLAN.md
rendered from its template; closing it unchanged creates nothing.
`plan greeting -m "app.txt says goodbye"` writes the goal and skips the
editor.

Every command also runs as `wp`: `wp plan greeting`, `wp accept 0000`.

`examples/demo.sh` runs this cycle in a temporary repository with a
scripted agent.

## Commands

| Command | Does |
|---|---|
| `init` | create `workplans/` with README, PRINCIPLES.md and config.toml; add the working files to .gitignore; commit |
| `plan NAME [-m GOAL]` | `workplans/<date>-NAME/WORKPLAN.md` from its template, on a new branch from master |
| `define-tasks [ID]` | the agent writes each new task's TASK.md and BREAKDOWN.md; they are listed in WORKPLAN.md and committed with it |
| `produce-patch NNNN` | the agent writes output.patch and COMMIT_MSG |
| `apply NNNN`, `diff NNNN` | stage the patch; show it |
| `accept NNNN` | commit the patch with COMMIT_MSG, together with the task's directory and WORKPLAN.md |
| `reject NNNN` | take an applied patch back out |
| `merge [ID]` | squash the workplan into master, with the message from its template |
| `status [ID \| ID/NNNN] [--json]` | each task's state, and layout problems in its files |
| `route [REV] [--dispatch]` | the next step after a commit |
| `install` | post-commit and post-merge hooks that run `route --dispatch` |

A task is `ID/NNNN`, or `NNNN` in the current branch's workplan.

## Configuration

`workplans/config.toml`; `workplan init` writes it with every key.
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

## Agents

`define-tasks` and `produce-patch` create a worktree at the head of
the workplan branch, copy `workplans/` into it, run `agent.setup`, then
the agent. The worktree is removed afterwards; the maintainer's own
tree is never touched.

- `define-tasks`: the new task directories the agent wrote under
  `workplans/<id>/` are copied back; existing tasks are left alone.
- `produce-patch`: the worktree's diff outside `workplans/` becomes
  output.patch.

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

A `command` agent receives `WORKPLAN_ACTION` (`define-tasks` or
`produce-patch`) and `WORKPLAN_TARGET` (the workplan or task id) in its
environment, and for `produce-patch`, `WORKPLAN_COMMIT_MSG`: the path
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
`review`, `produce-patch`, `define-tasks` or `none`, with its targets.
The rules are in SPEC.md, section 10. With `route.classifier = "llm"`,
a model chooses the action from the prompt in
`templates/prompts/route.md`; the targets still come from the commit,
and an answer that is not an action with targets falls back to the
rules. stderr shows both choices:

```
$ workplan route
route: llm chose produce-patch; the rules chose produce-patch
produce-patch 2026-11-24-greeting/0000
```

`workplan install` adds hooks that run `workplan route --dispatch` in
the background after each commit. `--dispatch` appends the decision to
`.git/workplan/route.log` and runs `route.dispatch` with the action and
its targets. `define-tasks` and `produce-patch` are also command
names, so a dispatch script can run `workplan "$@"` for those two.

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

The tests build temporary repositories, compare each command with its
"By hand" block in SPEC.md, rehearse two clones sharing one origin, and
run the `none` agent and the classifier against a local fake endpoint.

## Licence

MIT. See [LICENSE](LICENSE).
