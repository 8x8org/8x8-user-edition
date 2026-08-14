# Public Information Boundary

The 8x8 User Edition is a **public product surface**, not a public mirror of the private 8x8 system. It may contain software, schemas and documentation intentionally approved for users to consume the products, tools, intelligence and services offered by 8x8. It must not contain the proprietary machinery required to reproduce the OWNER_ROOT One-Fabric system.

## Three-reality publication model

1. **Private Past** contains private history, internal operations, private infrastructure, raw evidence, memories, experiments, donor implementations and recovery material.
2. **Future Lab** contains private research, candidate integrations, councils, adapters, simulations and canaries that have not completed public release gates.
3. **Public Present** contains only independently reviewed, privacy-safe product/release units with public provenance, tests and explicit publication approval.

Nothing moves directly from Private Past or Future Lab into Public Present.

## Public product material that may belong here

- user-facing product UI and static product assets;
- public product/API documentation and consumer SDK examples;
- deliberately public interoperability schemas and receipt verifiers;
- public account/profile/identity contracts that reveal no private authority;
- approved public evidence, release status and competition/product information;
- examples that demonstrate how to **use** an 8x8 product without revealing how the private One-Fabric system is built or operated.

Publishing a public protocol is an explicit design choice; it does not make the private implementation of that protocol public.

## Never publish here

- private infrastructure, device or runtime topology;
- private repository, dormant-feature or workspace inventories;
- internal agent rosters, SOUL/body implementation, leases, memory, messages or operational receipts;
- OWNER_ROOT command/control-plane implementation or agent-execution ingress packets;
- proprietary capability lattices, canonical-cell normalization, donor-selection, parity/frontier algorithms or internal benchmark deltas;
- internal A2A/PCEF implementation research, checkpoint/sandbox/guarded-session traces or council task envelopes unless separately sanitized into an intentionally public protocol contract;
- private continuity/context graphs, anti-loop operational memory or recovery procedures;
- credentials, tokens, private account data, wallet material, custody/signing authority or secret-broker internals;
- private paths, logs, database details, protected deployment identifiers or administrative routes;
- unpublished economic controls, settlement/signing implementation or private treasury policy;
- source sufficient to clone the private 8x8 system merely because a corresponding product feature is publicly usable.

## Product / implementation separation

A public label such as **Agents**, **Wallet**, **Studio**, **Trading**, **8x8 ID**, **NFT Vault**, **8x8 Network** or **Connector** means a user may be offered a product or service with that name. It does **not** authorize publication of the private implementation, privileged route graph, internal algorithms, provider credentials, private estate or owner controls behind that product.

The preferred boundary is:

```text
public user -> public product/API contract -> authenticated service boundary
                                         -> private One-Fabric implementation (not in this repo)
```

## Promotion contract

A public release unit must provide:

- an explicit public product scope;
- a source/license decision for every published implementation artifact;
- privacy, security, IP-boundary and accessibility checks;
- deterministic tests appropriate to the public unit;
- public-safe fixtures or approved public data sources;
- no private runtime dependency or hidden owner authority;
- an exact release receipt;
- owner publication approval.

Private details may be summarized only as neutral public claims such as `not connected`, `not available`, `planned`, `gated` or `not included`. Public diagrams and dashboards must never imitate live telemetry unless displayed data is bound to a public receipt.

## Historical remediation note

Detailed internal research/control-plane material was previously projected into this public repository. The current boundary removes that material from the active product tree and adds a fail-closed path/content guard. Earlier Git history, forks or third-party caches may retain prior public revisions; removing a file from current `main` does not erase prior disclosure. Any real secret found in historical public material must be rotated rather than merely deleted.
