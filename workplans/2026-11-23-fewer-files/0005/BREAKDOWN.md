# Breakdown

1. plans.py: add the template lookup and rendering, with `text`
   renamed `template_text`, and the state functions and `STATES`; the
   module docstring describes all three parts.
2. ops.py, agent.py, route.py: import from plans.
3. Delete src/workplan/templates.py and src/workplan/state.py.
4. TODO.md: remove "refactor the code to reduce number of files".
