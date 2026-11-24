# Breakdown

1. agent.py: `prompt(action, target, cfg)` renders the none agent's
   prompt from this tree, with no worktree.
2. agent.py: `add_patch(task, reply)` parses with `parse_patch`,
   checks the diff in a worktree of the branch head, and writes the two
   files; `add_tasks(wid, reply)` parses with `parse_files` and writes
   the new tasks as gen-task does.
3. commands.py: `--prompt` on gen-task and gen-patch; `cmd_add_patch`;
   `--reply` on add-task.
4. web: api.js functions; Copy prompt writes to the clipboard; Paste
   reply opens a text box and sends it.
5. tests: a prompt holds the task files; a good reply, a reply without
   a diff, a diff that does not apply; tasks from a reply.
6. README.md: manual mode.
