# 8x8 User Edition — version and release evidence reconciliation

**Source review checkpoint:** November 22, 2026. **Classification:** public-safe documentation reconciliation; this is neither a release promotion nor certification that the entire 8x8 One Fabric is complete.

Canonical root: `fabric://8x8/core`. Owner: FlashTM8, sole OWNER_ROOT. This public repository is a bounded user-facing projection; it is not the owner-private operating authority.

## Why several versions appear in the same repository

These labels belong to **different release/implementation scopes** and must not be presented as one universally deployed version.

| Source | Exact label | What the source actually establishes | Not established |
|---|---|---|---|
| [README.md](../README.md) | `0.0.1 Beta` | Public product/beta maturity label and historical public-carrier documentation | Whole-system maturity, current V50 production provenance or automatic user enrollment |
| [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md) and [stable/release-unit.json](../stable/release-unit.json) | `0.1.0 Stable` / `PUBLIC_WEB_CLIENT` | **Scoped web-client implementation/release contract**; release-unit acceptance explicitly says `TARGET_UNTIL_EXACT_HEAD_GATES_PASS` | The entire 8x8 OS is stable; production acceptance is already earned |
| [VERSION.md](../VERSION.md) / [RELEASE_NOTES_0.2.0.md](../RELEASE_NOTES_0.2.0.md) | `0.2.0 Stable · V50` | Versioned V50 source and multi-carrier release-generation claim; `VERSION.md` itself requires exact deployment, bot-binding and Android artifact readbacks | Current production web revision, public-signed APK, Telegram/Discord binding, complete native owner runtime |
| [vercel.json](../vercel.json) and [package.json](../package.json) | `USER_EDITION_THREE_GATE_EXPERIENCE_V55` header, `0.2.0` package value | Configuration/source-generation metadata | Authoritative product version or proof of a live carrier |

**Version decision rule:** retain `0.0.1 Beta` as the conservative public product maturity statement until a separately verified exact-release transition is approved; identify `0.1.0` solely by its `PUBLIC_WEB_CLIENT` scope and `0.2.0 V50` solely by recorded source/release-carrier evidence. Do not automatically replace the README badge with `0.2.0 Stable`.

## Provider evidence and deployment separation

The public carrier is `https://8x8-os-ecosystem.vercel.app`, whose project name is historical. The November 22, 2026 Vercel connector check found the last **production-targeted READY** deployment from October 4, 2026, source repo `horbolsi/8x8-OS-Ecosystem`, commit `2eed927f233e45b88569affeadc45ff8c4c79f32`. Newer review/preview deployments were **not** production-targeted. That readback does not establish that current production executes this repository's `0.1.0` or V50/V55 source. A fresh HTTP route test and deployment-to-source attestation are still required.

The README's earlier server-route receipt should be treated as a **dated historical acceptance artifact**, not a substitute for a new exact revision/current browser acceptance.

## Release publisher hazard and merge dependency

The existing default-branch [publish-v50-release.yml](../.github/workflows/publish-v50-release.yml) publishes on pushes to `main` touching:

- `VERSION.md`
- `RELEASE_NOTES_0.2.0.md`
- `v50.html`
- `android-app/**`
- `.github/workflows/publish-v50-release.yml`

Its current historical workflow grants `contents: write` and can execute `gh release upload v0.2.0 ... --clobber` or create a release. **No publisher-triggered path is modified in this documentation review**. The original release tag/assets must be independently preserved and byte-verified before any authorized transition that might affect them.

- [Draft PR #206](https://github.com/8x8org/8x8-user-edition/pull/206): proposal to freeze the old publisher to read-only audit. At head `d3192fc8fcefa611e9dfa5d6bd25e22c6018bfeb`, 2 hosted checks passed and 2 failed; not merged.
- [Draft PR #207](https://github.com/8x8org/8x8-user-edition/pull/207): public boundary + V50 build/test remediation. At head `7c58ad8dcffc3cf9cd54b17c9a7d637b7bd922dc`, 4 checked workflows succeeded, but **it changes `v50.html`**, which remains an old publisher trigger. Not merged.
- **Do not merge #207 while the old publisher remains capable of modifying historical release assets.** Any release transition must require current head/checks, verified no in-flight publisher jobs, preserved release hashes, owner authorization and provider readback. The provider's branch/permission rules remain separately enforceable.

## Security and externally visible claims

- No raw owner-private topology, credentials, customer information, wallet/signing material or internal agent identities in public docs or source projections.
- `SOURCE_PRESENT ≠ DEPLOYED ≠ BROWSER_ACCEPTED ≠ CLIENT_BOUND ≠ INSTALLED ≠ PRODUCTIVE ≠ VERIFIED`.
- No whole-Fabric `100/100`, current `0.2.0 Stable` production promotion, signed app release, authenticated tenant user account, active live trading, payments, token transfer or native device control without direct independent acceptance receipts.
- Keep the August 2026 [public-state checkpoint](https://github.com/8x8org/.github/blob/main/CURRENT_PUBLIC_STATE.md) as historical provenance; its date is not a November 2026 current deployment readback.

## Bounded next checks

1. Independently inventory source/release tags and all protected V50 asset bytes, metadata and SHA-256 receipts without altering them.
2. Audit the active publisher's exact GitHub workflow, open/in-flight jobs and permissions; obtain owner review for a reversible freeze or provider disable; do not bypass failed CI.
3. Rerun #206 exact-head policy/CI gates and verify the freeze effect only after separately authorized merge.
4. Rebase/test #207 only after release overwrite risk is removed; validate the public boundary, stable build routing, accessibility, browser behavior and rollback.
5. Prove deployment source SHA → build/artifact hash → public carrier routes and headers → physical browser/mobile verification before any version/maturity upgrade.
6. Reconcile the public README/implementation/version documents on a fresh signed acceptance receipt; preserve this page as a dated source audit, not a live status dashboard.

**State:** `PAST_PRESERVED` historical labels/releases; `PRESENT_PROVEN` dated source contents and exact-head checks; `FUTURE_GATED` publisher freeze, current production parity, version promotion and full 8x8 runtime. **Rollback:** close this documentation-only draft; all original release tags/assets and default-branch files remain intact.
