# Workplan 2026-11-28-docs-references: docs references

## Goal

The documents describe workplan as it stands after v0.3.0: PROTOCOL.md
in place of SPEC.md; master as the parent branch; the current workplan
as the one the checked-out branch names; `wp` as the command; links to
the site and to PyPI; and BACKLOG.md in a fixed item format, holding
the current candidate workplans.

## Context

- README.md: the opening, Install (`wp` as a short name, the WP-CLI
  clash), Getting started, Commands (the two tables, lines 51-124),
  Manual mode with a chat, Changelog, Configuration, Agents, Routing,
  Serve, Templates, Development, Removing workplan, Licence; 27 command
  lines start `workplan <command>` and 4 start `wp <command>`
- PROTOCOL.md: the terms table (parent branch); section 1, the layout,
  with BACKLOG.md as "candidate workplans, in order of priority";
  section 3, BACKLOG.md as free text under each `## ` heading, the
  headings in order of priority; section 8, Branches; section 12, the
  protocol commands; 24 lines with `workplan <command>`, 18 with `wp`
- GETTING_STARTED.md: 3 lines with `workplan <command>`, 21 with `wp`
- workplans/README.md: links SPEC.md, which v0.3.0 removed; lacks the
  BACKLOG.md and dispatch.sh lines that
  src/workplan/templates/project/README.md has
- workplans/PRINCIPLES.md: "merge, which squashes it into master";
  no line on publish
- workplans/BACKLOG.md: Release, Provenance, Item commands,
  gen-workplan, gen-prompts, prompt-log, Review page, Workplan order,
  Real agents, Internal agent, Animation, Hosted board, Unwind; names
  SPEC, the old command names gen-task, gen-patch, list-workplan, and
  examples/demo.tape
- src/workplan/templates/project/BACKLOG.md: the preamble written by
  init, "Items are in order of priority"
- src/workplan/plans.py: current_workplan() takes the workplan from a
  branch matching `workplan/<id>/`; otherwise the newest dated
  workplan by id, else the only workplan, else it fails
- src/workplan/commands.py: the merge help reads "squash the workplan
  into master"
- pyproject.toml: [project.urls] Homepage and Repository are the
  GitHub repository; Protocol is PROTOCOL.md on GitHub; Issues
- the site, https://workplan.bayis.co.uk, builds README.md,
  GETTING_STARTED.md, PROTOCOL.md, CHANGELOG.md and LICENSE from
  master: `/`, `/getting-started.html`, `/protocol.html`,
  `/changelog.html`
- the package, https://pypi.org/project/workplan/: its page shows
  README.md and [project.urls] as of the latest release

## Findings

- workplans/README.md links SPEC.md, which no longer exists (0000)
- the documents, the help and the prompts say master where the
  configured parent branch is meant, and nothing says so (0000)
- the documents mix `workplan <command>` and `wp <command>` (0000)
- the documents do not say how a command finds the current workplan,
  how to move to another, or what happens off a workplan branch (0001)
- PRINCIPLES.md names master as the branch merge squashes into, and
  does not say that publish is the one command that pushes (0002)
- no document links the site or PyPI, and the package metadata points
  at GitHub only; README.md is the page GitHub and PyPI show, and the
  links from it bring the site into search indexes (0003)
- BACKLOG.md has no fixed shape for an agent or a parser to read, and
  its order is described as priority, which carries no meaning for
  this project (0004)
- BACKLOG.md names SPEC, the old command names and examples/ which no
  longer exists; Item commands and gen-workplan predate the command
  groups; the animation, the examples and the self-hosted loop are
  missing or split across items (0005)

## Decisions

1. "master" in the documents, the help and the prompts refers to the
   parent branch of the workplan branch. One sentence says so, in the
   terms table of PROTOCOL.md and in README.md's Commands; the text
   is left as it is.
2. The documents use `wp` for every command. Install keeps one
   sentence: `workplan` is the full name, for use where WP-CLI's `wp`
   is installed. The package, the repository and the program keep the
   name workplan.
3. README.md's Commands opens with the model: `wp` works on the
   current workplan, its tasks and its patches, as git works on the
   checked-out branch. The checked-out branch names the current
   workplan; `git switch workplan/<id>/definition` moves to another,
   one git command, so no `wp switch`. Off a workplan branch, the
   newest dated workplan by id is current, else the only one. `list`,
   `changelog` and `serve` read across every workplan; `new` and
   `merge` move between the parent branch and a workplan branch.
4. PRINCIPLES.md: merge squashes into the parent branch, and publish
   is the command that pushes, in the existing branch line.
5. pyproject.toml [project.urls]: Homepage
   https://workplan.bayis.co.uk; Documentation
   https://workplan.bayis.co.uk/getting-started.html; Protocol
   https://workplan.bayis.co.uk/protocol.html; Changelog
   https://workplan.bayis.co.uk/changelog.html; Repository and Issues
   stay on GitHub. README.md links the site and the PyPI page under
   its opening paragraph. The metadata reaches PyPI with the next
   release.
6. The BACKLOG.md item format, in PROTOCOL.md section 3 and the init
   template: a `## ` heading names the item, and its slug, lower-case
   words joined by `-`, is the item's name; the first paragraph is
   the goal; `- ` lines are the tasks in view; an optional trailer
   block ends the item, `Depends: <item>, <item>`, read with
   `git interpret-trailers --parse`. The order of the items carries
   no meaning. Section 1's layout line drops "in order of priority".
7. BACKLOG.md is rewritten in that format, from the items as they
   stand:
   - Release, Provenance, gen-prompts, prompt-log, Review page,
     Workplan order, Hosted board, Unwind: kept, in the current
     command names, with PROTOCOL.md for SPEC
   - Item commands: `item list` and `item show` over BACKLOG.md, with
     `--json` for the board and the site; `new --item NAME` fills
     WORKPLAN.md from the item and removes it from BACKLOG.md in the
     workplan's first commit; items are added, edited and removed by
     hand, one edit and one commit each
   - gen-workplan: `new NAME --gen`, the agent writes WORKPLAN.md, a
     fourth source beside the editor, `-m` and `--reply`; combines
     with `--item`; Depends: gen-prompts
   - Self-hosted loop: Real agents and Internal agent as one item;
     the none agent and the internal tool loop against marigold, a
     self-hosted model layer, for an AI-assisted code loop with no
     hosted model; the claude-code and codex presets tried and
     recorded in README.md
   - Examples: a demo repository and script that runs a workplan from
     new to publish with a scripted agent
   - Animation: the Examples run recorded with VHS for README.md and
     the site; Depends: examples
   - Current workplan: off a workplan branch, commands that write
     need an explicit ID; reads keep the fallback
   - Program name: `--help` prints the name it was run as, `wp` or
     `workplan`
8. The work changes documents and package metadata only; the help
   text, prompts and code are unchanged.

## Tasks

0000  PROTOCOL.md for SPEC.md, master as the parent branch, and wp
      throughout the documents
0001  The current workplan in README.md's Commands
0002  PRINCIPLES.md on the parent branch and publish
0003  Links to the site and PyPI in pyproject.toml and README.md
0004  The BACKLOG.md item format in PROTOCOL.md and the init template
0005  BACKLOG.md in the item format, with the current candidates

## Dropped
