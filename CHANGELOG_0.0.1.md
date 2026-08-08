# 8x8 User Edition — 0.0.1 Beta Changelog

## 2026-08-07 public deployment repair

### Corrected

- restored canonical product maturity from accidental `0.1.x`/`v0.1.1` wording to **8x8 OS 0.0.1 Beta**;
- separated `MSG296E` and other historical identifiers from product-version semantics;
- made the Three Realities and `PROTECTED_BETA` promotion state explicit in public machine-readable state;
- added CI enforcement against future public product-version drift;
- hardened Vercel rewrites and browser response headers for `/`, `/first-blink`, `/world`, and `/art-board`;
- preserved the public/private information boundary and protected repository lineage rules.

### Released to canonical public source

PR #104 merged the correction into `8x8org/8x8-user-edition` main at:

`7f67c72c33ea940d80ca1e41ebea879be25eac0e`

The required Public Information Boundary and CodeQL checks passed before merge.

### Production carrier

The current public production carrier is:

`https://8x8-os-ecosystem.vercel.app`

Although the Vercel project retains a historical carrier name, the deployed page is sourced from the canonical 0.0.1 Beta User Edition release content. Server-side checks confirm browser-renderable HTML and inline disposition on the required routes.

### Still evidence-gated

- physical Android Chromium visual smoke;
- physical mobile Safari visual smoke;
- dedicated Vercel project creation under the canonical User Edition project name;
- private-runtime and whole-system completion claims;
- any live financial or mainnet authority.

The wider 8x8 system remains **0.0.1 Beta** and continues evolving across Private Past, Public Present and Future Lab.
