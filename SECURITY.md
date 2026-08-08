# Security Policy

## Scope

This repository is the public 8x8 User Edition shell. It must never contain or expose:

- owner credentials, API keys or authorization headers;
- wallet private material, seed phrases or signing authority;
- private repositories, messages, memory or agent context;
- private device topology, internal filesystem paths or raw logs;
- reusable privileged access to any device;
- arbitrary or remote shell execution;
- hidden camera, microphone, location or telemetry collection;
- automatic trading, mining, staking or asset movement.

## Current beta security posture

The canonical product version is **`0.0.1 Beta`**. The public cockpit is static/public-safe and has:

- no backend private-control bridge;
- no private database;
- no embedded environment secrets;
- no analytics SDK;
- no wallet connection;
- no public production account system;
- no private runtime API calls;
- no automatic camera, microphone, location, payment, USB, serial or Bluetooth permission;
- no remote command path.

The deployment configuration denies framing, restricts content sources and disables sensitive browser permissions.

## Three-Reality security boundary

- `PRIVATE_PAST` may contain private operational history, memory, receipts, topology and recovery material. It is not published here.
- `PUBLIC_PRESENT` contains only approved public-safe projection data.
- `FUTURE_LAB` contains research and unpromoted prototypes and must not be presented as production truth.
- `PROTECTED_BETA` is a promotion state, not permission to expose private data.

## Reporting a vulnerability

Do not publish secret values, wallet material, private messages, biometric data, protected repository inventory or private-system logs in a public issue.

GitHub's private vulnerability reporting is **not yet enabled** for this repository; enabling it is tracked in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md). Until it is enabled, open a GitHub issue that states only that you have a security report and how you can be reached, without vulnerability details, and a maintainer will arrange a private channel.

Reports should include the affected public path or revision, vulnerability class, public-safe reproduction steps, expected and observed behavior, suggested remediation, and whether the issue appears exploitable on the live public deployment. Never include a real credential value.

## Supported versions

| Version | Supported |
|---|---|
| 0.0.1 Beta | Yes |
| Historical pre-policy public beta labels | No; retained only as provenance where necessary |

## Security boundary

A paid subscription, future account, public node enrollment or public installer will not grant access to the private owner control plane. Public entitlement and private authority remain separate systems.
