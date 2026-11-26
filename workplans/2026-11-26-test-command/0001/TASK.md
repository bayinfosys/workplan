# PRINCIPLES.md, SPEC.md and README.md on the tests; the backlog item

The documents state what test.command relies on, and where to find the
tests; the Test command item leaves the backlog.

Effects:

- workplans/PRINCIPLES.md: each accepted task leaves the test suite
  passing; tasks may add to it; the suite exists before the workplan
- SPEC.md section 9: the project's tests run on the branch before the
  squash, in the text and in the by-hand block; the definition branch
  may be rewritten until it is merged
- README.md's Development section, which gives the test command, says
  `wp merge` runs it, through workplans/config.toml
- workplans/BACKLOG.md: the Test command item is removed

Depends on 0000.
