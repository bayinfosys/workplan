# Breakdown

1. In `in_worktree` in src/workplan/agent.py, after agent.setup, run
   `git add -A` and `git write-tree` in the worktree, and call
   `work(workdir, base)`; give the three work functions that argument.
2. In `capture`, take the base tree; stage everything but output.patch
   and COMMIT_MSG under workplans/; diff the index from the base tree;
   fail with "no change" when the diff is empty. Replace `EXCLUDE`
   with the two pathspecs.
3. Update the module docstring's steps and the gen-patch line.
4. In src/workplan/templates/prompts/gen-patch.md, replace the line on
   workplans/ with: change files under workplans/ only where TASK.md
   says so.
5. In README.md's Agents section and SPEC.md section 11, describe the
   base tree; in SPEC.md's by-hand block, stage and write the tree
   after the copy, and diff from it.
6. In tests/test_by_hand.py's test_gen_patch, follow the new by-hand
   block; in tests/test_manual.py, add a test: a reply whose diff adds
   a NOTES.md to another task, with an uncommitted edit to WORKPLAN.md
   in the maintainer's tree; output.patch holds NOTES.md and not
   WORKPLAN.md.
