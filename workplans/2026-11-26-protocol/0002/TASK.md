# PROTOCOL.md: each protocol command as git commands

PROTOCOL.md ends with a section per protocol command, in README's
order: its `wp` form, a sentence, and a bash block of the git
commands it performs, after a preamble naming the variables.

Effects:

- a preamble: `w` (workplan id), `n` (task number), `t`
  (workplans/$w/$n), `b` (workplan/$w/definition), `master`
- a `## wp <name>` section for each of the fourteen protocol commands,
  with a bash block; arguments and trailing comments aligned in
  columns
- editor and agent steps are comment lines; task gen and patch gen
  give the files produced, and say the library uses a worktree
- every block is what the command does, in its order: init, new,
  edit, merge, task add, gen, edit, drop, patch add, gen, apply,
  accept, reject, drop
- test_protocol.py passes

Depends: 0000, 0001
Change: docs
Audience: developers
