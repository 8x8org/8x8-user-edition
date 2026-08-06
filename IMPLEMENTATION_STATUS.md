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
| Root license | IMPLEMENTED | Apache License 2.0 published in `LICENSE` after explicit owner approval |
| Private vulnerability reporting | PENDING_OWNER_ACTION | GitHub private vulnerability reporting is not yet enabled for this repository |
| Signed installer | DESIGNED | Not released |
| User accounts and passkeys | DESIGNED | Not implemented in this beta |
| USD 8.88 subscription | CLAIMED TARGET | Billing is not live |
| 88 daily service minutes | CLAIMED TARGET | Entitlement service is not live |
| Voluntary compute/storage node | DESIGNED | Disabled and not released |
| Remote support | DESIGNED | Disabled and not released |
| Live trading, staking or rewards | NOT AUTHORIZED | Excluded from this beta |
| Private control-plane access | DENIED | No connector or code path exists in this repository |
| Agent body and capability registry | REGISTRY_PUBLISHED | `registry/AGENT_BODY_AND_CAPABILITY_REGISTRY.json` — public-safe archetypes, no private runtime |
| Model provider routing registry | REGISTRY_PUBLISHED | `registry/MODEL_PROVIDER_ROUTING_REGISTRY.json` — V2 design, free-lane-first policy |
| Connector and social adapter registry | REGISTRY_PUBLISHED | `registry/CONNECTOR_AND_SOCIAL_ADAPTER_REGISTRY.json` — adapter architecture, X/Facebook/TikTok disabled |
| Testnet economy registry | REGISTRY_PUBLISHED | `registry/TESTNET_ECONOMY_REGISTRY.json` — testnet only, no mainnet, no financial promises |
| Studio language and media registry | REGISTRY_PUBLISHED | `registry/STUDIO_LANGUAGE_AND_MEDIA_REGISTRY.json` — language-registry architecture, no fixed language list |
| Public release train | REGISTRY_PUBLISHED | `registry/PUBLIC_RELEASE_TRAIN.json` — four release lanes documented |
| Convergence scorecard | REGISTRY_PUBLISHED | `registry/100_PERCENT_CONVERGENCE_SCORECARD.json` — per-lane scores, whole-system NOT_INFERRED |
| Community operations policy | PUBLISHED | `COMMUNITY_OPERATIONS_POLICY.md` |
| Continuous operations runbook | PUBLISHED | `CONTINUOUS_OPERATIONS_RUNBOOK.md` |
| MSG233 receipt | PUBLISHED | `LATEST_MSG233_RECEIPT.md` |

## Beta acceptance criteria

The beta can be labeled `DEPLOYED` only after:

1. the public URL returns the intended HTML cockpit;
2. static assets load successfully;
3. security headers are present;
4. no private endpoint, wallet address, credential, terminal executor or fake live status is exposed;
5. `state/public-state.json` remains public-safe;
6. the exact deployment revision is recorded.

It can be labeled `PUBLICLY_RELEASED` only after a versioned GitHub release, changelog, provenance and public announcement packet exist.


The beta can be labeled `DEPLOYED` only after:

1. the public URL returns the intended HTML cockpit;
2. static assets load successfully;
3. security headers are present;
4. no private endpoint, wallet address, credential, terminal executor or fake live status is exposed;
5. `state/public-state.json` remains public-safe;
6. the exact deployment revision is recorded.

It can be labeled `PUBLICLY_RELEASED` only after a versioned GitHub release, changelog, provenance and public announcement packet exist.
