(()=>{
'use strict';
const X=(key,name,family,state,desc)=>({key,name,family,state,desc});
const EXTRA=[
X('journey.root_load','Root Load + Reload Persistence','journey','SOURCE_PRESENT','Root load, state restoration and reload persistence are explicit acceptance surfaces.'),
X('journey.login','Login','journey','SOURCE_PRESENT','Authenticated sign-in journey with separate runtime verification.'),
X('journey.register','Registration','journey','SOURCE_PRESENT','User registration journey with canonical identity issuance requirements.'),
X('journey.logout','Logout + Session Revoke','journey','SOURCE_PRESENT','Explicit logout, session revocation and negative-authentication verification.'),
X('journey.world_stage','World Stage','journey','SOURCE_PRESENT','World-stage transition and carrier integration.'),
X('journey.workbench','Workbench','journey','SOURCE_PRESENT','Operational user workbench for files, terminal, agents and device mesh.'),
X('proof.acceptance','Proof Acceptance','proof','SOURCE_PRESENT','Per-capability evidence, second-pass verification, receipt, rollback and freshness.'),
X('workbench.terminal_run','Terminal Run','workbench','EFFECT_GATED','Tenant-scoped terminal execution through explicit semantic authority.'),
X('workbench.files_list','Files List','workbench','SOURCE_PRESENT','Browse tenant-visible file collections.'),
X('workbench.file_read','File Read','workbench','SOURCE_PRESENT','Read permitted file content with provenance.'),
X('workbench.file_write_backup','File Write + Backup','workbench','EFFECT_GATED','Write permitted files with backup/rollback semantics.'),
X('workbench.system_status','System Status','workbench','SOURCE_PRESENT','Runtime, health, readiness and capability-state inspection.'),
X('workbench.agent_control','Agent Control','workbench','EFFECT_GATED','Address, start, stop, lease and revoke bounded agents.'),
X('device.mesh','Device Mesh','devices','SOURCE_PRESENT','Identity-bound device discovery, health and capability topology.'),
X('device.wireless_status','Wireless Status','devices','SOURCE_PRESENT','Read wireless/device-link state.'),
X('device.open_wireless_settings','Wireless Settings','devices','EFFECT_GATED','Open device wireless settings through approved local intent.'),
X('device.pair','Pair Device','devices','EFFECT_GATED','Pair an approved device under explicit identity and lease.'),
X('device.connect','Connect Device','devices','EFFECT_GATED','Connect to a previously approved device endpoint.'),
X('device.test_control','Test Device Control','devices','EFFECT_GATED','Run reversible canary device actions before broader control.'),
X('device.open_app','Open App','devices','EFFECT_GATED','Launch an approved app on an identified device.'),
X('device.verify_foreground','Verify Foreground App','devices','SOURCE_PRESENT','Confirm expected foreground app/state without assuming success.'),
X('device.home_back','Home + Back Navigation','devices','EFFECT_GATED','Bounded device navigation primitives.'),
X('device.revoke','Revoke Device Lease','devices','SOURCE_PRESENT','Emergency revoke and capability lease termination.'),
X('jarvis.start_stop','Agent Session Start / Stop','voice','SOURCE_PRESENT','Explicit embodied-agent session lifecycle.'),
X('jarvis.press_to_talk','Press To Talk','voice','SOURCE_PRESENT','Mic opens only for an explicit speaking window.'),
X('jarvis.text_turn','Text Turn','voice','SOURCE_PRESENT','Text conversation without requiring camera or microphone.'),
X('jarvis.agent_voice_test','Agent Voice Test','voice','SOURCE_PRESENT','Per-agent voice output canary.'),
X('jarvis.local_speaker_test','Local Speaker Test','voice','SOURCE_PRESENT','Local speaker-output canary independent from microphone capture.'),
X('jarvis.speaker_toggle','Speaker Toggle','voice','SOURCE_PRESENT','Explicit speaker enable/disable control.'),
X('jarvis.camera_foreground','Foreground Camera','voice','EFFECT_GATED','Camera access only through explicit foreground intent.'),
X('jarvis.browser_frame_decode','Browser Frame Decode','voice','SOURCE_PRESENT','Visual-frame reasoning for user-provided/foreground browser context.'),
X('jarvis.barehand_toggle','Barehand On / Off','spatial','SOURCE_PRESENT','Explicit activation and release of Barehand tracking.'),
X('jarvis.media_release','Media Release','voice','SOURCE_PRESENT','Stop camera/mic tracks on completion, hide, unload or revoke.'),
X('mail.shell','Mail Shell','mail','SOURCE_PRESENT','8x8 Mail operational shell.'),
X('mail.me','Mail Me','mail','EFFECT_GATED','Send owner/user-addressed mail through an authenticated connector.'),
X('mail.materialization','Mailbox Materialization','mail','SOURCE_PRESENT','Materialize permitted mailbox state into tenant scope.'),
X('mail.alias_queue','Alias Queue','mail','SOURCE_PRESENT','Identity-bound alias and routing queue.'),
X('mail.agent_lease','Mail Agent Lease','mail','EFFECT_GATED','Lease bounded mail actions to an agent.'),
X('mail.sync_connector','Mail Connector Sync','mail','EFFECT_GATED','Sync authenticated mail connector state.'),
X('mail.privacy_policy','Mail Privacy Policy','mail','SOURCE_PRESENT','Privacy, retention and tenant-boundary policy surface.'),
X('connectors.catalog_discovery','Connector Catalog Discovery','connectors','SOURCE_PRESENT','Discover available connectors without equating discovery with authorization.'),
X('connectors.setup_open','Connector Setup','connectors','SOURCE_PRESENT','Open connector setup and permission flow.'),
X('connectors.authenticated','Connector Authentication','connectors','SOURCE_PRESENT','Authenticated state tracked separately per provider.'),
X('connectors.granted','Connector Grants','connectors','SOURCE_PRESENT','Scope/permission grants tracked separately from authentication.'),
X('connectors.read_productive','Connector Read Productivity','connectors','SOURCE_PRESENT','Verify a real useful read, not merely a successful OAuth handshake.'),
X('connectors.write_lease','Connector Write Lease','connectors','EFFECT_GATED','External writes require a separate lease and destination authority.'),
X('connectors.revoke','Connector Revoke','connectors','SOURCE_PRESENT','Revoke connector access and leases.'),
X('identity.custom_assistants','Custom User Assistants','agents','SOURCE_PRESENT','Users may define preferred assistant names/personality/provider policy without replacing canonical built-in agents.'),
X('identity.byok','BYOK Model Routing','agents','SOURCE_PRESENT','Tenant-scoped model-provider credentials through brokered/opaque handling; raw keys are never rendered.'),
X('models.universal_router','Universal Model Router','models','SOURCE_PRESENT','Provider-neutral model routing with bounded fallback and evidence per round-trip.'),
X('models.credential_broker','Credential Broker','models','SOURCE_PRESENT','Opaque provider capability mounting without exposing raw credential values.'),
X('growth.referrals','Referral Lineage','growth','SOURCE_PRESENT','Referral graph and attribution rules; cash payout effects remain separately gated.'),
X('growth.tasks','User Task Catalog','growth','SOURCE_PRESENT','Owner-curated tasks with links, point values and approval/rejection.'),
X('growth.points','Points Ledger + Leaderboard','growth','SOURCE_PRESENT','Approved task/game/community points feed a unified evidence-backed ledger.'),
X('growth.badges','Badges + Titles','growth','SOURCE_PRESENT','Role/title/badge assignments for multiple user classes.'),
X('growth.daily_access','Daily Access Meter','growth','SOURCE_PRESENT','Server-metered usage policy for ordinary access and paid-entitlement overrides.'),
X('presence.heartbeat','Presence Heartbeat','presence','SOURCE_PRESENT','Session/device/agent presence heartbeat with stale-state handling.'),
X('world.portal','World Portal','spatial','SOURCE_PRESENT','Portal transitions between public horizon, identity and world/workbench surfaces.'),
X('identity.access_control','Access + Entitlements','identity','SOURCE_PRESENT','Role, membership and entitlement evaluation separated from mere login.'),
X('schedulers.program_sentinel','8x8 Unified Program Sentinel','missions','SOURCE_PRESENT','Canonical scheduler support lane; one of the fixed scheduler-level support surfaces.'),
X('schedulers.communications','FlashTM8 Communications Brief','missions','SOURCE_PRESENT','Communications/status support lane.'),
X('schedulers.crypto','8x8 Crypto + Multichain','missions','SOURCE_PRESENT','Crypto/multichain research and evidence support lane.'),
X('schedulers.trading','8x8 Trading Intelligence','missions','SOURCE_PRESENT','Trading research/simulation support lane.'),
X('schedulers.studio','8x8 Content Studio Scheduler','missions','SOURCE_PRESENT','Content/Studio support lane.'),
X('responsive.s22_portrait','S22 Portrait Client','clients','SOURCE_PRESENT','Responsive acceptance target for Samsung portrait orientation.'),
X('responsive.s22_landscape','S22 Landscape Client','clients','SOURCE_PRESENT','Responsive acceptance target for Samsung landscape orientation.'),
X('responsive.desktop','Desktop Client','clients','SOURCE_PRESENT','Desktop responsive acceptance target.'),
X('responsive.iphone','iPhone Client','clients','SOURCE_PRESENT','iPhone responsive acceptance target.'),
X('security.cross_tenant','Cross-Tenant Isolation','security','SOURCE_PRESENT','Cross-tenant access must fail closed.'),
X('security.raw_secret','Raw Secret Non-Rendering','security','SOURCE_PRESENT','Raw credentials, seeds and private keys must never be rendered.'),
X('security.background_camera','No Background Camera','security','SOURCE_PRESENT','Camera capture releases when not explicitly foreground-leased.'),
X('security.background_mic','No Background Microphone','security','SOURCE_PRESENT','Microphone capture releases when not explicitly foreground-leased.'),
X('security.no_unleased_device','No Unleased Device Effect','security','SOURCE_PRESENT','Physical/device effects require explicit identity-bound authority.'),
X('release.rollback_archive','Release Rollback Archive','dormant','PAST_PRESERVED','Previously qualified releases retained byte-exactly for emergency restore and history.'),
X('revival.dormant_estate','Dormant Revival Estate','dormant','PAST_PRESERVED','Historical code, designs, agents, routes, models, interfaces, datasets and experiments available for evidence-led extraction.'),
X('design.historical_census','Historical UI / Feature Census','design','SOURCE_PRESENT','Source-by-source historical design and capability census with exact-hash dedup.'),
X('design.owner_acceptance','Owner Visual Acceptance','design','OWNER_REQUIRED','Public design promotion requires explicit owner acceptance distinct from deployment success.'),
X('design.telemetry_truth','Telemetry Truth Gate','design','SOURCE_PRESENT','Decorative/concept telemetry is never presented as live runtime truth.'),
X('design.accessibility_performance','Accessibility + Performance Gate','design','SOURCE_PRESENT','Promotion gate for accessibility, mobile/desktop fit and performance.'),
X('economy.membership_settlement','Membership Settlement + Entitlement Reconciliation','economy','EFFECT_GATED','Settled recurring payment, entitlement activation, cancellation/failure/refund reconciliation are distinct states.'),
X('economy.genesis_membership','Genesis Membership Program','economy','SOURCE_PRESENT','Membership program surface with token/NFT Vault entitlements separately gated from issuance.'),
X('blockchain.native_network','8x8 Network / Native Blockchain','blockchain','FUTURE_GATED','Native-network constitutional lineage; deployment, validators/nodes and mainnet effects require current evidence.'),
X('blockchain.external_adapters','External Network Adapters','blockchain','FUTURE_GATED','Bitcoin, Ethereum-family, BNB-family, Solana-family, TON-family, Pi and future adapters without creating parallel roots.'),
X('blockchain.bridge_security','Bridge Security + Governance','blockchain','FUTURE_GATED','Cross-network bridges remain disabled until exact security/governance gates pass.'),
X('economy.ux8_modes','Ux8 Native / Payment-Stable / Reference Modes','economy','FUTURE_GATED','Distinct Ux8 economic modes; a market pair does not itself prove a fixed peg or redemption right.'),
X('release.design_census_coverage','Historical Design Census Coverage','design','SOURCE_PRESENT','Promotion denominator includes connected GitHub, Drive, devices, backups, visual registry and archived carriers.'),
X('release.exact_hash_dedup','Exact-Hash Dedup','design','SOURCE_PRESENT','Binary-identical historical artifacts are deduplicated before capability extraction.'),
X('release.capability_reconciliation','Capability Reconciliation','design','SOURCE_PRESENT','Recovered feature/design signals map back into canonical capability owners.'),
X('release.public_private_boundary','Public / Private Boundary Gate','security','SOURCE_PRESENT','Public User Edition must not export owner-private topology or authority.'),
X('release.functional_denominator','Full Functional Denominator','proof','SOURCE_PRESENT','HTTP 200 alone never equals full functionality; applicable interactions require evidence or explicit future-gated rationale.')
];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function boot(){
 if(document.getElementById('interactionEstate53')) return;
 const b=document.createElement('button'); b.id='interactionEstate53'; b.className='btn'; b.textContent=`INTERACTION ESTATE +${EXTRA.length}`;
 const target=document.querySelector('#g3 .actions')||document.querySelector('.top'); if(target) target.appendChild(b);
 const ov=document.createElement('div'); ov.id='interactionOverlay53'; ov.className='overlay';
 ov.innerHTML=`<div class="overlayShell"><div class="overlayTop"><h2>INTERACTION + GROWTH + CONTROL ESTATE · V53</h2><span class="truthchip">${EXTRA.length} RECOVERED ENTRIES</span><button class="btn close" id="closeInteraction53">CLOSE</button></div><input class="search" id="interactionSearch53" placeholder="Search login, terminal, files, device mesh, Jarvis, mail, referrals, points, badges, BYOK, scheduler, rollback, design gates…"><div class="overlayGrid" id="interactionGrid53"></div></div>`;
 document.body.appendChild(ov);
 const grid=ov.querySelector('#interactionGrid53'), q=ov.querySelector('#interactionSearch53');
 const render=()=>{const s=(q.value||'').toLowerCase();grid.innerHTML=EXTRA.filter(x=>!s||`${x.key} ${x.name} ${x.family} ${x.state} ${x.desc}`.toLowerCase().includes(s)).map(x=>`<article class="module"><span class="cat">${esc(x.family.toUpperCase())}</span><h3>${esc(x.name)}</h3><p>${esc(x.desc)}</p><span class="state ${x.state==='SOURCE_PRESENT'?'source':x.state==='PAST_PRESERVED'?'dormant':x.state==='OWNER_REQUIRED'?'research':'gated'}">${esc(x.state)}</span></article>`).join('');};
 q.addEventListener('input',render); render();
 b.addEventListener('click',()=>ov.classList.add('on')); ov.querySelector('#closeInteraction53').addEventListener('click',()=>ov.classList.remove('on'));
 window.EightX8InteractionEstateV53={canonicalRoot:'fabric://8x8/core',entries:EXTRA,truth:'RECOVERED_CURRENT_DENOMINATOR_NE_GLOBAL_HISTORY_COMPLETE'};
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();
