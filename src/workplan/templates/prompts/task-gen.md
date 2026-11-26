Define the tasks of one workplan in this repository. The repository
plans its work under workplans/ with the workplan protocol.

Workplan: $id

The files describing the work:

$context

Read WORKPLAN.md and the code it names. Break the goal into tasks. A
task is one change, applied as one commit and reviewed as one diff,
and needs no further decisions before work starts. Order the tasks so
that each depends only on tasks before it.

For each new task, numbered from $next upwards, write two files.

workplans/$id/<nnnn>/TASK.md, in this form, with each $$name and each
<...> replaced; "Depends on" names earlier task numbers, or "none":

$task_template
workplans/$id/<nnnn>/BREAKDOWN.md, in this form:

$breakdown_template
- Write only these files. Change no code and no other file under
  workplans/; leave existing task directories as they are.
- Do not commit, stage or change branches.
- Hold to workplans/PRINCIPLES.md and to the decisions in WORKPLAN.md.

Finish with the list of tasks, one line each.
