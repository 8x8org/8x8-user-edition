const views = [...document.querySelectorAll('.view')];
const viewButtons = [...document.querySelectorAll('[data-view]')];
const worldGrid = document.getElementById('worldGrid');
const sectorPanel = document.getElementById('sectorPanel');
const evidenceGrid = document.getElementById('evidenceGrid');
const missionForm = document.getElementById('missionForm');
const missionResult = document.getElementById('missionResult');
const missionState = document.getElementById('missionState');

const params = new URLSearchParams(location.search);
const requestedApi = params.get('api');
if (requestedApi) localStorage.setItem('eightx8CompetitionApi', requestedApi.replace(/\/$/, ''));
const API_BASE = localStorage.getItem('eightx8CompetitionApi') || '';

function setView(id) {
  views.forEach(view => view.classList.toggle('active', view.id === id));
  viewButtons.forEach(button => button.classList.toggle('active', button.dataset.view === id));
  history.replaceState(null, '', `#${id}`);
  window.scrollTo({top:0, behavior:'smooth'});
}

viewButtons.forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
const initialView = location.hash.slice(1);
if (views.some(view => view.id === initialView)) setView(initialView);

async function loadJson(path) {
  const response = await fetch(path, {cache:'no-store'});
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.json();
}

function stateFor(registry, world, sector) {
  return registry.initial_truth?.[`${world.id}/${sector}`] || 'DESIGNED';
}

function renderWorlds(registry) {
  worldGrid.innerHTML = registry.worlds.map(world => `
    <button class="world-card" data-world="${world.id}">
      <b>${world.id} • 8 SECTORS</b>
      <h3>${world.name}</h3>
      <p>${world.sectors.slice(0, 3).join(' • ')} and five more accountable sectors.</p>
      <span>${world.visibility}</span>
    </button>
  `).join('');

  document.querySelectorAll('[data-world]').forEach(card => card.addEventListener('click', () => {
    document.querySelectorAll('[data-world]').forEach(item => item.classList.remove('active'));
    card.classList.add('active');
    const world = registry.worlds.find(item => item.id === card.dataset.world);
    sectorPanel.innerHTML = `
      <div class="panel-title"><span>${world.id} • ${world.name}</span><em>${world.visibility}</em></div>
      <div class="sector-grid">
        ${world.sectors.map((sector, index) => {
          const state = stateFor(registry, world, sector);
          return `<div class="sector"><b>${world.id}S${index + 1} • ${sector}</b><span class="state-${state}">${state}</span></div>`;
        }).join('')}
      </div>
    `;
  }));
}

function flattenEvidence(state) {
  return [
    ['Overall readiness', state.overall_status, state.ready_100 ? 'Verified complete' : 'Not 100/100'],
    ['Public web', state.surfaces.public_web.state, `Live URL verified: ${state.surfaces.public_web.live_url_verified}`],
    ['Public Telegram Mini App', state.surfaces.public_telegram_miniapp.state, `Binding verified: ${state.surfaces.public_telegram_miniapp.binding_verified}`],
    ['Private owner Mini App', state.surfaces.private_owner_miniapp.state, `Owner boundary verified: ${state.surfaces.private_owner_miniapp.owner_allowlist_verified}`],
    ['HERMES', state.runtime.hermes.state, state.runtime.hermes.last_user_evidence],
    ['8x8 OS runtime', state.runtime.eightx8_os.state, state.runtime.eightx8_os.last_user_evidence],
    ['Studio runtime', state.runtime.studio.state, state.runtime.studio.last_user_evidence],
    ['24/7 agent fabric', state.runtime.continuous_agents_24_7.state, 'Current continuous receipt required'],
    ['Gemini production call', state.cloud.gemini_api_production_call.state, 'Cloud execution receipt required'],
    ['Google Cloud product', state.cloud.google_cloud_product.state, 'Named deployed service required'],
    ['MSG205 local receipt', state.evidence.msg205_local_receipt, 'Samsung census completion evidence'],
    ['Genesis convergence', state.evidence.genesis_convergence, 'Current source manifests required'],
    ['External users', state.business.external_users.verified_count ? 'VERIFIED' : 'NOT_PROVEN', `${state.business.external_users.verified_count} verified`],
    ['Paid users', state.business.arms_length_paid_users.verified_count ? 'VERIFIED' : 'NOT_PROVEN', `${state.business.arms_length_paid_users.verified_count} verified`],
    ['Demo video', state.evidence.demo_video, 'Under three minutes'],
    ['Final submission', state.evidence.final_submission, 'Owner action required']
  ];
}

function evidenceClass(status) {
  const value = String(status).toUpperCase();
  if (/(VERIFIED|RUNNING|DEPLOYED|RELEASED|ADOPTED|SUCCESS)/.test(value) && !/NOT_/.test(value)) return 'state-TESTED';
  if (/(BLOCKED|MISSING|FAILED|NOT_PROVEN|NOT_RETURNED|NOT_DEPLOYED)/.test(value)) return 'state-BLOCKED';
  return 'state-DESIGNED';
}

function renderEvidence(state) {
  document.getElementById('overallStatus').textContent = state.overall_status.replaceAll('_', ' ');
  evidenceGrid.innerHTML = flattenEvidence(state).map(([label, status, detail]) => `
    <article class="evidence-card">
      <b>${label}</b>
      <span class="${evidenceClass(status)}">${String(status).replaceAll('_', ' ')}</span>
      <p>${detail}</p>
    </article>
  `).join('');
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[character]));
}

function renderMission(payload) {
  const plan = payload.result || {};
  const receipt = payload.receipt || {};
  const tasks = Array.isArray(plan.tasks) ? plan.tasks : [];
  missionResult.className = 'result';
  missionResult.innerHTML = `
    <h3>Summary</h3><p>${escapeHtml(plan.summary || 'No summary returned.')}</p>
    <h3>Diagnosis</h3><ul>${(plan.diagnosis || []).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    <h3>Agent tasks</h3>
    ${tasks.map(task => `<article class="task"><header><b>${escapeHtml(task.title || 'Task')}</b><em>${escapeHtml(task.authority || 'UNSET')} • ${escapeHtml(task.agent || 'Unassigned')}</em></header><p>${escapeHtml(task.evidence || 'Evidence requirement not supplied.')}</p></article>`).join('')}
    <h3>Deliverables</h3><ul>${(plan.deliverables || []).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    <h3>Risks</h3><ul>${(plan.risks || []).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    <h3>Success metrics</h3><ul>${(plan.success_metrics || []).map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    <div class="receipt">MISSION ${escapeHtml(receipt.mission_id || 'UNKNOWN')}<br>STATE ${escapeHtml(receipt.execution_state || 'PLANNED_NOT_EXECUTED')}<br>REVISION ${escapeHtml(receipt.service_revision || 'UNVERIFIED')}<br>RECEIPT ${escapeHtml(receipt.receipt_digest || 'MISSING')}</div>
  `;
}

missionForm.addEventListener('submit', async event => {
  event.preventDefault();
  missionState.textContent = 'PLANNING';
  missionResult.className = 'result-empty';
  missionResult.textContent = API_BASE ? 'Contacting the configured 8x8 Competition API…' : 'No API URL is configured for this static build.';
  if (!API_BASE) {
    missionState.textContent = 'API NOT CONFIGURED';
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/api/v1/missions/plan`, {
      method:'POST',
      headers:{'content-type':'application/json'},
      body:JSON.stringify({
        template:document.getElementById('template').value,
        goal:document.getElementById('goal').value,
        context:document.getElementById('context').value,
        consent:document.getElementById('consent').checked
      })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || `HTTP_${response.status}`);
    renderMission(payload);
    missionState.textContent = 'PLANNED • NOT EXECUTED';
  } catch (error) {
    missionState.textContent = 'BLOCKED';
    missionResult.className = 'result-empty';
    missionResult.textContent = `Mission planning failed safely: ${error.message}`;
  }
});

Promise.all([
  loadJson('./system-registry.v1.json'),
  loadJson('./competition-state.v1.json')
]).then(([registry, state]) => {
  renderWorlds(registry);
  renderEvidence(state);
}).catch(error => {
  evidenceGrid.innerHTML = `<article class="evidence-card"><b>State loading</b><span class="state-BLOCKED">BLOCKED</span><p>${escapeHtml(error.message)}</p></article>`;
});
