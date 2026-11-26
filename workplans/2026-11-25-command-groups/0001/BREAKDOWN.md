# Breakdown

1. In src/workplan/route.py, rename the two actions in ACTIONS, in
   `candidates` and in the docstring.
2. In src/workplan/templates/prompts/route.md, rename them in the list
   of actions.
3. Rename the four prompt templates with git mv, and the names in
   `patch_prompt`, `task_prompt`, `prompt`, the adapters' action
   arguments and the docstring of src/workplan/agent.py; and the
   action names commands.py passes to `agent.prompt`.
4. In src/workplan/templates/project/dispatch.sh, the case labels and
   the commands; in templates/project/config.toml, the comment.
5. In tests/support.py, the scripted agent's cases; in tests, the route
   outputs and actions they assert, including the hook test's
   dispatched line.
