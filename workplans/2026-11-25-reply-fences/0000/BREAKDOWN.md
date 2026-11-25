# Breakdown

1. In src/workplan/agent.py, anchor both ends of `FENCE` at the start
   of a line, with `re.M`.
2. In tests/test_manual.py, add a test: a repository with a README.md
   holding a fenced block, and a reply whose diff adds a line inside
   it and keeps the fence lines as context, fenced and unfenced; both
   give an output.patch that applies.
