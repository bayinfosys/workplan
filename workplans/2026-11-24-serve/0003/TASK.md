# The board page

src/workplan/web/ holds the page: a workplan selector, the workplan's
title, branch and goal, a board with a column for each state, and a
panel for each task with its documents, its patch and its actions.

Effects:

- each task's card sits in its state's column and opens a panel with
  TASK.md, BREAKDOWN.md, NOTES.md and the patch, rendered, with Edit
  and Save on the editable workplan
- buttons run plan, define-tasks, produce-patch, apply, accept, reject
  and merge, each shown only where its state allows; merge edits the
  message in a text box
- workplans on other branches open read-only, with no edit or action
  buttons
- the page refreshes from status every five seconds unless an editor
  is open or an operation runs
- Markdown and diffs are rendered by the page's own code; the page
  loads nothing from outside the server
- TODO.md no longer lists serve

Depends on 0002.
