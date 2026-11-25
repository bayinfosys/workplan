# Describe BACKLOG.md in SPEC.md, and the task commit as optional

SPEC.md describes workplans/BACKLOG.md: a `## ` heading per item,
free text under it, the order of the headings as priority, and an item
chosen for work leaving the file in the new workplan's first commit.
Section 5's step 2 says the task files may be committed when they are
defined, or with each task's patch.

Effects:

- section 1's layout lists BACKLOG.md
- section 3 has a BACKLOG.md subsection, with its form
- section 5's step 1 starts from a backlog item, with the item removed
  in the workplan's first commit, and step 2 makes committing the task
  files before work optional
- section 5's by-hand block shows the item removed from BACKLOG.md
- README.md's walkthrough mentions BACKLOG.md as the place work starts

Depends on 0003.
