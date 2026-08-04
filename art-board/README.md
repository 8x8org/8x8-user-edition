# 8x8 Global Art Board V1

The Global Art Board is the first independently scored public 8x8 release unit.

## Declared scope

This slice contains only a static, public-safe spatial interface:

- eight visible worlds;
- health and evidence colors;
- zoom, pan, filtering and keyboard controls;
- an evidence inspector;
- Seraphim public-guide onboarding;
- simulated region markers with zero users;
- a treasury policy view with no addresses, balances or signing;
- developer-extension guidance;
- responsive, reduced-motion and forced-color support.

It has no backend, account system, private runtime, precise location, wallet connection, billing, trading, publication executor or remote-control path.

## Score meaning

`100/100` applies only to the declared static slice and its tests.

It does not mean:

- the complete 8x8 system is finished;
- private agents or models are publicly active;
- the user map contains real users;
- treasury balances or wallets are connected;
- public billing or subscriptions are live;
- Roblox, Unreal, Vectras, ROM or mobile releases are deployed.

Unfinished worlds remain yellow, orange, black or purple rather than being hidden.

## Status colors

| Color | Meaning |
|---|---|
| Green | Healthy or complete inside the displayed scope |
| Cyan | Verified information or read-only state |
| Yellow | Incomplete dependency or warning |
| Orange | Degraded or awaiting review |
| Red | Down or blocked |
| Black | Unknown, stale or intentionally hidden |
| Purple | Planned or experimental |
| Gray | Disabled or not applicable |

Every status also includes text. Color is never the only indicator.

## Run locally

From the repository root:

```bash
python3 -m http.server 8080
```

Open `/art-board/` on the local URL.

## Validation

```bash
python3 -m unittest tests.test_art_board -v
```

The public-beta workflow also validates JSON, required files, private-boundary exclusions and forbidden endpoint or credential references.

## Canonical and preview roles

- This repository is the canonical public source.
- The Vercel-connected `horbolsi/8x8-OS-Ecosystem` repository may mirror the slice for a protected branch preview.
- A protected preview is not a production public release.
- Production promotion requires an exact target, current tests, rollback and a deployment receipt.
