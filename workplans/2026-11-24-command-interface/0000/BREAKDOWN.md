# Breakdown

1. registry.py: the verb table (verb to HTTP method and route suffix)
   and the noun table (noun to collection and item routes).
2. registry.py: the markers `Positional` (with `optional` and `many`)
   and `Flag`, read from each parameter's `Annotated` metadata. Over
   HTTP a value comes from the route when the route names it, else the
   query string for GET and DELETE, else the JSON body, so no marker
   is needed for that.
3. registry.py: `Command`, holding the function, its name, alias,
   help, renderer and CLI-only mark; `Registry.command` as the
   decorator.
4. registry.py: `parser()` builds a subparser per command, and one per
   alias; `run_cli` parses, calls, and prints through the renderer, or
   as JSON when there is none.
5. registry.py: `match` compiles each route to a pattern once and
   returns the command with its path values; `call` converts values to
   the declared types and fails on a missing one.
6. tests/test_registry.py: a registry of two or three test commands,
   checked in-process for names, aliases, flags, positional arguments,
   routes, methods and CLI-only commands.
