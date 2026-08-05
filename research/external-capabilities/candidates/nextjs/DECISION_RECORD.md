# MSG197-NEXT-001 Static Client versus Next.js Decision

## Decision

`DEFER_STATIC_CLIENT_REMAINS_CANONICAL`

The observed upstream pin is from Next.js `canary`, which is unsuitable as a production dependency selection. The current User Edition delivers public-safe static assets on Vercel without a server runtime, server actions, middleware, authenticated server sessions or framework-specific routing.

Moving to Next.js now would add server and middleware attack surfaces, cache/revalidation complexity, framework supply-chain exposure and new operational ownership without a requirement the static client cannot satisfy.

## Reopen conditions

A migration can be reconsidered only after a specific product requirement is approved, a stable release is pinned, a server owner is named, the data-boundary threat model is accepted, bundle and hosting budgets are measured, logged-out privacy tests pass and rollback to the static client is rehearsed.

No framework installation, hosting change or migration is authorized.
