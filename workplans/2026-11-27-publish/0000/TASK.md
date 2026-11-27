# wp publish

`publish` pushes the parent branch, then deletes the workplan's
branches on the remote, as WORKPLAN.md's decisions say, with the
`remote` key, dispatch.sh's commented case, and the documents.

Effects:

- after `wp merge`, `wp publish` pushes the parent branch to the
  remote and deletes `workplan/<id>/definition` and any
  `workplan/<id>/task/*` there; it prints what it pushed and deleted
- when the push fails, as when the remote's parent branch has moved
  on, it fails with git's message and deletes nothing
- it refuses with another branch checked out, for a workplan not
  merged into the parent branch, and while the local definition
  branch exists
- config.toml takes `remote = "origin"`; WORKPLAN_REMOTE overrides it
- merge's next steps read `workplan publish`
- dispatch.sh: `# complete) workplan publish "$@" ;;`, commented
- PROTOCOL.md: a `## wp publish` section, saying it is the only command
  that pushes to a pre-existing remote branch, and that it may fail;
  `remote` in the preamble; section 5's last step and Working
  together name it
- README.md: the command's row, the walkthrough's last steps, the
  `remote` key, and the sentence on pushing

Depends: none
Change: feat
Audience: users
