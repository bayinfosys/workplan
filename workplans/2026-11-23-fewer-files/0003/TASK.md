# Drop the usage epilog from the CLI

cli.py's `USAGE` epilog is deleted; `workplan --help` lists the
subcommands from their own help text.

Effects:

- `workplan --help` lists each subcommand once
- cli.py holds no text that repeats argparse's

Depends on none.
