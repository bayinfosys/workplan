# The last old names in comments, and the commands that commit in README.md

The docstring of tests/test_drop.py and a section comment in
tests/test_cycle.py use the command names of
2026-11-25-command-groups, and README.md's sentence on what the
commands commit lists every command that commits.

Effects:

- `grep -rnE '(list|show|add|edit|merge|gen|drop|apply|accept|reject)-(workplan|task|patch)' src tests README.md SPEC.md`
  finds only the web page's element ids and the registry test that
  checks the old names fail
- README.md names init, new, edit, task add, task gen, task edit,
  task drop, patch accept and merge as the commands that commit, and
  says patch apply commits nothing

Depends: none
Change: docs
Audience: users
