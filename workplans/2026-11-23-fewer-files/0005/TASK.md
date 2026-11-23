# Move templates.py and state.py into plans.py

plans.py holds workplans on disk: ids, documents, templates and task
states. templates.py and state.py are deleted, and their importers use
plans.

Effects:

- `plans.render`, `plans.template_text`, `plans.state`,
  `plans.master_ref`, `plans.commit_for` and `plans.patch_applied`
  replace the functions of the two modules
- src/workplan/ holds ten modules
- TODO.md no longer lists the refactoring

Depends on 0001, 0002, 0004.
