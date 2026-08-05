# ADR-003: Computer use requires a synthetic, deny-by-default sandbox

- Status: Accepted for MSG197 research
- Date: 2026-08-05

## Context

Computer-use tooling can browse sites, operate accounts, submit forms, send messages, publish content or trigger purchases. Visual ambiguity and prompt injection can cause unintended actions.

## Decision

The first computer-use proof may interact only with a synthetic site controlled for the canary. It receives no owner account, cookies, passwords, personal data, payment details, wallet, messaging identity or production API credentials.

The sandbox must enforce:

- explicit domain allowlist;
- no arbitrary navigation;
- no download or upload outside synthetic fixtures;
- no clipboard, local filesystem or host secret access;
- bounded wall time and action count;
- screen and event receipts;
- owner-visible kill switch;
- zero public publishing or financial action.

## Consequences

`cloudflare/computer` remains `SANDBOX_EXPERIMENT`. A successful synthetic test proves only the declared fake-site workflow, not general autonomous browsing safety.

## Reversal

Broader domains or real accounts require a separate exact owner approval, candidate-specific threat review and a fresh expiring lease. Financial, government and legal actions remain independently prohibited.
