# Read a task's trailer block with git

A task's facts are read from the trailer block at the end of TASK.md,
with `git interpret-trailers --parse`. Depends is read from its
trailer, and from the "Depends on" sentence when there is no trailer.

Effects:

- `plans.trailers(text)` returns the trailer block as a list of
  (key, value) pairs, in order, from `git interpret-trailers --parse`
  given the text on standard input; a TASK.md with no block gives none
- `plans.trailer(text, key)` returns the first value for a key, case
  ignored, or None
- `depends_of` reads `Depends: 0000, 0002` from the block; with no
  Depends trailer it reads the "Depends on" sentence, as now; `none`
  gives no dependencies
- states, `patch show` and the board read dependencies the same way
  from either form

Depends: none
Change: refactor
Audience: developers
