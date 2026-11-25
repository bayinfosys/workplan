# Breakdown

1. In `merge` in src/workplan/ops.py, after the commit succeeds, run
   `git branch -q -D <branch>`, and drop that command from `next`.
2. In SPEC.md section 9's by-hand block, put `git branch -D $b` on its
   own line after `git commit -e -F /tmp/msg`, and keep
   `git push origin --delete $b` after `git push origin master`.
3. In README.md's walkthrough, extend the comment on
   `workplan merge-workplan` to say the local branch is deleted.
4. In tests/test_fixes.py, check after a merge that the local
   definition branch is gone; in tests/test_by_hand.py's test_merge,
   add the `git branch -D` line to the by-hand script so the two
   repositories match.
