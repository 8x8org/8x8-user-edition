# 8x8 User Edition

> **8x8 OS 0.0.1 Beta · Public Present projection · Protected Beta promotion state. Not whole-system stable or complete.**

8x8 User Edition is the canonical public-safe client for the wider 8x8 Fabric. It exposes an evidence-gated projection of the operating model, Three Realities, public repository DNA, agent archetypes, mission/evidence concepts, Studio, trading research, blockchain research and spatial-interface direction without exposing the private owner control plane.

## ❤️ Sponsor 8x8

[**Sponsor 8x8 on GitHub → github.com/sponsors/8x8org**](https://github.com/sponsors/8x8org)

Sponsorship supports the **public** project only: documentation, testing, security hardening, accessibility, developer tooling, community maintenance, and bounded infrastructure costs. It is support, not an investment: no financial returns, tokens, equity, guaranteed features, private/customer data, or private-repository access. See the organization [governance](https://github.com/8x8org/.github/blob/main/GOVERNANCE.md).

## 🛠️ Contribute

Contributions of code, tests, docs, accessibility, and security review are welcome. Read the [Contributing guide](https://github.com/8x8org/.github/blob/main/CONTRIBUTING.md), follow the [Code of Conduct](https://github.com/8x8org/.github/blob/main/CODE_OF_CONDUCT.md), and keep public/private boundaries intact.

## Project maturity

**Canonical product version: `0.0.1 Beta`.** Historical MSG identifiers, branch names, commit SHAs, protocol revisions and runtime generations are implementation metadata only. They do not promote product maturity.

The public repository is evidence-gated. A feature can be implemented or even deployed while the whole 8x8 system remains 0.0.1 Beta. Track exact capability states in [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

## Three Realities

8x8 treats time and maturity as executable system state, not branding:

- **PRIVATE_PAST** — private operational history, memory, evidence, superseded work and recovery truth.
- **PUBLIC_PRESENT** — current privacy-safe, evidence-backed public projection.
- **FUTURE_LAB** — research, simulations, candidate capabilities and unpromoted prototypes.
- **PROTECTED_BETA** — transition state used to validate promotion into Public Present; it is not a fourth reality.

Machine-readable public state is published in [`state/public-state.json`](state/public-state.json) and [`public/reality-snapshot.json`](public/reality-snapshot.json).

## Run locally

No package installation is required.

```bash
git clone https://github.com/8x8org/8x8-user-edition.git
cd 8x8-user-edition
python3 -m http.server 8080
```

Then open the local address the server prints.

## Fabric Mirror

The current public interface organizes the public-safe view around the Fabric itself:

`8x8 Gate → First Blink → Live Reality Graph → Systems → Evidence → Three Realities`

It includes public-safe representations of:

- Agent Fleet and Council;
- hardware/device mesh;
- public repository DNA;
- Universal Model Fabric;
- Mission Fabric;
- Security and Authority;
- Memory and Evidence;
- Studio and publication channels;
- Trading Intelligence as signal/research only;
- blockchain/economy as testnet/research unless separately promoted;
- Command Deck, Council Wall, Art Board 360, Memory Graph and Operator HUD;
- 3D/5D/360/XR/adaptive-8K direction as Future Lab / progressive convergence.

Protected repository inventory, private topology, secrets, private memory/messages, wallet signing material and privileged controls are deliberately excluded.

## Public demo vs. private owner system

This repository is an isolated public projection. It contains no owner credentials, private control plane, private agents, private memory, private messages, wallet authority or reusable privileged device access. Public screenshots and source files do not prove private-runtime deployment.

Capability claims follow the evidence ladder documented in [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

## Explicit beta limits

The public beta has no public production account database, no live subscription billing, no private-control access, no live financial execution authority, no hidden telemetry and no unrestricted remote shell.

Buttons in the static public mirror demonstrate interface contracts. They do not silently grant external authority.

## Product targets

- Target monthly subscription: **USD 8.88**
- Target service allowance: **88 auditable minutes** where a future entitlement service explicitly grants them
- Billing status: **not live**
- Signed installer: **not released**
- Whole-system maturity: **0.0.1 Beta**

No guaranteed profit, rewards, APY, token value, zero gas or zero latency is promised.

## Deployment acceptance

A deployment is not considered verified merely because Vercel accepted a deployment request. The public release requires a real project/deployment record and route checks proving that `/`, `/first-blink`, `/world`, and `/art-board` return browser-renderable HTML without attachment headers. See [`docs/MSG296E_FABRIC_MIRROR_V010.md`](docs/MSG296E_FABRIC_MIRROR_V010.md).

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Implementation status](IMPLEMENTATION_STATUS.md)
- [Security policy](SECURITY.md)
- [Public information boundary](PUBLIC_INFORMATION_BOUNDARY.md)
- [Machine-readable public state](state/public-state.json)
- [Reality snapshot](public/reality-snapshot.json)
- [MSG296E Fabric Mirror implementation metadata](docs/MSG296E_FABRIC_MIRROR_V010.md)

## Organization

| Repository | Purpose |
|---|---|
| [8x8org/8x8-user-edition](https://github.com/8x8org/8x8-user-edition) | Canonical public User Edition |
| [8x8org/8x8-protocol](https://github.com/8x8org/8x8-protocol) | Public protocol/contracts |
| [8x8org/.github](https://github.com/8x8org/.github) | Organization governance and public product map |

## License

The public 8x8 User Edition repository is licensed under the [Apache License 2.0](LICENSE). The license applies only to material published here and does not publish, license or grant access to the separate private 8x8 owner control plane.

## Security

Do not submit credentials, wallet keys, private messages, biometric templates, protected repository inventory or private-system logs to public issues. See [SECURITY.md](SECURITY.md).
