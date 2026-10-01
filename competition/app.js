const views = [...document.querySelectorAll('.view')];
const viewButtons = [...document.querySelectorAll('[data-view]')];
const worldGrid = document.getElementById('worldGrid');
const sectorPanel = document.getElementById('sectorPanel');
const evidenceGrid = document.getElementById('evidenceGrid');
const missionForm = document.getElementById('missionForm');
const missionResult = document.getElementById('missionResult');
const missionState = document.getElementById('missionState');

function configuredApiBase() {
  const raw = document.querySelector('meta[name="eightx8-api-base"]')?.content.trim() || '';
  if (!raw) return '';
  const parsed = new URL(raw, window.location.href);
  const localDevelopment = ['localhost', '127.0.0.1'].includes(parsed.hostname);
  if (parsed.protocol !== 'https:' && !(localDevelopment && parsed.protocol === 'http:')) {
    throw new Error('API_CONFIGURATION_REQUIRES_HTTPS');
  }
  return parsed.origin;
}

let API_BASE = '';
try {
  API_BASE = configuredApiBase();
} catch {
  missionState.textContent = 'API CONFIGURATION BLOCKED';
}

function createElement(tag, {className = '', text = '', attributes = {}} = {}, children = []) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== '') node.textContent = String(text);
  for (const [name, value] of Object.entries(attributes)) {
    node.setAttribute(name, String(value));
  }
  for (const child of children) node.append(child);
  return node;
}

function replace(node, ...children) {
  node.replaceChildren(...children);
}

function setView(id) {
  views.forEach(view => view.classList.toggle('active', view.id === id));
  viewButtons.forEach(button => button.classList.toggle('active', button.dataset.view === id));
  history.replaceState(null, '', `#${id}`);
  window.scrollTo({top: 0, behavior: 'smooth'});
}

viewButtons.forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
const initialView = location.hash.slice(1);
if (views.some(view => view.id === initialView)) setView(initialView);

async function loadJson(path) {
  const response = await fetch(path, {cache: 'no-store', credentials: 'omit'});
  if (!response.ok) throw new Error(`STATE_LOAD_HTTP_${response.status}`);
  return response.json();
}

function stateFor(registry, world, sector) {
  return registry.initial_truth?.[`${world.id}/${sector}`] || 'DESIGNED';
}

function renderSectorPanel(registry, world) {
  const title = createElement('div', {className: 'panel-title'}, [
    createElement('span', {text: `${world.id} • ${world.name}`}),
    createElement('em', {text: world.visibility})
  ]);
  const sectors = createElement('div', {className: 'sector-grid'});

  world.sectors.forEach((sector, index) => {
    const state = stateFor(registry, world, sector);
    sectors.append(createElement('div', {className: 'sector'}, [
      createElement('b', {text: `${world.id}S${index + 1} • ${sector}`}),
      createElement('span', {className: `state-${state}`, text: state})
    ]));
  });

  replace(sectorPanel, title, sectors);
}

function renderWorlds(registry) {
  const fragment = document.createDocumentFragment();
  registry.worlds.forEach(world => {
    const card = createElement('button', {
      className: 'world-card',
      attributes: {'data-world': world.id, type: 'button'}
    }, [
      createElement('b', {text: `${world.id} • 8 SECTORS`}),
      createElement('h3', {text: world.name}),
      createElement('p', {text: `${world.sectors.slice(0, 3).join(' • ')} and five more accountable sectors.`}),
      createElement('span', {text: world.visibility})
    ]);

    card.addEventListener('click', () => {
      worldGrid.querySelectorAll('[data-world]').forEach(item => item.classList.remove('active'));
      card.classList.add('active');
      renderSectorPanel(registry, world);
    });
    fragment.append(card);
  });
  replace(worldGrid, fragment);
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
  document.getElementById('overallStatus').textContent = String(state.overall_status).replaceAll('_', ' ');
  const fragment = document.createDocumentFragment();
  flattenEvidence(state).forEach(([label, status, detail]) => {
    fragment.append(createElement('article', {className: 'evidence-card'}, [
      createElement('b', {text: label}),
      createElement('span', {className: evidenceClass(status), text: String(status).replaceAll('_', ' ')}),
      createElement('p', {text: detail})
    ]));
  });
  replace(evidenceGrid, fragment);
}

function appendHeading(container, text) {
  container.append(createElement('h3', {text}));
}

function appendList(container, values) {
  const list = createElement('ul');
  for (const value of Array.isArray(values) ? values : []) {
    list.append(createElement('li', {text: value}));
  }
  container.append(list);
}

function renderMission(payload) {
  const plan = payload.result || {};
  const receipt = payload.receipt || {};
  const tasks = Array.isArray(plan.tasks) ? plan.tasks : [];
  missionResult.className = 'result';
  replace(missionResult);

  appendHeading(missionResult, 'Summary');
  missionResult.append(createElement('p', {text: plan.summary || 'No summary returned.'}));
  appendHeading(missionResult, 'Diagnosis');
  appendList(missionResult, plan.diagnosis);
  appendHeading(missionResult, 'Agent tasks');

  for (const task of tasks) {
    missionResult.append(createElement('article', {className: 'task'}, [
      createElement('header', {}, [
        createElement('b', {text: task.title || 'Task'}),
        createElement('em', {text: `${task.authority || 'UNSET'} • ${task.agent || 'Unassigned'}`})
      ]),
      createElement('p', {text: task.evidence || 'Evidence requirement not supplied.'})
    ]));
  }

  appendHeading(missionResult, 'Deliverables');
  appendList(missionResult, plan.deliverables);
  appendHeading(missionResult, 'Risks');
  appendList(missionResult, plan.risks);
  appendHeading(missionResult, 'Success metrics');
  appendList(missionResult, plan.success_metrics);

  missionResult.append(createElement('div', {
    className: 'receipt',
    text: [
      `MISSION ${receipt.mission_id || 'UNKNOWN'}`,
      `STATE ${receipt.execution_state || 'PLANNED_NOT_EXECUTED'}`,
      `REVISION ${receipt.service_revision || 'UNVERIFIED'}`,
      `RECEIPT ${receipt.receipt_digest || 'MISSING'}`
    ].join('\n')
  }));
}

missionForm.addEventListener('submit', async event => {
  event.preventDefault();
  missionState.textContent = 'PLANNING';
  missionResult.className = 'result-empty';
  missionResult.textContent = API_BASE ? 'Contacting the configured 8x8 Competition API…' : 'No deployment-bound API URL is configured for this build.';
  if (!API_BASE) {
    missionState.textContent = 'API NOT CONFIGURED';
    return;
  }

  try {
    const endpoint = new URL('/api/v1/missions/plan', `${API_BASE}/`);
    const response = await fetch(endpoint, {
      method: 'POST',
      mode: 'cors',
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      headers: {'content-type': 'application/json'},
      body: JSON.stringify({
        template: document.getElementById('template').value,
        goal: document.getElementById('goal').value,
        context: document.getElementById('context').value,
        consent: document.getElementById('consent').checked
      })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(typeof payload.error === 'string' ? payload.error : `HTTP_${response.status}`);
    renderMission(payload);
    missionState.textContent = 'PLANNED • NOT EXECUTED';
  } catch (error) {
    missionState.textContent = 'BLOCKED';
    missionResult.className = 'result-empty';
    missionResult.textContent = `Mission planning failed safely: ${error instanceof Error ? error.message : 'UNKNOWN_ERROR'}`;
  }
});

Promise.all([
  loadJson('./system-registry.v1.json'),
  loadJson('./competition-state.v1.json')
]).then(([registry, state]) => {
  renderWorlds(registry);
  renderEvidence(state);
}).catch(() => {
  replace(evidenceGrid, createElement('article', {className: 'evidence-card'}, [
    createElement('b', {text: 'State loading'}),
    createElement('span', {className: 'state-BLOCKED', text: 'BLOCKED'}),
    createElement('p', {text: 'Competition state could not be loaded.'})
  ]));
});
