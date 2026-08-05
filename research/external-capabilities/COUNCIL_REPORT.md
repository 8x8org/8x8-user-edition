# MSG197 Research Council Report V1.1

## Truth state

`PRIMARY_RESEARCH_COMPLETE_COUNCIL_EXECUTION_NOT_YET_RECEIPTED`

This report records the initial evidence synthesis performed from exact GitHub repository identities, default branches, immutable commit pins, license files and selected upstream documentation. It does not falsely claim that Hermes, Seraphim, Claude, OpenCloud agents or the full 8x8 fleet independently executed the review. Independent council votes require agent IDs, leases, input digests, output digests and signed receipts.

## Semantic correction

The requested `uber/adr` repository resolves to `uber/ADR`, where ADR means **Agentic AI Detection and Response**. It is an enterprise agent-security system containing an activity sensor, synthetic security benchmark and detector. It is not architecture-decision-record tooling. The original intake wording that described Markdown ADR creation was incorrect and is superseded by this report.

## Coordinator contract

Hermes is the preferred coordinator. If Hermes is unavailable or rate-limited, the coordinator must emit a complete `HANDOFF_PACKET`, preserve all evidence hashes, release its lease and stop. A replacement coordinator may resume only from the exact packet digest.

Each council work item must include:

- mission and task ID;
- canonical agent and body ID;
- specialization;
- lease issuer, issue time and expiry;
- exact upstream commit pins;
- input-manifest SHA-256;
- output SHA-256;
- disagreement records;
- cleanup and residual-resource state;
- final receipt status.

## Initial decisions

| Priority | Repository | Decision | Reason |
|---:|---|---|---|
| 1 | `donnemartin/system-design-primer` | Curate as a cited knowledge source | Educational content, low runtime risk, no reason to install as software. |
| 2 | `TencentCloud/TencentDB-Agent-Memory` | Study as an adapter reference | Valuable memory schemas, but substantial overlap and sensitive-data implications. |
| 3 | `addyosmani/agent-skills` | Extract skill-contract patterns | Useful manifest ideas; every imported instruction must remain subordinate to 8x8 policy. |
| 4 | `obra/superpowers` | Extract workflow patterns | Useful process discipline without importing automatic hooks or a second execution authority. |
| 5 | `uber/ADR` | Map security telemetry and synthetic benchmark contracts | Strong Guardian value, but real agent traces and provider keys are prohibited from the first canary. |
| 6 | `firecrawl/pdf-inspector` | Prepare hostile-file sandbox design | High document-intelligence value, but untrusted PDF parsing needs strict limits. |
| 7 | `roboflow/supervision` | External-node vision canary design | Useful specialist capability, too large and dependency-heavy for casual phone installation. |
| 8 | `cloudflare/computer` | Restricted sandbox research only | Preview execution backends can expose durable state, full Linux binaries and real network access. |
| 9 | `lyogavin/airllm` | External GPU feasibility test | Current model requirements make the Samsung node an unsuitable first target. |
| 10 | `huangruiteng/loopx` | Architecture comparison, no runtime adoption | Strong overlap with Hermes, task ownership and Control Fabric. |
| 11 | `esengine/DeepSeek-Reasonix` | Protocol comparison, no history merge | Useful extension and receipt patterns, but exceptionally high architectural overlap. |
| 12 | `tailwindlabs/tailwindcss` | Conditional dependency only | Adopt solely inside a reviewed frontend migration, never as a system-wide fashion choice. |
| 13 | `vercel/next.js` | Defer pending a product requirement | The current public client does not justify a full framework migration or a canary-branch dependency. |

## Principal disagreements the real council must test

1. Whether TencentDB Agent Memory offers enough portability and deletion guarantees to justify an adapter rather than schema inspiration only.
2. Whether LoopX or Reasonix contain bounded protocols that can be reused without introducing a competing orchestrator.
3. Whether the Uber ADR sensor schema can be mapped to 8x8 events without collecting private prompts, tool arguments or execution traces.
4. Whether `pdf-inspector` should be invoked as browser WASM, a local binary, an isolated service or an ephemeral job.
5. Whether Supervision can deliver meaningful mobile value within measured CPU, memory and storage ceilings.
6. Whether a future tenant product warrants Next.js while the current public release remains intentionally static and auditable.

## Council voting model

Every candidate receives independent votes for:

- architectural value;
- duplication risk;
- security risk;
- license compatibility;
- resource feasibility;
- data-governance fit;
- rollback quality;
- recommendation confidence.

A candidate cannot advance merely by majority vote. Advancement also requires all mandatory security, privacy, license and rollback gates. One security veto with evidence blocks the canary until reconciled.

## Advancement states

`CENSUSED -> STATIC_REVIEWED -> COUNCIL_REVIEWED -> CANARY_DESIGNED -> CANARY_PASSED -> ADAPTER_DESIGNED -> IMPLEMENTED_NOT_DEPLOYED -> RELEASE_CANDIDATE -> OWNER_APPROVED`

No candidate in this package is beyond `STATIC_REVIEWED`.

## Immediate bounded work packets

1. **KNOWLEDGE-001:** Create a citation-preserving, non-executable system-design index.
2. **MEMORY-001:** Compare memory object, tenant, deletion, retention and retrieval contracts using synthetic records.
3. **SKILLS-001:** Map external skill declarations to 8x8 capability IDs and deny undeclared permissions.
4. **SECURITY-ADR-001:** Map the Uber ADR sensor schema and attack taxonomy using synthetic traces only.
5. **PDF-001:** Design an untrusted PDF corpus canary with size, time and filesystem limits.
6. **VISION-001:** Benchmark one tiny synthetic video on an external node with no model download.
7. **COMPUTER-001:** Design a synthetic-workspace-only canary with explicit egress denial and zero credentials.
8. **AIRLLM-001:** Produce a hardware feasibility report before downloading any model.

## Completion boundary

MSG197 static intake is complete only when every candidate has an evidence-backed classification. Full research-council completion requires independent agent receipts or a documented owner-approved deferral. Installation, deployment and production readiness remain separate candidate-level missions.
