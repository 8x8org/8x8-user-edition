---
name: one-fabric-verified-upgrade
description: Inspect available 8x8 User Edition releases, propose safe versioned upgrades, and request operating-system installation approval without uninstalling existing applications or bypassing STOP/PAUSE.
---
# ©️8x8 One Fabric · Verified Upgrade

Canonical capability root: `fabric://8x8/core`.

## Trigger

A user or another authorized agent requests: “update yourself,” “upgrade 8x8,” “check release,” “update app/APK/skill/MCP,” or “keep 8x8 current.”

## Agent procedure

1. Identify exactly which surface is being upgraded: Android package, public web/PWA, Telegram Mini App, MCP deployment, skill, or an OS-specific client. Do not mistake a static web deployment for a native APK update.
2. Discover the **existing** 8x8 package, installation identity, signing fingerprint, source repo branch, canonical deployment environment, version and STOP/PAUSE state. Use read-only inspection first.
3. Read the authenticated release index appropriate to that surface. A locally saved build, draft PR, signed ZIP, or available download is **not** an automatically approved release. Do not invent update URLs.
4. For Android, the application's update center reads the same-origin `/updates/android/latest.json` manifest. It must prove `schema`, `available:true`, matching package ID, newer versionCode, bounded HTTPS same-origin artifact, SHA-256 checksum, matching installed/archive signer SHA-256, and successful installation acceptance on a real device.
5. If signatures differ, **do not uninstall the old app**. Offer an independently identified side-by-side preview package while preserving the installed app/data; its debug signing does **not** provide long-term upgrade continuity.
6. Build and test candidates in isolation, record commit SHA, package identity, signer, artifact SHA, real CI results and rollback plan. Promote only through actual owner/provider review gates.
7. An agent may automatically perform routine read-only checks, stage a hash-verified candidate and prepare a voice/bubble update request. Opening a device installer, granting unknown-app install permission, granting biometric access and installing into a user account remain OS-owned actions with explicit authorization.
8. Resume only if the owner-paired control reports RESUMED; never treat nonresponse as consent. Do not remove PAUSE/STOP. Do not assume another agent's vote adds missing operating-system authority.
9. After installation, independently verify package version, signing identity, app data continuity, actual UI launch, server routes and media playback. Reconcile the post-install receipt with the release candidate.
10. For web/PWA, let the same-origin versioned service worker refresh eligible public assets while avoiding private/API/OAuth caching. For iOS, Windows and Linux, use each platform's legitimate signed update/store flow.
11. A public skill definition is source, not automatically installed in ChatGPT. A public MCP must independently pass OAuth, tenant authorization, release and client-discovery gates before claiming ChatGPT tool access.

## State of this release candidate

The Android `/updates/android/latest.json` seed is fail-closed (`available:false`); it deliberately does not promote any APK. Release candidate v0.2.1 has development builds; the separately named preview package `world.eightx8.user.preview` avoids the conflict with `world.eightx8.user.dev`. A stable signing key and a verified hosted release are required before the Android in-place self-update feature can operate end to end.
