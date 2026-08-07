# 8x8 First Blink Public Release — v0.0.8

Status: `PUBLIC_PREVIEW_READY / UNIVERSAL_RUNTIME_CERTIFICATION_PENDING`

This is the first deliberately tiny release slice of the revised 8x8 spatial/Reality-Graph vision. It is intentionally small enough to be independently verified and rolled back.

## Public preview

Source deployment project: `horbolsi/8x8-OS-Ecosystem`

Exact preview commit: `1411183a64c1063feef9ab6695a90b015099a9d6`

Vercel deployment: `dpl_HFoZGVUe9LovewprkWa3kS5T16z3`

Protected preview host: `https://8x8-os-ecosystem-5lf9ck1ep-8x8-team-url.vercel.app/first-blink/`

A Vercel share URL may be required while preview authentication is enabled. The stable public URL is not claimed until production promotion is verified.

## What this release proves

- a public-safe First Blink interface exists as source;
- the exact commit triggered a READY Vercel preview;
- the interface visually binds the First Blink sequence to the Live Reality Graph / Three-Realities model;
- the public/private boundary is explicit;
- the fourteen VIS records are acknowledged as design references, not live telemetry;
- no private runtime, secret, private key, wallet execution, live trading, raw telemetry or hidden device control is introduced.

## What it does not prove

It does not prove universal context bootstrapping across Hermes, Jarvis, Claude Code, Codex, OpenClaw, every model call or the broader agent fleet. That requires fresh-session canaries and `CONTEXT_BOOTSTRAP_RECEIPT` evidence from each certified client/agent wave.

It does not prove whole-system 100/100. The `100/100` label on this release refers only to the ten-check bounded scorecard in `FIRST_BLINK_CONTEXT_BOOTSTRAP_V008.md`.

## Visual basis

The canonical registry remains 14 VIS records / 13 unique binaries. Recurring interface ideas applied here include the central truth core, orbiting domains, spatial hierarchy, dark-neon command surfaces, Three Realities, explicit status, evidence-first language and Seraphim/Gate continuity.

## Security finding discovered during deployment review

The current `8x8-os-ecosystem.vercel.app` root was observed returning raw `server/index.ts` source instead of a normal product route. This is treated as `PUBLIC_DEPLOYMENT_ROUTING_MISCONFIGURATION` and must be remediated before that domain is presented as a stable public front door. The new First Blink route stays isolated on its preview release while root routing is repaired.

## Next beta gate

Next beta work should implement a signed latest-good context snapshot, a model/client bootstrap adapter, stale/unsigned rejection, omission reporting, on-demand evidence retrieval and deterministic context-rehydration evals before expanding the public Reality Graph.
