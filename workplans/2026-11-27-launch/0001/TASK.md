# With no agent, the failure says how to go on

When `task gen` or `patch gen` has no agent to run, the failure names
the three ways on.

Effects:

- with `agent.name = "none"` and no `llm.api_base`, `wp task gen` and
  `wp patch gen 0000` fail with:
  "no agent configured: set agent.name to claude-code or codex, or
  llm.api_base for the none agent, in workplans/config.toml; or run
  with --prompt, paste the prompt into a chat, and give its reply to
  task add --reply or patch add"
- the message is the same over HTTP

Depends: none
Change: fix
Audience: users
