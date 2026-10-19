# 8x8 public MCP and app bridge — release candidate (2026-10-19)

**Canonical authority:** `fabric://8x8/core`. **Public client:** `8x8org/8x8-user-edition`.

The hosted public MCP is owned by the separate existing private One Fabric codebase, not reimplemented in this public client. This repository must **not** contain private owner data, credentials, private agent topology or authority grants.

## Existing hosted service

- Public HTTPS origin: https://eightx8-one-fabric-public.onrender.com
- MCP endpoint: `/mcp`
- OAuth discovery: `/.well-known/oauth-protected-resource`
- Public brand asset path in reviewed source: `/assets/8x8-logo.png`
- Permission: `8x8.public.read`, separately issued by verified OAuth provider
- Tools in reviewed source: `one_fabric.capability_catalog`, `one_fabric.world_status`, `one_fabric.agent_catalog`, `one_fabric.studio_status`, `one_fabric.brand_preview`, `one_fabric.release_status`
- **Readiness:** hosted OAuth discovery and authenticated app image rendering NOT independently proven. The source-only PNG transport correction is not a live end-to-end receipt.

Do not provide a fabricated one-click Connect URL or bypass signature, audience, issuer, scope or tenant checks. The ChatGPT app connection requires verified issuer, audience, JWKS and resource configuration, provider consent, and tenant-isolated client testing.

## User Edition local Studio bridge

- Preview URI once deployed: `/studio` (same origin; Web/PWA, Telegram iframe and Android web carrier)
- Local-only assets; no public model or upload permission is implied.
- Ordinary Windows, Linux, macOS and iOS browsers may use the public web/PWA routes subject to actual browser support. A PWA is **not** proof of a signed native Windows/Linux/iOS installer.
- For the public video/audio flow, a browser media player and a single video-frame export are source features; long-form audiovisual AI analysis needs separate authorized compute and model adapters.
- Public skills **source**: `skills/one-fabric-public-media-review/SKILL.md`. Repository presence does not install it in ChatGPT.

## Image blank-triage (separate tests)

1. Static user-app icon: verify `/icon.svg` returns a real SVG image, not HTML or HTTP 404; Vercel build must include it.
2. MCP-hosted PNG: test HTTP 200, `image/png`, valid PNG signature, byte SHA-256, no text decoding, access control and cache restrictions.
3. MCP `one_fabric.brand_preview`: independently test authorized `tools/call`, an MCP `image` block with base64 bytes, and real ChatGPT Android visual rendering.
4. If OAuth discovery returns 503, mark hosted tool blocked regardless of successful static image HTTP delivery.

## Promotion rule

SOURCE_COMMITTED ≠ CI_TESTED ≠ DEPLOYED ≠ AUTHENTICATED ≠ INSTALLED ≠ VERIFIED. Preserve development branch, source hashes, release checks and rollback references. No forced prod deployment or public directory listing should precede complete gates.
