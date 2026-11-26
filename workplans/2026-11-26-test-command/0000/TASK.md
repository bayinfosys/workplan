# merge runs test.command before squashing

`test.command` joins the configuration, and `merge` runs it on the
workplan's branch before squashing, refusing to merge when it fails.

Effects:

- config.toml takes `[test] command = "..."`, a shell command, empty by
  default; WORKPLAN_TEST_COMMAND overrides it
- `wp merge`, with the command set and the workplan's branch checked
  out, runs it in the working tree first; on success it squashes as
  now, and its output says "test.command passed: <command>"
- on failure it merges nothing, leaves the branch checked out, and
  fails with the exit status, the command and the last lines of its
  output
- with the command set and another branch checked out, merge fails
  with "switch to <branch> to run test.command"
- with the command empty, merge behaves as now; `merge --show` runs
  nothing
- the project template's config.toml and this repository's
  workplans/config.toml have a `[test]` section; this repository's
  command is `python -m unittest discover -s tests -q`
- README.md's configuration table and merge row name it

Depends: none
Change: feat
Audience: users
