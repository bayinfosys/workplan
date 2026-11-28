# Breakdown

1. Replace the preamble with the init template's.
2. Rewrite each kept item in the item format and the current names.
3. Merge Real agents and Internal agent into self-hosted-loop.
4. Add examples, animation, current-workplan and program-name.
5. grep -nE 'SPEC|gen-task|gen-patch|list-workplan|demo\.tape'
   workplans/BACKLOG.md prints nothing; each item with a trailer
   block parses with `git interpret-trailers --parse`.
