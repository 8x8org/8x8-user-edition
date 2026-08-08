# 8x8 OS 0.0.1 Beta — Production Health and Provenance

## Canonical public source

`8x8org/8x8-user-edition`

## Current public carrier

`https://8x8-os-ecosystem.vercel.app`

The Vercel project name is a historical carrier identity. It is not the canonical source authority.

## Route-health contract

The public carrier must return browser-renderable HTML for:

- `/`
- `/first-blink`
- `/world`
- `/art-board`

For every route:

- HTTP status must be `200`;
- `Content-Type` must be `text/html`;
- `Content-Disposition: attachment` is forbidden;
- the response body must contain the canonical `0.0.1 Beta` marker;
- the response body must identify the Fabric Mirror.

`.github/workflows/production-health-gate.yml` runs this contract hourly and on demand after merge.

## Security expectations

The production response should preserve browser-safe security controls including `nosniff`, HSTS, frame denial and restrictive permissions. Public health validation must never require private credentials, protected topology, owner memory, wallet material or internal repository enumeration.

## Provenance is a separate gate

A healthy URL does not prove that the served bytes came from the canonical reviewed GitHub commit.

Issue #106 remains open until an independent reviewer can reconstruct:

`canonical GitHub source -> reviewed artifact digest -> Vercel production deployment -> public alias`

The current production carrier may therefore be classified as **HEALTHY / PROVENANCE-PARTIAL**, not fully provenance-verified.

## Physical-client certification

Server-side HTTP checks do not replace logged-out physical testing on Android Chromium and mobile Safari. Those remain separate evidence gates.

## Product maturity

Whole-system maturity remains **8x8 OS 0.0.1 Beta**. Route availability, CI success or one completed release contract must not be promoted into a whole-system `100/100` claim.
