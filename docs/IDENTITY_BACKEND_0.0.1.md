# 8x8 Identity Backend 0.0.1

**Product maturity:** 8x8 OS 0.0.1 Beta  
**Reality:** PROTECTED_BETA → PUBLIC_PRESENT only after deployment and verification  
**Canonical public source:** `8x8org/8x8-user-edition`

## Purpose

Make account creation, permanent 8x8 identity, profile/workspace ownership, consent, recovery and audit state real rather than simulated UI state.

## Identity path

`auth account → permanent 8x8 ID → profile → workspace → explicit consents → First Blink → bounded Fabric services`

The permanent identity is generated server-side and stored under a unique constraint. Browser-local identifiers are never accepted as canonical identity.

## Included schema

`supabase/migrations/0001_identity_core.sql` defines:

- `profiles` bound 1:1 to `auth.users`;
- globally unique `8x8_<random>` IDs;
- user-owned workspaces;
- separate consent classes instead of installation-as-consent;
- identity audit events;
- automatic account bootstrap;
- row-level security so users can access only their own protected records.

## Explicit consent classes

The first schema separates Terms, Privacy, Device Contribution, Telemetry, Wallet, Economy, Marketing, Voice and Location. Granting one does not grant another.

## Deployment gates

The backend must not be described as PUBLIC_PRESENT until all of these pass:

1. canonical Supabase organization selected by the owner;
2. current project cost shown and explicitly acknowledged;
3. project created in an approved region;
4. migration applied successfully;
5. RLS and database security advisors reviewed;
6. email/passkey/recovery policy configured;
7. duplicate 8x8-ID collision tests pass;
8. cross-account isolation tests pass;
9. export/delete paths verified;
10. rate limiting and abuse controls defined;
11. protected-beta canary accounts complete onboarding;
12. source commit, migration digest, project ID and rollback receipt recorded;
13. load test establishes measured capacity before any user-count claim.

## Financial boundary

The identity backend does not authorize wallet custody, token issuance, NFT minting, purchases, staking, autonomous signing, trading or billing. Those require independent contracts, security review, compliance review and owner authorization.

## 88k capacity truth

`88,000 users` is a capacity target until a controlled load test proves the account and application path at a declared concurrency/rate profile. Registration UI alone is not capacity evidence.

## Rollback

Before production promotion, retain a clean migration history and database backup strategy. A failed protected-beta release must be able to disable new registrations without deleting existing identity records.
