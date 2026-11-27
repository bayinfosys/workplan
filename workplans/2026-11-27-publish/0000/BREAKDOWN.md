# Breakdown

1. src/workplan/config.py: `remote`; the config.toml templates.
2. src/workplan/ops.py: `publish(arg, parent, remote)`; merge's next
   step.
3. src/workplan/commands.py: `cmd_publish_workplan`, protocol, as
   merge is declared.
4. dispatch.sh, PROTOCOL.md and README.md.
5. tests/test_clones.py: publish after a merge with a task branch on
   the remote; a push refused when the remote moved on, with the
   remote branches kept; the three refusals.
