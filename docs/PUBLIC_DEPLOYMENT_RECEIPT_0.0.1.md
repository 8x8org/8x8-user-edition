# 8x8 User Edition 0.0.1 Beta — Public Deployment Receipt

**Reality:** `PUBLIC_PRESENT`  
**Promotion state:** `PROTECTED_BETA`  
**Source authority:** `8x8org/8x8-user-edition`  
**Reviewed source merge:** `7f67c72c33ea940d80ca1e41ebea879be25eac0e`  
**Public production carrier:** `https://8x8-os-ecosystem.vercel.app`

## Purpose

This receipt records the public-safe production carrier currently serving the canonical 8x8 User Edition 0.0.1 Beta source. The Vercel carrier project retains a historical project name; it is a deployment carrier only and does not replace the canonical GitHub source repository.

Protected Vercel deployment/project identifiers are retained outside public source under the existing information-boundary policy. The public receipt records the stable public alias and exact canonical source commit instead.

## Source gates

Before merge of PR #104:

- Public Information Boundary: `PASS`
- CodeQL: `PASS`
- product maturity restored to `0.0.1 Beta`
- Three Realities retained as `PRIVATE_PAST`, `PUBLIC_PRESENT`, `FUTURE_LAB`
- `PROTECTED_BETA` retained as promotion state
- public version-drift validation added

## Production route verification

The production carrier was verified after deployment of the canonical 0.0.1 Beta `index.html` and `vercel.json` content.

| Route | HTTP | Content type | Disposition | Result |
|---|---:|---|---|---|
| `/` | 200 | `text/html; charset=utf-8` | `inline` | PASS |
| `/first-blink` | 200 | `text/html; charset=utf-8` | `inline` | PASS |
| `/world` | 200 | `text/html; charset=utf-8` | `inline` | PASS |
| `/art-board` | 200 | `text/html; charset=utf-8` | `inline` | PASS |

Observed production response protections include `X-Content-Type-Options: nosniff`, framing denial, restrictive permissions policy, Content Security Policy, cross-origin opener/resource policies, HSTS and inline HTML disposition.

The response body contains the expected `8x8 OS · Fabric Mirror · 0.0.1 Beta` title and the advanced Fabric Mirror interface rather than a source-file download or Vercel 404 page.

## What this proves

This receipt proves that the public production carrier is currently serving browser-renderable 0.0.1 Beta HTML at the required routes with the required public-safe response behavior.

It does **not** prove:

- whole-system 100/100 completion;
- dedicated Vercel project creation under the canonical repository name;
- private Termux/Ubuntu runtime state;
- private agent, memory, message, wallet or credential exposure;
- physical-device visual rendering on every supported client;
- mainnet financial authority;
- Future Lab capabilities as deployed Present facts.

## Remaining certification

Physical logged-out Android Chromium and mobile Safari visual smoke remain separate client-side evidence. The previous failed URL is superseded by the current production carrier above.

## Rollback

Vercel retains a prior READY production deployment as a rollback candidate. Its protected deployment identifier is intentionally omitted from public source. Any rollback must preserve the public/private boundary and must not reintroduce the obsolete 0.1.x product-maturity wording.
