# ©️8x8 One Fabric — All-in-One Consolidation Contract v1

**Canonical root:** `fabric://8x8/core`  
**Public projection:** `8x8org/8x8-user-edition`  
**Target:** one navigable app experience and one authenticated 8x8 MCP gateway; specialized backends and historical repositories remain separately versioned.

## What is actually integrated in the public source

- Existing V50 Web/PWA/Android asset bundle.
- The `/atlas` single searchable directory now routes to `/`, `/world`, `/studio`, `/agents`, `/telegram`, `/android`, `/projects`, and the existing presale source.
- `atlas/one-fabric-public-catalog-v1.js` is the single typed public projection of capability families, route source status and skill source definitions. Nothing there claims a live trading account, A2A session, MCP plugin authorization or provider publishing grant.
- Existing `one-fabric-public-media-review` and `one-fabric-verified-upgrade` skill sources are retained. The additive `one-fabric-unified-navigation` skill is public source only.
- The Android offline carrier builds its web assets from the same static `dist` and asset-loader origin; this is not an in-place migration of separate Android applications.

## Convergence requirements

| Surface | Canonical decision | Evidence gate |
|---|---|---|
| Android | One future stably signed One Fabric ID, not a blind uninstall of older development IDs | Installed package backup, signing, unique state, feature parity, owner-approved migration, on-device launch |
| Web/PWA | One approved User Edition web destination with true source routes | Deploy identity, /atlas, /studio, /agents distinct content, image MIME, frontend tests |
| Telegram | Same user-facing Gate 3 modules with Telegram's approved authentication flow | Real Telegram init data verification, tenant binding, launch receipts |
| ChatGPT MCP | One public tenant-scoped API gateway to 8x8 tools, not a mirrored owner control plane | OAuth discovery, verifier/JWKS, scoped tool calls, hosted image render, directory eligibility |
| Skills | One discoverable index federating public-source and owner-authorized skills | Package contents, installed/authenticated/runtime distinction, rights and execution receipts |
| Voice/A2A | Signed, attributed model and agent responses | Actual round-trip utterance transcript, speaker identity, STOP and offline fallback |
| Data/services | Reuse existing authorized private databases, cloud services and connectors behind Gate 2 | Stable identifiers, roles, external grants, backups and rollback |

## Device migration: no data loss by assumption

Earlier apps can contain different logins, databases, files, feature sets and signing identities. A successful development APK compilation is not evidence that the four packages share data or can be uninstalled. Inspect each package's exported, owner-authorized data and signing identity. Build a written gap matrix, then ask Android to uninstall only after migration acceptance.

## Cross-domain scope

Gate 3 capability families must not silently omit Studio, agents, models, A2A, trading, social, wallets, digital assets, research, education, books, science, climate, games, radio, streaming, commerce, developer tools, connected apps, devices, maps, and accessibility. **In-scope** is not equivalent to **operational**.

## Acceptance test contract

1. Unit-tests assert the unique public catalog, non-sensitive routes, honest capability states and skill source integrity.
2. Browser tests load the real Atlas and prove search/filter, route navigation and no invented action.
3. Android build includes `atlas/index.html`, `atlas/one-fabric-public-catalog-v1.js`, `studio/index.html`, `agents/index.html`; verify actual APK entries.
4. Stage external deployment, test website on independent device, then authorized production promotion.
5. Roll back individual versioned components and keep old user content intact until explicit deletion approval.

Current state: design/source consolidation only. This document is not proof of a single installed app, a public ChatGPT plugin, a complete data migration or fully autonomous agents.
