# ©️8x8 by FlashTM8 ⚡️🌎🤖 — One ID, many carriers, no owner-private core

**Authority:** `fabric://8x8/core` · **Status:** SOURCE-ONLY RELEASE REVIEW · **Public version:** 0.0.1 Beta. Nothing below promotes a future capability to a live service. Use `docs/data/ONE_FABRIC_PUBLIC_DISTRIBUTION_STATE_V1.json` for the separately versioned claims and blockers. Public-safe source, not a credential or a grant.

## Public user experience (product contract)

A person should enter from a trusted Web/PWA address, the official Wix discovery site, Telegram Mini App, Discord integration, signed Android client, or independently approved ChatGPT MCP plugin; each is a *carrier*, not an independent 8x8 authority. An 8x8 ID belongs to exactly one ordinary isolated tenant. Use a provider-specific authorization code/session exchange only after real server verification; never trust a URL parameter, Telegram `initDataUnsafe`, a Discord username, a Telegram user ID, an unverified JWT, or a ChatGPT model prompt as proof of identity. Bind every tool invocation to exact user + tenant + action + scope + time + idempotency key. The owner private root is never exposed.

### The simple journey when each carrier is actually released
1. Discover 8x8 through the verified public page; read the current availability badge linked to the *actual release receipt*, not a hardcoded marketing claim.
2. Open the already-released carrier. Sign in or create your own 8x8 ID through the canonical, protected auth service. On every carrier, the identity provider performs its own verified account linking.
3. Choose an agent and capability (research, creation, learning, Studio, accessibility or tools). The agent only receives capabilities approved for this tenant. A fictional/avatar identity does not prove an agent is executing.
4. Grant specific connectors using provider-approved OAuth and opaque Vault handles. Tools show `REGISTERED → REACHABLE → HEALTHY → AUTHENTICATED → GRANTED → LEASED → STARTED → PRODUCTIVE → VERIFIED`, with independent evidence. The latest status cannot be inferred from a screenshot or code.
5. Launch a task; preserve progress and only report completed outcomes with real artifact/receipt. When a provider quota expires, propose an authorized native or alternative route, or explicitly label a partial deliverable.
6. See usage, limits, subscription status, device grants, STOP and revoke controls. The historical target is *88 minutes* of usage and *USD 8.88 per month*; the exact period, included operations, throttles, taxes, refund policy and billing availability must be proven and disclosed **before charging**. Do not advertise these as currently live or as literally unlimited compute.

## Surface acceptance, not fake parity

- **Browser/Vercel:** canonical public URL, six distinct routes, secure login, privacy, performance, accessibility, PWA install and offline failure state. A `READY` deployment from an unmerged review branch is only a deployment state, not production acceptance. Current public guide: `https://8x8-os-ecosystem.vercel.app` (status must be rechecked).
- **Wix:** existing published site `https://8x8org.wixsite.com/my-site-6`; link or embed *only* the approved public-safe app with correct HTTPS, CSP/frame policy and account session. Wix may be discovery, blog, SEO and marketing first; it must not duplicate the private 8x8 control plane or create independent subscription identities.
- **Telegram:** already existing Mini App source must validate the exact signed `Telegram.WebApp.initData` server-side, enforce freshness/replay and tenant linking, use Bot API permission checks, and never trust `initDataUnsafe` as authentication. Bot menu binding and a rendered HTML preview do not prove a signed data-plane session. Reference: https://core.telegram.org/bots/webapps.
- **Discord:** app/Activity or bot must follow Discord developer approvals and OAuth scopes, validate signed interaction requests, and use a tenant-bound session. Server membership and a visible UI do not grant permission to another person's account; limit outbound messaging and moderator actions.
- **Android/APK:** publish a versioned signed APK/AAB and signed release manifest; verify APK SHA-256, signing certificate, package identifier, install, migration and rollback. Do not point users to a draft source archive or unsafe unverified APK. Separate the basic Android app from optional advanced device companion.
- **ChatGPT 8x8 MCP:** deliver a genuine **remote HTTPS** MCP resource with standards-compliant OAuth, per-user scopes and audience validation; approved discoverable plugin metadata and optional skills only through the actual OpenAI review/installation mechanism. ChatGPT account/plan/workspace permissions and web-first custom MCP setup vary; no universal mobile automatic install and no blanket ability of ChatGPT to control 8x8. Official references: https://developers.openai.com/api/docs/mcp and https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt.
- **Skills:** share public-safe versioned and signed skill bundles when the host client supports installation and verification; user agents must never consume the private root or retrieve owner-only secrets. Installing a skill is not a grant to execute the full capability.
- **iOS and future wearable/robot/XR:** advertise only when a genuine client/hardware release is qualified. No iPhone App Store or physical embodiment claim from a source-only worker.

## Optional Android device linking (advanced, only after accepted signed client release)

An ordinary user should use 8x8 without ADB. A user choosing advanced local device actions installs a **signed, reviewed public companion** from a release with exact version, APK hash and signer identity. The existing owner-repository user bootstrap is a possible reviewed donor, not a public download command. **Do not distribute the private repository.** No `curl | bash` installation, hidden scanning, silent permission escalation, remote shell, or owner keys.

Safe opt-in setup concept:
1. Create an ordinary tenant account and use a device-local consent screen to choose permitted operations (view/screen control/storage/shell/sensors/audio are distinct grants).
2. On a supported Android device, the owner manually enables developer options and wireless debugging if needed. Pair with a *trusted same-LAN* host using the Android screen's pairing-code workflow. Never paste pairing codes, raw serials or ADB addresses into a public chat or central 8x8 service.
3. Use a trusted, locally installed platform-tools client and user-controlled temporary pairing prompt. After pairing, bind the user's own companion to their own tenant using a short-lived one-time authorization challenge, device-bound credentials and independent server verification.
4. Never expose ADB TCP ports to the open Internet. For remote use from elsewhere, the *application-level* companion initiates an authenticated encrypted outbound session; server actions require narrow scoped leases, explicit sensitive-action approvals, real STOP/revoke controls and observable receipts. An 8x8 cloud login alone is **not** an ADB grant.
5. Provide visible disconnect, token rotation and uninstall options. For Android, users can forget a paired host or revoke debugging authorizations in system settings; an old cloud account token must not reactivate a revoked local device. Official reference: https://developer.android.com/tools/adb.

**Install command publication gate:** Do not publish any executable `8x8 install` shortcut, shell snippet, QR installer, package hash or package-signing claim until the immutable release and verified public CDN asset exist. Show a real guide and honest unavailable state instead of inventing a working command.

## Economic and access fairness
- Proposed `88` free minutes should be server-accounted with clear local-day definition, abuse resistance, persisted entitlements, device-independent identity and receipts; duplicate Telegram, Discord and ChatGPT logins must not create separate unearned quotas. Treat existing sandbox code as not-production.
- Proposed `$8.88/month` requires an actual payment-provider contract, webhook signature, chargeback/refund/renewal/cancel tests and consumer disclosures. Paid service is never authorization for physical actions, financial trades or private data.
- Public/free services should remain available at declared limits and degrade transparently to local alternatives or queueing, rather than claiming unbounded server resources.
- Accessibility: WCAG-based accessible 2D interface, keyboard/screen-reader support, captions, reduced motion, low-bandwidth and multilingual modes are first-class. Human and animal welfare projects use expert-approved safe workflows; no claims of universal capability.

## Source/private boundary and observability
- Public CDN: minimum client HTML/JS/icons/manifest, documented APIs. Browser bytecode/JavaScript cannot be hidden; private algorithms, Vault, orchestrator, 212-agent historical identity data and owner resources stay in the private service.
- Every carrier consumes the same signed API release identity and capability/entitlement policy; never invent parallel tenant roots or create a sixth scheduler. All replicas show provenance/last-verified timestamps.
- For each carrier record `PRESENT_PROVEN`, `SOURCE_PRESENT` or `FUTURE_GATED`, required release SHA/artifact hash/URL, runtime client/device, login result, cross-tenant denial, STOP/revoke, cost, p95 latency, recovery receipt and rollback.
- Preserve research donors and 1,000+ historical URL/link/power ideas under the canonical source graph; candidate links are NOT installed functions, approved licenses or live features. Reuse existing code/PRs and reconcile overlapping V50 branches before accepting release.

## Launch acceptance gates
No universal launch until the six existing product gates close at a reconciled immutable head: authenticated Web/PWA, artifact provenance, signed Android, 8x8 ID/MCP, Studio/World real task, and agent/owner controls. Add per-carrier entrypoint tests and one complete two-tenant task where source → grant → execution → result → independent receipt → visible output remains identical across web and another authorized carrier. No `Top-1` or `100%` without external benchmarks and a closed denominator.


## Guided everyday and advanced 8x8 scenarios

These are **intended use cases and acceptance examples**, not assertions that every workflow is currently released. Check the exact public product version and status at https://github.com/8x8org/8x8-user-edition and https://github.com/8x8org/.github/blob/main/CURRENT_PUBLIC_STATE.md before entering sensitive data.

| Who | Example request after authenticated release | Required real result | Main release limitation |
|---|---|---|---|
| Student | "Teach photosynthesis in Arabic and English; quiz me" | source-backed lesson, accessible quiz, saved consented progress | education quality and signed-in memory not yet accepted |
| Creator | "Make a 30s original subtitled trailer from licensed media" | actual verified playable video, rights, artifact hash and review draft | a script/storyboard is partial, not a rendered film |
| Accessibility user | "Read this file aloud; provide large text" | authorized text/audio and accessible interaction | rights, voice consent and hardware tests |
| Developer | "Improve this app, run tests and prepare a rollback" | inspectable code diff, test and source identity | no private repo or deployment grants by default |
| Small business | "Draft a service FAQ and propose approved support automation" | reviewed draft and individually authorized connectors | no unapproved customer outreach or billing |
| Scientist | "Compare credible sources and reproduce a calculation" | links, methodology, verifiable computation | research and domain qualification |
| Animal-care volunteer | "Make multilingual adoption materials from provided facts" | accurate accessible poster/text with human approval | no unsupported veterinary or partnership claim |
| Player | "Enter a moderated friends-only World room" | an identity-bound session and revocable invites | source for a World is not proof of live multiplayer |
| Advanced device user | "Connect my phone and approve one diagnostic action" | local device consent, short lease, STOP and receipt | signed companion and device acceptance gated |
| Finance learner | "Run paper trading simulations and explain risk" | simulated dataset and labeled results | no real orders, wallet signing or guaranteed return |
| Film team | "Version dialogue, natural voices and captions for my scene" | rights-cleared voice/media asset and reviewed provenance | no unconsented impersonation or invented founder likeness |
| XR/robotics researcher | "Simulate a safe navigation mission" | simulation, collision and safety verification logs | no assumption of independently actuated physical robot |
| NGO/community organizer | "Draft an accessible event and invite outline" | opt-in invitation drafts | no unsolicited mass messaging |
| Founder/private operator | "Show release evidence and dispatch one approved task" | private authenticated controls with scoped receipts | not a public User Edition feature |

### What a new public user does
1. Inspect the public User Edition and the current state at the links above. The beta discovery carrier is https://8x8-os-ecosystem.vercel.app; its current sign-in and feature status must be verified before use.
2. Open a genuinely released client and authenticate with a personal isolated 8x8 ID. A Telegram handle, Discord nickname or ChatGPT message is not proof of 8x8 authentication.
3. Choose the required capability, then approve only its specific connector scopes. Do not upload secrets, private keys, passwords or sensitive documents to an unauthenticated demo.
4. Ask the agent to execute a bounded job and inspect the actual output and provenance. See limitations and authentic use/read-only/STOP status instead of false green lights.
5. Revoke individual connector/device permissions and confirm the change. One linked user may operate multiple explicitly paired clients, not inherit the founder's rights.

### How to use 8x8 across surfaces
- **Web and Wix:** Start with public project status and the existing published Wix discovery site https://8x8org.wixsite.com/my-site-6. A published site is not automatically an accepted authenticated 8x8 product.
- **Telegram:** The Mini App release must first prove server-side signed session validation; https://core.telegram.org/bots/webapps describes the platform. Do not treat a bot menu link as authorization.
- **Discord:** An approved integration must use Discord OAuth/interaction validation and map the account to the individual's 8x8 ID. An ordinary server invite is not a tool grant.
- **Android:** Use the future officially signed 8x8 APK only after the release receipt and signing certificate are independently checked. Normal user journeys do not need ADB or command lines.
- **Advanced optional device pairing:** A user manually pairs their own Android device with a trusted nearby computer; see https://developer.android.com/tools/adb. No raw pairing codes in chat, no public-network ADB endpoint, no indefinite shell authority. iPhone has different native permission requirements.
- **ChatGPT MCP:** Search for the 8x8 plugin only when officially published. Custom remote MCP server connections are not universally installable from all ChatGPT mobile clients and may require an eligible managed workspace; https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt. Remote HTTPS/tunnel, tenant-bound OAuth and explicit plugin permissions are mandatory.
- **Skills:** An installable public skill bundle needs its own publisher identity, version, rights, hash and per-capability permission review; it is not the owner-private software.
- **88 free minutes and $8.88/month:** These are proposed plan parameters, not live payment instructions. The final product must display usage counting, reset windows, provider restrictions, cost, cancellation and refund policy before collecting a charge.

### Failure and support examples
**No account service:** Use the public demo without sharing private information; report the feature as unavailable rather than creating a fake local 8x8 ID.

**Provider quota reached:** Preserve the task, check an eligible exact-output native fallback, or deliver a clearly labeled draft/partial result. Do not bypass provider terms by rotating accounts.

**Lost or unsafe device session:** Stop and revoke the individual device grant locally and at the service boundary; do not retry remote control until reauthenticated.

**Need support or contribution:** Use public issues/discussions at https://github.com/8x8org/8x8-user-edition and public organization governance at https://github.com/8x8org/.github, with sanitized descriptions only.

Every real scenario needs a current exact-source client, authenticated account/tenant, granted scoped capability, genuine execution, verified artifact or action, revocation and an evidence receipt. Label PREVIEW_ONLY or UNAVAILABLE wherever any necessary gate is missing.

