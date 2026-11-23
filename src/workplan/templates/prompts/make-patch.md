Make one task's change in this repository. The repository plans its
work under workplans/ with the workplan protocol.

Task: $id

The files describing the work:

$context

Make the change TASK.md states, following BREAKDOWN.md, holding to
workplans/PRINCIPLES.md and to the decisions in WORKPLAN.md.

- Edit files in the working directory. Do not commit, stage or change
  branches.
- Change nothing under workplans/ except the commit message file.
- Build the code and run its existing checks where the repository has
  them. Remove temporary and debugging changes before finishing.
- Leave out any change the task needs outside its scope, such as a
  refactoring or an unrelated fix, and name it in the final message.
- Write the commit message to $commit_msg: one line, starting
  "$id ", then what the change does.

Finish with a short summary of the change and anything left out.
