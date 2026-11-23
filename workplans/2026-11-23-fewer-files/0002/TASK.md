# Route on the current branch, fold classify into decide, drop the route log

route.py loses `branch_containing` and the log written by `dispatch`;
the model's question moves into `decide`.

Effects:

- the rules read the current branch, so routing HEAD after a commit
  is unchanged
- `route --dispatch` runs route.dispatch with the action and targets,
  and writes nothing under .git/
- route.py holds `facts`, `candidates`, `decide` and `dispatch`
- README.md's Routing section describes `--dispatch` without the log

Depends on none.
