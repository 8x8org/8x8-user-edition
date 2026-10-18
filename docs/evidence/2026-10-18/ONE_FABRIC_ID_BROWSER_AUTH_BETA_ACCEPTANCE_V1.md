# ©8x8 One Fabric — Protected browser identity bootstrap acceptance
Date: 2026-10-18 UTC. Authority: `fabric://8x8/core`. Branch: `feat/unified-8x8-id-mcp-user-edition-20261016`.

## Implemented in the existing 8x8 User Edition
- Existing deployed Supabase `one-fabric-id` Edge Function remains **ACTIVE** with `verify_jwt=true`. Database RLS `one_fabric_user_ids_self_select` and `one_fabric_user_ids_self_insert` restrict access to `auth.uid()`.
- Added `protected-beta/account/identity-client.mjs` and `identity-ui.mjs`. The pre-existing account page now offers email-based passwordless PKCE S256 sign-in, optional email OTP if the email template sends a code, one-time code exchange, read-only ID lookup, and deliberate **separate** create-ID confirmation before protected POST. Local session remains ephemeral in memory; only PKCE verifier is in sessionStorage and is cleared on exchange or logout. No refresh-token persistence.
- The client has **only the existing Supabase project's publishable key** (`sb_publishable_` type), never service-role secrets. Source and output reject account-provider API keys, wallet secrets, trades, public posts and Vault access. Sign-in uses strict exact Supabase origin and no arbitrary redirect.
- Existing static Vercel build explicitly copies the two new JS modules into `dist/account`; CSP adds only `https://kjvmagncyednwfezbjww.supabase.co` to connect-src. All existing surfaces remain preserved.

## Executed acceptance
Connected Samsung native Node.js v24.18.0, isolated scratch directory under `~/.8x8/identity-beta-acceptance-20261018`. Exact two source files fetched from this branch and written without modifying owner OS git checkout; `nice -n 10 node --test test-identity-client.mjs` exited 0: **16 tests / 16 passed**. Cases: email validation, HTTPS origin, PKCE challenge + exact redirect, missing secrets, verifier destruction on network failure, one-time authorization-code exchange, malformed code refusal, OTP verification, missing authenticated session refusal, read-only GET not-enrolled, deliberate authenticated POST, forged ID rejection, bad session rejection, logout and no financial/publishing authority.

From authorized Samsung device, a **CORS OPTIONS preflight** to `https://kjvmagncyednwfezbjww.supabase.co/functions/v1/one-fabric-id` with the exact known Vercel origin `https://8x8-user-8888-8x8-team-url.vercel.app` returned HTTP **204** plus `access-control-allow-headers: authorization, x-client-info, apikey, content-type, ...`, `access-control-allow-methods: GET, POST, ...`. This verifies the network browser preflight only, **not an authenticated browser request**.

## Source file fingerprints (Git object blob SHA, not SHA256)
- `protected-beta/account/identity-client.mjs`: Git blob `4245f9451994c623bea02a1a4ae4966a3f436cb0` (5229 UTF-8 characters)
- `protected-beta/account/identity-ui.mjs`: Git blob `d319c66f9a72e5b7597b8b5c1c9db300397348af` (3364 UTF-8 characters)
- `protected-beta/account/index.html`: Git blob `14ab89bb23839a1677f76edf666c649c190cb3c1` (6334 UTF-8 characters)
- `protected-beta/account/test-identity-client.mjs`: Git blob `8566324074c13ebcaca0396861d9d4122974ac09` (6907 UTF-8 characters)
- `scripts/build-vercel-static.mjs`: Git blob `5286e5f93291ba31de481d09b02cb60e73fec811` (4736 UTF-8 characters)
- `vercel.json`: Git blob `c4e258f06d29c4dd505119f3194c7397613d49b5` (2752 UTF-8 characters)

## Operational truth and gates
- At latest live database read, `auth.users=0` and `vault.secrets=0`: no enrolled user, no credential storage, no native account connection.
- Supabase Auth email delivery/templates, registered callback URL, sender domain/reputation, actual email code link and complete browser login → ID issuance have **NOT** been exercised. If Auth redirect is not allowlisted, login requires configuration; no forged callback URLs.
- This is a **staged, test-accepted browser-auth source improvement**, not a user-authorized authenticated provider OAuth flow or finished all-in-one World release. Do not describe a successful UI sign-in until a real user explicitly signs in and receives verified ID.
- No real email sent, funds moved, orders placed, public content posted, wallet signed, device foreground touched, service restarted, scheduler added or Vault secret created. Owner historical repositories and existing five lanes were preserved.
- Users must never paste broker/exchange/bot/password private credentials into chat, GitHub, Google Docs, shell logs or MCP tool arguments. Provider consent requires server-held OAuth state and independently verified backend before any credential intake.

Source snapshots are on the existing PR #200 branch. Production promotion, supported OAuth callback, private key custody, tenant-bound provider connection and the larger estate census remain separate gates.
