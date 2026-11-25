# Record the departures of 2026-11-24-command-interface in NOTES.md

Four tasks of 2026-11-24-command-interface were made with changes
their TASK.md did not state. Each departure is written as a question
and its answer in a NOTES.md in that task's directory.

Effects:

- 0004/NOTES.md: the agent module's functions were renamed with the
  actions
- 0005/NOTES.md: the TASK.md template gained the `$change` value
- 0006/NOTES.md: a reply is a file or standard input on the CLI and
  text over HTTP, so the server reads no files; add-patch keeps the
  diff git produces in the worktree, in place of the reply's text;
  add-patch and gen-patch share the worktree and capture code
- 0007/NOTES.md: the patch was built after 0006, so it depends on
  0006 in place of 0003 alone
- each file follows the NOTES.md template

Depends on none.
