# TASK.md ends with a trailer block

The TASK.md template, `task add` and the task-gen prompts write the
trailer block of WORKPLAN.md's decision 1 in place of the "Depends on"
sentence, and SPEC.md describes it.

Effects:

- the template ends with a paragraph of trailers:
  `Depends: $depends`, then `Change: <feat | fix | docs | refactor |
  test | chore>`, `Audience: <users | developers | internal>` and
  `Breaking: <what breaks, or remove this line>`
- `wp task add TITLE --depend 0000` writes `Depends: 0000`; with no
  `--depend`, `Depends: none`
- task-gen.md and task-gen-none.md ask for the block, with the keys
  and their values, and the line left out when nothing breaks
- SPEC.md section 3 describes the block, its keys and that values are
  hints, with `git interpret-trailers --parse` to read it by hand; its
  example ends with the block; section 4 lists the template's values
  as now; the states table names the Depends trailer
- README.md, where it shows a task, shows the block

Depends: 0000
Change: feat
Audience: users
