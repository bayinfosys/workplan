# patch accept refuses a task WORKPLAN.md does not list

`accept` checks that the task's number is listed under Tasks in
WORKPLAN.md before it applies or commits anything.

Effects:

- `wp patch accept 0003`, with workplans/<id>/0003/ and its patch in
  place and no `0003` line under Tasks, fails with "<id>/0003 is not
  listed in WORKPLAN.md; add its line under ## Tasks", and changes
  nothing
- a task listed under Dropped is refused in the same way
- listed tasks are accepted as now

Depends: none
Change: fix
Audience: users
