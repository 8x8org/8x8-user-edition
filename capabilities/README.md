# 8x8 External Capabilities Observatory

This directory is the canonical User Edition source for the static MSG197 capability observatory.

## Canonical truth

The page reads the current ledger directly:

`../research/external-capabilities/CANDIDATE_STATUS_LEDGER_V4.json`

It does not maintain a second candidate decision ledger.

Ledger V4 records:

- thirteen of thirteen candidate packets merged;
- one of two required measured external benchmarks complete;
- one disabled-by-default adapter contract merged;
- zero third-party candidates installed into active 8x8;
- zero of four valid council votes;
- no production, phone, credential, service, database, wallet, private-data or public-deployment mutation.

## Supervision contract boundary

The Supervision adapter contract merged at `a7d3be2dabce36b6cc994bbaab0d27ed5de5ae99` and remains:

- `enabled=false`
- `install_state=NOT_INSTALLED`
- `runtime_authority=NONE`
- `production_ready=false`

The observatory presents that contract as evidence. It does not execute it.

## Public projection

The previously verified protected integration projection remains bound to:

- ecosystem repository: `horbolsi/8x8-OS-Ecosystem`;
- integration commit: `6b7e5bf8fb13587a2e26f4949ae774a41571cc5f`;
- Vercel deployment: `dpl_6k8vV7jYRENNMepCBJMTGuYJEPHB`;
- route: `/capabilities/`;
- route result: HTTP 200;
- production alias changed: no.

That receipt covers the earlier V3 projection. A separate exact-head mirror, deployment and route receipt is required before the protected projection may claim V4.

## Scope

The scoped source validation covers only the tested static observatory and its canonical ledger projection logic. It does not mean:

- MSG197 is fully closed;
- AirLLM has completed its external CUDA benchmark;
- the real research council reached quorum;
- any candidate is installed in active 8x8;
- the phone, private runtime, databases, services or production alias changed;
- the whole 8x8 system is complete.

## Security boundary

The release has no external scripts, write routes, credentials, wallets, private data, service authority, database mutation, model download or third-party runtime execution.

## Validation

```bash
python3 scripts/validate_msg197_candidate_ledger_v4.py
python3 -m unittest tests.test_capabilities_observatory -v
```

The dedicated workflow also validates JSON, JavaScript syntax, canonical ledger truth, private-boundary exclusions and accessibility contracts.

## Rollback

Before a new protected projection is receipted, rollback is a source revert to the previous observatory commit. The existing protected integration projection and production alias remain unchanged.
