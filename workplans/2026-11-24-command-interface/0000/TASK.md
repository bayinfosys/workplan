# The command registry

src/workplan/registry.py declares commands once and gives both
interfaces from the declaration: an argparse parser for the CLI, and
the HTTP method and route for the API.

Effects:

- a command is a function `cmd_<verb>_<noun>(ctx, *, ...)` registered
  with `@registry.command(...)`; its CLI name is `verb-noun`
- each keyword-only parameter is declared, with `typing.Annotated`, as
  positional or a flag on the CLI, and as a path segment, query field
  or body field over HTTP; `str`, `int`, `bool` and `list[str]` are
  supported
- the verb gives the HTTP method and the noun the route, as decision 6
  sets out; `workplan` is one path segment and `task` two (`{id}/{nnnn}`)
- a command can carry a CLI name alias, a text renderer for the CLI,
  and a CLI-only mark
- `Registry.parser()` and `Registry.run_cli(argv, ctx)` serve the CLI;
  `Registry.match(method, path)` finds the command and its path
  parameters, and `Registry.call(command, ctx, values)` runs it

Depends on none.
