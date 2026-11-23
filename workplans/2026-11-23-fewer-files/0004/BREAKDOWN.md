# Breakdown

1. agent.py: add the adapters as functions `run_none` and
   `run_command`, with their helpers (`parse_patch`, `parse_files`,
   `use_patch`, `use_files`), the presets, and `ADAPTERS`; the module
   docstring describes the adapter interface from agents/__init__.py.
2. Delete src/workplan/agents/.
3. pyproject.toml: confirm package discovery needs no change.
