# Install / First Blink — 8x8 User Edition

Canonical root: `fabric://8x8/core`

This repository is the **public, tenant-safe User Edition**. It does not contain or inherit FlashTM8 OWNER_ROOT authority, owner credentials, owner-private device control, private App Twins, private memory, or wallet/signing authority.

## Option A — Run the public User Edition in Termux now

These commands clone the public source and serve it locally. They do **not** grant ADB/device-control authority and do not install a privileged Android package.

```bash
pkg update
pkg install -y git python
git clone --depth 1 https://github.com/8x8org/8x8-user-edition.git
cd 8x8-user-edition
python -m http.server 8080 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8080/
```

To update later:

```bash
cd ~/8x8-user-edition
git pull --ff-only
```

Truth boundary: cloning/running the static carrier proves only that the public source is locally served. It does not prove authenticated backend access, subscription entitlement, connectors, device enrollment, APK installation, or private One-Fabric runtime access.

## Option B — Android APK

The repository contains Android source plus workflows capable of producing:

- a **development debug-signed APK** for testing;
- a **release-unsigned APK** for release-candidate verification.

A production-signed APK is **not** treated as released until all of these are present together:

1. exact version/release ID;
2. immutable release asset URL;
3. SHA-256 checksum;
4. signing-certificate SHA-256;
5. source commit;
6. build/workflow receipt;
7. install/launch receipt;
8. public release state explicitly promoted.

Current state: `APK_RELEASE_REQUIRES_ARTIFACT_AND_SIGNING_READBACK`.

Do not copy an APK from chat, random mirrors, shared storage, or an unverified URL. Do not use `curl | sh`.

## Device enrollment

Public-user device control follows a separate consent and capability flow:

```text
8x8 ID
→ isolated tenant
→ user Vault
→ device registration
→ device attestation
→ explicit capability grants
→ short leases
→ action
→ before/after verification
→ receipt
```

Capabilities are separate. For example, screen viewing does not imply input control; input control does not imply shell access; shell access does not imply wallet/signing authority.

ADB/Wireless Debugging must never be silently enabled. The user must enable developer options/wireless debugging and accept pairing where that route is used.

## Authentication / credential reuse

The target product minimizes repeated human work without teaching agents raw secrets.

Preferred order:

1. provider OAuth/passkey/session;
2. OS or hardware-backed credential manager/keystore;
3. opaque Vault handle/capability;
4. local step-up authentication when required;
5. continue from a scoped/revocable success receipt.

Agents must not learn, log, store, replay, or expose raw passwords, OTP/TOTP seeds, biometric templates, recovery codes, private keys, or reusable secrets.

A fingerprint/Face/PIN confirmation occurs locally through the OS/provider. The agent receives only the result/capability needed to continue.

## Three gates

```text
Gate 1 — Discover / First Blink
Gate 2 — 8x8 ID + tenant + authority + optional subscription/connections
Gate 3 — personal 8x8 World
```

Each user gets an isolated World. Shared software never means shared OWNER_ROOT authority.

## Troubleshooting

If the local web carrier does not load:

```bash
pwd
git status --short
python --version
ss -ltn 2>/dev/null | grep 8080 || true
```

If port 8080 is already occupied, choose another local port, for example:

```bash
python -m http.server 8888 --bind 127.0.0.1
```

This is a local web port only; it does not claim the historical/private 8x8 runtime role of any other port.

## Security

Report security issues using [SECURITY.md](SECURITY.md). Never post credentials, recovery material, biometric data, private repository information, private device inventories, or private runtime logs in public issues.
