# The parent branch is the config key parent, written by init

The configuration names the parent branch `parent`, overridden by
WORKPLAN_PARENT, and `init` writes the branch checked out when it
runs.

Effects:

- config.toml takes `parent = "<branch>"` in place of `master =`;
  WORKPLAN_PARENT overrides it; the default is `master`
- `wp init` on a branch `main` writes `parent = "main"` into the new
  config.toml, and `wp new` then branches from `main`
- this repository's workplans/config.toml reads `parent = "master"`
- README.md's configuration table names `parent` and WORKPLAN_PARENT
- the code's own names, such as `ctx.master`, are unchanged

Depends: none
Change: fix
Audience: users
Breaking: the config key master is now parent, and WORKPLAN_MASTER is now WORKPLAN_PARENT
