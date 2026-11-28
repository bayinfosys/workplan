# A Code section in PRINCIPLES.md, for agents

PRINCIPLES.md ends with a Code section: a few lines an agent reads in
the patch-gen prompt.

Effects:

- the section says, one line each: comments only where the code
  cannot say it; no docstrings that restate the name; no checks for
  cases that cannot happen; no helpers used once; short plain names;
  British English, full sentences, in comments and messages
- under 10 lines

Depends: none
Change: docs
Audience: developers
