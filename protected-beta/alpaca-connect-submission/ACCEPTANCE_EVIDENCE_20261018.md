# ©️8x8 One Fabric — Alpaca Connect submission preflight evidence

- Date: 2026-10-18
- Canonical root: `fabric://8x8/core`
- Scope: 8x8 independent third-party Alpaca Connect application, initial **paper account / read-only** consent
- Existing source reused: `protected-beta/one_fabric_native_provider_readiness_v2.py` and `protected-beta/one_fabric_oauth_launch_gate_v3.py`
- New app submission draft: `protected-beta/alpaca-connect-submission/APPLICATION_DRAFT.md`
- New customer-facing proposed static UI: `protected-beta/alpaca-connect-submission/index.html`
- Local HTML/draft safety tests: 25/25 PASS (test suite provided with separate owner downloadable kit; tests are offline only)
- Browser screenshot captured at 1024×500 and 1024×576; actual screenshot from generated HTML in kit, not production or Alpaca-hosted UI.
- Live Alpaca OAuth app registration: **NOT SUBMITTED**
- Compliance/app approval: **NOT VERIFIED**
- App logo: **PENDING CANONICAL OWNER LOGO**
- Public app homepage: **NOT INDEPENDENTLY VERIFIED**
- Published Terms & Privacy Policy: **NOT VERIFIED**
- Exact registered production callback: **ABSENT/NOT VERIFIED**
- 8x8 Auth user session, backend/PKCE/state service, owner-only Vault custody and read-only provider canary: **NOT ESTABLISHED**
- Secret collection/transfer: **NONE**
- Live trading, transfers, wallet signing, publishing: **NONE**
- Old third-party integrations remain independent and cannot be acquired by mere inclusion in the 8x8 catalog.
- Important: the Alpaca form's prescribed disclosure mentions authority to place transactions, whereas initial OAuth integration deliberately omits the `trading` scope. Obtain compliance direction on an accurate read-only disclosure before submitting.
- The application draft is deliberately incomplete. Never invent a valid callback/terms/privacy URL or submit bogus legal pages.
- No sixth scheduler, foreground device action, installation or production deployment.

Docs: https://docs.alpaca.markets/us/docs/registering-your-app and https://docs.alpaca.markets/us/docs/using-oauth2-and-trading-api
