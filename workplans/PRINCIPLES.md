# Principles

Every task and every review holds to these.

- a task makes the change it states and nothing else
- every step of the protocol can be carried out by hand with git and
  an editor; SPEC.md gives the step, and a change to a step changes
  SPEC.md in the same task
- all state is in files and git history; no command keeps state of
  its own
- templates use substitution only
- the standard library only
- few commands and parameters; an existing command in preference to a
  new one
- operations return data; the CLI and the web server format it
- a command that changes a document commits it
- commands write to the checked-out branch only; add-workplan, which
  starts a workplan's branch, and merge-workplan, which squashes it
  into master, are the commands that change branches
- documentation changes with the code, in the same task
- a change a task needs outside its scope is raised for a later
  workplan
