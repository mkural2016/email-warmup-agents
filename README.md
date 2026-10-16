# Email Warmup for agents

Connect Codex or Claude Code to your Email Warmup account. One installation adds the MCP connection and the `email-warmup` skill, including domain, mailbox, and campaign workflows.

Paste an installation prompt into your agent with the MCP endpoint shown in **Integrations** in Email Warmup. The agent installs the package, connects the MCP server, and helps you complete browser authorization. No API key belongs in the prompt.

For a manual handoff, replace `YOUR_MCP_ENDPOINT` with the exact address shown in Integrations and paste:

```text
Install Email Warmup for my current agent from https://github.com/mkural2016/email-warmup-agents/blob/v0.1.0/INSTALL.md. My MCP endpoint is YOUR_MCP_ENDPOINT. Install both the MCP connection and the bundled email-warmup skill, preserve my existing configuration, guide me through browser authorization, and verify access with a read-only workspace query. Do not create or change workspace resources.
```

The package uses the installed agent CLI and Python 3.9 or later. It requires no package manager, API key, local MCP server, or access to Email Warmup source code. The MCP server runs remotely; the skill runs in your agent.

## What is included

- [`INSTALL.md`](INSTALL.md): the installation handoff for your agent.
- [`install.py`](install.py): configures the selected CLI and installs the skill without replacing existing customized files or a different MCP connection.
- [`skills/email-warmup`](skills/email-warmup): customer workflow instructions and references.

Browser authorization is a separate step from installing configuration. You choose permissions on Email Warmup's consent screen. The installer does not authenticate, send emails, start campaigns, or change your workspace.

Codex CLI and Claude Code running locally are supported. Hosted chat environments and organizational restrictions can require a different connection flow.

Client references: [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Claude Code skills](https://code.claude.com/docs/en/skills).
