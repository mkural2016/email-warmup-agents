# Customer workflows

Discover exact `warmup_` tool names and schemas from the connected MCP server. The live service's fields and allowed actions take precedence over these examples.

| Journey | Tools to discover | Permissions |
| --- | --- | --- |
| Workspace | `workspace_summary`, `list_domains`, `get_domain` | read |
| Domain setup | `create_domain`, `start_domain_verification`, `verify_domain`, `scan_domain`, `get_dns_scan`, `domain_health` | read/write |
| Domain maintenance | `update_domain`, `delete_domain` | read/write; delete for removal |
| Mailbox setup | `list_mailboxes`, `get_mailbox`, `connect_mailbox` | read; browser consent for connection |
| Mailbox readiness | `send_mailbox_verification`, `verify_mailbox`, `check_mailbox_readiness`, `mailbox_readiness_history`, `disconnect_mailbox` | read/write for effects; delete for disconnect |
| Campaign planning | `generate_schedule`, `preview_template`, `list_campaigns`, `get_campaign` | read; write for preview |
| Campaign changes | `create_campaign`, `update_campaign`, `pause_campaign`, `resume_campaign`, `delete_campaign` | read/write; send for create/resume; delete for removal |
| Observations | `campaign_results`, `warmup_activity`, `message_timeline` | read |
| Account usage | `credit_balance`, `credit_history`, `subscription_status` | read |

## Domains and mailboxes

List existing resources before creating anything. Register the intended domain only when requested. Return the exact ownership challenge and expiry. Ask the customer to publish the proof or read the delivered code; never synthesize it. Recheck ownership and DNS health separately.

Use the signed-in console continuation for mailbox credentials or provider consent. Once the customer finishes, read the actual mailbox and check readiness. Complete email verification using the real received code. Surface SMTP/IMAP, permissions, ownership or DNS blockers with their returned recovery actions.

## Campaigns

Read the mailbox, domain and current campaign first. Generate a bounded schedule from the customer's dates, timezone and volume. A template preview may incur product usage: establish intent before running it. Creation and resume require send permission and all readiness checks; a granted permission does not override a blocked state.

After an operation, inspect its result and a narrow follow-up read. For an uncertain result, retain the original idempotency UUID and inspect current state. A completed rejection remains stable on replay: after the customer fixes prerequisites, a new intended attempt uses a new UUID.

## Example requests

- “List my domains and explain missing ownership or DNS checks. Do not change anything.”
- “Help connect this mailbox, wait for my provider consent, then check readiness.”
- “Prepare a seven-day schedule capped at ten emails per day. Show it before creating anything.”
- “Pause this campaign, then show its current status.”
- “Show my balance and the last ten credit-history entries.”
