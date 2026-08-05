# MSG197-ADR-001 Agentic AI Detection Compatibility Review

## Identity correction

`uber/ADR` is **Agentic AI Detection and Response**, not an Architecture Decision Record generator. The pinned repository describes an ADR Sensor, ADR-Bench, ADR Detector, synthetic security fixtures and a separately unavailable prevention component.

## Verdict

`ADOPT_TELEMETRY_SCHEMA_AND_ATTACK_TAXONOMY_ONLY`

The useful integration surface is defensive: normalized agent intent, tool-use and execution telemetry; a benchmark taxonomy; detector verdicts; and synthetic attack scenarios. These can inform the 8x8 Guardian, Three-Reality event bus and security council.

## Privacy boundary

Production conversations, prompts, credentials, files and agent sessions are prohibited. A future canary must use only synthetic fixtures, keyless detection, bounded resources, redacted output and ephemeral retention. The phone and active Ubuntu PRoot remain out of scope.

## Authority boundary

ADR observations may create a security finding or veto proposal. They cannot grant permissions, block production autonomously, become the canonical event store or claim prevention capability that the open-source release does not provide.

## License boundary

The repository is Apache-2.0. The vendored `Detection/benchmark/agentdojo/` subtree carries a separate MIT license and must remain separately attributed.

## Completion

Static compatibility research is complete. An executable benchmark remains owner-gated until a dependency SBOM, vulnerability scan, synthetic corpus manifest, resource limits and cleanup receipt are approved.
