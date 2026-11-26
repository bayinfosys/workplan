# Remove SPEC.md

SPEC.md is deleted, and nothing in the repository names it.

Effects:

- SPEC.md does not exist
- workplans/PRINCIPLES.md: PROTOCOL.md defines the protocol; a change
  to a format or to a protocol command's git steps changes PROTOCOL.md
  in the same task
- the project template's README.md and pyproject.toml's Specification
  URL link PROTOCOL.md
- tests/test_by_hand.py's docstring names PROTOCOL.md
- `grep -rn SPEC.md` outside workplans/ finds nothing

Depends: 0001, 0002, 0003
Change: docs
Audience: users
Breaking: SPEC.md is removed; the protocol is in PROTOCOL.md
