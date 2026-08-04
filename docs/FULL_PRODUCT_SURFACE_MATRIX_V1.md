# 8x8 Full Product Surface Matrix V1

Status: **ROADMAP AND EVIDENCE MAP — NOT A CLAIM THAT EVERY SURFACE IS LIVE**

This document prevents the public product from being reduced to a single web dashboard while older mobile, CLI, Telegram, connector, VR and device-system work disappears into unrelated repositories.

## Product classes

| Product class | Audience | Authority |
|---|---|---|
| Private Owner Product | FlashTM8 and explicitly trusted operator agents | Owner-gated private control |
| Public User Product | External users, developers and creators | Least-authority public access |
| Simulation Product | Agents, maps, worlds and digital twins | Synthetic or redacted inputs only |
| Developer Product | CLI, SDK, API, MCP and connector clients | Scoped tokens and deterministic receipts |

## Shared commercial intent

- Trial: 88 minutes, exactly 5,280 server-metered seconds.
- Intended paid price: USD 8.88.
- Billing cadence: unresolved owner decision.
- Payment and entitlement contracts: `8x8org/8x8-protocol` MSG213 draft.
- No production billing, wallet signing or live payment is claimed here.

## Surface matrix

| Surface | Intended role | Existing evidence | Current truth | Next evidence gate |
|---|---|---|---|---|
| Private Sovereign Command Deck | Owner command, agents, missions, approvals, evidence, systems, connectors, Studio, markets, memory, repositories, security and worlds | `horbolsi/8x8-os-june2026` draft PR #14 | Source implemented, not merged or activated | security, mobile, parity and local canary receipts |
| Public Spatial Cockpit | Public-safe product, agent constellation, maps, worlds, tools and receipts | `horbolsi/8x8-OS-Ecosystem@beta/8x8-dual-monitor-v0.1`, Vercel previews | Preview evidence, production unverified | current CI, privacy, accessibility, mobile and release identity |
| Public Web/PWA | Browser product with offline and installable behavior | public cockpit, legacy public-app and hub sources | Multiple partial implementations | convergence branch and PWA canary |
| Android app | Native or wrapped public/private mobile surface | Android Termux runtime and prior mobile plans | Architecture and runtime evidence, product app unverified | platform decision, build, emulator/device canary |
| iOS app | Public user and owner companion | prior owner plans and cross-platform requirements | Design requirement, source not yet canonical | platform decision, simulator build and review |
| CLI | Stable terminal access from supported shells | launcher, command, relay and control-fabric sources | Multiple launchers and aliases exist | command inventory, supersession, conformance and rollback |
| SDK | Typed developer integration | protocol and product repositories | Planned | language priorities, generated clients and conformance tests |
| MCP connector | Tool-based app integration | connector registry and MCP research | Design and partial tooling evidence | least-authority server canary and tool tests |
| ChatGPT app connector | 8x8 inside compatible assistant clients | connected-source architecture and Apps requirements | Design target | official app contract, auth and review canary |
| Telegram Mini App | Mobile social product and owner/public entry point | `horbolsi/8x8/miniapp`, public-app and bot sources | Source present; deployment and security unresolved | current code audit, auth boundary and private preview |
| Telegram bots | Owner, public and specialist communication | multiple bot and service records | Mixed live, disabled, legacy and unknown states | exact receiver ownership and service receipts |
| VR environment | Immersive Art Board 360 and agent-world interface | Art Board 360 and world designs | Design only | engine choice and synthetic canary |
| GeoLibre map | Spatial nodes, agents, routes, incidents and environments | MSG212/MSG214 design program | Adapter not yet proven | local synthetic map canary |
| Unreal bridge | High-fidelity simulation and digital twins | MSG212/MSG214 design program | External-node mock target | mock protocol, then compatible GPU-node canary |
| Lemonade/Roblox world | Rapid playable prototypes and social experiments | MSG212/MSG214 research program | Account-gated design target | dedicated test account and disposable private canary |
| Vectras node | Emulated or external device environment | prior system plans and user directive | Evidence to reconcile | node inventory, isolation and emulator-only canary |
| 8x8 ROM | Device-level 8x8 environment | prior roadmap and user directive | Architecture target, not a shipped ROM | threat model, hardware support matrix and emulator-first build |
| Browser extension/embedded widget | Contextual 8x8 access in third-party surfaces | connector and UI research | Unresolved | need and permission review |
| Replit app | Detached or legacy web implementation | connected app `8x8` | Read-only, unaudited | focused discovery and selective port plan |

## Shared capabilities

Every supported surface should consume the same public contracts for:

- identity and authentication;
- entitlement and usage;
- tasks and receipts;
- agents and symbolic bodies;
- worlds, maps and simulations;
- artifacts and provenance;
- connectors and scopes;
- payment intents and payment status;
- status, errors, offline mode and rollback.

Private-only contracts must never be projected into public clients.

## Canonical command direction

The CLI and launchers should converge toward one namespace while retaining temporary compatibility aliases:

```text
8x8 status
8x8 doctor
8x8 agents
8x8 tasks
8x8 receipts
8x8 worlds
8x8 maps
8x8 simulations
8x8 studio
8x8 content
8x8 trading paper
8x8 trial
8x8 plans
8x8 usage
8x8 payments
8x8 connectors
8x8 update
8x8 self-test
```

Commands that can mutate services, repositories, credentials, wallets, payments or deployments remain separately gated.

## Agent bodies

Agent bodies are symbolic operational representations tied to canonical agent IDs, roles, capabilities, health, work, receipts, environments and authority.

They are not claims of consciousness, humanity, legal personhood or independent wallet ownership.

## Release truth

A surface may use only one of these states:

- `DESIGN_ONLY`
- `SOURCE_PRESENT`
- `LOCAL_CANARY`
- `PREVIEW_DEPLOYED`
- `PRIVATE_BETA`
- `PUBLIC_BETA`
- `PRODUCTION_BLOCKED`
- `PRODUCTION_APPROVED`

No marketing page may call a design or source-present surface live.

## Program authority

The complete convergence program is MSG214 in `horbolsi/8x8-os-june2026`.

Production merge, deployment, payment activation, wallet action, public publication, service restart, database mutation and destructive cleanup remain exact-gated.