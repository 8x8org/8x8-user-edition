# ©️8x8 One Fabric — live provider connection-intent registry receipt (2026-10-18)

Canonical root: `fabric://8x8/core`

Authoritative location: existing Supabase project `8x8-one-fabric` (`kjvmagncyednwfezbjww`), pre-existing `public.fabric_sources` table. This file is an evidence pointer, **not a second registry or a Vault credential store**.

## Observed and independently read back
- 23 metadata-only connection-intent rows added and checked through connected Supabase management access.
- 11 trading provider candidates: Alpaca, Tradier, tastytrade, TradeStation, Charles Schwab, Coinbase Advanced, Kraken, Gemini, Interactive Brokers, Robinhood Crypto, OANDA US. First 8 are the priority group. (Bitget is not enabled for U.S. enrollment.)
- 12 publishing destinations: TikTok, YouTube, Instagram, Facebook, Threads, X, Telegram, Discord, Pinterest, Bluesky, LinkedIn, Google Business Profile.
- Every row has prefix `connection_intent:`, `auth_state=NOT_AUTHENTICATED`, `operational_state=NOT_CONNECTED_NATIVE`, `sensitive_policy=NO_RAW_SECRETS`, absent credential refs and user auth identifiers. Each row has documentation URL and next action metadata.
- Pre-existing table RLS policy denies `anon` and `authenticated` directly. Records are for administrative recovery only until verified 8x8 ID/Gate 2 authentication and tenant-scoped APIs are deployed.
- Observed `auth.users=0`, `vault.secrets=0`; no deployed Supabase enrollment Edge Function. Supabase security advisor returned no lint findings during assessment. This is **not** security signoff.
- Alpaca Go CLI `v0.0.14` already installed on Samsung, path fixed in previous run; this receipt does not authenticate the account.

## Required protection and next implementation
1. Reuse existing 8x8 ID/Gate 2 and `protected-beta/one_fabric_native_provider_readiness_v2.py`, `protected-beta/one_fabric_oauth_launch_gate_v3.py`. No replacement identity fabric.
2. Resolve actual owner authentication and tenant membership; deploy and test a private enrollment interface, authoritative provider-specific OAuth flow or server-only credential entry, Vault storage, secret rotation and revocation.
3. Allow only authenticated owner/tenant to see their own connection records; agent interfaces must never display, log, or transmit raw keys. Enroll privately, not through chat, git, Hermes logs or the remote shell command line.
4. Verify the first provider with paper/sandbox/read-only scopes and an attributable receipt; activate trading or publishing as a separate explicitly authorized action, with bounded permissions, STOP and audit.
5. Preserve existing Upload-Post historical delivery receipts until direct provider publishing achieves authenticated and independently verified delivery.

## Evidence and roll-forward caveat
Metadata insertion and readback occurred on 2026-10-18. This receipt records the database state observed at that checkpoint. It does not claim account connection, Vault secret enrollment, OAuth approval, order ability, automatic trading, direct publishing, identity creation, deployed World, installed APK or task scheduler modification.

No raw keys or credential fingerprints are contained in this file.
