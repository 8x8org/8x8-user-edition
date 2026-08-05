# MSG197 Current Status V4

## Canonical truth

- Candidate repositories resolved and pinned: **13/13**
- Candidate research, decision, plan, or blocked-evidence packets merged: **13/13**
- Measured external canaries complete: **1/2**
- Disabled-by-default 8x8 adapter contracts merged: **1**
- Third-party candidates installed into active 8x8: **0**
- Valid identity- and lease-bound council votes: **0/4 required**
- Production, phone, service, credential, wallet, database, private-data, and public-deployment changes: **0**

`CANDIDATE_STATUS_LEDGER_V4.json` supersedes V3 for current status.

## Newly completed adapter contract

Supervision at `bc20dd19fbc7b6cceaec447f1182346ca9158523` already passed its no-model external-node canary on Python 3.11 and 3.12.

PR #84 now adds the tested 8x8 adapter contract and merged at:

`a7d3be2dabce36b6cc994bbaab0d27ed5de5ae99`

The contract contains:

- a versioned manifest;
- bounded request and response schemas;
- deterministic synthetic fixture hashes;
- explicit privacy, resource and authority denials;
- rollback doctrine;
- dedicated validation and CodeQL.

Its immutable state remains:

- `enabled=false`
- `install_state=NOT_INSTALLED`
- `runtime_authority=NONE`
- `production_ready=false`

This is a complete adapter-contract slice. It is not a runtime installation or production activation.

## Existing blocked candidate

PDF Inspector passed its synthetic parser canary but remains blocked from promotion at the current pin by recorded Rust advisories and an unmaintained dependency warning.

## Remaining dependency 1: AirLLM

Issue #53 still requires:

- an approved dedicated NVIDIA CUDA node;
- an owner-approved model with verified license and access rights;
- reserved storage and cost authority;
- measured GPU, RAM, disk, latency, thermal, cleanup, and uninstall evidence.

It cannot be completed truthfully on Samsung Termux, the active Ubuntu PRoot, or a standard GitHub CPU runner. No model download or paid GPU allocation is authorized by MSG197.

## Remaining dependency 2: real research council

Issue #58 still requires four valid votes. Each vote must contain a canonical agent identity, active lease, shared input digest, output digest, recommendation, security-veto state, and cleanup receipt.

The deterministic aggregation framework is merged, but valid votes remain **0/4**. ChatGPT advisory output is not a leased 8x8 council vote, and no unavailable agent may be impersonated.

## Completion boundary

MSG197's intake, candidate packet, public observatory, deterministic council framework, measured Supervision canary, and disabled Supervision adapter-contract layers are complete.

Whole MSG197 closure still depends on:

1. the AirLLM external CUDA benchmark, or an explicit owner-approved supersession receipt; and
2. four valid identity- and lease-bound council votes, or an explicit owner-approved supersession of the quorum requirement.

Neither dependency may be silently marked complete merely to improve a percentage.
