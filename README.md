# 8x8 User Edition

> **Public beta 0.1 release candidate. Static cockpit only. No installer, private-control access or live subscription is available yet.**

8x8 User Edition is the minimal public client for user-owned, isolated 8x8 workspaces. The first beta is a fast visual cockpit that explains the operating model, agent roles, evidence ladder, roadmap and permission boundary without exposing the private owner system.

## Run locally

No package installation is required.

```bash
git clone https://github.com/8x8org/8x8-user-edition.git
cd 8x8-user-edition
python3 -m http.server 8080
```

Then open the local address the server prints (port 8080) in your browser.

## Public demo vs. private owner system

This is the **public demo repository** of 8x8 OS. It contains the isolated static cockpit and public-safe documentation only. The private owner control plane, agents, memory, messages, credentials, wallets and device authority are excluded — no code path, connector or configuration in this repository can reach them.

Nothing in this repository is evidence that a private runtime, productive agent or production service exists or performs as depicted. Capability claims are tracked separately in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) using the nine-stage evidence ladder described in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## OpenAI Build Week judges

This project was submitted to OpenAI Build Week on Devpost as **“8x8 OS: Human-Controlled AI & Web3 Operating System.”**

- This repository is the **public-safe demo**: a static, local-only cockpit with no backend. Judge it as a demonstration of the operating model, truth ladder and permission boundary — not as the full system.
- The complete private system is **not published**. Judge access to the private canonical source can be arranged on request through the submission’s contact channel.
- Every capability shown in the cockpit is labeled with its evidence state in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md); nothing labeled below `IMPLEMENTED` should be treated as existing software.

## Beta contents

- responsive spatial cockpit;
- public agent-archetype explorer;
- conceptual world interface with tracking disabled;
- nine-stage claim-to-adoption truth model;
- public/private security boundary;
- evidence-gated roadmap;
- installable progressive web app shell;
- machine-readable public state;
- static deployment security headers;
- GitHub Actions validation.

## Explicit beta limits

The beta has no backend, account database, credentials, wallet connection, private memory, private messages, private agents, terminal executor, live trading, mining, rewards, hidden telemetry or device administration.

Buttons change the local interface only. They do not execute an external action.

## Intended public package

Later releases may contain only:

- signed installer and complete uninstaller;
- public permission center;
- isolated task runner;
- public schemas and receipt verifier;
- user-owned account and device enrollment flows;
- examples, tests, SBOMs, signatures and build provenance.

They must not contain owner credentials, private control-plane code, private agents, private memory, private messages, owner wallets, signing keys, raw telemetry or reusable privileged access to an owner device.

## Permission model

Installation is separate from every later permission:

`installation ≠ node enrollment ≠ compute consent ≠ storage consent ≠ telemetry consent ≠ remote-support consent ≠ rewards consent`

All optional device contribution is disabled by default and must be visible, limited, revocable and receipted.

## Product targets

- Target monthly subscription: **USD 8.88**
- Target daily free allowance: **88 auditable service minutes**
- Billing status: **not live**
- Beta source status: **IMPLEMENTED**
- Live deployment status: see [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md)

No guaranteed profit, rewards, APY, token value, zero gas or zero latency is promised.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Machine-readable public state](state/public-state.json)

## Organization

| Repository | Purpose |
|---|---|
| [8x8org/8x8-user-edition](https://github.com/8x8org/8x8-user-edition) | This public demo cockpit |
| [8x8org/8x8-protocol](https://github.com/8x8org/8x8-protocol) | Public protocol repository |
| [8x8org/.github](https://github.com/8x8org/.github) | Organization profile |

The permanent public website is **pending deployment**. No official social-media profile links are published here yet; treat any account claiming to be official as unverified until it is linked from this organization.

## License status

This repository currently has **no license**. Until the owner selects and publishes one, default copyright applies: you may view and fork on GitHub, but no other reuse rights are granted. A license decision is pending and tracked as an explicit release blocker.

## Security

Do not submit credentials, wallet keys, private messages, biometric templates or private-system logs to public issues. See [SECURITY.md](SECURITY.md) for the reporting route and the full public/private boundary.
