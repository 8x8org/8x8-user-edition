# 8x8 External Capabilities Observatory

This directory is a static, public-safe release unit for MSG197.

## Purpose

It renders the canonical thirteen-candidate status ledger without installing, importing, executing or granting authority to any third-party candidate.

The page shows:

- exact candidate identities and immutable source pins;
- adopted, blocked, pattern-only and deferred decisions;
- measured benchmark counts;
- installed candidate count;
- real council quorum state;
- remaining AirLLM and research-council gates.

## Canonical source

The page reads:

`../research/external-capabilities/CANDIDATE_STATUS_LEDGER_V3.json`

It does not maintain a second candidate truth file.

## Security and privacy boundary

The release unit has:

- no external scripts, fonts, images or APIs;
- no inline JavaScript;
- no `innerHTML` rendering;
- no form submission or write path;
- no private endpoint, local path, credential, wallet, model or database reference;
- no service, scheduler, runtime, browser-control or filesystem authority;
- strict same-origin Content Security Policy;
- fail-closed behavior when the canonical ledger is missing or invalid.

## Score meaning

A future `100/100` applies only to this declared static observatory after every release gate is evidenced.

It does not mean:

- MSG197 is completely closed;
- AirLLM has been benchmarked;
- the real research council reached quorum;
- any candidate is installed in active 8x8;
- the phone, private runtime or production alias changed;
- the whole 8x8 system is complete.

## Validation

Run from the repository root:

```bash
python3 -m unittest tests.test_capabilities_observatory -v
```

The dedicated workflow also validates JSON, forbidden private patterns, external-resource absence, DOM-safe rendering and the exact truth boundaries.

## Rollback

Before merge, close the pull request or delete the feature branch.

After merge, revert the release commit. The page has no runtime state, database schema, credentials, service ownership or external account to uninstall.
