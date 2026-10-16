# ©8x8 One Fabric User Edition — Bitget connection and Vault gate (2026-10-16)

Status: **PRELAUNCH / NO LIVE ACCOUNT AUTHORIZATION**. This is a public-safe guidance contract, not a running Vault, broker or account link.

## Current independently observed boundaries

- ChatGPT personal plugin `8x8-one-fabric-world` v0.4.1 contains the branded 19-domain, read-only interface, bundled 8x8 logo and guidance. Plugin release readback preserved the original MCP source and UI; a plugin archive does not prove its remote endpoint is available.
- Supabase project `8x8-one-fabric` was reported ACTIVE_HEALTHY, with nine metadata-oriented public tables all RLS-enabled and reporting zero rows. This is **not** proof of a deployed tenant-secret Vault, a verified OAuth 8x8 ID, or a Bitget account.
- Vercel `8x8-user-edition` has a READY production deployment record, which does **not** prove the presence of tested Vault credential enrollment or a wallet signer.
- A Samsung owner-local `~/.8x8/vault` directory existed in a read-only existence probe; its contents were not examined. Directory presence does **not** prove a deployed audited secret broker. A local FlashTM8 Assistant `/health` response is not Vault health.
- A public proposed MCP endpoint in the plugin configuration could not be verified by an unauthenticated external health retrieval in this review. Therefore account-linking eligibility remains `NOT_VERIFIED`.

## Official Bitget API constraints

Official documentation: https://www.bitget.com/docs/uta/quick-start
Official terms: https://www.bitget.com/support/articles/12560603797947

Bitget API credentials consist of `APIKey`, `SecretKey`, and a separately set `Passphrase`. Read-only permissions are distinct from read-write/trading and account-management permissions. Bitget strongly recommends IP whitelisting and, in its API Key Terms of Use, tells users **not to store API keys in the cloud**. The policies may change; recheck before deploying.

**Do not request or ingest Bitget API credentials in ChatGPT text, speech, model-visible MCP calls, source code, CI, logs, repositories, or the proposed 8x8 cloud Vault.** A user-owned, audited local credential broker with a stable approved outbound IP and provider-compliant storage is the proposed first implementation; it is not presently accepted or production deployed. Counsel/provider review is required before alternative custody models.

## Verified safe steps users can do now

1. Open Bitget's official documentation and inspect the relevant account's API management and permission options while signed in **only on Bitget**. Do not share screenshots containing secrets.
2. Decide which **single** user-owned account should be evaluated first; up to five account slots in 8x8 are proposals, not linked accounts. No assumption that all five are Bitget.
3. Read the read-only vs read-write, transfer and withdrawal scope definitions. Plan separate single-purpose **read-only** credentials with IP whitelisting, not live order permissions.
4. **Do not create or hand credentials to 8x8 yet.** A real approved user-controlled local broker needs security, encryption, zero-secret egress, revocation, outbound-IP and signing canaries, current device consent and STOP acceptance.
5. Once separately accepted, run a read-only provider account identity canary, issue a tenant-bound opaque capability handle, demonstrate explicit revocation, and publish a non-sensitive receipt. Only then consider risk-controlled test trading with separate approval.

## All providers and user isolation

Social providers with supported OAuth use individual user grants. Telegram bot tokens and other provider credentials require service-specific secure enrollment approval and cannot be requested in ChatGPT. Private founder-controlled agent resources, native device control, NFT signing and wallet seeds must never be exposed to public users. Every user maintains tenant-scoped identity, memory, tools, agent configurations and consent.

88 daily free minutes and $8.88/month are **proposed** User Edition entitlements, not deployed guaranteed quotas or external API exemptions. Self-improvement on user data requires informed, separate and revocable consent; never train shared models on customer secrets by default.

The ChatGPT plugin source release v0.4.1 adds a non-executing provider-custody preflight, with 16/16 offline tests passed and no authenticated account linkage or secret collection.
