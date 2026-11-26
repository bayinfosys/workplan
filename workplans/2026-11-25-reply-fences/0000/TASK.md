# Fences in a reply open and close at the start of a line

`FENCE` matches an opening fence at the start of a line and closes at
the next line that starts with three backticks, so lines of backticks
inside a diff are part of the diff.

Effects:

- add-patch takes a fenced reply whose diff adds or keeps a line of
  three backticks in a Markdown file, and the patch applies
- add-patch takes the same diff with no fence
- replies that worked before work the same

Depends: none
Change: fix
Audience: users
