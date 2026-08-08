# 8x8 User Edition 0.0.1 Beta — Public Deployment Receipt

**Reality:** `PUBLIC_PRESENT`  
**Promotion state:** `PROTECTED_BETA`  
**Source authority:** `8x8org/8x8-user-edition`  
**Current canonical source merge:** `10a32aa97165598ddddcaa34600db58b10aac7c4`  
**Public production carrier:** `https://8x8-os-ecosystem.vercel.app`

## Purpose

This receipt records the public-safe production carrier currently serving the canonical 8x8 User Edition 0.0.1 Beta source. The Vercel carrier project retains a historical project name; it is a deployment carrier only and does not replace the canonical GitHub source repository.

Protected deployment/project identifiers remain outside public source under the existing information-boundary policy. The public receipt records the stable public alias and exact canonical source authority instead.

## Current source generation

The current public source identifies the deployed interface as:

`8x8 OS · Omniversal Command Atlas · 0.0.1 Beta`

The Omniversal Command Atlas R2 source was merged at canonical commit `10a32aa97165598ddddcaa34600db58b10aac7c4` after public-boundary and CodeQL validation. Historical names such as Fabric Mirror, Command Fabric, MSG identifiers and carrier commit generations remain provenance only and do not change product maturity from `0.0.1 Beta`.

## Production route verification

The production carrier has been observed serving browser-renderable HTML at the required public routes:

| Route | Expected HTTP | Expected content type | Expected disposition |
|---|---:|---|---|
| `/` | 200 | `text/html` | inline/browser render |
| `/first-blink` | 200 | `text/html` | inline/browser render |
| `/world` | 200 | `text/html` | inline/browser render |
| `/art-board` | 200 | `text/html` | inline/browser render |

The canonical source also contains continuous production-health checks intended to fail on route failure, non-HTML responses, attachment/download regressions or product-marker drift.

## Deployment provenance boundary

The Vercel production project still uses the historical carrier repository `horbolsi/8x8-OS-Ecosystem`. Current production metadata records a carrier commit whose commit message states that it mirrors canonical User Edition commit `10a32aa...`.

Therefore the current evidence classification is:

- canonical public source: `VERIFIED`;
- production deployment state: `READY` in Vercel;
- carrier-to-canonical mirror declaration: `OBSERVED`;
- direct canonical-repository-to-Vercel Git provenance: `PARTIAL`, because the production project remains attached to the historical carrier rather than directly to `8x8org/8x8-user-edition`;
- whole private Fabric deployment: `NOT_INFERRED`.

This distinction must remain visible until the deployment topology is normalized or an independently reproducible artifact-digest chain is available.

## What this proves

This receipt supports that the public production carrier is serving the current 0.0.1 Beta public interface through the historical Vercel carrier topology.

It does **not** prove:

- whole-system 100/100 completion;
- direct Vercel Git attachment to the canonical organization repository;
- complete private local-runtime state;
- private agent, memory, message, wallet or credential exposure;
- physical-device visual rendering on every supported client;
- global persistent account or 8x8-ID backend readiness;
- 88k-user load certification;
- mainnet financial authority;
- Future Lab capabilities as deployed Present facts.

## Remaining certification

The remaining release-grade gates include direct deployment provenance normalization, physical logged-out Android Chromium and mobile Safari visual smoke, protected-beta identity backend verification, accessibility/browser regression coverage, and any other acceptance gates declared by the active 0.0.1 release train.

## Rollback

Vercel retains READY rollback candidates. Any rollback must preserve the public/private boundary, keep product maturity at `0.0.1 Beta`, and must not restore obsolete 0.1.x maturity language or unsupported live-capability claims.
