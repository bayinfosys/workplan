A commit was made in a repository that plans work in workplans/.
workplans/<id>/WORKPLAN.md is a workplan; workplans/<id>/<nnnn>/TASK.md
and BREAKDOWN.md define a task; a commit whose subject starts
<id>/<nnnn> is that task's change; a commit on master with a Workplan
trailer completes a workplan.

Actions:
complete: a workplan reached master
review: code changed under a task, so it needs checking against the task
patch-gen: a task definition changed, so its patch needs producing
task-gen: the workplan changed, so its tasks need defining
none: nothing to do

Branch: $branch
Parents: $parents
Subject: $subject
Workplan trailer: $workplan
Changed paths:
$paths

Answer with the action's name only.
