# patch add refuses a reply whose commit line names another task

`parse_patch` reads the commit message line from the text before the
diff, and `use_patch` refuses a reply whose line there names another
task of the same workplan.

Effects:

- `wp patch add 0000 reply.md`, where the reply's line is
  `<id>/0003 ...`, fails with "the reply is for <id>/0003, not
  <id>/0000", and writes no output.patch or COMMIT_MSG
- a reply with no commit line still gets COMMIT_MSG from TASK.md's
  title, with the note, as now
- a line inside the diff that starts with a task id is not taken for
  the commit message
- the none agent's patch gen gets the same error back, and retries

Depends: none
Change: fix
Audience: users
