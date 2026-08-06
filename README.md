# 8x8 User Edition

> **8x8 OS 0.0.1 Beta. Public-safe static cockpit only. No installer, private-control access, live subscription, or whole-system completion claim is available.**

8x8 User Edition is the minimal public client for user-owned, isolated 8x8 workspaces. It explains the operating model, agent roles, evidence ladder, Three-Reality architecture, roadmap, and permission boundary without exposing the private owner system.

## Canonical maturity

The entire 8x8 product remains **`0.0.1 Beta`** until an explicit, evidence-backed, owner-approved system-wide promotion occurs.

Historical mission IDs, document revisions, protocol generations, service names, and internal implementation labels remain provenance metadata. They do not change the product maturity version and must not be mistaken for stable or whole-system completion.

## Three-Reality model

Past, Present, and Future are executable system realities rather than branding language:

- **`PRIVATE_PAST`** contains private operational history, evidence, memory, superseded work, recovery truth, and the owner runtime.
- **`PUBLIC_PRESENT`** contains only the current privacy-safe, evidence-backed public 0.0.1 Beta projection.
- **`FUTURE_LAB`** contains research, candidates, designs, simulations, and unpromoted prototypes.
- **`PROTECTED_BETA`** is a reversible promotion state between Future Lab and Public Present, not a fourth reality.

A screenshot, roadmap, issue, branch, commit, or interface element does not promote a capability into Public Present. Promotion requires evidence, review, rollback, and explicit authorization.

## ❤️ Sponsor 8x8

[**Sponsor 8x8 on GitHub → github.com/sponsors/8x8org**](https://github.com/sponsors/8x8org)

Sponsorship supports the **public** project only: documentation, testing, security hardening, accessibility, developer tooling, community maintenance, and bounded infrastructure costs. It is **support, not an investment**: no financial returns, tokens, equity, guaranteed features, private/customer data, or private-repository access. See the organization [governance](https://github.com/8x8org/.github/blob/main/GOVERNANCE.md).

## 🛠️ Contribute

Contributions of code, tests, docs, accessibility, and security review are welcome. No special access is required.

- Read the [Contributing guide](https://github.com/8x8org/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/8x8org/.github/blob/main/CODE_OF_CONDUCT.md).
- Pick up an issue labeled [`good first issue`](https://github.com/8x8org/8x8-user-edition/labels/good%20first%20issue) or [`help wanted`](https://github.com/8x8org/8x8-user-edition/labels/help%20wanted).
- For substantial changes, open an issue first so a maintainer can agree on the approach.

**Contributor recognition:** every merged contributor appears in the repository's contributors graph and is credited in release notes. Optional public name/logo recognition is available to sponsors. Recognition is acknowledgment only. It grants no private-system access and no payment is offered.

## Project maturity

**Public beta `0.0.1` — early, incomplete, and evidence-gated.** This repository is a static cockpit with no backend, accounts, wallet, or live billing. Product targets below are targets, not live entitlements. Track staged status in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

## Run locally

No package installation is required.

```bash
git clone https://github.com/8x8org/8x8-user-edition.git
cd 8x8-user-edition
python3 -m http.server 8080
```

Then open the local address printed by the server.

## Public demo vs. private owner system

This is the **public demo repository** of 8x8 OS. It contains the isolated static cockpit and public-safe documentation only. The private owner control plane, agents, memory, messages, credentials, wallets, and device authority are excluded. No code path, connector, or configuration in this repository can reach them.

Nothing in this repository alone proves that a private runtime, productive agent, or production service exists or performs as depicted. Capability claims are tracked separately in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) using the evidence ladder described in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## OpenAI Build Week judges

This project was submitted to OpenAI Build Week on Devpost as **“8x8 OS: Human-Controlled AI & Web3 Operating System.”**

- This repository is the public-safe demo: a static, local-only cockpit with no backend. Judge it as a demonstration of the operating model, truth ladder, Three-Reality model, and permission boundary, not as the full system.
- The complete private system is not published. Judge access to private canonical evidence may be arranged through the submission contact route.
- Every capability shown in the cockpit is labeled with an evidence state; nothing below `IMPLEMENTED` should be treated as existing software.

## Beta contents

- responsive spatial cockpit;
- public agent-archetype explorer;
- conceptual world interface with tracking disabled;
- claim-to-adoption evidence model;
- public/private security boundary;
- Three-Reality architecture;
- evidence-gated roadmap;
- installable progressive web app shell;
- machine-readable public state;
- static deployment security headers;
- GitHub Actions validation.

## Explicit beta limits

The beta has no backend, account database, credentials, wallet connection, private memory, private messages, private agents, terminal executor, live trading, mining, rewards, hidden telemetry, or device administration.

Buttons change the local interface only. They do not execute an external action.

## Intended public package

Later releases may contain only:

- signed installer and complete uninstaller;
- public permission center;
- isolated task runner;
- public schemas and receipt verifier;
- user-owned account and device enrollment flows;
- examples, tests, SBOMs, signatures, and build provenance.

They must not contain owner credentials, private control-plane code, private agents, private memory, private messages, owner wallets, signing keys, raw telemetry, or reusable privileged access to an owner device.

## Permission model

Installation is separate from every later permission:

`installation ≠ node enrollment ≠ compute consent ≠ storage consent ≠ telemetry consent ≠ remote-support consent ≠ rewards consent`

All optional device contribution is disabled by default and must be visible, limited, revocable, and receipted.

## Product targets

- Target monthly subscription: **USD 8.88**
- Target daily free allowance: **88 auditable service minutes**
- Billing status: **not live**
- Beta source status: **IMPLEMENTED**
- Live deployment status: see [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md)

No guaranteed profit, rewards, APY, token value, zero gas, zero latency, unlimited capability, or whole-system completion is promised.

## Supported public scope

This repository is an isolated public client. Supported public-safe work includes the static cockpit UI, accessibility, documentation, tests, security headers, and machine-readable public state. It contains no owner credentials, private control plane, private agents, private memory, wallets, or reusable privileged access. Contributions must preserve that boundary.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)
- [Testing and validation](https://github.com/8x8org/.github/blob/main/CONTRIBUTING.md#testing-requirements)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Machine-readable public state](state/public-state.json)
- [Organization version and Three-Reality policy](https://github.com/8x8org/.github/blob/main/docs/8X8_VERSION_AND_THREE_REALITY_POLICY_0.0.1.md)

## Organization

| Repository | Purpose |
|---|---|
| [8x8org/8x8-user-edition](https://github.com/8x8org/8x8-user-edition) | This public demo cockpit |
| [8x8org/8x8-protocol](https://github.com/8x8org/8x8-protocol) | Public protocol repository |
| [8x8org/.github](https://github.com/8x8org/.github) | Organization profile, estate policy, and governance |

The permanent public website is pending deployment. No official social-media profile links are published here yet; treat any account claiming to be official as unverified until linked from this organization.

## License

The public 8x8 User Edition repository is licensed under the [Apache License 2.0](LICENSE). The license applies to material published in this repository. It does not publish, license, or grant access to the separate private 8x8 owner control plane or its private operational material.

## Security

Do not submit credentials, wallet keys, private messages, biometric templates, or private-system logs to public issues. See [SECURITY.md](SECURITY.md) for the reporting route and full public/private boundary.
