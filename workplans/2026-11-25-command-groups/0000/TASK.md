# The CLI takes the new names

The registry builds the CLI as `wp <noun> <verb>` for tasks and
patches, and as top-level verbs for the workplan and for commands with
no noun. Every command is renamed as below, and messages name commands
by their new names.

| Before | After |
|---|---|
| `wp init` | `wp init` |
| `wp list-workplan` | `wp list` |
| `wp show-workplan [ID]` | `wp show [ID]` |
| `wp add-workplan NAME` | `wp new NAME` |
| `wp edit-workplan [ID]` | `wp edit [ID]` |
| `wp merge-workplan [ID]` | `wp merge [ID]` |
| `wp list-task [ID]` | `wp task list [ID]` |
| `wp status` | `wp status`, the alias of `wp task list` |
| `wp show-task TASK` | `wp task show TASK` |
| `wp add-task TITLE` | `wp task add TITLE` |
| `wp gen-task [ID]` | `wp task gen [ID]` |
| `wp edit-task TASK` | `wp task edit TASK` |
| `wp drop-task TASK` | `wp task drop TASK` |
| `wp show-patch TASK` | `wp patch show TASK` |
| `wp add-patch TASK [FILE]` | `wp patch add TASK [FILE]` |
| `wp gen-patch TASK` | `wp patch gen TASK` |
| `wp apply-patch TASK` | `wp patch apply TASK` |
| `wp accept-patch TASK` | `wp patch accept TASK` |
| `wp drop-patch TASK` | `wp patch drop TASK` |
| `wp reject-patch TASK` | `wp patch reject TASK` |
| `wp route [REV]` | `wp route [REV]` |
| `wp install` | `wp install` |
| `wp serve` | `wp serve` |

Effects:

- each command in the After column does what the command in the
  Before column did, with the same parameters, `--json` and HTTP route
- the names in the Before column that change are errors
- `wp task` or `wp patch` with no verb prints its verbs and fails, and
  `wp task --help` lists the task verbs
- a command's name, in its errors and in `Command.name`, is its After
  form without `wp`: `task add`, `merge`
- the messages in ops.py, agent.py and commands.py that name a command
  use the After form
- `wp patch show` goes through the pager, as show-patch did

Depends on none.
