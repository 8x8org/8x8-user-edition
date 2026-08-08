# 8x8 OS 0.0.1 Beta — Public Modernization Convergence

## Purpose

This document turns the remaining public-repository modernization work into one reviewable convergence lane. It does not promote whole-system maturity, expose protected runtime details, or treat historical pull requests as automatically mergeable.

## Canonical public truth

- Product maturity: **8x8 OS 0.0.1 Beta**.
- Canonical public source: `8x8org/8x8-user-edition`.
- Public production carrier: historical Vercel project name, with canonical-source provenance still tracked separately.
- Private runtime, protected repository inventory, credentials, wallet authority, unrestricted memory/messages, and owner-only topology remain excluded.
- Past, Present and Future are executable system realities; Protected Beta is a promotion state, not a fourth reality.

## Modernization objectives

1. Keep README, architecture, security, implementation status, deployment receipts and machine-readable state mutually consistent.
2. Reconcile old pull requests by evidence, not age or enthusiasm.
3. Preserve useful security, accessibility, testing, supply-chain and receipt-verification work from historical branches.
4. Prevent product-version drift away from `0.0.1 Beta`.
5. Keep public claims generated only from approved Public Present evidence.
6. Bind deployment claims to exact source and artifact provenance.
7. Make repository presentation strong enough to explain the Fabric without leaking the private estate.

## Legacy PR treatment

Historical public PRs fall into five classes:

- `MERGE`: still cleanly applicable and independently verified against current main.
- `PORT`: useful idea or implementation, but must be re-applied to current main because the branch is stale or conflicts with newer architecture.
- `SUPERSEDE`: outcome already achieved by later reviewed work.
- `ARCHIVE`: historically useful reference that should remain unmerged.
- `CLOSE`: no longer useful, unsafe, or incompatible with current policy.

No historical PR is merged merely because its checks passed against an old base commit.

## High-value legacy work to reconcile

| Area | Historical PRs | Current treatment |
|---|---|---|
| Public boundary validator | #16, #17, #24, #87 | PORT or SUPERSEDE after current validator comparison |
| Accessibility and keyboard UX | #18, #21, #28 | PORT only after current Fabric UI audit |
| Developer experience | #19, #20 | PORT selected low-risk improvements |
| Browser smoke tests | #22 | PORT after adapting to current routes and First Blink |
| Security headers | #23 | PORT only where compatible with current inline/static architecture |
| SBOM and build provenance | #25 | PORT; valuable for Issue #106 provenance closure |
| Public receipt verifier | #26 | PORT after updating receipt IDs and `0.0.1 Beta` semantics |
| Service-worker integrity | #27 | PORT only if the current public client still uses the same caching model |
| Economy / node research | #32 | ARCHIVE or split into Future Lab artifacts; no live authority |
| Competition Edition | #34 | ARCHIVE or isolate as competition-specific Future Lab work |
| Provider routing / fleet registries | #90 | PORT public-safe schemas only; private runtime remains authoritative |
| Continuous organization registries | #91 | PORT public-safe governance pieces after overlap review |

## Definition of modernization-complete for this repository

A timestamped `100/100` repository audit is allowed only when:

- all current public files are inventoried;
- all active PRs are classified;
- version, reality and evidence states agree across docs and JSON;
- every public route has automated and physical-client evidence where required;
- security, accessibility, supply-chain and boundary checks pass at exact head;
- production provenance can be independently reconstructed;
- rollback is documented;
- no critical unknown public-release dependency remains.

This definition applies only to the declared public repository scope. It does not imply that the full 8x8 estate or the future is complete.
