# Community Operations Policy

**Document class:** PUBLIC_POLICY  
**Truth state:** PUBLIC_SOURCE_VALIDATED  
**MSG ref:** MSG233  
**Generated:** 2026-08-06

## Purpose

This policy governs how 8x8 operates community channels, responds to issues, schedules content, and interacts with external platforms. All automation must comply with the public information boundary and must not take autonomous action without the evidence and owner gates defined here.

## Operating principles

- One scheduler owner per automation loop.
- Evidence-based cadences only — no millisecond loops for LLM calls or public posting.
- All community responses must pass moderation and rate-limit checks before delivery.
- No secrets, credentials, or private runtime data in community messages, issues, or public posts.
- Every automated action produces a receipt.

## Channels and their governance

| Channel | Status | Automation allowed | Owner gate required |
|---|---|---|---|
| GitHub Issues | Active | Triage labeling only | Yes for closing/merging |
| GitHub Discussions | Active | None currently | Yes for all |
| Telegram | Designed | Owner-canned replies only | Yes |
| Discord | Designed | Owner-canned replies only | Yes |
| YouTube | Designed | Scheduled posts only | Yes |
| X / Twitter | Disabled | None | Owner + developer app |
| Facebook | Disabled | None | Owner + developer app |
| TikTok | Disabled | None | Owner + developer app |

## Automated loop cadences

| Loop | Minimum cadence | Notes |
|---|---|---|
| Health monitoring | 60 seconds | Lightweight local event only |
| Incident detection | 30 seconds | Alert threshold check |
| Community triage | 5 minutes | Issue labeling |
| Content scheduling | 1 hour | After owner approval |
| Dependency / security updates | 24 hours | Via CI |
| Model evaluation | 1 week | Requires budget policy |

## Revocation and rollback

Any community action can be revoked by the owner. Automated posting must support a per-platform disable switch and a 30-second rollback window where platform APIs permit.

## Prohibited actions without explicit owner gate

- Publishing content to any social platform
- Closing or merging GitHub issues or PRs
- Changing community membership or permissions
- Spending budget on paid APIs
- Accessing any platform on behalf of a user account not explicitly delegated
