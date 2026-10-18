# ©️8x8 One Fabric — Alpaca Connect submission draft (2026-10-18)

Status: INCOMPLETE; **do not submit** until the website, legal policies and exact callback are public and independently verified, the privacy/disclosure language is reviewed and the owner accepts Alpaca's terms. This document contains no credentials or regulated financial advice.

## Application fields
- **Name:** 8x8 One Fabric
- **Category:** Algos And Strategies, if that category exists in the actual application dropdown; otherwise pick the closest accurate supported category. First release is portfolio analytics/paper-research, **not** live algorithmic execution.
- **Description (copyable):** 8x8 One Fabric is an independent research and creative-work platform with an optional Alpaca account connection. Its initial Alpaca integration is designed for owner-authorized, paper-account, read-only portfolio and position viewing, education, simulated strategy testing, and audit records. It does not request live order placement, withdrawals, transfers, or unattended brokerage execution during the initial launch. Users connect through Alpaca's official OAuth consent flow and can revoke access. The broader 8x8 product includes a research workspace, Studio, agent-assisted tools and visual dashboards. Any later live trading capabilities would require separate compliance approval, appropriate scopes, risk limits and explicit user authorization.
- **Application Website:** **PENDING PUBLIC VERIFICATION**. A Vercel project named `8x8-user-edition` exists. Candidate hostname `https://8x8-user-edition.vercel.app` is NOT yet independently verified as a publicly reachable, suitable application homepage in this run. Do not enter as valid without browser validation.
- **Redirect URI:** **DO NOT GUESS OR SUBMIT**. Must be an exact HTTPS URL for the verified backend callback, on a reviewed stable domain, with valid trusted session binding and server-side state verification. No working 8x8 callback is proven.
- **Terms of Use:** **PENDING PUBLIC URL + owner/legal review**. The repository's identity consent data is not a published Terms page.
- **Privacy Policy:** **PENDING PUBLIC URL + owner/legal review**. Include financial data collection/use/retention/revocation, children/access requirements, security, data sharing, contact details and actual service practices.
- **Commercial use:** **DISCLOSE intended subscriptions/services and any other monetization truthfully**. Alpaca's current terms require written approval for monetized apps.
- **App Logo:** **PENDING CANONICAL RIGHTS-OWNED 8x8 IMAGE**, PNG/JPG/GIF, <=256x256 pixels, <=1 MB according to user's displayed form. Do not substitute borrowed marketplace logos or an invented official identity.
- **Customer-facing screenshots:** The attached screenshot mockup is **proposed**, not a functioning product; the form calls for screenshots of all customer-facing pages and an account authorization disclosure screenshot. Before submission, obtain actual screenshots of every relevant working 8x8 user interface. The displayed requirements simultaneously say `1024×500` and `16:9`, which differ; generate both aspect ratios for review and confirm which Alpaca actually accepts.
- **Publish App:** Do not mark as approved/operational or activate promotion until Alpaca review and owner signoff.

## Disclosure issue requiring Alpaca confirmation
The user-shared Alpaca form's prescribed disclosure includes *authorization to place transactions*, but the initial requested integration will omit the `trading` OAuth scope and use `env=paper`. The preview intentionally includes the supplied wording and an adjacent warning that this mismatch needs compliance review. The preview is **not** a live Alpaca-issued consent page.

## Scope and security
- OAuth authorization code flow; `env=paper`; no `trading`, `account:write` or `data` scope initially; read-only default.
- One-use random OAuth `state` in a server-side expiring transaction bound to authenticated 8x8 user and tenant. Reject missing/mismatch/replay/expired callbacks.
- Backend-only client secret and token exchange; authenticated 8x8 ID; authorized tenant; vault encrypted token custody with isolated read permissions; revocable grants; no raw credentials through chatbot, Hermes, logs, public MCP tool arguments, or documents.
- Deployment checks: app approved, exact redirect registered, privacy/terms reachable, OAuth callback ready, auth works, RLS/tenant isolation checked, consent recorded, one read-only paper canary independently received, receipts redact all tokens.
- Do not infer live trading from a portfolio read. Keep trade execution and post permissions independent.

## Existing-source continuity
Continue using `fabric://8x8/core`, User Edition PR #200 and `protected-beta/one_fabric_native_provider_readiness_v2.py`, `protected-beta/one_fabric_oauth_launch_gate_v3.py`. Keep the 24-repository/research/visual estate and only five canonical scheduled lanes in scope; do not introduce another authority root or scheduler. Preserve existing agent/Studio/GG/Atlas/SOMA/Omni assets via evidence-backed reuse.

## Provider documentation
- https://docs.alpaca.markets/us/docs/registering-your-app
- https://docs.alpaca.markets/us/docs/about-connect-api
- https://docs.alpaca.markets/us/docs/using-oauth2-and-trading-api
- https://app.alpaca.markets/connect (owner-facing dashboard page; requires authorized login)

## Marketplace research leads (NOT 8x8 integrations)
From user-supplied screenshot: TradingView (charting), TradersPost (automation), SignalStack (signal-to-order routing), MachineTrader (strategy platform), QuantMage (portfolio/system strategies), StockHero (bot marketplace), Market Gear (options analytics), Alpaca CLI (developer workflow), AlgoBulls (system trading). All third-party functionality requires its own licenses/permissions/terms and independent evidence. No confirmed integrated accounts or owned source code.

## Status
Draft and static visual tests are evidence of proposal quality only. Not app registration, not approval, not 8x8 direct credential custody, and not live release.