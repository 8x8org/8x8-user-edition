# MSG197-LOOPX-001 Overlap and Unique-Value Review

## Verdict

`DEFER_RUNTIME_ADOPTION_EXTRACT_SELECTED_PROTOCOL_PATTERNS`

LoopX is explicitly a local control plane for long-running agent work. Its objectives, gates, todos, evidence, quota, claims, leases and handoffs overlap heavily with 8x8 missions, receipts, authority leases, the Control Fabric and the Memory Truth Graph.

## Useful ideas

The strongest reusable ideas are typed continuation outcomes, explicit hard-pause semantics, bounded turn accounting, peer-agent claim records, stale-evidence visibility and a clear statement that final dangerous authority remains human.

## Conflicts

Running LoopX would introduce another source of truth, another scheduler/heartbeat surface, another agent registry projection and another local state directory. Those conflicts exceed the value of adopting the runtime.

## Decision

Do not install LoopX into the active system. Reimplement only selected protocol ideas through existing 8x8 schemas after a zero-action fixture proves compatibility. The source remains an external reference, not an authority.
