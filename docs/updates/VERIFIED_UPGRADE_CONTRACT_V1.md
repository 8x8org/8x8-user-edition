# 8x8 User Edition — Verified Upgrade Contract v1

**Canonical capability root:** `fabric://8x8/core`

## Operational rule

An agent, a user or a scheduled check may **propose** an update. A trusted release verifier independently validates the target before the operating system's own installation or store flow is invoked. Updates do not confer extra privileges, unlock devices or override PAUSE/STOP.

### Android app

- Current release-candidate preview has a distinct package identity `world.eightx8.user.preview`, preserving an already-installed `world.eightx8.user.dev` package and its data.
- The native **8x8 Updates** button is user initiated. It contacts only the HTTPS origin in `BuildConfig.HOME_URL` at `/updates/android/latest.json`.
- A release manifest has schema `eightx8.android.update.v1`. Only `available:true` with a newer `versionCode`, the **same** installed `packageId`, an exact SHA-256 hash, the same installed signing certificate SHA-256 and a package path below `/updates/android/` may be considered.
- The complete APK is downloaded with bounded size, without redirects or cross-origin URLs. The native preflight checks downloaded bytes and installed/archive package/signing identities again before offering an Android installer handoff.
- A one-file, read-only, non-exported content provider grants temporary URI read capability only for the staged verified APK. Android must approve installation; no silent PackageManager bypass, uninstall or data erasure is attempted.
- If no release is promoted, or the signature or package version differs, update fails closed. This is the state of `updates/android/latest.json` in this branch.
- Signing continuity requires an owner-controlled **stable signing key**, retained in a protected signing service or release environment. GitHub Actions debug signing changes between builds and **cannot** support in-place upgrades. Debug/preview builds are not production releases.
- The app must be tested physically: preview install and launch, the update menu, missing-manifest UI, mismatch refusal, accepted signed same-identity update, Android installation confirmation, app-data preservation, and rollback or recovery.

### Web/PWA

Web assets may be refreshed by a versioned same-origin service worker. They are not a substitute for updating Android native code. Browser tabs and downloaded files remain inside ordinary browser sandbox limits.

### Other platforms

- iOS: approved Apple signing and OS/TestFlight/App Store consent flows.
- Windows: signed MSIX/App Installer or an equivalently trusted package channel.
- Linux: signed repository/package manifests with transactional rollout and rollback.
- Telegram Mini App: versioned HTTPS deployment and actual Telegram-client acceptance.
- ChatGPT MCP and skills: explicit publication, tenant-scoped OAuth, verified tool schemas and client interoperability are separate from installing an Android APK.

### Agent-oriented release workflow

Discover eligible updates → compare installed and candidate metadata → run compile/tests/security review → verify signer/provenance and immutable hashes → prepare a scoped update request → ask for required Android/OS approval → verify installed version/data and record an auditable result.

An agent can retry a network failure, choose a safe equivalent source, or defer a task. Council consensus cannot invent OS permissions, credentials or new financial/public-publishing authority.

## Release states

Source implemented on draft PR #201, with CI builds and source regression tests. This is **not** a claim of auto-deployment, store review, official stable signing, physical Android installation, full live agent integration, or public plugin availability.
