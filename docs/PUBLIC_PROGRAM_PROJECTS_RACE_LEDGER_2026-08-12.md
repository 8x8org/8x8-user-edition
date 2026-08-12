# 8x8 OS Public Program — Projects / Race Ledger

**Brand:** ©️8x8 by FlashTM8 ⚡️🌎🤖  
**Canonical root:** `fabric://8x8/core`  
**Evidence cutoff:** 2026-08-12  
**Scope:** public-safe competition transparency  
**Architecture priority:** One Fabric first; competition deadlines are informational, not governing

This ledger makes competition work visible without creating a second product truth. A race may evaluate or accelerate useful 8x8 work, but it does not outrank the long-running 8x8 program and does not authorize shortcuts around evidence, security, provenance, rollback, eligibility, or owner authority.

Machine-readable source: [`public/projects/races.json`](../public/projects/races.json)  
Public Projects UI: [`projects/index.html`](../projects/index.html)

## PRESENT_PROVEN — OpenAI Build Week

**Participation:** `SUBMITTED`  
**Current status:** `SUBMITTED_OUTCOME_PENDING`  
**Public submission receipt:** not yet linked in this repository  
**Private-evidence boundary:** the submission state is supported by connected owner evidence, but private communications are not republished into the public program.

Current authoritative public sources disagree on the post-submission schedule:

- OpenAI's current Build Week sponsor page says the judging period is **July 22 through August 24, 2026** and winners are announced **August 25, 2026**.
- The Devpost official rules still say judging is **July 22 through August 5, 2026** and winners are announced **on or around August 12, 2026 at 2:00 PM Pacific**.

Therefore the only evidence-safe result state is `WAIT_FOR_OFFICIAL_RESULT_RECEIPT`. A date passing does not convert the project into a winner, finalist, loser, or ranked entry without an authoritative result receipt.

### Pending

1. Link an approved public submission receipt if one becomes available.
2. Record official outcome only from an authoritative public result or owner-provided result receipt.
3. Preserve the submitted competition lineage and archive it without changing One Fabric product truth.

### Public sources

- https://openai.com/build-week/
- https://openai.devpost.com/rules
- https://openai.devpost.com/updates/45418-submissions-are-closed

## PRESENT_PROVEN + FUTURE_GATED — Build with Gemini XPRIZE

**Participation:** `BUILDING_NOT_SUBMITTED`  
**Current status:** `ACTIVE_BUILD_FUTURE_GATED_SUBMISSION`  
**Current public engineering receipt:** https://github.com/8x8org/8x8-venture-operator/pull/3

The current XPRIZE engineering PR explicitly preserves clean-room competition provenance while keeping the broader ©️8x8 by FlashTM8 ⚡️🌎🤖 estate classified as pre-existing infrastructure, brand, and research rather than pretending the whole system was created during the competition window.

The current PR also explicitly does **not** claim a real Gemini production call, cloud deployment, stable judge URL, customer acquisition, arms-length revenue, billing activation, or final XPRIZE submission. Those remain future gates.

XPRIZE's public announcement says the build period runs **May 19 through August 17, 2026**. Entries are judged equally on **Business Viability**, **AI-Native Operations**, and **Category Impact**, and teams must launch a real business, acquire real users, and generate real revenue. Those requirements are evidence obligations, not reasons to fabricate activity or weaken 8x8.

### Pending

1. Pass exact-head backend tests, secret scan, and frontend build for the current XPRIZE PR.
2. Produce a real Gemini production-call receipt.
3. Produce a real Google Cloud deployment and stable judge URL receipt.
4. Produce truthful real-user evidence.
5. Produce truthful arms-length revenue and business evidence required by the competition.
6. Complete judge-facing evidence and a reproducible product path.
7. Create the final XPRIZE submission receipt.
8. Preserve disclosure/provenance for all pre-existing One Fabric material.

### Public sources

- https://www.xprize.org/news/xprize-launches-hackathon-with-2-million-prize-pool-backed-by-google
- https://www.geminixprize.com/
- https://github.com/8x8org/8x8-venture-operator/pull/3

## FUTURE_GATED watchlist — DEV Big Summer Bug Smash

**Participation:** `NOT_ENTERED`  
**Current status:** `DISCOVERY_ONLY`

DEV's current challenge is relevant only if an already-needed 8x8 bug fix or performance optimization naturally qualifies. It does not justify creating unrelated feature work or diverting the One Fabric roadmap. The public challenge states submissions are due **August 23, 2026 at 11:59 PM PDT** and winners are announced **September 17, 2026**.

Public source:

- https://dev.to/devteam/devs-big-summer-bug-smash-is-now-live-share-5000-in-cash-prizes-skateboards-and-more-across-57mk

## Eight fair-race rules

1. **ONE FABRIC FIRST** — every race is a projection under `fabric://8x8/core`, never a parallel root.
2. **THREE-TIME TRUTH** — every material race claim is `PAST_PRESERVED`, `PRESENT_PROVEN`, or `FUTURE_GATED`.
3. **PUBLIC RECEIPT BEFORE PUBLIC CREDIT** — missing public receipts remain visibly marked instead of silently inferred.
4. **SAME DENOMINATOR** — comparisons use the same scope, environment, measurement method, and evidence standard for 8x8 and competitors.
5. **NO FABRICATED METRICS** — users, revenue, latency, uptime, telemetry, scores, capability counts, and placements are never invented.
6. **DEADLINES DO NOT OVERRIDE SAFETY** — security, provenance, privacy, rollback, eligibility, and owner authority remain mandatory.
7. **NO SELF-AWARDED RANK** — first place or superiority requires an official result or a frozen reproducible benchmark covering the stated competitor set.
8. **PRESERVE HISTORY + ROLLBACK** — publication must not destroy prior evidence or expose credentials, private topology, private messages, or signing authority.

## Current truth boundary

- A branch or PR is not a deployment receipt.
- A deployment is not user-adoption proof.
- A submission is not a finalist or winner receipt.
- A feature count is not a benchmark.
- A competition date is not an architecture priority.
- A hackathon result, whatever it becomes, is one measurement surface over the larger 8x8 program.

**©️8x8 by FlashTM8 ⚡️🌎🤖 | public race transparency | fair comparison | One Fabric first**
