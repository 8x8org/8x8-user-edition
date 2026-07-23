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

Open `http://127.0.0.1:8080`.

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
- [Machine-readable public state](state/public-state.json)

## Security

Do not submit credentials, wallet keys, private messages, biometric templates or private-system logs to public issues.
