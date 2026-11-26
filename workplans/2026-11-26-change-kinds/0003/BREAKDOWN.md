# Breakdown

1. In src/workplan/ops.py, add `changelog(start, end, audience)`
   returning the heading, the range and the entries, each with its
   section, task, title and workplan.
2. In src/workplan/commands.py, add `cmd_changelog`, a top-level
   command with a GET route `/api/changelog`, and `render_changelog`.
3. In README.md, add the row and a section after Manual mode; in
   SPEC.md, a section on the changelog with its by-hand block.
4. In tests, a test module of its own: two workplans merged between
   tags, with feat, fix, no Change, a Breaking line, an audience, and a
   dropped task; the defaults for FROM and TO; `--audience`; and that
   HEAD and the refs are unchanged.
