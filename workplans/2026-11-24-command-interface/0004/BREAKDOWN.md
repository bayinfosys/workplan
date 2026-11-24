# Breakdown

1. route.py: `ACTIONS` and `candidates` use the new names.
2. templates/prompts/route.md: the action list.
3. agent.py: the action names passed to adapters and the
   `WORKPLAN_ACTION` values; templates/prompts/ renamed to gen-task
   and gen-patch; agent.py names them.
4. tests: the routing tests, the classifier tests, and the scripted
   agent's `WORKPLAN_ACTION` cases.
5. SPEC.md sections 4 and 10, README.md Agents and Routing.
