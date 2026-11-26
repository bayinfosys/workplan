# The commands, named verb-noun, on the CLI

src/workplan/commands.py declares every command that exists today
under its new name through the registry, and cli.py runs them; the
old names are removed, except `status`.

Effects:

- `init`, `list-workplan`, `show-workplan`, `add-workplan`,
  `edit-workplan`, `merge-workplan`, `list-task` (and `status`),
  `show-task`, `gen-task`, `edit-task`, `show-patch`, `gen-patch`,
  `apply-patch`, `accept-patch`, `reject-patch`, `route`, `install` and
  `serve` run from the CLI, with today's behaviour and output
- `edit-workplan` and `edit-task` open the editor on the document, as
  `add-workplan` does on WORKPLAN.md; `merge-workplan --show` prints
  the message without merging
- `show-workplan` and `show-task` give the documents' text with the
  states, in their data, for the API
- cli.py holds `main` only; the entry points are unchanged
- the tests, README.md and SPEC.md use the new names

Depends: 0000
Change: refactor
Audience: users
Breaking: the commands are named verb-noun: plan is now add-workplan, define-tasks gen-task, produce-patch gen-patch, apply apply-patch, diff show-patch, accept accept-patch, reject reject-patch and merge merge-workplan; status is kept
