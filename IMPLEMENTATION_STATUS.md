# Implementation Status

**Canonical product version:** `0.0.1 Beta`

Historical MSG labels, branch names, commit SHAs and internal implementation generations are preserved as provenance. They are not product-maturity versions.

| Capability | State | Evidence |
|---|---|---|
| Public repository foundation | RECEIPT_VERIFIED | Organization bootstrap receipt held in the private governance repository |
| Fabric Mirror / responsive public cockpit | IMPLEMENTED | `index.html`, `styles.css`, `app.js` |
| Three-Reality public projection | IMPLEMENTED | `public/reality-snapshot.json`, public UI |
| Agent archetype explorer | IMPLEMENTED | Local-only cards and detail drawer |
| Conceptual spatial world view | IMPLEMENTED | Local CSS/DOM visualization, no location tracking |
| Public truth ladder | IMPLEMENTED | Evidence-gated UI and docs |
| Public/private security statement | IMPLEMENTED | UI, `SECURITY.md`, `state/public-state.json` |
| Progressive web app shell | IMPLEMENTED | Manifest, icon and service worker |
| Static deployment routing/security headers | IMPLEMENTED | `vercel.json` |
| Product-version drift validation | IMPLEMENTED | `.github/workflows/validate-public-beta.yml` rejects public 0.1.x/v0.1.1 maturity strings |
| CI validation | IMPLEMENTED | GitHub Actions validation and public-information-boundary checks |
| Canonical Vercel deployment | BLOCKED | A READY deployment tied to the canonical repository has not yet been verified |
| Historical Vercel carrier | DEPLOYED_HISTORICAL | Existing historical carrier may be READY but is not proof of canonical User Edition deployment |
| Android logged-out route certification | BLOCKED | Screenshot evidence shows 404 for the failed deployment URL; recertification required |
| Root license | IMPLEMENTED | Apache License 2.0 in `LICENSE` |
| Private vulnerability reporting | PENDING_OWNER_ACTION | Enable GitHub private vulnerability reporting when available |
| Signed installer | DESIGNED | Not released |
| User accounts and passkeys | DESIGNED | Not implemented in this beta |
| USD 8.88 subscription | CLAIMED TARGET | Billing is not live |
| 88 service minutes | CLAIMED TARGET | Entitlement service is not live |
| Voluntary compute/storage node | DESIGNED | Disabled and not released |
| Remote support | DESIGNED | Disabled and not released |
| Live trading, staking or rewards | NOT AUTHORIZED | Excluded from this public beta unless separately owner-gated |
| Private control-plane access | DENIED | No connector or code path exists in this repository |

## Deployment acceptance criteria

The canonical public beta can be labeled `DEPLOYED` only after all of the following are true for the exact reviewed commit:

1. a real Vercel project and deployment record exists for the canonical User Edition source;
2. deployment state is READY;
3. `/`, `/first-blink`, `/world`, and `/art-board` return HTTP 200;
4. route documents return `Content-Type: text/html`;
5. no route emits `Content-Disposition: attachment`;
6. logged-out Android Chromium renders the interface;
7. logged-out mobile Safari renders the interface;
8. security headers and public-information-boundary checks pass;
9. project ID, deployment ID, source commit and rollback target are recorded in a deployment receipt;
10. no private topology, protected inventory, secret material or privileged authority is exposed.

A release can be labeled `PUBLICLY_RELEASED` only after exact-head validation, a versioned GitHub release/changelog/provenance packet, and deployment evidence exist. Whole-system maturity remains `0.0.1 Beta` until an explicit owner-approved promotion.
