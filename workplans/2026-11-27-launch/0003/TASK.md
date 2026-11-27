# PROTOCOL.md: glossary, version and the parent branch

PROTOCOL.md opens with a glossary and a version policy, says "parent
branch", and its section 5 matches what the commands do.

Effects:

- a glossary after the introduction: workplan, task, patch, state and
  parent branch, a line each
- the version line reads 0.3, and says: pre-1.0; it changes without
  compatibility until 1.0; its version follows the package's minor
  version
- "parent branch" where PROTOCOL.md means the configured branch, and
  `$parent` in place of `$master` in the blocks
- section 5: merge runs the project's tests; the commands commit, and
  agents do not

Depends: none
Change: docs
Audience: developers
