# Breakdown

1. commands.py: the registry and its context (the config and master,
   loaded once per call); a command for each name above, calling the
   function in ops.py or agent.py that the old subcommand called.
2. commands.py: text renderers that reproduce today's CLI output:
   the status table, the agent's report, the merge result.
3. ops.py: `edit_document(wid, name)` opens the editor on a document
   of the editable workplan, as `plan` does on its draft; `merge`
   gains nothing, `merge_message` serves `--show`.
4. cli.py: `main` runs the registry's CLI, with the Fail handling and
   SIGPIPE setting it has now.
5. tests: every `Repo.wp` call uses the new names; test_by_hand.py's
   commands too.
6. README.md: the flow, the commands table and Agents use the new
   names. SPEC.md names no commands; its action and template names
   change with 0004.
