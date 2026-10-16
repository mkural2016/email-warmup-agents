# Connection and access

For installation, follow the public [agent handoff](https://github.com/mkural2016/email-warmup-agents/blob/v0.1.0/INSTALL.md). It installs both the MCP connection and this complete skill. Use the exact MCP endpoint supplied by the customer from **Integrations**.

## Browser authorization

For Codex, request only read access during setup:

```sh
codex mcp login email-warmup --scopes warmup:read
```

For Claude Code, authenticate the `email-warmup` connection through `/mcp`. The customer signs in and chooses permissions in their browser. Do not ask for credentials or consent codes in chat. If a new connection is unavailable in the current session, reconnect or restart the client before attempting a tool call.

Start with a read-only workspace summary or domain list. Configuration installed, browser authorized, and authenticated read verified are separate states.

## Permissions and recovery

| Scope | Access |
| --- | --- |
| `warmup:read` | Owned resources, readiness, observations, balances and browser continuations |
| `warmup:write` | Domain changes/proof, scans, verification checks, template previews and campaign changes |
| `warmup:send` | Create or resume a campaign, together with read/write |
| `warmup:delete` | Delete a domain/campaign or disconnect mailbox credentials, together with read/write |

Ask for additional permissions only when needed for the customer's requested action. For Codex campaign changes, a customer can authorize `codex mcp login email-warmup --scopes warmup:read,warmup:write,warmup:send`. If offered, **Keep access between sessions** is a separate choice on the consent screen.

For a custom workflow, a customer may create a scoped, expiring API key in Integrations. Keep it in the client's supported credential mechanism; never include it in prompts, repository files, URLs, or shell history. Do not create one as a shortcut around OAuth installation.

- **401:** reconnect or replace an expired/revoked credential through the supported client flow.
- **403 insufficient_scope:** request the permissions required for the intended operation.
- **429:** wait for the returned retry interval.
- **Readiness rejection:** complete the returned recovery actions.
- **Uncertain effect:** reconcile current resources before retrying with the same idempotency key.

Integrations shows creation, expiry, revocation and last successful credential check. **Active** means access is granted; it does not establish that the agent is currently online. Revocation denies subsequent requests but does not undo accepted operations.
