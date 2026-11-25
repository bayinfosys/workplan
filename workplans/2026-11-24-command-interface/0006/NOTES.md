# Notes 2026-11-24-command-interface/0006: Manual mode: prompts and pasted replies

Did the patch change anything TASK.md does not state?

Yes, in three places.

How does a reply reach add-patch and add-task?

On the command line, as a file or standard input. Over HTTP, as text
in the request body: the server reads no files, so a path is not
accepted there.

Is output.patch the reply's diff?

No. add-patch applies the reply's diff in a worktree of the branch
head and keeps the diff git produces there, as gen-patch does, so
output.patch has git's form whatever the form of the reply.

Do add-patch and gen-patch share code?

Yes. Both run in the worktree from `in_worktree` and keep their result
with `capture` and `keep_patch`; add-task and gen-task share
`keep_tasks` in the same way. TASK.md states the commands, and not
the code they share.
