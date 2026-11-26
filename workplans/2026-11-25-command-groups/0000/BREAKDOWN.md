# Breakdown

1. In src/workplan/registry.py, give `Registry` a `top` argument, the
   nouns whose verbs are top-level, and `("workplan",)` from
   commands.py. `Registry.command` sets `Command.words`: `(verb,)`
   for no noun or a top noun, else `(noun, verb)`; `Command.name` is
   the words joined by a space.
2. In `http_of`, route the verb `new` as `add`.
3. In `parser`, add the top-level commands to the top subparsers, and
   one subparser per other noun with its own required subparsers of
   verbs; aliases stay top-level.
4. In `get`, find a command by its name or alias; `call` names it as
   now.
5. In src/workplan/commands.py, rename `cmd_add_workplan` to
   `cmd_new_workplan`; update the help and messages that name
   commands.
6. In src/workplan/cli.py, `PAGED = ("patch show",)`.
7. In src/workplan/ops.py and src/workplan/agent.py, use the new names
   in messages: `patch accept` commits on the workplan branch, `patch
   reject` takes it out first, `task gen` commits on the branch.
8. In tests/test_registry.py, test the words, the names, a noun with no
   verb, an old name failing, and the routes as before; in every other
   test module and tests/support.py, run commands by the new names.
