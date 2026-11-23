Define the tasks of one workplan in a git repository. The repository
plans its work under workplans/ with the workplan protocol.

Workplan: $id

The files describing the work, and the files they name:

$context

Break the goal in WORKPLAN.md into tasks. A task is one change,
applied as one commit and reviewed as one diff, and needs no further
decisions before work starts. Order the tasks so that each depends
only on tasks before it. Hold to PRINCIPLES.md and to the decisions in
WORKPLAN.md. Existing tasks stay as they are.

For each new task, numbered from $next upwards, give two files.

TASK.md, in this form, with each $$name and each <...> replaced;
"Depends on" names earlier task numbers, or "none":

$task_template
BREAKDOWN.md, in this form:

$breakdown_template
Reply with each file after a line of its own naming its path, and
nothing else:

===== workplans/$id/<nnnn>/TASK.md =====
<the file>
===== workplans/$id/<nnnn>/BREAKDOWN.md =====
<the file>
