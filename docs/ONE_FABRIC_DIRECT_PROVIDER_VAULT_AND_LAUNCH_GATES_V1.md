# ©8x8 One Fabric — Direct connection, Vault and launch contract (v1)

**Authority:** Public-safe User Edition, `fabric://8x8/core`.  **Status:** Source implementation, locally tested; not a deployed vault, payment service, user-authenticated MCP, exchange adapter, or content publisher.

## Owner and user experience

The user asks FlashTM8 Assistant to connect Bitget, Telegram, YouTube, a wallet or another provider. The MCP may display a verified provider guide, request an explicit 8x8-account authorization, and generate a **short-lived connection intent**. It must never request a password, API secret, passphrase, bot token or wallet seed in ChatGPT free-form chat or in model-visible MCP tool arguments.

After 8x8 OAuth 2.1 + PKCE and current tenant membership are verified, the user goes to an **independently authenticated, deployed HTTPS 8x8 Secure Vault origin**. No origin is hard-coded or invented in public source. The server validates the one-time intent and shows a protected, no-logging secure provider form *only if* that route has been independently deployed and tested. A server-side KMS or HSM encrypts sensitive material under tenant-specific key policy. The provider's authorized access is represented in the agent fabric by a revocable opaque **vault handle**. Agents must not receive recoverable raw credentials in prompts, tool outputs, analytics, tracing, memory, logs or public source.

Connection stage ladder: `DISCOVERED → USER_INTENT → SERVER_AUTHENTICATED → EXPLICIT_CONSENT → SECRET_STORED_OR_OAUTH_BOUND → PROVIDER_HEALTH_CANARY → CAPABILITY_GRANTED → LEASED → ACTIONED → RECEIPTED`. None of these states implies the following one. Private founder and user tenants remain isolated. User memory cannot be used to train a shared agent template without separate opt-in.

### Trading: minimum eight separately authorized accounts — target, not current count

The owner's expanded requirement supersedes the historical five-account target: support **at least eight separately authorized, eligible provider account connections** with a discoverable pool of **11 documented U.S. provider candidates**. Historical five account slots are retained for reconciliation and migration; they are **not** to be counted as eight working accounts or merged across distinct brokers without explicit verified identity linking. Each venue has independently verified owner consent, product/account eligibility, market-data scope, paper/read-only canary, revoke control, owner-visible receipts and bounded risk settings. Do NOT activate live trading merely because an account is connected. The connected 8x8 Vault extension presently stores zero owner provider secrets, and the trusted HTTPS 8x8 ID enrollment endpoint is still unverified.

The five original slots remain historical source leads. **Bitget is U.S.-restricted under its published terms and must not be offered as an eligible U.S. live trading account.** Do not attempt geographic workarounds. Do not ask users to enter API keys, access tokens, private wallet keys or passwords in ChatGPT, Hermes/Claude/OpenClaw conversations, Word/Drive documents, GitHub files or shell-history commands. Official OAuth with independently verified scopes, or an authenticated no-logs HTTPS private intake feeding an authorized encrypted Vault, must exist first. Begin with **read-only/paper** and user-controlled key rotation. No withdrawals, transfers, account-management writes or live order permissions by default. When the service has production access, verify balances and fills only through the actual connected exchange and demonstrate order-signature correctness against an approved non-funded route. Only a **separate user-authorized per-account risk envelope**, independent step-up confirmation, model-vs-executor separation, global STOP, position/leverage/spending caps, idempotency, latency/slippage checks, API rate controls and kill switch can authorize a trade. The connection intent is not a trade grant.

Relevant official documentation: [Bitget UTA Quick Start](https://www.bitget.com/docs/uta/quick-start), [Bitget order management](https://www.bitget.com/docs/catalog/trading/order-management). Rates and availability change; never imply unlimited orders or assured $1 million returns.

### Direct social publishing

Eleven canonical destination types: TikTok, YouTube, Instagram, Telegram, Facebook, X, Threads, Pinterest, Bluesky, LinkedIn, Discord. Use the platform's own officially authorized APIs where available. OAuth is preferable; Telegram's bot token, where appropriate, may be entered only on the real secure Vault site. Public posts require rights checks, channel permission, media inspection, user approval or an explicitly approved bounded publishing policy, platform-limit accounting, de-duplication, status reconciliation and receipt. Distinguish an **8x8-owned web publication** (the user controls hosting/storage) from third-party distribution (subject to API quotas, Terms of Service and moderation). No system can guarantee unlimited free external posting. Avoid creating fake/unverified API capabilities.

### Subscription and minute meter

The desired **88 free minutes per day** is a proposed allowance, **not an active entitlement** or guarantee of unlimited compute. Its reset period and storage/compute caps require a verified atomic per-tenant meter, cost controls and abuse prevention. An optional **$8.88/month** subscription should use hosted Stripe Checkout, server-verified signed webhooks, subscription lifecycle reconciliation, customer portal, refunds/cancellations and a robust payment-failure fallback. The paid tier cannot grant broker, social, device or wallet authority and still respects provider quotas. Do not bill the user just for expressing intent. A connected Stripe account is not equivalent to a deployed checkout.

### Crypto wallet and tokenomics

Self-custody defaults: generate/sign keys in an appropriate user-controlled wallet or approved signer, not in the LLM. Bind public wallet addresses by signed challenge, provide watch-only views and vault-protected connection metadata. Crypto checkouts require per-network per-asset invoice, quote expiry, confirmations/reorg handling, anti-fraud and compliance review before acceptance. **8x8 Coin / other 8 tokens, NFT Vault, mining and staking are feature families, not proven deployed tokens or payment networks.** Tokenomics allocations require the exact recovered and reviewed canonical policy; do not invent payout proportions, mint allocations or live contracts.

### ChatGPT ↔ User Edition integration

The single 8x8 One Fabric MCP should expose **one authorized catalog with feature routes**, not literally a limitless MCP tool list or unrestricted device shell. Offer to install connected official ChatGPT plugins only through user consent and product-supported installation flows. ChatGPT and other plugins do not donate access tokens, memories or existing paid subscriptions to 8x8. Optional `Sign in with ChatGPT` is distinct from 8x8 IdP and needs supported identity linking. MCP Apps can provide an embedded dashboard or verified secure-link launch UI; do not ask for sensitive API credentials inside a model-visible chat widget. Native mobile overlays/always-on voice need platform-specific permissions and runtime integrations.

Local device/ADB onboarding is user initiated and can be revoked. ADB pairing happens on the user's own device, using Android's supported flow and local presence; never collect the pairing code into chat or grant the MCP an unrestricted terminal. Separate `terminal.read` from short-lived `terminal.exec` consent, and respect foreground owner priority and STOP. The owner root/founder vault is a separate control plane inaccessible to users regardless of payment tier.

## Deployment acceptance gates

1. Existing 8x8 ID backend deployed; token signature, `iss`, `aud`, expiry, scopes, PKCE and tenant membership verified on every request; cross-tenant negative tests and RLS accepted.
2. Vault hostname controlled and HTTPS certified; single-use intent and callback state stored durably/atomically; CSRF, expiry, replay and session fixation tests; secrets encrypted with managed KMS, no plaintext in tool telemetry.
3. Bitget API keys entered only at Vault, allowed IPs and read-only permissions verified; provider-specific account canary with idempotent request and receipt; trade authority separately gated.
4. OAuth grants for each social destination; published post status only with provider confirmation; use own website independent of external social aggregators without violating official limits.
5. Stripe Checkout and signed lifecycle webhooks, atomic minute usage ledger, cancel/refund/revoke flow and explicit billing disclosure certified. Crypto payment route only after independently verified custody and compliance.
6. User-agent memory isolation, data export/delete, template licensing, custom agents, owner/core separation and voice consent accepted.
7. Same 8x8 ID session mapped to ChatGPT MCP, website/PWA, APK, Telegram Mini App by independently validated provider-specific tokens—not shared passwords or a common leaked bearer token.
8. Five existing mission scheduler lanes preserved. Canary results and their cryptographic hashes are the only criteria for promoting a capability as live.

## What the current commit proves

The `one_fabric_secure_connection_intents_v1.py` policy can prepare a short-lived *non-operational* connection proposal with an opaque intent ID and a SHA-256 nonce digest, scoped to a verified internal tenant representation. It denies unknown providers, unsafe scopes, secret fields, cross-tenant intent reuse, and invalid Bitget slots. It does not create a vault record or execute any external provider operation. An actual server-side OAuth/JWKS middleware, secure vault callback, atomic nonce store and egress connectors have not been implemented by this change. Do not deploy this pure policy module as an authenticating endpoint by itself.
