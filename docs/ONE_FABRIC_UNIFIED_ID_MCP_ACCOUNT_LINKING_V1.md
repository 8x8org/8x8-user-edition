# ©8x8 One Fabric — Unified 8x8 ID + ChatGPT MCP User Edition (prelaunch v1)

**Authority:** public User Edition; `fabric://8x8/core` is the logical fabric root, **not** a public administrative credential.  
**State:** SOURCE_IMPLEMENTED / OFFLINE_POLICY_TESTED / **PUBLIC AUTH NOT DEPLOYED**.  
**Target surfaces:** ChatGPT MCP Apps, browser/PWA, Android APK, Telegram Mini App, future iOS, authorized voice clients.

## One identity, separate authentications

1. User starts with an account at the trusted 8x8 authorization server (existing Supabase Auth identity may be reused after verifying account ownership), receiving a canonical `8x8_<server-generated-random>` identifier from the protected identity backend. No browser-generated or user-supplied ID is authoritative.
2. The 8x8 MCP resource exposes HTTPS OAuth protected-resource metadata; 8x8 authorization server exposes OAuth/OIDC metadata and supports authorization-code + S256 PKCE, issuer-mix-up protection (RFC 9207 `iss`), resource indicator (RFC 8707), and CIMD-compatible ChatGPT client registration. Bind each token's `iss`, `aud`/`resource`, `exp`, `scope` and internal tenant membership to the requested MCP action; authenticate all user-owned operations server-side. **Never validate a JWT by decoding without signature verification.** A trusted library/IdP must create the internal Principal after complete validation.
3. Optional **Sign in with ChatGPT** is a different flow for identity linking; only integrate once OpenAI approval, OIDC configuration, identity/permission separation and consent are established. It does **not** import ChatGPT history/memory, install plugins, transfer API keys or make ChatGPT subscription limits available to 8x8 automatically. A separate approved grant is required for delegated model usage where supported.
4. Do not bind external ChatGPT accounts by editable email/name alone. Verify `sub` from the correct issuer and persist a tenant-owned provider-link record; permit link/revoke/export and challenge identity changes. Store tokens encrypted in server-side secrets storage only.
5. Other surfaces use their own verified authenticators: Telegram Mini App signed initData checked server-side with age limit; Android PWA/APK via system browser PKCE/deep link with state/nonce; device and its on-device runtime require local consent + revocable device lease. **Never treat Telegram username, phone IMEI, MCP session ID or a URL parameter as proof of account ownership.**

## Multi-tenant protection

`user auth subject → 8x8 ID → tenant membership → workspace → own agent instances and memories → explicit connector grants → action receipt`.

Default Seraphim, FlashTM8 Assistant, Aegis, Jarvis, Hermes and Anvil are **public-safe archetype templates**, NOT replicas of owner-private agent memory, internal prompts, model credentials or founder vault. Users can create custom agent instances within their own tenant. Each instance's memory belongs to that user and must be exportable, deletable, revocable and encrypted. Shared template updates are versioned, signed and audited; no user data is folded back into shared souls/template content without separate permission.

Every tool invocation and storage query MUST enforce tenant ownership via authenticated server policy plus database RLS (defense in depth). A user subscription does not upgrade tenant privileges. Collaborative cross-tenant resources require explicit named ACLs; default DENY. OWNER_ROOT is a separate service and remains unavailable in User Edition.

## One MCP with domain routing

All modules are discoverable through one authenticated MCP endpoint; listing an action is not execution authority. Domains include agents, models, memory, world, studio, publishing, finance, trading, wallets, blockchain, games, radio, books, research, planet, security, devices, community, settings. Each action has an independent OAuth scope and capability gate. Connections to other ChatGPT plugins must be suggested and opened through the user's **own** ChatGPT plugin management and provider consent; One Fabric cannot silently install/connect other apps or borrow their tokens.

**MCP transport**: HTTPS Streamable HTTP + OAuth metadata, stable CIMD or configured alternative. **MCP Apps** can display an in-chat world/agent console; native system overlays, microphone access and background activities are not implied by an MCP connection. A public static preview has no privileged tool execution.

**Provider grant lifecycle:** `DISCOVERED → USER_SELECTED → CONSENT_GRANTED → TOKEN_VERIFIED → HEALTHY → CAPABILITY_BOUND → ACTION_RECEIPTED → REVOKABLE`. No automatic financial or sensitive device grants. STOP/owner foreground preemption and five existing scheduler lanes remain enforced by device runtimes.

## Usage and payments (product targets, not current promises)

- Proposed free account: **88 promotional metered minutes (5,280 seconds)**, initial grant. Whether this is once per account or renewed per period requires explicit product policy before commercialization. Never fabricate credits on the basis of OAuth login.
- Proposed Premium: **USD 8.88/month**. Unlock only on verified server-side subscription webhook and current entitlement state, not a frontend button or client claim. Provider quotas, abuse limits and permitted model costs still apply.
- Charge metered minutes only for verified delivered inference/creation work, with idempotent `request_id` and an atomic ledger transaction. Reject duplicates, uncertainty and cross-tenant reuse; require refund/reconciliation for failed provider calls. Pure policy helper in `protected-beta/one_fabric_user_gateway_policy.py` is NOT a transactional ledger.
- Financial research, paper trading and order preview are separate from brokerage API permissions and live order placement. Live trades require explicit user exchange connection, account-specific risk limits, confirmation, kill switch, compliance and signed receipts. Publishing needs per-destination OAuth, content-rights clearance and explicit approval. Premium payment alone authorizes neither.

## Integration gates before production

| Gate | Current state |
|---|---|
| Existing protected identity core source | Present: `supabase/migrations/0001_identity_core.sql`; production state not assumed |
| Pure fail-closed tenant/capability/usage policy | Implemented, 35/35 local tests |
| OAuth 2.1 provider, JWKS, PKCE/CIMD, `iss`, audience validation deployed | NOT VERIFIED |
| User identity mapping and RLS staging negative tests | NOT VERIFIED |
| ChatGPT account linkage approval and OIDC integration | NOT VERIFIED |
| Web, Android, Telegram user sign-in acceptance | NOT VERIFIED |
| Cloud metering and Stripe webhook reconciliation | NOT VERIFIED |
| 88-minute grant active | NO |
| $8.88 subscription active for User Edition | NOT VERIFIED |
| Public MCP hostname deployed + certified in ChatGPT | NOT VERIFIED |
| AI agents/Studio/trades/publishing accessible end-to-end | NOT VERIFIED |

Do not apply the historical identity migration unreviewed: its public-schema privileged functions and grants require a dedicated security audit. Run Supabase advisors, RLS tests, consent/revocation tests, then bounded canaries before promoting beta. Never expose owner private sources in this repository.

## Sources

- OpenAI Plugin Authentication: https://developers.openai.com/plugins/build/auth
- Sign in with ChatGPT: https://developers.openai.com/siwc/quickstart
- MCP Security Considerations: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- Telegram Mini App initData verification: https://core.telegram.org/bots/webapps
- This repository: `docs/IDENTITY_BACKEND_0.0.1.md`, `SECURITY.md`, `PUBLIC_INFORMATION_BOUNDARY.md`.
