# Mark the protocol commands in the registry

The registry marks each command as protocol or supporting, and a test
checks that PROTOCOL.md has a section for every protocol command once
the file exists.

Effects:

- `Registry.command` takes `protocol: bool`, default False, kept on
  `Command`
- protocol: init, new, edit, merge, task add, task gen, task edit,
  task drop, patch add, patch gen, patch apply, patch accept, patch
  reject, patch drop; every other command is supporting
- tests/test_protocol.py: for each protocol command, PROTOCOL.md has a
  heading `## wp <name>`; skipped while PROTOCOL.md does not exist

Depends: none
Change: refactor
Audience: developers
