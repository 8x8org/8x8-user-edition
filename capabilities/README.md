# 8x8 External Capabilities Observatory

This directory is the canonical User Edition source for the static MSG197 capability observatory.

## Public projection

The verified protected integration projection is bound to:

- ecosystem repository: `horbolsi/8x8-OS-Ecosystem`;
- integration commit: `6b7e5bf8fb13587a2e26f4949ae774a41571cc5f`;
- Vercel deployment: `dpl_6k8vV7jYRENNMepCBJMTGuYJEPHB`;
- route: `/capabilities/`;
- route result: HTTP 200;
- production alias changed: no.

## Canonical truth

The page reads the existing ledger directly:

`../research/external-capabilities/CANDIDATE_STATUS_LEDGER_V3.json`

It does not maintain a second candidate decision ledger.

## Scope

The scoped 100/100 score covers only the tested static observatory and its protected public projection. It does not mean:

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
python3 -m unittest tests.test_capabilities_observatory -v
```

The dedicated workflow also validates JSON, JavaScript syntax, canonical ledger truth, private-boundary exclusions and accessibility contracts.

## Rollback

Revert the scoped source commit and, if necessary, the integration release commit `6b7e5bf8fb13587a2e26f4949ae774a41571cc5f`. Production remains unchanged.
