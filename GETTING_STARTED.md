# Getting started

## Install

```bash
pipx install workplan
```

Python 3.11 or later and git, on Linux. `wp` is installed as a short
name for `workplan`; where WP-CLI's `wp` is also installed, use
`workplan`.

## Try it on this repository

The workplan repository is planned with workplan: every change since
v0.1.0 is a workplan in `workplans/`, merged as one squash commit.

```bash
git clone https://github.com/bayinfosys/workplan
cd workplan
wp list                            # the workplans, and where they are held
wp show 2026-11-26-change-kinds    # a workplan's goal and its tasks' states
wp changelog v0.1.0                # what changed since v0.1.0, from git alone
wp serve                           # the board, in a local web page
```

## A first workplan, without an agent

A chat does the agent's work: workplan prints the prompt, and takes
the reply.

```bash
mkdir hello && cd hello && git init -b main
echo 'print("hello")' > app.py
git add app.py && git commit -m "hello"

wp init                                        # workplans/, committed
wp new goodbye -m "app.py says goodbye"        # a branch and WORKPLAN.md, committed
wp task add "Say goodbye" -m "app.py prints goodbye in place of hello"
wp patch gen 0000 --prompt > ../prompt.md      # paste it into a chat
```

Save the chat's reply as `../reply.md`: a commit message line that
starts with the task id, then a diff. Then:

```bash
wp patch add 0000 ../reply.md                  # output.patch and COMMIT_MSG
wp patch show 0000                             # the task, its commit and the diff
wp patch accept 0000                           # committed with the task's files
wp merge                                       # one squash commit on main
wp publish                                     # with a remote: push main, delete the branches
```

`wp status` shows each task's state at any point. Every step is a
sequence of git commands, given in [PROTOCOL.md](PROTOCOL.md); the
commands run them in order.

## With an agent

Name the agent in `workplans/config.toml`:

```toml
[agent]
name = "claude-code"     # or codex; or none, with model and llm.api_base
```

Then the agent writes the tasks and the patches, and you review:

```bash
wp new greeting                    # the editor opens on WORKPLAN.md: goal, context, findings
wp task gen                        # the agent writes the tasks; committed
wp patch gen 0000                  # the agent writes output.patch and COMMIT_MSG
wp patch show 0000                 # read it
wp patch accept 0000               # or: wp patch reject 0000
wp merge && wp publish
```

## Manual, semi-automatic, full auto

- **Manual:** git and an editor. [PROTOCOL.md](PROTOCOL.md) gives every
  step as git commands; the `workplan` command is optional.
- **Semi-automatic:** run each command; an agent or a chat writes the
  tasks and patches; you read the diffs and accept or reject.
- **Full auto:** `wp install` adds hooks that route each commit to its
  next step, and `route.dispatch = "workplans/dispatch.sh"` runs
  `task gen` and `patch gen` as soon as they are due. Accepting each
  patch and merging stay with you.

The commands and their options are in [README.md](README.md).
