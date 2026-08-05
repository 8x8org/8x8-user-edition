# MSG197-COMPUTER-001 Durable Workspace Safety Review

## Identity correction

Cloudflare Computer is a preview virtual filesystem and execution substrate, not primarily a browser-clicking computer-use agent. Its authoritative workspace state lives in a Durable Object backed by SQLite, and it can expose container, shell and JavaScript runtime backends.

## Verdict

`ADOPT_WORKSPACE_BOUNDARY_IDEAS_DEFER_ALL_EXECUTION`

The potentially useful ideas are an explicit workspace authority, stable backend identifiers, structured execution results and a separation between filesystem state and runtime selection. Those patterns may inform a future 8x8 sandbox.

## Security boundary

Every runtime backend is denied in this packet. The container backend includes full Linux and real network, while the isolate backends still execute shell or JavaScript. No Cloudflare account, deployment, secret, Durable Object, Worker, FUSE mount or artifact publication was created.

## Canonical-state boundary

Cloudflare workspace state cannot become 8x8 memory truth, policy, identity or release authority. A future canary must be disposable, synthetic, account-scoped, network-denied where technically possible, and deletion-tested.

## Upstream maturity

The upstream explicitly labels the package preview-only, unstable and unsuitable for production. That status is preserved and blocks production classification.

## Completion

Static safety review and a zero-execution fixture contract are complete. Runtime experimentation remains owner-gated and requires an ephemeral Cloudflare environment, cost ceiling, deletion receipt and independent security review.
