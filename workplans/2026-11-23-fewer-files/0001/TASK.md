# Remove layout problems from status

`status` reports each task's state and detail only; `problems` leaves
state.py, the `problems` field leaves `status --json`, and the `!`
lines leave the text output.

Effects:

- state.py holds `master_ref`, `commit_for`, `patch_applied` and
  `state`
- `status --json` gives id, state, detail, title and depends per task
- README.md describes `status` without layout problems

Depends on none.
