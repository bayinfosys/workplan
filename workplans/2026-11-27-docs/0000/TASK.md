# GETTING_STARTED.md, and README.md as overview and reference

GETTING_STARTED.md holds the first steps, from install to a merged and
published workplan; README.md loses them and links it.

Effects:

- GETTING_STARTED.md: Install; Try it on this repository; A first
  workplan, without an agent: `wp init`, `wp new -m`, `wp task add`,
  `wp patch gen --prompt` into a chat, `wp patch add`, `wp patch
  show`, `wp patch accept`, `wp merge`, `wp publish`; With an agent:
  `agent.name`, then `wp task gen` and `wp patch gen`
- every command in it runs as written in a new repository
- README.md: the opening, the two points, Install, a "Getting started"
  line linking GETTING_STARTED.md, Commands, Manual mode with a chat,
  Changelog, Configuration, Agents, Routing, Serve, Templates,
  Development, Removing workplan, Licence
- the walkthrough, "Try it on this repository" and the three modes
  leave README.md; their content is in GETTING_STARTED.md
- links between the documents are by file name

Depends: none
Change: docs
Audience: users
