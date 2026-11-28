# The BACKLOG.md item format in PROTOCOL.md and the init template

PROTOCOL.md defines the shape of a BACKLOG.md item, so that people,
agents and a parser read the backlog the same way; the order of the
items carries no meaning.

Effects:

- PROTOCOL.md section 1: the layout line reads "BACKLOG.md
  candidate workplans", without "in order of priority"
- PROTOCOL.md section 3, BACKLOG.md:
  - each `## ` heading is an item; its name is the heading as a slug,
    lower-case words joined by `-`, as a workplan name is: "Item
    commands" is item-commands
  - the first paragraph under the heading is the goal of the
    workplan it would become
  - `- ` lines after it are the tasks already in view
  - an optional trailer block ends the item, one `Key: value` line
    each; `Depends` names other items by name
  - an item is the text from its heading to the next; by hand,
    `git interpret-trailers --parse` on that text prints its trailers
  - the order of the items carries no meaning
  - an example backlog of two items in this shape, one with a
    Depends trailer, naming no real project
- the sentence on an item chosen for work, which leaves BACKLOG.md in
  the workplan's first commit, stays
- src/workplan/templates/project/BACKLOG.md: the preamble describes
  the shape in two or three lines, and drops "Items are in order of
  priority"
- the test suite passes

Depends: none
Change: docs
Audience: users
