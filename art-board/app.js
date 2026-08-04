(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const zoomLevels = [55, 65, 75, 88, 100, 110, 120, 135, 150, 165, 180];
  const worldPositions = [[50,12],[76,24],[86,51],[73,76],[50,86],[27,76],[14,51],[24,24]];
  const nodePositions = [[50,31],[63,40],[64,60],[50,68],[36,60],[37,40]];
  const state = { data: null, zoomIndex: 4, mapMode: false, selected: null, dragging: false, pointerX: 0, pointerY: 0, suggestionIndex: 0 };

  function safeToken(value) {
    return String(value ?? '').replace(/[^A-Za-z0-9_-]/g, '') || 'UNKNOWN';
  }

  function boundedPercent(value) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric) || numeric < 0 || numeric > 100) throw new Error('Invalid board coordinate');
    return numeric;
  }

  function createNode(tag, options = {}) {
    const element = document.createElement(tag);
    if (options.className) element.className = options.className;
    if (options.text !== undefined) element.textContent = String(options.text);
    if (options.title !== undefined) element.title = String(options.title);
    for (const [name, value] of Object.entries(options.attributes || {})) element.setAttribute(name, String(value));
    for (const child of options.children || []) if (child) element.append(child);
    return element;
  }

  function replaceChildren(target, children) {
    target.replaceChildren(...children.filter(Boolean));
  }

  function labelledParagraph(label, value) {
    return createNode('p', { children: [createNode('b', { text: `${label}: ` }), document.createTextNode(String(value ?? ''))] });
  }

  function applyZoom() {
    const zoom = zoomLevels[state.zoomIndex];
    $('#board').dataset.zoom = String(zoom);
    $('#zoomReadout').textContent = `${zoom}%`;
    $('#zoomReset').textContent = `${zoom}%`;
  }

  function changeZoom(delta) {
    state.zoomIndex = Math.max(0, Math.min(zoomLevels.length - 1, state.zoomIndex + delta));
    applyZoom();
  }

  function resetView() {
    state.zoomIndex = 4;
    applyZoom();
    const viewport = $('#boardViewport');
    viewport.scrollTo({ left: Math.max(0, (viewport.scrollWidth - viewport.clientWidth) / 2), top: Math.max(0, (viewport.scrollHeight - viewport.clientHeight) / 2) });
  }

  function renderLegend() {
    replaceChildren($('#legend'), Object.entries(state.data.palette).map(([token, description]) => createNode('div', {
      className: 'legend-item',
      children: [
        createNode('span', { className: `swatch status-${safeToken(token)}`, attributes: { 'aria-hidden': 'true' } }),
        createNode('span', { children: [createNode('b', { text: token }), createNode('br'), document.createTextNode(String(description))] })
      ]
    })));
  }

  function renderWorlds() {
    replaceChildren($('#worldLayer'), state.data.worlds.map((world, index) => {
      const [x, y] = worldPositions[index] || [50, 50];
      const button = createNode('button', {
        className: `world status-${safeToken(world.status)}`,
        attributes: { 'data-world': world.id, 'data-position': index, 'data-x': boundedPercent(x), 'data-y': boundedPercent(y), 'aria-label': `${world.label}, ${world.status}` },
        children: [createNode('b', { text: world.label }), createNode('small', { text: `${world.score}/100 • ${world.evidence}` })]
      });
      return button;
    }));
  }

  function renderNodes() {
    replaceChildren($('#nodeLayer'), state.data.nodes.map((record, index) => {
      const positionIndex = index % nodePositions.length;
      const [x, y] = nodePositions[positionIndex];
      return createNode('button', {
        className: `node status-${safeToken(record.status)}`,
        text: record.shortcut,
        title: record.label,
        attributes: { 'data-node': record.id, 'data-position': positionIndex, 'data-x': boundedPercent(x), 'data-y': boundedPercent(y), 'aria-label': `${record.label}, ${record.status}` }
      });
    }));
  }

  function renderPresence() {
    replaceChildren($('#presenceLayer'), state.data.presence_clusters.map((cluster, index) => createNode('button', {
      className: `presence status-${safeToken(cluster.status)}`,
      attributes: {
        'data-presence': cluster.id,
        'data-position': index % 4,
        'data-x': boundedPercent(cluster.x),
        'data-y': boundedPercent(cluster.y),
        'data-label': cluster.label,
        'aria-label': `${cluster.label}; simulated; count zero`
      }
    })));
  }

  function renderWidgets() {
    const treasury = state.data.treasury;
    replaceChildren($('#treasuryWidget'), [
      labelledParagraph('Status', treasury.status),
      createNode('p', { text: treasury.notice }),
      labelledParagraph('Networks', treasury.networks.join(', ')),
      createNode('p', { children: [createNode('b', { text: 'Balances: ' }), document.createTextNode('hidden / unavailable'), createNode('br'), createNode('b', { text: 'Signing: ' }), document.createTextNode('disabled')] })
    ]);
    replaceChildren($('#suggestions'), state.data.suggestions.map((item) => createNode('li', { text: item })));
  }

  function addFact(fragment, label, value) {
    if (value === undefined || value === null || value === '') return;
    fragment.append(createNode('dt', { text: label }), createNode('dd', { text: value }));
  }

  function inspect(item, kind) {
    if (!item || typeof item !== 'object') return;
    state.selected = { item, kind };
    $('#detailTitle').textContent = item.label || item.id || 'Unknown record';
    $('#detailSummary').textContent = item.summary || item.description || item.help || 'Public-safe record.';
    const fragment = document.createDocumentFragment();
    addFact(fragment, 'Type', item.type || String(kind).toUpperCase());
    for (const field of ['status', 'evidence', 'score', 'world', 'mode', 'region', 'count']) addFact(fragment, field, item[field]);
    $('#detailFacts').replaceChildren(fragment);
    $('#showEvidence').disabled = false;
  }

  function showModal(title, children) {
    $('#modalTitle').textContent = title;
    replaceChildren($('#modalBody'), children);
    $('#modal').showModal();
  }

  function filterNodes(query) {
    const term = String(query ?? '').trim().toLowerCase();
    for (const [selector, records, key] of [['.node', state.data.nodes, 'node'], ['.world', state.data.worlds, 'world']]) {
      $$(selector).forEach((element) => {
        const record = records.find((item) => item.id === element.dataset[key]);
        element.hidden = Boolean(term && !JSON.stringify(record ?? {}).toLowerCase().includes(term));
      });
    }
  }

  function toggleMap() {
    state.mapMode = !state.mapMode;
    $('#mapLayer').hidden = !state.mapMode;
    $('#worldLayer').hidden = state.mapMode;
    $('#nodeLayer').hidden = state.mapMode;
    $('#toggleMap').setAttribute('aria-pressed', String(state.mapMode));
    $('#modeReadout').textContent = state.mapMode ? 'GLOBAL MAP' : 'ART BOARD';
    state.zoomIndex = state.mapMode ? 3 : 4;
    applyZoom();
  }

  function bindEvents() {
    $('#zoomIn').addEventListener('click', () => changeZoom(1));
    $('#zoomOut').addEventListener('click', () => changeZoom(-1));
    $('#zoomReset').addEventListener('click', resetView);
    $('#toggleMap').addEventListener('click', toggleMap);
    $('#togglePanels').addEventListener('click', (event) => {
      const minimized = $('#widgets').classList.toggle('minimized');
      event.currentTarget.setAttribute('aria-pressed', String(minimized));
      event.currentTarget.textContent = minimized ? 'Expand panels' : 'Minimize panels';
    });
    $('#openHelp').addEventListener('click', () => showModal('How to use the Art Board', [createNode('p', { text: 'Green means complete only inside the displayed release-unit scope. The map is simulated, contains zero users and performs no tracking.' })]));
    $('#closeModal').addEventListener('click', () => $('#modal').close());
    $('#showEvidence').addEventListener('click', () => {
      if (!state.selected) return;
      showModal('Public evidence record', [createNode('pre', { text: JSON.stringify(state.selected, null, 2) }), createNode('p', { text: 'Public fixture evidence only. Private runtime state is not exposed or inferred.' })]);
    });
    $('#showSuggestion').addEventListener('click', () => {
      const suggestions = Array.isArray(state.data.suggestions) ? state.data.suggestions : [];
      const suggestion = suggestions.length ? suggestions[state.suggestionIndex++ % suggestions.length] : 'No public suggestion is available.';
      showModal('8x8 suggestion', [createNode('p', { text: suggestion })]);
    });
    $('#nodeFilter').addEventListener('input', (event) => filterNodes(event.target.value));
    $$('.quick-links button').forEach((button) => button.addEventListener('click', () => inspect(state.data.worlds.find((world) => world.id === button.dataset.focus), 'world')));
    $$('.widget-toggle').forEach((button) => button.addEventListener('click', () => {
      const collapsed = button.closest('.widget').classList.toggle('collapsed');
      button.textContent = collapsed ? '+' : '−';
      button.setAttribute('aria-expanded', String(!collapsed));
    }));
    $('#board').addEventListener('click', (event) => {
      const world = event.target.closest('[data-world]');
      const recordNode = event.target.closest('[data-node]');
      const presence = event.target.closest('[data-presence]');
      if (world) inspect(state.data.worlds.find((item) => item.id === world.dataset.world), 'world');
      if (recordNode) inspect(state.data.nodes.find((item) => item.id === recordNode.dataset.node), 'node');
      if (presence) inspect(state.data.presence_clusters.find((item) => item.id === presence.dataset.presence), 'presence');
    });

    const viewport = $('#boardViewport');
    const stopDragging = () => { state.dragging = false; };
    viewport.addEventListener('pointerdown', (event) => {
      state.dragging = true;
      state.pointerX = event.clientX;
      state.pointerY = event.clientY;
      viewport.setPointerCapture(event.pointerId);
    });
    viewport.addEventListener('pointermove', (event) => {
      if (!state.dragging) return;
      viewport.scrollLeft -= event.clientX - state.pointerX;
      viewport.scrollTop -= event.clientY - state.pointerY;
      state.pointerX = event.clientX;
      state.pointerY = event.clientY;
    });
    viewport.addEventListener('pointerup', stopDragging);
    viewport.addEventListener('pointercancel', stopDragging);
    viewport.addEventListener('lostpointercapture', stopDragging);
    viewport.addEventListener('wheel', (event) => {
      if (!event.ctrlKey) return;
      event.preventDefault();
      changeZoom(event.deltaY < 0 ? 1 : -1);
    }, { passive: false });
    window.addEventListener('keydown', (event) => {
      if (event.target instanceof HTMLInputElement) return;
      if (event.key === '+' || event.key === '=') changeZoom(1);
      if (event.key === '-') changeZoom(-1);
      if (event.key === '0') resetView();
      if (event.key.toLowerCase() === 'm') toggleMap();
      if (event.key === 'Escape' && $('#modal').open) $('#modal').close();
    });
  }

  function renderFailure(error) {
    document.body.replaceChildren(createNode('main', {
      className: 'panel glass failure-panel',
      children: [createNode('h1', { text: 'Art Board blocked' }), createNode('p', { text: 'The public state failed validation. Nothing was rendered.' }), createNode('pre', { text: error instanceof Error ? error.message : 'Unknown error' })]
    }));
  }

  async function start() {
    try {
      const response = await fetch('./state.json', { cache: 'no-store', credentials: 'same-origin', redirect: 'error' });
      if (!response.ok) throw new Error(`State request failed: ${response.status}`);
      if (!(response.headers.get('content-type') || '').includes('json')) throw new Error('State response is not JSON');
      state.data = await response.json();
      if (state.data.schema_version !== '8x8.public-art-board.v1' || state.data.mode !== 'PUBLIC_SAFE_FIXTURE') throw new Error('Unsupported public state');
      if (state.data.score.earned !== 100 || state.data.score.possible !== 100) throw new Error('Release-unit score is not complete');
      $('#truthBanner').textContent = state.data.truth_banner;
      $('#sliceScore').textContent = `${state.data.score.earned}/${state.data.score.possible}`;
      renderLegend(); renderWorlds(); renderNodes(); renderPresence(); renderWidgets(); bindEvents(); applyZoom(); resetView();
    } catch (error) {
      renderFailure(error);
    }
  }

  start();
})();
