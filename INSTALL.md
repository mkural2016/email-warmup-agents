# Agent installation handoff

The user has asked you to install Email Warmup. Complete installation rather than returning instructions for the user to run. Use the agent named in the user's prompt, or your own current client if none was named. Supported clients are **Codex CLI** and **Claude Code**.

## Install the MCP connection and skill

1. Use the exact MCP endpoint supplied by the user or their Integrations prompt. If it is missing, ask for that address; do not invent an endpoint. Do not request a password, API key, OAuth token, or authorization code in chat.
2. Check that the selected client CLI and Python 3.9+ are available. Do not install or upgrade the agent CLI or system packages without the user's authorization. If this environment cannot modify the client's local configuration, explain that limitation.
3. Clone this public package into a temporary directory at the release used by this handoff:

   ```sh
   git clone --depth 1 --branch v0.1.0 https://github.com/mkural2016/email-warmup-agents.git
   ```

4. Read `install.py`, then run it from the cloned package. Pass the endpoint as one properly quoted argument; never interpolate it into shell code. Replace the agent and endpoint below with the actual values:

   ```sh
   python3 install.py --agent codex --endpoint 'YOUR_MCP_ENDPOINT'
   ```

   For Claude Code, use `--agent claude`. Run this in the customer's real client environment, without replacing `HOME`, `CODEX_HOME`, or `CLAUDE_CONFIG_DIR`. Respect existing custom configuration directories. The installer uses the native CLI for MCP configuration and copies the complete skill folder to `~/.agents/skills/email-warmup` for Codex or `${CLAUDE_CONFIG_DIR:-~/.claude}/skills/email-warmup` for Claude Code. These are personal installations, available across projects.

   The installer preserves existing configuration. An identical installation is reused. If an existing connection points elsewhere, is disabled, or the skill contains different files, stop and explain the conflict instead of removing or replacing it. Never remove another MCP server or overwrite the user's broader configuration. A failed installation is not a successful connection.

## Authorize in the browser

For Codex, initiate the existing OAuth flow with read access:

```sh
codex mcp login email-warmup --scopes warmup:read
```

For Claude Code, use its `/mcp` interface to select `email-warmup` and authenticate. If you cannot invoke that host interface, ask the user to open `/mcp` and complete that single authentication action. Do not replace browser OAuth with an API key or attempt to read the client's credential store.

The user signs in to Email Warmup and approves permissions in their browser. Do not approve consent on their behalf or request write/send/delete permissions for installation. If the client already has a working connection, reuse it without changing its permissions.

## Verify and hand back

- Confirm `email-warmup` appears in the client's MCP configuration and that the installed skill and its references are present.
- Read the installed `SKILL.md`. If the current session cannot load the new MCP connection, state that the configuration and skill are installed and ask the user to restart or reconnect the client. Do not claim the connection is verified yet.
- Once the authenticated MCP connection is available, discover its tools and run a read-only workspace summary or domain list. Use the advertised schemas; do not create resources to test access.
- Report the installed client, endpoint, skill path, and the verification outcome. Distinguish configuration installed, browser authorization pending, and authenticated read verified.

Only after an authenticated read succeeds should you report that setup is complete. The installation request does not authorize verification emails, paid content, resource changes, or campaign sending.
