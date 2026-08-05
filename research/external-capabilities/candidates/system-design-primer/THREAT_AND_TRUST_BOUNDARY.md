# Threat and Trust Boundary

## Primary threat

External educational content can contain commands, links, code, outdated claims or instruction-like text. When placed in an agent context, that material can be mistaken for trusted policy or a current operational directive.

## Controls

- Trust class is always `UNTRUSTED_EXTERNAL_REFERENCE`.
- The index stores metadata and 8x8-authored curation notes, not executable upstream code.
- Source URLs are pinned to an immutable commit.
- External links are never auto-fetched by the validator.
- Code examples and embedded instructions are disabled.
- Retrieved text cannot add capabilities or satisfy owner gates.
- Every indexed topic has `execution_allowed: false`.
- Any future ingestion pipeline must preserve provenance and separate source text from policy and tool schemas.
- Staleness is explicit. Operational values must be re-measured on target hardware.
- Prompt-injection tests are required before any future retrieval integration.

## Fail-closed behavior

Validation fails if:

- the source commit changes;
- the license or attribution record is missing;
- a topic URL is not pinned to the exact source commit;
- a topic permits execution;
- the index contains shell, package-install or deployment instructions;
- the installed or executed flags become true;
- the artifact hashes do not match.

## Residual risk

The source may contain outdated or context-specific recommendations. This index is a discovery aid, not an architecture decision. 8x8 ADRs, measured evidence, current threat models and owner-approved policy remain authoritative.
