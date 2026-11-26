# Breakdown

1. In src/workplan/git.py, let `run` take text for standard input, if
   it does not already.
2. In src/workplan/plans.py, add `trailers` and `trailer`, calling
   `git interpret-trailers --parse`.
3. Change `depends_of` to read the Depends trailer first, and DEPENDS,
   the sentence, when there is none.
4. In tests, a test module of its own for the trailers: a block of
   several keys, no block, a Depends trailer, the old sentence, and
   `Depends: none`.
