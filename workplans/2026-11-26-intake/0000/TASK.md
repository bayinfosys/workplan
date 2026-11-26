# new takes a whole WORKPLAN.md with --reply

`wp new NAME --reply FILE` writes the given WORKPLAN.md in place of the
template, on the new branch, and commits it as `<id> workplan`.

Effects:

- `wp new intake --reply WORKPLAN.md` creates the branch and commits
  that file unchanged; `-` reads standard input
- over HTTP, `POST /api/workplan` takes `reply` as the text
- a reply whose first heading reads `# Workplan <other id>:` fails with
  "the WORKPLAN.md is for <other id>, not <id>", and creates nothing
- `-m` and `--reply` together fail
- an empty reply fails, as for the other replies
- README.md's command table and the paragraph on `new` describe it

Depends: none
Change: feat
Audience: users
