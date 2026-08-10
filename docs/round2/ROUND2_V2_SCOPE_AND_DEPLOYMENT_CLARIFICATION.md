# ♾️x♾️ ∞₈x₈∞ OS | ROUND 2 — v2 Scope & Deployment Clarification

Brand: ©️8x8 by FlashTM8 ⚡️🌎🤖

Status: CANONICAL_CLARIFICATION
Applies to: `ROUND2_AWAKENING_CANONICAL_EXECUTION_EVIDENCE_MANIFESTATION_VALIDATION_DIRECTIVE_V2.md`

## 1. Version scopes

The canonical Round 2 directive version is **v2**.

The string `v2.0 AWAKENING` inside the embedded JavaScript self-proof kernel is a **preserved kernel-internal version literal**. It is not a second directive version and does not change the canonical Round 2 contract from v2.

The kernel is explicitly byte-preserved by the directive. Therefore:

- directive_version = `v2`
- preserved_kernel_literal = `v2.0 AWAKENING`
- modifying the kernel literal merely to make those strings visually identical is forbidden unless the owner separately authorizes a kernel change
- validators SHALL treat the difference as intentional scope separation, not version drift

## 2. Deployment identity relationship

The repository currently documents the public production carrier as:

`https://8x8-os-ecosystem.vercel.app`

The source authority for that carrier is:

`8x8org/8x8-user-edition`

The Round 2 string `∞₈x₈∞.vercel.app` is **TARGET / branded future deployment identity only**. It is not the current production carrier, is not asserted to resolve in DNS, and does not replace the repository's current public deployment receipt.

Until external deployment evidence establishes otherwise:

- current_public_carrier = `https://8x8-os-ecosystem.vercel.app` (VERIFIED from repository deployment receipt)
- round2_branded_deployment_identity = `∞₈x₈∞.vercel.app` (TARGET)
- source_authority = `8x8org/8x8-user-edition`

No deployment promotion may be inferred from the branded target string.

## 3. Execution timestamp rule

`08:08:08 Universal Time` is a canonical brand marker only.

Machine execution receipts SHALL record their actual observed UTC execution timestamp. A receipt SHALL NOT use `2026-08-10T08:08:08Z` as an execution time unless evidence proves execution occurred at that instant.

## 4. Precedence

This clarification is normative for interpreting the v2 directive and resolves the two ambiguities identified in PR #147 review without modifying the byte-preserved kernel.

©️8x8 by FlashTM8 ⚡️🌎🤖
