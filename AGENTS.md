# ©️8x8 — Public User Edition coding-agent instructions

This is the **public-safe** 8x8 User Edition. Read `ONE_FABRIC_ROLE.md`, `README.md`, `docs/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2.md` and `docs/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2.json`, then the actual versioned public status/implementation/release receipts. The V2 bootstrap is a draft source guide, not a new release.

- Single logical root: `fabric://8x8/core`. This repository is a bounded public client, not a second sovereign root or the owner's private control plane.
- Never expose, recreate, fetch or embed private owner repositories, personal messages, credentials, internal device topology, raw logs, wallet keys, biometric templates, or privileged actions in public code, tests, screenshots or documentation.
- Normal users have isolated 8x8-ID tenant data and separately consented/scoped capabilities. An agent/skill/UI preview is not a running authenticated tool.
- Claims must distinguish PAST_PRESERVED, PRESENT_PROVEN, FUTURE_GATED and UNKNOWN. Preserve the recorded 0.0.1 Beta state unless newer immutable release evidence proves an upgrade. Do not advertise billing, native apps, Studio publishing, trading, blockchain mainnet or unrestricted agent autonomy as live without actual acceptance.
- Reuse existing source and reviewed adapters. Preserve source provenance, licensing, security review, test fixtures, privacy and accessibility; do not copy private internal architecture across the public boundary.
- Required release gates: web/PWA, source/deployment provenance, signed Android, 8x8 ID/MCP, actual Studio/World use, owner-safe agents. CI success or HTTP 200 alone is insufficient.
- Test the bootstrap with `node --test tests/public-bootstrap-v2.test.mjs` on the exact head. Review browser/native UX, security denial, API scopes, real user workflows and rollback independently. Do not merge or deploy simply because this document is present.
