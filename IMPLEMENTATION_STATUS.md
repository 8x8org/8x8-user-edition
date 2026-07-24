# Implementation Status

**Release candidate:** `0.1.0-beta`

| Capability | State | Evidence |
|---|---|---|
| Public repository foundation | RECEIPT_VERIFIED | Organization bootstrap receipt held in the private governance repository |
| Responsive public cockpit | IMPLEMENTED | `index.html`, `styles.css`, `app.js` |
| Agent archetype explorer | IMPLEMENTED | Local-only cards and detail drawer |
| Conceptual spatial world view | IMPLEMENTED | Local CSS/DOM visualization, no location tracking |
| Public truth ladder | IMPLEMENTED | Interactive nine-stage evidence model |
| Public/private security statement | IMPLEMENTED | UI, `SECURITY.md`, `state/public-state.json` |
| Progressive web app shell | IMPLEMENTED | Manifest, icon and service worker |
| Static deployment security headers | IMPLEMENTED | `vercel.json` |
| CI validation | IMPLEMENTED | `.github/workflows/validate-public-beta.yml`; earlier runs on `main` failed on scanner false-positives, corrected in the public-readiness branch |
| Live public deployment | DEPLOYMENT_CANDIDATE | Requires a successful hosting deployment and URL verification |
| Root license | BLOCKED_PENDING_OWNER_DECISION | No `LICENSE` file exists; owner legal decision required, explicit release blocker |
| Private vulnerability reporting | PENDING_OWNER_ACTION | GitHub private vulnerability reporting is not yet enabled for this repository |
| Signed installer | DESIGNED | Not released |
| User accounts and passkeys | DESIGNED | Not implemented in this beta |
| USD 8.88 subscription | CLAIMED TARGET | Billing is not live |
| 88 daily service minutes | CLAIMED TARGET | Entitlement service is not live |
| Voluntary compute/storage node | DESIGNED | Disabled and not released |
| Remote support | DESIGNED | Disabled and not released |
| Live trading, staking or rewards | NOT AUTHORIZED | Excluded from this beta |
| Private control-plane access | DENIED | No connector or code path exists in this repository |

## Beta acceptance criteria

The beta can be labeled `DEPLOYED` only after:

1. the public URL returns the intended HTML cockpit;
2. static assets load successfully;
3. security headers are present;
4. no private endpoint, wallet address, credential, terminal executor or fake live status is exposed;
5. `state/public-state.json` remains public-safe;
6. the exact deployment revision is recorded.

It can be labeled `PUBLICLY_RELEASED` only after a versioned GitHub release, changelog, provenance and public announcement packet exist.
