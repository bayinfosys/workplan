# Delete the local definition branch in merge-workplan

Once the squash commit is made, merge-workplan deletes the local
branch `workplan/<id>/definition` with `git branch -D`. Pushing
master and deleting the remote branch stay with the maintainer.

Effects:

- after `wp merge-workplan`, `git branch --list 'workplan/<id>/*'`
  lists nothing
- the result's next steps are `git push origin master` and
  `git push origin --delete workplan/<id>/definition`
- a merge that fails leaves the branch in place, as now
- SPEC.md section 9's by-hand block deletes the local branch in a
  line of its own after the commit, and README.md's walkthrough says
  merge-workplan deletes it

Depends: none
Change: feat
Audience: users
