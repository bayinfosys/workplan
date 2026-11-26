# PROTOCOL.md: files, formats, states and branches

PROTOCOL.md takes from SPEC.md the parts that define the protocol:
the layout, identifiers, documents and their formats, the states, the
branches, merging's preconditions and message, review and working
together. Their text moves unchanged, apart from headings and
cross-references; the by-hand blocks stay in SPEC.md for 0002.

Effects:

- PROTOCOL.md: an introduction of a few lines, then sections for the
  layout and identifiers, documents (BACKLOG.md, WORKPLAN.md, TASK.md
  with its trailer block, BREAKDOWN.md, NOTES.md, output.patch,
  COMMIT_MSG), the document templates and their values, states,
  branches, merging, review and working together
- the states are given as the git reads that decide them
- nothing about routing, agents, prompt templates or the changelog

Depends: none
Change: docs
Audience: developers
