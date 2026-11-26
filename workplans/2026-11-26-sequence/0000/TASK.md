# README and PRINCIPLES.md on sequence and git; release and provenance in the backlog

README.md says the library ensures the order of git operations;
PRINCIPLES.md records it and the git-only rule; BACKLOG.md gains
Release and Provenance.

Effects:

- README.md, after the three modes: a paragraph on by-hand steps and
  the order the library ensures, with accept, merge and release as
  examples
- PRINCIPLES.md: the library ensures the order of git operations
  within a step, and restores the tree when one fails; the repository
  is read and changed through git commands only; a command exists
  where a step is several git operations whose order matters
- BACKLOG.md: Release and Provenance as its first two items

Depends: none
Change: docs
Audience: users
