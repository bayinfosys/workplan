# Breakdown

1. Rewrite the walkthrough's commands in the new names, keeping its
   comments.
2. Regroup the command table under three subheadings, with the new
   names and the same descriptions.
3. Update the examples in manual mode, agents, routing, the board and
   configuration.
4. Check with `grep -nE '(list|show|add|edit|merge|gen|drop|apply|accept|reject)-(workplan|task|patch)|gen-(task|patch)' README.md`
   that nothing is left.
