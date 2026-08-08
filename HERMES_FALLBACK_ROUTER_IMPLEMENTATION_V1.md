# Provider Fallback Router — Implementation V1

## Purpose

This document describes the implementation of provider-level circuit breaking and deterministic fallback routing for the AI coordinator. It addresses the incident in MSG231 where a provider-wide daily free-tier quota failure triggered ten same-provider retries instead of immediately routing to another eligible provider.

## Incident root cause

The router received HTTP 429 with `free-models-per-day` and `remaining=0` from the provider. The response was classified as a transient rate limit rather than provider quota exhaustion. The retry loop re-attempted the same exhausted provider ten times before giving up, consuming approximately seven minutes and never routing to another provider.

## Architecture

```
Request
  │
  ▼
┌─────────────────────────┐
│  Failure Classifier      │  Classifies provider response into one of
│  (classify_failure)      │  ten canonical failure classes.
└────────────┬────────────┘
             │  failure_class
             ▼
┌─────────────────────────┐
│  Circuit Breaker         │  Opens provider or model circuit according
│  (apply_circuit_rule)    │  to policy. Updates suppression registry.
└────────────┬────────────┘
             │  updated_suppression_state
             ▼
┌─────────────────────────┐
│  Route Scorer            │  Scores all non-suppressed provider/model
│  (score_routes)          │  combinations deterministically.
└────────────┬────────────┘
             │  ranked_routes
             ▼
┌─────────────────────────┐
│  Route Selector          │  Picks highest-scoring route ≥ minimum
│  (select_route)          │  score threshold, or emits BLOCKED receipt.
└────────────┬────────────┘
             │  selected_route | BLOCKED
             ▼
┌─────────────────────────┐
│  Receipt Writer          │  Records redacted selection receipt or
│  (write_receipt)         │  BLOCKED receipt; preserves mission queue.
└─────────────────────────┘
```

## Failure classifier

The classifier inspects the HTTP status code and response body before any retry decision is made. Classification order (first match wins):

1. **PROVIDER_QUOTA_EXHAUSTED** — HTTP 429 with `remaining=0` or error codes containing `free-models-per-day`, `quota_exceeded`, or `daily_limit_exceeded`. Entire provider circuit opens immediately.
2. **INVALID_CREDENTIAL** — HTTP 401 or 403 not caused by content policy. Provider disabled; owner remediation gate raised.
3. **MODEL_UNAVAILABLE_OR_RETIRED** — HTTP 404 or 400 with `model_not_found` or `model_deprecated`. Model retired from registry.
4. **CONTEXT_TOO_LARGE** — HTTP 400 or 413 with `context_length_exceeded`. Context compaction or large-context model selection triggered.
5. **AUTHORITY_DENIED** — HTTP 403 with safety or content-policy signal. Escalated to owner; no retry.
6. **PROVIDER_UNAVAILABLE** — 5xx after transient retry budget exhausted.
7. **MODEL_QUOTA_EXHAUSTED** — HTTP 429 scoped to one model; provider circuit remains open.
8. **TOOL_INCOMPATIBLE** — HTTP 400 with tool/function-calling rejection. Model excluded for tool tasks.
9. **TRANSIENT_RATE_LIMIT** — HTTP 429 or 503 with Retry-After. Bounded jittered retry, then failover.
10. **UNKNOWN_FAIL_CLOSED** — All other errors. Provider circuit opens; BLOCKED receipt if no eligible route.

## Circuit-breaker implementation

```python
class ProviderCircuit:
    """Tracks open/closed state per provider and per model."""

    def open_provider(self, provider_id: str, reset_at: datetime | None) -> None:
        """Suppress all models on provider until reset_at (or manual reset)."""

    def open_model(self, provider_id: str, model_id: str, reset_at: datetime | None) -> None:
        """Suppress one model while keeping other models on the provider eligible."""

    def is_provider_eligible(self, provider_id: str) -> bool:
        """Return False if provider circuit is open and reset_at has not passed."""

    def is_model_eligible(self, provider_id: str, model_id: str) -> bool:
        """Return False if model circuit is open or provider circuit is open."""
```

## Route scoring

For each eligible (provider, model) pair:

```
score = (
    provider_health_score(provider)    # 0–20
  + model_health_score(model)          # 0–15
  + context_capacity_score(model, task)# 0–15
  + capability_match_score(model, task)# 0–15
  + tool_support_score(model, task)    # 0–10
  + error_rate_score(provider, model)  # 0–10
  + latency_score(provider, model)     # 0–5
  + cost_policy_score(model)           # 0–5
  + authority_score(model)             # 0–3
  + privacy_class_score(model, task)   # 0–2
)
```

Minimum score to select: **30 / 100**. Routes below threshold are rejected with recorded reason.

## No-eligible-route handling

When no route scores ≥ 30:

1. Emit `BLOCKED` receipt containing task ID, UTC timestamp, attempted routes, failure classes, queue position, and resume condition.
2. Preserve the mission in the queue at its current position.
3. Do not drop or corrupt the task.
4. Notify owner if priority task is BLOCKED for more than the configured timeout.

## Receipt format

All receipts are redacted before storage — provider credentials, API keys, and internal host paths are never written.

**ROUTE_SELECTED receipt fields:**
- `task_id`
- `timestamp_utc`
- `selected_provider_alias` (public alias, not credential)
- `selected_model_alias`
- `score`
- `rejected_route_count`
- `rejection_summary_redacted`

**BLOCKED receipt fields:**
- `task_id`
- `timestamp_utc`
- `attempted_routes`
- `failure_classes`
- `queue_position`
- `resume_condition`

## Testing requirements

Five synthetic canary scenarios must pass before production promotion:

1. Provider-wide daily quota exhaustion → zero same-provider retries → successful route to another provider.
2. Model-only quota failure → provider remains eligible → another model on same provider selected.
3. Oversized context → context compaction attempted → route to larger-context model if compaction fails.
4. No eligible route → BLOCKED receipt emitted → mission queue intact.
5. Transient rate limit → bounded jittered retry ≤ 3 attempts → failover to next provider.

## Configuration surface

No credentials are stored in this document. Provider registration and credential binding occur through the existing authenticated configuration system. The router reads provider health, model registry, and cost policy from the in-memory configuration layer only.
