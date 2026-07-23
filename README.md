# 8x8 User Edition

> **Pre-release public shell. No installer or live subscription is available yet.**

8x8 User Edition is the planned minimal public client for user-owned, isolated 8x8 workspaces.

## Intended public package

The released repository may contain only:

- signed installer and complete uninstaller;
- public permission center;
- isolated task runner;
- public schemas and receipt verifier;
- user-owned account and device enrollment flows;
- examples, tests, SBOMs, signatures, and build provenance.

It must not contain owner credentials, private control-plane code, private agents, private memory, private messages, owner wallets, signing keys, raw telemetry, or reusable privileged access to any owner device.

## Permission model

Installation is separate from every later permission:

`installation ≠ node enrollment ≠ compute consent ≠ storage consent ≠ telemetry consent ≠ remote-support consent ≠ rewards consent`

All optional device contribution is disabled by default and must be visible, limited, revocable, and receipted.

## Product targets

- Target monthly subscription: **USD 8.88**
- Target daily free allowance: **88 auditable service minutes**
- Billing status: **not live**
- Public release status: **DESIGNED**

No guaranteed profit, rewards, APY, token value, zero gas, or zero latency is promised.

## Security

Do not submit credentials, wallet keys, private messages, biometric templates, or private-system logs to public issues.
