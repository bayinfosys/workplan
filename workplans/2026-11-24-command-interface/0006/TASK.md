# Manual mode: prompts and pasted replies

`gen-task --prompt` and `gen-patch --prompt` print the prompt the
`none` agent would send, with the files' contents, and change nothing.
`add-patch NNNN [FILE]` takes a reply in the `none` agent's form, from
the file or standard input, and writes output.patch and COMMIT_MSG.
`add-task --reply FILE` takes a gen-task reply and writes its new task
files, with their task lines.

Effects:

- a prompt pasted into any chat, and its reply pasted back, does the
  same as the `none` agent
- add-patch refuses a reply with no diff, or a diff that does not apply
  to the workplan branch's head, and says why
- add-task with a reply leaves existing tasks alone, as gen-task does
- the page's panel has Copy prompt and Paste reply beside Gen patch,
  and the header the same beside Gen task
- README.md describes manual mode with a chat

Depends on 0003, 0005.
