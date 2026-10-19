---
name: one-fabric-unified-navigation
description: Route people and authorized assistants to the correct existing 8x8 application surface, MCP tool family, public skill, and verification gate without duplicating tenant control planes or pretending integrations are live.
---
# ©️8x8 One Fabric · Unified Navigation

Canonical root: `fabric://8x8/core`. Public projection repository: `8x8org/8x8-user-edition`.

## Scope
Use the existing Atlas at `/atlas`, public catalog at `/atlas/one-fabric-public-catalog-v1.js`, and the established /studio, /agents, /world, /telegram and /projects screens. Never create a separate competing 8x8 root, standalone gateway authority, private credential store or duplicate app solely to expose an already-known capability.

## Agent process
1. Interpret the request as one or more product **modules** in the public catalog. Read the source registry. Resolve existing routes and available tools first.
2. Distinguish `SOURCE_PREVIEW`, `LOCAL_SOURCE_PREVIEW`, `SOURCE_SKILLS_AVAILABLE`, `OAUTH_AND_PUBLIC_RELEASE_PENDING`, `DEVICE_ACCEPTANCE_PENDING` and other states; all are **source classifications**, not production uptime attestations.
3. For browser/PWA/Android/Telegram, use the same public User Edition bundle and canonical navigation. Preserve tenant-scoped owner-private execution and the platform's trusted login/install flow.
4. For MCP, use the existing authorized One Fabric endpoint once resource metadata, issuer, audience, JWKS, consent, scopes, deployment and ChatGPT-client tool results are verified. A GitHub `mcp` directory or a ChatGPT plugin listing is not automatically an authenticated connection.
5. For skills, verify the source package, license, permissions, installation, user consent and actual invocation separately. Public skill definitions may help onboarding without implying installation.
6. For devices, reconcile each separately signed installed package and its data **before** uninstall or migration. Use a stably signed canonical app after device acceptance; do not uninstall to fix debug-signature conflicts.
7. Preserve STOP/PAUSE, fingerprint and provider security authorization. Agent votes cannot create OS privileges or substitute for signed owner consent. High-impact financial/publishing actions need their actual provider permissions.
8. Capture receipt: source identifier, tenant-safe capability name, action requested, agent/tool used, observed result, timestamp, test evidence and rollback. If capability cannot be used, say so and route to verified alternatives.
9. Share public user-facing navigation in Gate 3. Keep private accounts, API keys, precise device/runtime topology and owner evidence in tenant-protected stores.

## Continuous migration acceptance
One app package only **after** export/restore of unique content, side-by-side comparison of the four historical packages, version/signature continuity, actual Studio/Agent Room playback, bubble/voice checks, and owner-approved cleanup. Consolidating a UI does not require deleting specialized runtime services.

## Public status
This skill is a source definition, not a public ChatGPT-installed skill or evidence of a released all-in-one plugin.
