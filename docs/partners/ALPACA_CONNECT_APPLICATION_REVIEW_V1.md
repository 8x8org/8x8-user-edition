# ©️8x8 One Fabric — Alpaca Connect application review packet v1

**Canonical authority:** `fabric://8x8/core` · **Status:** INTERNAL APPLICATION DRAFT / NOT SUBMITTED / NOT APPROVED / NOT CONNECTED.
**Reuse:** PR #200 OAuth preflight `protected-beta/one_fabric_oauth_launch_gate_v3.py`, protected user-account gateway and public User Edition. Do not create a second independent 8x8 account system.

## User-supplied developer form, 2026-10-18
Screenshots show the official Alpaca Connect marketplace, an authenticated Paper Trading context, and the 'Submit Your App' form. They **do not** establish that 8x8 has already registered, received a Client ID, deployed a callback or been approved. The form requests Application Details (name, category, description, website, redirect, Terms, Privacy) and Graphics (logo and customer-facing pages with specific disclosure text). The form shows an estimated review period of approximately **30 business days**; this is Alpaca's estimate, not an 8x8 launch promise.

## Exact proposed application fields (review before submission)
- **Name:** 8x8 One Fabric
- **Category:** Algos And Strategies (select only if that category is actually offered by the current dropdown).
- **Description:** 8x8 One Fabric is a protected-beta, consent-based software experience combining portfolio research, charts, simulated strategies, model-assisted market intelligence and account-linking within 8x8 World and related interfaces. Our initial Alpaca Connect integration is limited to user-authorized, paper-account read-only account information; it will not request order placement, withdrawals or account-configuration writes. Broader agent-assisted execution, publishing and wallet capabilities are separate future features subject to security, consent, eligibility and provider approvals. We do not promise returns or claim Alpaca endorsement.
- **Application Website candidate:** https://8x8-os-ecosystem.vercel.app — this appears as the public carrier in the existing User Edition README, **but independent availability and final Alpaca-facing landing content are NOT ACCEPTED**.
- **Redirect URI:** **BLOCKED — DO NOT INVENT**. Register only an exact HTTPS callback after the authenticated 8x8 ID backend, one-use OAuth state persistence, token broker and callback error handling are deployed and verified. Never point this to a static marketing page.
- **Terms of Use:** **BLOCKED — NEEDS USER/LEGAL REVIEWED, PUBLIC HTTPS PAGE**. Do not substitute GitHub source docs for user-facing terms.
- **Privacy Policy:** **BLOCKED — NEEDS USER/LEGAL REVIEWED, PUBLIC HTTPS PAGE**. Must accurately document Alpaca scopes, collected data, retention, deletion, sharing, user rights, contact channel, security and revocation.
- **Logo:** **BLOCKED — verify canonical owner-authorized 8x8 logo**, PNG/JPG/GIF maximum 256×256 and 1 MB per user screenshot. Do not synthesize or replace original without approval.
- **Screenshots:** Every actual customer-facing page plus explicit disclosure screenshot; user screenshot requests PNG/JPG around 1024×500 up to 2 MB but also describes 16:9 (mathematically inconsistent; verify upload validation). Concept previews cannot be described as actual deployed screenshots.
- **Publish App option:** Leave off until Alpaca review/consent, legal pages, authenticated experience, full required screenshots and user approval are complete.
- **Commercial disclosure:** The 8x8 project contemplates subscription/paid services; disclose commercial features to Alpaca as appropriate. Source proposals are not evidence of active billing.
- **Agreement/Submit:** Owner must review Alpaca terms and authorize final submission. Do not auto-check agreement or submit under someone else's authority.

## Exact Alpaca disclosure as supplied by the owner
> Authorize [Your App Name] By allowing [Your App Name] to access your Alpaca account, you are granting [Your App Name] access to your account information and authorization to place transactions in your account at your direction. Alpaca does not warrant or guarantee that [Your App Name] will work as advertised or expected. Before authorizing, learn more about [Your App Name].

The provider's mandatory wording is broader than the initial requested read-only paper permission. Present it faithfully, alongside a separate precise current-scope description. Do not represent the disclosure as itself granting trading authority.

## Actual OAuth acceptance for first canary
1. Registered, reviewed OAuth app and verified exact callback (no hard-coded invented Client ID).
2. Verified owner/user 8x8 session and tenant membership; never caller-supplied identity.
3. Generate unpredictable one-use state bound to user/tenant/account slot and persist atomically with expiry.
4. Provider authorization **env=paper**, with **no trading or account:write scopes** in initial request; Alpaca docs say read-only is the default.
5. Callback verifies state, lifetime, tenant and server-side session; exchange code on backend only.
6. Encrypt provider tokens inside user-scoped private custody; keep tokens out of tool arguments, logs, prompts and frontend.
7. Read-only account canary and durable receipt; observe STOP/revocation; no live orders.
8. One live account requires separate owner authority, risk limits, account eligibility, compliance approval and independently verified execution.

## Marketplace capability intelligence — research leads, not inherited permissions
- TradingView: charting/alerts; inspect integration and licensing before reuse.
- TradersPost: strategy/alert automation concepts; risk-gate, deduplicate and verify executed fills.
- SignalStack: event routing concepts; audit permissions and signal provenance.
- MachineTrader, QuantMage, StockHero, Market Gear, AlgoBulls: evaluate their documented interfaces/terms, but do not install, connect or copy assets merely because they are displayed on Alpaca.
- Alpaca CLI: official CLI can support paper verification behind the existing Hermes/FlashTM8 permission boundary. It is not a secure replacement for a tenant-aware user authorization flow.

## Whole-estate interface requirement
This application must be one leaf of existing `fabric://8x8/core` capability/evidence/authority graphs, projected through 8x8 World, 8x8 MCP, User Edition, APK and Telegram Mini App. Preserve owner/private vs public tenant scope; original Agent Theater, GG donor, SOMA/Omni/Atlas, Studio, 24 known repositories, research provenance, five existing lanes and STOP policy. No invented complete census.

## Provenance / checkpoints
- GitHub User Edition PR #200: source-only protected-beta; status at this intake open draft.
- Vercel project `8x8-user-8888` has a READY preview deployment but is not evidence of public callback or legal-route readiness.
- Supabase project `8x8-one-fabric`: last rechecked 0 Auth users, 0 Vault secrets, 0 Edge Functions. This is not a functioning custody and callback service.
- No real account linked by this review, no registration submitted, no Alpaca app approved, no live trading, no public post.
- Official registration: https://docs.alpaca.markets/us/docs/registering-your-app
- Official OAuth flow: https://docs.alpaca.markets/us/docs/using-oauth2-and-trading-api
- Official Connect terms/overview: https://docs.alpaca.markets/us/docs/about-connect-api
