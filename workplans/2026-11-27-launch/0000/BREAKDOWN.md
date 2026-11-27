# Breakdown

1. src/workplan/config.py: DEFAULTS and OVERRIDES use `parent`.
2. src/workplan/commands.py and route.py: read `cfg["parent"]`.
3. The project template's config.toml: `parent = "master"`; in
   `init`, replace that line with the current branch when writing it.
4. workplans/config.toml and README.md's configuration table.
5. tests: `init` on `main` writes the key and `new` works there;
   WORKPLAN_PARENT overrides it.
