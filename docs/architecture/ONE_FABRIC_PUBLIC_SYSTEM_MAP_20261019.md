# 8x8 One Fabric — public system map (2026-10-19)

**Canonical root:** `fabric://8x8/core`. **Canonical public client:** `8x8org/8x8-user-edition`. **Status:** interface specification, not deployed production.

## Three gates, one application

1. **Gate 1** public discovery → web/PWA, Android, Telegram Mini App, mobile and desktop entry points.
2. **Gate 2** explicit tenant/account identity, OAuth, entitlement, privacy, device leases and permissions. User-facing controls do not confer privileged agent authority.
3. **Gate 3** 8x8 World and Mission Cinema with these modules: Agents & Voice, Studio & Publishing, Research & Science, Trading & Markets, Wallet & NFTs, Books & Education, Planet Earth, Games & Radio & TV, Partners & Ventures, MCP & Skills & Models, Devices, Memory & Evidence, and Security & Operations.

All screens should use consistent route names, tenant context, clear evidence states, activity receipts, permissions and rollback. Unknown and proposed capabilities must never be displayed as authenticated or working.

## UI and release acceptance

| Screen | User surface | Gate |
|---|---|---|
| World | 8x8 home, missions and spatial navigation | Real hosted route and tenant separation |
| Agent Room | Character concepts, opt-in voice, messages | Real model/A2A replies authenticated separately |
| Studio | Image/audio/video inspection and creation | Actual media bytes, local/privacy constraints |
| Research | Sources, rights, repository candidates, findings | Provenance and licensing |
| Tools & models | Unified public tools, skills, MCP and model inventory | Provider grants, scope, latency and health |
| Trading & wallet | Charts, account reads and strategies | Strictly separate genuine funded action authority |
| Publishing | Asset review and per-account destinations | Platform permissions and delivery receipts |
| Device & App | Android, PWA, Telegram, iOS/Windows/Linux | App signing, stable version, migration and rollback |
| Mission Control | Five original scheduled lanes | Independent successful run receipts |

## Release / consolidation

- Keep **one user-facing brand, one authoritative public interface and one governed capability directory**, while retaining independent service processes where isolation and scaling require them.
- Use the existing historical source and public repository as donor and client, respectively. Do not put protected owner topology, tokens or privileged execution code in this public repository.
- **Deploy and verify** `/agents`, `/studio`, `/world`, correct icon MIME, static bundle, ChatGPT OAuth and media blocks before claiming live features.
- To reach one installed Android 8x8 application: establish a stable signing key, confirm backup/restore of each old app's data, verify package identity and native functionality, then retire duplicates in an explicitly recorded migration.
- A ChatGPT plugin publication/install card cannot be forced from source commits. The public MCP must pass genuine authentication and distribution acceptance.
- Preserve STOP/PAUSE, account-specific publishing/trading approval, tenant isolation, immutable receipts and no-loss rollback.

**Provenance:** Based on October 19 repository and deployment preflight; this file is a design contract, not production deployment evidence.
