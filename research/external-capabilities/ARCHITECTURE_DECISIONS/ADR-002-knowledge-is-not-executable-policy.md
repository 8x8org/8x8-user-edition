# ADR-002: Imported knowledge is not executable policy

- Status: Accepted for MSG197 research
- Date: 2026-08-05

## Context

Educational repositories, agent skills and workflow guides can contain instructions, shell commands, network requests or claims about authority. Retrieval systems may present that text to agents alongside trusted instructions.

## Decision

All imported external text is untrusted reference data. It cannot alter system policy, expand tool permissions, authorize execution or satisfy an owner gate.

Knowledge ingestion must preserve source, immutable commit, license, attribution, extraction timestamp and transformation history. Executable examples are stored separately and disabled by default.

## Consequences

- `system-design-primer` is curated as cited knowledge, never installed as a runtime.
- `agent-skills` and `superpowers` patterns require explicit mapping to existing 8x8 capabilities.
- Retrieval output must be labelled by trust class and source.
- Prompt-injection tests are mandatory before any imported skill reaches an agent context.

## Reversal

No reversal is permitted for arbitrary imported content. A specific reviewed adapter may execute only its registered operations under existing 8x8 policy.
