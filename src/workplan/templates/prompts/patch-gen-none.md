Make one task's change in a git repository. The repository plans its
work under workplans/ with the workplan protocol.

Task: $id

The files describing the work, and the files they name:

$context

Make the change TASK.md states, following BREAKDOWN.md, holding to
PRINCIPLES.md and to the decisions in WORKPLAN.md. Change only what the
task needs.

Reply with two parts:

1. The commit message on a line of its own: one line, starting "$id ",
   then what the change does.
2. The change as one unified diff in a ```diff fenced block: paths
   relative to the repository root with a/ and b/ prefixes, three lines
   of context for each hunk, applicable with git apply. A new file uses
   --- /dev/null.
