# V56 Live Membership Activation

Canonical root: `fabric://8x8/core`

## Access policy

Free users receive exactly 88 minutes of active foreground/interacting use per allowance window. Idle/background time must not consume quota. When the authoritative remaining value reaches zero, the user enters `LOCKED_FREE_QUOTA`; `unlock_at` is exactly 24 hours after exhaustion. The server clock is authoritative. Clearing local storage, changing a device clock, reinstalling a client, or switching between Web, Telegram Mini App and User Edition must not reset quota.

An active paid membership overrides the free-quota lock immediately and remains unlocked while the paid entitlement remains active.

## Payment state

`PAYMENT_CREATED -> PAYMENT_SEEN -> CONFIRMING -> CONFIRMED -> RECONCILED -> MEMBERSHIP_ACTIVE`

A client-supplied transaction hash is never proof by itself. Server-side verification must match the configured chain/network, receiving destination, required amount/reference and network finality before reconciliation.

## Direct rails

BTC, ETH, BNB, SOL, TON and PI are direct-crypto membership rails. Stripe is not required for this lane.

## Safety separation

Membership payment confirmation does not authorize native 8x8 mainnet launch, wallet signing, token minting, NFT minting, funds movement, live exchange execution or airdrop distribution. Those remain independently gated.

## Truth boundary

A rail may be shown as configured after its destination is owner-provided, but may be labeled `LIVE` only after the production verifier for that rail is deployed and passes an end-to-end payment reconciliation test.
