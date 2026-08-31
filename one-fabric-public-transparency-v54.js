(()=>{
'use strict';
const ROOT='fabric://8x8/core';
const SUGGEST='https://github.com/8x8org/8x8-user-edition/issues/182';
const rows=[
 ['Research intake','80 original owner links','PAST_PRESERVED','Original TikTok/research intake; item-by-item verification remains separate.'],
 ['Canonical research registry','121 source objects','PRESENT_PROVEN_SOURCE_DENOMINATOR','Current Drive registry checkpoint. A source object is not automatically an implemented power.'],
 ['Broader research estate','170-source candidate estate','RECONCILIATION_PENDING','Separately scoped candidate denominator; must not be presented as 170 verified implementations.'],
 ['Atomic mission registry','920 tasks','PRESENT_PROVEN_REGISTRY','Execution/recovery task denominator; task existence does not imply completion.'],
 ['Research races','11 bounded race families','SOURCE_PRESENT','GitHub, spatial, memory, runtime, browser, robotics, content, trading, security, venture and competition races.'],
 ['AGI target','100% target','TARGET_NOT_ACHIEVED','Evidence-gated target. Current preserved ARC-AGI-3 public canary score is 0.0; no AGI/rank claim is allowed yet.']
];
const competitions=[
 ['Build with Gemini XPRIZE','EVIDENCE_STREAM_ACTIVE','Venture Operator judge surface and Gemini proof exist; final submission state must be revalidated from current evidence before public claim.'],
 ['ARC Prize 2026','BENCHMARK_REFERENCE_ACTIVE','ARC-AGI-3 public canary runtime proven; score 0.0; official/comparable evaluation still required.'],
 ['All Things Agentic — Google','REVALIDATE_ENTRY','Strong One-Fabric multi-agent fit; current eligibility/submission state must be refreshed.'],
 ['Agentic Cinema — Google','REVALIDATE_ENTRY','Strong Studio/media-agent fit; sponsor-tech and deadline must be freshly verified.'],
 ['Agents for Humans — Amazon','REVALIDATE_ENTRY','Human-in-the-loop and bounded-agent fit; official rules/state require refresh.'],
 ['CALL-E: Your Code Is Calling','REVALIDATE_ENTRY','Voice/phone-agent fit with explicit call authority and revocation.'],
 ['AWS Trainium Frontier','REVALIDATE_ENTRY','Inference/runtime efficiency and benchmark fit.'],
 ['RevenueCat Shipaton 2026','REVALIDATE_ENTRY','Subscription/mobile product fit; eligibility depends on current official rules.'],
 ['CockroachDB × AWS Agentic Memory','PAST_OR_REVALIDATE','Agent memory/provenance fit; prior intake deadline has passed unless extended.'],
 ['YouCam API Hackathon','PAST_OR_REVALIDATE','Studio/commerce/visual-agent fit; prior intake deadline has passed unless extended.'],
 ['Arm Create AI Optimization','PAST_PRESERVED','Closed historical donor lane for mobile/edge optimization.']
];
const recovered=[
 'Agent Civilization + SOUL/Memory + Councils + Dynamic Specialists + Agent Bus + Shared Brain',
 'Art Board + Whole-System Puzzle + relationship graph + movable evidence/artifact nodes',
 'multidimensional spatial world + 2D/3D/5D/XR + WebGPU/WebXR + Unreal/Unity + hologram + Reality Graph',
 'Barehand fullscreen + multi-object spatial physics + agent↔human artifact throws',
 '8x8 Studio + content hub + research→script→storyboard→image/video/audio→TTS→captions→render→publish',
 'Trading intelligence + scanners + market/news/sentiment + backtests + paper engine + risk + portfolio/execution simulation',
 'Live Log/Observability + FTS + timeline + telemetry + agent context + CSV/Excel evidence export',
 'Browser/computer use + device mesh + Android/iPhone/desktop/XR + robotics simulation/control',
 'MCP/connectors + ToolJet/Agent-Reach patterns + remote desktop + model routing/BYOK + code intelligence/RAG',
 'Commerce/venture/freelance/social publishing + marketplace + TikTok Shop + CRM/support',
 '8x8 ID + Mail + memberships + wallet/account + blockchain/network + 8x8Scan + NFT Vault',
 'Humanity + Animals/Biodiversity + Planet Earth + Quran + Academy + AGI/evals + competitions + Future +N'
];
const researchFamilies=[
 'Jarvis / hologram / spatial UI','Robotics / embodied agents / sensors','Memory / agents / cognition','Connectors / MCP / browser / device control','Content / commerce / venture automation','Security / cryptography / defensive research','Models / AI infrastructure / education','Hardware / compute / manufacturing / XR'
];
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function boot(){
 if(document.getElementById('publicTransparency54'))return;
 const gate=document.querySelector('#g1')||document.querySelector('main')||document.body;
 const section=document.createElement('section'); section.id='publicTransparency54'; section.className='transparency54';
 section.innerHTML=`
 <style>
 .transparency54{margin:22px 0;padding:18px;border:1px solid rgba(120,180,255,.28);border-radius:22px;background:linear-gradient(135deg,rgba(13,24,43,.94),rgba(20,9,38,.9));box-shadow:0 18px 60px rgba(0,0,0,.28)}
 .transparency54 .t54top{display:flex;gap:12px;justify-content:space-between;align-items:flex-start;flex-wrap:wrap}.transparency54 h2{margin:0;font-size:clamp(1.25rem,3vw,2rem)}
 .transparency54 .truth54{font-size:.75rem;letter-spacing:.09em;border:1px solid rgba(120,255,210,.35);padding:7px 10px;border-radius:999px}.transparency54 .grid54{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:10px;margin-top:14px}
 .transparency54 article{padding:13px;border-radius:16px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.08)}.transparency54 h3{margin:0 0 6px;font-size:1rem}.transparency54 p{margin:4px 0;font-size:.84rem;opacity:.82;line-height:1.45}.transparency54 .state54{font-size:.68rem;letter-spacing:.06em;opacity:.72}.transparency54 .actions54{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.transparency54 a,.transparency54 button{color:inherit;text-decoration:none;border:1px solid rgba(150,200,255,.3);background:rgba(255,255,255,.06);padding:9px 12px;border-radius:12px;cursor:pointer}.transparency54 details{margin-top:12px}.transparency54 summary{cursor:pointer;font-weight:700}.transparency54 .agi54{margin-top:14px;padding:14px;border-radius:16px;border:1px solid rgba(255,190,90,.3);background:rgba(255,170,50,.05)}
 </style>
 <div class="t54top"><div><span class="state54">GATE 1 · PUBLIC TRANSPARENCY</span><h2>BUILDING 8x8 IN PUBLIC · RESEARCH · COMPETITIONS · AGI TARGET</h2><p>See what is proven, what is being recovered, what remains gated, and where the community can help.</p></div><span class="truth54">${esc(ROOT)}</span></div>
 <div class="grid54">${rows.map(r=>`<article><span class="state54">${esc(r[2])}</span><h3>${esc(r[0])}</h3><p><strong>${esc(r[1])}</strong></p><p>${esc(r[3])}</p></article>`).join('')}</div>
 <div class="agi54"><h3>AGI 100% — TARGET, NOT A MARKETING CLAIM</h3><p>Target: 100%. Current evidence does not prove AGI. The preserved ARC-AGI-3 public canary completed its 100 requested steps but scored 0.0. Promotion requires an actual solver, reproducible comparable evaluation, official/external evidence where required, and fresh receipts.</p></div>
 <details><summary>Competitions / challenges (${competitions.length})</summary><div class="grid54">${competitions.map(c=>`<article><span class="state54">${esc(c[1])}</span><h3>${esc(c[0])}</h3><p>${esc(c[2])}</p></article>`).join('')}</div></details>
 <details><summary>Recovered + still-expanding capability universe</summary><div class="grid54">${recovered.map(x=>`<article><p>${esc(x)}</p></article>`).join('')}</div></details>
 <details><summary>External research families (${researchFamilies.length})</summary><div class="grid54">${researchFamilies.map(x=>`<article><p>${esc(x)}</p></article>`).join('')}</div></details>
 <div class="actions54"><a href="${SUGGEST}" target="_blank" rel="noopener">SUGGEST A POWER / REPO / COMPETITION</a><a href="/presale">SUPPORT / JOIN MEMBERSHIP</a><button id="openPowers54" type="button">OPEN ALL POWERS</button></div>
 <p class="state54">Truth law: SOURCE_PRESENT ≠ DEPLOYED ≠ PRODUCTIVE ≠ VERIFIED. Community suggestions are intake only and pass source/license/security/dedupe/canary/benchmark gates before promotion.</p>`;
 gate.appendChild(section);
 section.querySelector('#openPowers54')?.addEventListener('click',()=>document.querySelector('#allPowers')?.click());
 window.EightX8PublicTransparencyV54={canonicalRoot:ROOT,research:{originalOwnerIntake:80,canonicalSourceObjects:121,broaderCandidateEstate:170,atomicTaskRegistry:920},competitions,recovered,researchFamilies,agi:{targetPercent:100,currentClaimAllowed:false,arcAgi3PublicCanaryScore:0.0},suggestionIssue:SUGGEST,truth:'PUBLIC_TRANSPARENCY_NE_COMPLETION_CLAIM'};
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
