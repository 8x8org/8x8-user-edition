# Proof-Carrying Execution Fabric (PCEF) V1 — public reference

This module is the **public, least-authority reference** for the 8x8 execution
law. It exists to make one criticism impossible to hand-wave away:

> A consequential action is not "done" because a process returned `0`.

```
process exit 0  !=  EFFECT_COMMITTED  !=  VERIFIED  !=  TERMINAL
```

## Canonical lifecycle

```
CREATED → PICKED_UP → LEASED → STARTED → PROGRESS
        → EFFECT_COMMITTED → VERIFIED → TERMINAL
```

`FAILED_SAFE` is the explicit fail-closed terminal path from any non-terminal
state. Verification is the whole point: `VERIFIED` is reachable only when the
committed output evidence hash equals an **independently supplied** expected
hash. A mismatch transitions the mission to `FAILED_SAFE` and raises.

## What is verifiable here (software, deterministic, dependency-free)

- legal-transition enforcement (illegal edges rejected);
- compare-and-swap revision guard (stale / racing workers rejected);
- unique idempotency keys (duplicate creation rejected);
- explicit leases with deterministic expiry enforcement;
- SHA-256 canonical input / dependency / output evidence;
- append-only, hash-chained receipt ledger;
- optional secret-backed HMAC integrity tags per receipt;
- deterministic `export → reopen → replay` with chain re-verification;
- tamper detection (any altered receipt body breaks the chain).

Run it:

```bash
python3 -m unittest fabric.proof_carrying_execution.test_pcef -v
python3 fabric/proof_carrying_execution/pcef.py
```

## Public information boundary

This reference deliberately does **not** publish the private owner runtime.
Actors, holders and runtime fingerprints are opaque caller-supplied strings.
Real process identifiers, device topology, durable store locations, credentials
and lease material remain behind the boundary described in
`../../PUBLIC_INFORMATION_BOUNDARY.md` and are never present in this repository.

A private owner runtime may bind this same protocol to a durable store and real
leases; that binding is **owner runtime, not published**, and measured
distributed throughput is **not claimed** by this module.

## Relationship to the KHRONAPEIRON-8 capability contract

This module realizes, as verifiable software, the CHRONOS-row cells that the
core capability contract (`../khronapeiron8/contract.v1.json`) previously listed
as implementation targets: `1.3` durable state machine (reference model),
`1.5` idempotency, `1.6` checkpoint & replay, `1.8` temporal provenance, plus
`6.7` cryptographic receipt validation and `7.4`/`7.5` receipts & replay.
