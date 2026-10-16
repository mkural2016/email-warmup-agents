---
name: email-warmup
description: Manage a customer's Email Warmup domains, mailbox readiness, campaign schedules and results through the authenticated Email Warmup MCP tools.
---

Use the customer's configured `email-warmup` MCP connection. Read [setup.md](references/setup.md) for connection or access errors; read [workflows.md](references/workflows.md) for domain, mailbox and campaign journeys.

Discover the available tools and read the current workspace/readiness state. Use actual returned IDs and advertised schemas. A domain registration, DNS scan, browser callback or mailbox connection does not by itself prove readiness to send.

Ask for missing intent before issuing a mutation that sends a verification email, creates paid content, starts/resumes sending, disconnects or deletes a resource. Use the customer's requested scope; do not treat connection authorization as permission for unrelated actions.

Effectful tools require `confirm: true` and a fresh UUID `idempotency_key` for each intended operation. Keep the same key and identical arguments after a transport timeout. Reconcile `outcome_unknown` by reading the affected resources; never bypass its fence with a new key. After a definitive rejection and a verified prerequisite fix, use a new key for the new intended attempt.

Follow safe browser continuations for provider consent or credential entry. Never ask the customer to paste provider passwords, OAuth secrets or MCP keys into chat. Query actual readiness after the customer returns. Respect blocking reasons, allowed actions, expiry, quotas and credit authority returned by the service.

Use bounded pages and narrow reads. Report missing, stale or unavailable observations honestly. Pausing or deleting a campaign does not recall messages already accepted for delivery. Operator seed accounts, global controls and unrelated customer data are outside this connection.
