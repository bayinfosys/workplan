# Breakdown

1. route.py: `facts` takes the branch from `git.branch()`; delete
   `branch_containing`.
2. route.py: move the body of `classify` into `decide`, keeping its
   fallback to the rules and its stderr messages.
3. route.py: `dispatch` runs the command only; drop the log, the
   `datetime` import, and its return value; cli.py ignores it already.
4. tests/test_fixes.py: `test_dispatch_records` checks the dispatched
   command's arguments only, renamed `test_dispatch`.
5. README.md, Routing: the `--dispatch` paragraph without the log.
