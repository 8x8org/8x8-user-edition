# One-Fabric Repository Role Contract

**Project:** ©️8x8 by FlashTM8 ⚡️🌎🤖  
**Canonical logical root:** `fabric://8x8/core`  
**Repository:** `8x8org/8x8-user-edition`  
**Primary lifecycle classification:** `DEPLOYMENT`  
**Contract version:** `ONE_FABRIC_REPOSITORY_ROLE_V1`  
**Recorded:** `2026-09-11 UTC`

## Why this repository exists

Canonical public-safe user product/client for ordinary tenant-isolated users, excluding owner-private controls and raw internal topology.

This repository is one bounded organ of **ONE Fabric**. Repository separation is an engineering, security, release, or provenance boundary; it does not create another 8x8 root.

## Authority and ownership

Public client UX and release artifacts that have passed its evidence gates.

When documentation or code conflicts across repositories, apply this precedence:

1. The private One-Fabric architecture defines overall OWNER_ROOT policy.
2. The bounded blockchain implementation defines native-chain internals and economic invariants within that policy.
3. `8x8org/8x8-protocol` defines versioned public interoperability promises.
4. Deployment/product repositories consume those authorities.
5. Specialist implementations remain bounded to their declared capability.
6. Backups and dormant donors preserve history but do not override current authority.

## Dependencies and information flow

Consumes 8x8-protocol and approved public projections; may use deployment carriers while retaining source identity.

A dependency is not automatically active. Source must be adopted, configured, authenticated, granted, started, tested, and independently verified before being labeled productive.

## Runtime placement

Browser/PWA and separately certified Telegram/native clients; each channel needs its own receipt.

Private device topology, local storage paths, internal service placement, build hosts, and owner execution infrastructure are intentionally outside this public repository contract. Carrier certification is based only on public interfaces and independently reproducible receipts.

## Prohibited responsibilities

Shared UI never means shared authority; no owner Vault, private agents, raw secrets, unrestricted device control, or unproven value-bearing features.

Across every repository, raw private keys, seed phrases, live Vault secrets, bearer credentials, and raw biometric templates are forbidden in Git. Agents receive opaque handles and scoped capabilities, never raw custody material.

## Evidence and lifecycle semantics

Use the following state distinctions exactly:

`REGISTERED ≠ REACHABLE ≠ HEALTHY ≠ AUTHENTICATED ≠ GRANTED ≠ LEASED ≠ STARTED ≠ PRODUCTIVE ≠ VERIFIED`

Material claims must be classified as:

- **PAST_PRESERVED:** historical evidence retained with provenance.
- **PRESENT_PROVEN:** freshly verified against a named source/runtime, timestamp, and receipt.
- **FUTURE_GATED:** proposed or implemented work not yet promoted to live authority.

The repository lifecycle classes are:

- **AUTHORITATIVE:** defines a bounded truth domain.
- **IMPLEMENTATION:** implements a bounded capability under authority.
- **DEPLOYMENT:** packages or serves approved capabilities.
- **BACKUP:** preserves recoverable state; never the development root.
- **DORMANT DONOR:** preserves useful historical code/design/evidence for explicit adoption.

## Change and promotion protocol

1. Research current authoritative rules and prior evidence.
2. Census existing files, branches, deployments, and runtime copies.
3. Reconcile conflicts without deleting historical donors.
4. Plan the target authority and rollback.
5. Implement on a review branch.
6. Test the bounded capability.
7. Verify against the actual target runtime.
8. Produce a hash-linked receipt.
9. Promote only with explicit authority.

Every adoption from this repository into another must record source repository, source commit, source path, destination, semantic changes, tests, receipt hashes, rollback, and invalidation/freshness rules.

## Current verification boundary

This role contract classifies intent and authority. It does **not** prove deployment, authentication, health, or productivity. Fresh carrier and deployment receipts are required for those claims.
