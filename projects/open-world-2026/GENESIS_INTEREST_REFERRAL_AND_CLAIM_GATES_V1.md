# ©️8x8 by FlashTM8 ⚡️🌎🤖 — Interest, Referral & Future Genesis Claim Gates V1

**Canonical root:** `fabric://8x8/core`  
**Date:** 2026-11-01 · **State:** REVIEW_SOURCE_ONLY / NO VALUE EFFECTS  
**Companion:** Public issue #205, review PR #204, private native-chain acceptance issue [horbolsi/8x8-blockchain#41](https://github.com/horbolsi/8x8-blockchain/issues/41).

This artifact reconciles the user's requested invitee form, 8x8 ID, Telegram identifier, reference-code entry in Gate 3, future onchain purchase, treasury settlement, Genesis Vault and airdrop **without implying that any real financial flow has launched**. The inherited canonical `core/presale_api.py` continues to return 423 with `sale_open=false` and `registration_open=false`. It must not be bypassed.

## Live/nonfinancial user entry

- **Official event:** https://github.com/8x8org/8x8-user-edition/issues/205 — verified public announcement, not a deployed full app.
- **External community-interest form:** https://form.jotform.com/263041117453044 — form build reported completed on Nov 1, 2026. Independent external submission, retention and privacy-path acceptance remain open.
- **Interest meaning:** Nonbinding expression of interest. No paid reservation, coin, NFT, airdrop eligibility, claim, priority, verified 8x8 ID, wallet enrollment or financial reference code is created.
- **Personal data:** Ask consent separately for contact and optional communications; prefer email only as required; 8x8 ID, Telegram username and referrer are optional. Never require wallet keys, seed words, Telegram verification codes, passports or bank details in this interest form. Do not publish respondents' data.
- **Privacy prerequisite before promotion:** Complete the user-facing data-controller identity, retention/deletion request channel, optional-email consent, approved external processor disclosure and verified removal workflow. A public GitHub issue is not an appropriate place for personal data.
- **Support link:** https://buy.stripe.com/bJe4gz0aUcOD7N93Fr4Rq01 is separately documented as optional **project support only**, not a purchase of assets, launch access or future rights.

## Separate immutable event classes

| Event | Authoritative proof | Economic effect |
|---|---|---|
| INTEREST_RECEIVED | Third-party form submission with opt-in & source receipt | None |
| INVITATION_ATTRIBUTED | Signed, tenant-bound referral event; consented / rate-limited | None |
| ACCOUNT_AUTHENTICATED | Production 8x8 ID provider assertion with tenant denial tests | None |
| WALLET_AUTHENTICATED | Chain-specific nonce+domain+expiry signature & address binding; no private keys | None |
| OFFER_ELIGIBLE | Reviewed jurisdiction, exact disclosure/terms, eligibility/risk checks | None |
| CHECKOUT_AUTHORIZED | Eligible payment rail, signed owner production release approval | Pending only |
| PAYMENT_SETTLED | Verified PSP webhook + provider API readback OR qualified onchain finality + ledger reconciliation; idempotent | Customer liability, not tokens minted |
| ALLOCATION_APPROVED | Independently reconciled supply cap, contract terms, governance/treasury proof | Bounded, specifically contracted entitlement only |
| CLAIM_REFERENCE_ISSUED | Random opaque, expiring, one-time code; server stores keyed hash; bound to tenant/account/settlement/allocation; never includes PII | Unlocks claim eligibility check, not custody |
| GENESIS_FINALIZED | Audited native Genesis & multi-node chain receipt, signed distribution roots | Native asset ready under exact rules |
| CLAIM_EXECUTED | Authenticated signature, chain-specific transaction, finality, vesting, idempotency, explorer verification | Actual coin transfer only on chain |
| CLAIM_REVOKED / REFUNDED | Original settlement refund/chargeback, appeal/audit receipt | Blocks duplicate or improper claims |

**Critical invariants:**
1. An email, referral code, interest receipt or optional support payment **must never** be promoted into allocation.
2. A claim code does **not** prove payment by itself. Every redemption revalidates issuer signature, tenant, offer/eligibility, settlement/finality, allocation, expiration, one-time use, chain ID and current STOP/revocation policy.
3. All issued reference codes must be cryptographically random with at least 128 bits entropy; only a keyed digest is stored server-side. Rate-limit entry attempts and reject cross-tenant reuse.
4. Webhook events are untrusted until cryptographic verification and provider-side status readback. Duplicate, out-of-order, refunded and chargeback events cannot create double liabilities or coin distribution.
5. User visible states distinguish **interest**, **pending payment**, **settled liability**, **approved allocation**, **locked vesting balance**, **claimable balance** and **actually received coins**. Never say that someone owns withdrawable assets merely because a database shows a pending entry.
6. Distinct ledger accounts must separate operating donations, subscriptions, pending settlement, token-sale liabilities (when authorized), treasury custody, network supply, Vault backing and unlocked claims.
7. Keep `8x8` native-network asset identity unique; external USDT/USDC/BTC/other accepted rail requires explicit verified chain, contract, custody, processor support, sanctions/AML handling, refund rules and per-asset qualification. No universal "any wallet/any coin" claim.
8. Show full consideration, fees, rounding, unlock dates (if approved), cancellations and risks before any future paid checkout. A reference quote ($8.88) is not a traded price or investment forecast.
9. No unattended owner-wallet signing, mainnet activation, live mint, distribution, LP funding or financial publication from this public-facing project. These require exact authenticated, owner-controlled financial release authority and independent receipts.

## Future Gate 3 user experience

1. The user signs into their own 8x8 ID, including a separately consented account link with Telegram if supported.
2. The user can view **interest** and nonfinancial invitation attribution separately from the wallet or assets.
3. Once a legally/technically accepted paid offer actually opens, the user purchases on a clearly labeled rail. Settlement and allocation verification are asynchronous and independently read back.
4. Only then may Gate 3 show a verified reference code and a signed `CLAIM_REFERENCE_ISSUED` receipt. A submitted code rechecks the exact tenant and current allocation.
5. Before mainnet, a legitimate future contractual right may be shown as **conditional/locked and nonwithdrawable**, never as already-minted coins or available funds.
6. Mainnet claim must be opt-in and bound to the user's chosen, independently authenticated wallet/network with onchain finality evidence. Revoked, refunded, blocked or ineligible claims fail closed.
7. Accessible support offers ticket submission, agent triage with limited scopes and human appeal. No promise of autonomous resolution or 24/7 response until measured.
8. A nonfinancial invitation link can be shared now, but financial referral rewards and airdrop bonuses remain disabled. Build referral click/event consent, anti-Sybil protection and abuse appeals before any reward policy is proposed.

## Acceptance matrix (current = gated)

- [ ] Verify external form desktop/mobile submission, retention and privacy access/deletion mechanism; no automated emails until opted in.
- [ ] Authenticate two independent real 8x8 ID tenants, ensure cross-tenant/admin/OWNER_ROOT denial, auth expiration/revocation.
- [ ] Prove nonfinancial invitation attribution and rate limiting, no payment/entitlement creation.
- [ ] Verify PSP/webhook and/or native payment adapter in sandbox, including duplicate, reversed, fraudulent, delayed and mismatch events.
- [ ] Reconcile double-entry liabilities vs settled assets vs treasury, immutable provider receipt ids and auditable voids.
- [ ] Require explicit signed financial release gate and counsel/provider eligibility before accepting a real paid order.
- [ ] Prove signer-free Genesis devnet, two independent native nodes, cap/conservation, Vault segregations and 8x8Scan consistency.
- [ ] Test claim code tenant binding, opacity, expiration, one-time use, brute-force throttling and refund invalidation.
- [ ] Test actual locked/unlocked user-visible balances against native verified chain state, not synthetic cards.
- [ ] Test accessibility, receipt export, refunds/complaints, STOP, rollback and disaster recovery.
- [ ] Recheck present exact production URLs, source hashes, PR status and independent customer session before releasing launch claims.

**Current result:** This is a review-only specification. Creating the form is real progress on nonfinancial community enrollment; it does **not** change sale readiness, mint any coins, deploy Gate 3, enable crypto reception, publish a new film or create active referral rewards. No irreversible financial effects.