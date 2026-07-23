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

The `0.1.0-beta` cockpit is static and local-only. It has:

- no backend;
- no database;
- no environment variables;
- no analytics SDK;
- no wallet connection;
- no account system;
- no network API calls;
- no camera, microphone, location, payment, USB, serial or Bluetooth permission;
- no remote command path.

The deployment configuration denies framing, restricts content sources and disables sensitive browser permissions.

## Reporting a vulnerability

Do not publish secret values, wallet material, private messages, biometric data or private-system logs in a public issue.

Use GitHub's private vulnerability reporting feature for this repository when available. Reports should include:

- affected public path or revision;
- vulnerability class;
- reproduction steps using public-safe test data;
- expected and observed behavior;
- suggested remediation;
- whether the issue appears exploitable on the live public deployment.

Never include a real credential value. Report only the path, pattern class and remediation.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x beta | Yes |
| Pre-beta README-only shell | No |

## Security boundary

A paid subscription, future account, public node enrollment or public installer will not grant access to the private owner control plane. Public entitlement and private authority are separate systems.
