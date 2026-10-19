# ©8x8 One Fabric — Alpaca Connect paper/read-only live preflight

**Date:** 2026-10-18 (America/New_York)
**Canonical root:** `fabric://8x8/core`
**Classification:** `BLOCKED_NOT_AUTHORIZED`
**Scope:** existing 8x8 User Edition / native first-party Alpaca paper read-only onboarding. No live account authorization, trades, posts, or device-control changes.

## Fresh connected-source observations

| Gate | Evidence | Verdict |
|---|---|---|
| Supabase project | Existing `8x8-one-fabric` project `kjvmagncyednwfezbjww`: `ACTIVE_HEALTHY` | Project alive, no user authorization implied |
| Gate 2 | `auth.users=0`, `public.one_fabric_user_ids=0`; `one-fabric-id` Edge Function v1 active, `verify_jwt=true`; deployed function has no Alpaca OAuth callback / one-use state flow | BLOCKED |
| Alpaca metadata | Existing `public.fabric_sources` row `connection_intent:trading:alpaca` reads `NOT_AUTHENTICATED` / `NOT_CONNECTED_NATIVE` and `NO_RAW_SECRETS` | Metadata only |
| Alpaca developer app | Existing `protected-beta/alpaca-connect-submission/ACCEPTANCE_EVIDENCE_20261018.md` records NOT SUBMITTED. No more-recent direct developer-console approval was available; targeted email search found no Alpaca Connect/OAuth app-approval evidence. Absence of an email is not proof of no developer app. | Not independently verified |
| Exact redirect URI | Existing `APPLICATION_DRAFT.md` says DO NOT GUESS; no registered stable HTTPS Alpaca callback proved; Vercel deployment project exists, but account-route verification failed with 403 protected deployment | BLOCKED |
| One-use state | `protected-beta/one_fabric_oauth_launch_gate_v3.py` requires `one_time_state_server_persistent` as a server-verified prerequisite, but this pure policy helper does not create, persist, expire, or consume state | No live replay/CSRF acceptance |
| Vault | `vault.secrets=0`; neither managed encrypted tenant storage, narrow decrypt access, nor provider credential callback was independently verified | BLOCKED |
| Remote World MCP | Fresh GET `/health`: HTTP 200, `configured=false`; GET `/.well-known/oauth-protected-resource`: HTTP 503 `AUTH_CONFIGURATION_REQUIRED` | NO LIVE 8X8 MCP OAUTH |
| Supabase security advisor | `lints=[]` at time of check; not a comprehensive authorization or security acceptance | Not an approval |
| Samsung safeguards | A5-B `OWNER_PAUSE` and Hermes voice `STOP` present, file modes `600`; not removed | Preserved |

## Official Alpaca specifications and exact clickable user-owned steps

1. Open [Alpaca Trading Dashboard](https://app.alpaca.markets/) in the owner's own browser and sign in privately. Under **Alpaca Connect → My Developed Apps**, inspect whether a registered **8x8 One Fabric** application exists. [Official app registration steps](https://docs.alpaca.markets/us/docs/registering-your-app). Do **not** represent the existing proposal as submitted or approved.
2. Review [existing 8x8 application draft](../../../protected-beta/alpaca-connect-submission/APPLICATION_DRAFT.md) before submission. Publicly reachable real application homepage, correct rights-owned logo, Privacy Policy, Terms, accurate paper/read-only customer disclosure, exact running callback, and Alpaca's own approval/review remain outstanding. Do not submit placeholder values or secrets.
3. For eventual authorization, the **8x8 authenticated backend**, not chat, must derive the **Alpaca-registered** `client_id` and **exact allowlisted HTTPS** `redirect_uri`, and generate/store a random one-use `state` bound to the verified current tenant/session. Start **only** `env=paper`, omit `trading`, `account:write`, and optional `data` scopes (read-only is Alpaca's default), and verify callback state before a server-only code exchange. [Official OAuth requirements](https://docs.alpaca.markets/us/docs/using-oauth2-and-trading-api).
4. Enforce fail-closed outcomes for state missing/expired/replayed, wrong redirect/issuer/client, unverified 8x8 user or tenant, Vault/custody failure, STOP presence, live-account selection or unauthorized scope. After a legitimate provider grant, make one paper **read-only** account canary with a redacted attributable receipt. Never infer trading authority from a successful read.
5. **No executable Alpaca OAuth consent URL can be issued now:** a verified registered client, callback and one-use state are absent. Never invent a Connect URL or request password, client ID/secret, API key, callback code, access token, or one-use state in chat. User-held developer-console secrets must remain private.

## Actions deliberately NOT performed

- No OAuth authorize redirect, authorization-code exchange, developer app submission, client secret access, credential intake, order placement, public post or funds movement.
- No Supabase SQL writes, Vault changes, OAuth settings edits, Vercel deploy, plugin release publication, phone foreground action, STOP reset, or sixth scheduler.
- Source preflight is policy-only and cannot attest a provider account session or token.

**Next deployment gate:** independently establish a real Gate 2 sign-in with tenant isolation and approved public OAuth configuration, verify Alpaca's actual application registration and canonical allowed redirect, deploy atomic one-use callback state and tenant Vault with rollback, then test negative/positive canaries before revealing any per-session authorization link.
