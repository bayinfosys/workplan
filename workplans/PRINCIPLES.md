# Principles

Every task and every review holds to these.

- a task makes the change it states and nothing else
- every step of the protocol can be carried out by hand with git and
  an editor; PROTOCOL.md defines the protocol, and a change to a format
  or to a protocol command's git steps changes PROTOCOL.md in the same
  task
- the library ensures the order of the git operations within a step,
  and restores the tree when one fails
- the repository is read and changed through git commands only
- a command exists where a step is several git operations whose order
  matters; a step that is one git command stays by hand
- all state is in files and git history; no command keeps state of
  its own
- templates use substitution only
- the standard library only
- few commands and parameters; an existing command in preference to a
  new one
- operations return data; the CLI and the web server format it
- a command that changes a document commits it
- commands write to the checked-out branch only; new, which
  starts a workplan's branch, and merge, which squashes it
  into master, are the commands that change branches
- documentation changes with the code, in the same task
- the project has a test suite before a workplan starts; each accepted
  task leaves it passing, and tasks may add to it
- a change a task needs outside its scope is raised for a later
  workplan

## Code

- comment only what the code cannot say
- no docstring that restates the name
- no check for a case that cannot happen
- no helper used once
- short, plain names
- comments and messages in British English, in full sentences
