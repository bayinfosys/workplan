# merge says it is running test.command

`ops.merge` takes `on_test`, a callback it calls with the test command
just before running it; `cmd_merge_workplan` passes one that writes to
stderr on the CLI.

Effects:

- `wp merge` with test.command set prints "running test.command:
  <command>" to stderr once the workplan is ready to merge and before
  the tests run
- a merge refused before the tests, such as one with an uncommitted
  task, prints no such line
- over HTTP, the result is as now, with nothing printed
- with test.command empty, nothing is printed

Depends: none
Change: feat
Audience: users
