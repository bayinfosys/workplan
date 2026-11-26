# Commands commit the documents they change

add-workplan, add-task, add-task --reply, edit-workplan and edit-task
commit the documents they write, alone, on the checked-out branch,
with the messages in WORKPLAN.md's decisions; workplans/PRINCIPLES.md
gains the two rules.

Effects:

- after any of these commands, `git status --porcelain` shows nothing
  from them, and `git log -1` shows their commit
- other staged changes stay staged and out of the commit
- an edit that changes nothing commits nothing; the CLI prints
  "nothing to commit"
- each result has `commit`, the new commit's `%h %s`, or null
- README.md and SPEC.md section 4, with its by-hand block, say what
  each command commits

Depends: none
Change: feat
Audience: users
