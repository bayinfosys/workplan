# README.md for a new user

README.md says what the project is for, how to try it on this
repository, where it runs, and how to remove it.

Effects:

- after the opening, two points: git as state, with no other store;
  and a protocol, not a service, with no server and any agent
- "Try it on this repository": `git clone`, install, then `wp list`,
  `wp serve` and `wp changelog v0.1.0` on its own workplans
- the examples/demo.sh line is removed
- under Install: Linux, with git and Python 3.11 or later
- "Removing workplan": delete the hooks `install` wrote, the two
  .gitignore lines, workplans/, and uninstall the package
- "parent branch" where README says master for the configured branch

Depends: 0000
Change: docs
Audience: users
