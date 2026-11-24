# TODO

Each item below becomes a workplan in workplans/.

## Next

- review: an agent step for the `review` action, and where its notes go
- internal agent: a tool loop over chat completions (read, list,
  grep, edit, allowlisted command), paths confined to the worktree
- animation: render examples/demo.tape with VHS for the README and
  the website
- try the claude-code and codex presets on a real repository, and the
  none agent against marigold and a hosted endpoint

## Later

- hosted board: a GitHub Action builds the board from `status --json`
  and publishes it to Pages
- writes from the hosted board through pull requests to
  workplan/<id>/task/<nnnn>, with a fine-grained token, then OAuth
  through a token-exchange proxy
- the agent in GitHub Actions: read-only job returns its result as an
  artefact; a separate job opens the pull request

## Open

- whether `apply` and `diff` remain two commands
- whether `route --dispatch` runs define-tasks and produce-patch itself
