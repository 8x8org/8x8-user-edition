# MSG197-REASONIX-001 Extension and Receipt Protocol Comparison

## Verdict

`ADOPT_SELECTED_EXTENSION_PROTOCOL_IDEAS_DEFER_RUNTIME`

Reasonix exposes several mature patterns relevant to 8x8: versioned extension packages, sidecar protocols, provider abstraction, structured tool approvals, checkpoints, bounded subagent progress and checksum-based distribution.

## Compatibility

These ideas map to the existing 8x8 capability manifest, adapter processes, model registry, owner and Guardian gates, receipt-bound rollback and Three-Reality event stream.

## Conflicts

Reasonix is itself an agent harness with provider credentials, tools, plugins, remote workflows and local runtime state. Installing it as another primary runtime would duplicate Hermes, the Control Fabric, the model router, the capability registry and the release authority.

## Decision

Study and reimplement selected protocol patterns only. Do not merge Git history, install the global package, configure providers or enable remote shell behavior. A future zero-action fixture may validate a small extension manifest and event exchange with no credentials or executable tools.
