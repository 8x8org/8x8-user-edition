# ADR-001: External code remains subordinate to the 8x8 core

- Status: Accepted for MSG197 research
- Date: 2026-08-05
- Owner: FlashTM8 / Meher Trabelsi

## Context

Several candidate repositories provide agents, memory, schedulers, extensions, computer use, frontend frameworks or specialist tools. Some overlap strongly with Hermes, the Control Fabric, the capability broker, 8x8 memory and public clients.

## Decision

External repositories may enter 8x8 only as one of the classifications defined by MSG197. No candidate becomes a second control plane, mission authority, agent registry, memory truth, identity authority or release controller.

Executable candidates must integrate through a versioned adapter and capability manifest. The Control Fabric remains authoritative for task identity, risk, leases, gates, receipts and rollback.

## Consequences

- LoopX and Reasonix are comparison targets, not merge targets.
- TencentDB Agent Memory may inform or implement an adapter but cannot replace memory truth without a separate migration decision.
- Computer-use tools receive only explicit, expiring capabilities.
- Frontend frameworks do not redefine public/private product boundaries.
- Direct vendoring or blind Git history merges are rejected.

## Reversal

Reversal requires a new owner-approved ADR with migration evidence, independent security review, state transfer and full rollback rehearsal.
