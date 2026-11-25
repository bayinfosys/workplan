# A patch is the diff from the worktree as the agent receives it

`in_worktree` stages the worktree after copying workplans/ and running
agent.setup, and passes the tree from `git write-tree` to the work it
runs; `capture` diffs the whole repository from that tree, leaving out
output.patch and COMMIT_MSG.

Effects:

- gen-patch and add-patch keep a change to a file under workplans/ in
  output.patch, and accept-patch commits it
- uncommitted documents in the maintainer's tree, copied into the
  worktree, are not part of the patch
- files agent.setup creates are not part of the patch
- a reply or agent run that changes nothing fails with "no change"
- the gen-patch prompt, the module docstring, README.md's Agents
  section and SPEC.md section 11, with its by-hand block, describe the
  base tree

Depends on none.
