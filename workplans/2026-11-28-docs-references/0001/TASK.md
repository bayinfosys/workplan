# The current workplan in README.md's Commands

README.md's Commands opens with how `wp` finds the workplan it works
on, how to move to another, and which commands read across every
workplan.

Effects:

- a paragraph, or two, at the top of README.md's Commands, before
  "The commands that complete a step...":
  - `wp` works on the current workplan, its tasks and its patches, as
    git works on the checked-out branch
  - the checked-out branch names the current workplan:
    `workplan/<id>/definition` and `workplan/<id>/task/<nnnn>` both
    name `<id>`
  - `git switch workplan/<id>/definition` moves to another workplan;
    for a workplan only on the remote, git creates the tracking branch;
    there is no `wp switch`, as switching is one git command
  - off a workplan branch, the current workplan is the newest dated
    workplan by id, else the only workplan; otherwise a command needs
    the id
  - `list`, `changelog` and `serve` read across every workplan; `new`
    and `merge` move between the parent branch and a workplan branch
- the paragraph's account matches current_workplan() in
  src/workplan/plans.py

Depends: 0000
Change: docs
Audience: users
