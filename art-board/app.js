(() => {
  'use strict';

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const state = {
    data: null,
    zoom: 1,
    mapMode: false,
    selected: null,
    panX: 0,
    panY: 0,
    dragging: false,
    pointerX: 0,
    pointerY: 0
  };

  const worldPositions = [
    [50, 12], [76, 24], [86, 51], [73, 76],
    [50, 86], [27, 76], [14, 51], [24, 24]
  ];
  const nodePositions = [
    [50, 31], [63, 40], [64, 60], [50, 68], [36, 60], [37, 40]
  ];

  function safeToken(value) {
    return String(value ?? '').replace(/[^A-Za-z0-9_-]/g, '') || 'UNKNOWN';
  }

  function boundedPercent(value) {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return 0;
    return Math.min(100, Math.max(0, numeric));
  }

  function node(tag, options = {}) {
    const element = document.createElement(tag);
    if (options.className) element.className = options.className;
    if (options.text !== undefined) element.textContent = String(options.text);
    if (options.title !== undefined) element.title = String(options.title);
    for (const [name, value] of Object.entries(options.attributes || {})) {
      element.setAttribute(name, String(value));
    }
    for (const child of options.children || []) {
      if (child) element.append(child);
    }
    return element;
  }

  function labelledParagraph(label, value) {
    return node('p', {
      children: [
        node('b', { text: `${label}: ` }),
        document.createTextNode(String(value ?? ''))
      ]
    });
  }

  function replaceChildren(target, children) {
    target.replaceChildren(...children.filter(Boolean));
  }

  function position(element, x, y, centered = false) {
    element.style.left = `${boundedPercent(x)}%`;
    element.style.top = `${boundedPercent(y)}%`;
    if (centered) element.style.transform = 'translate(-50%,-50%)';
  }

  function applyTransform() {
    const board = $('#board');
    board.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
    $('#zoomReadout').textContent = `${Math.round(state.zoom * 100)}%`;
    $('#zoomReset').textContent = `${Math.round(state.zoom * 100)}%`;
  }

  function setZoom(next) {
    const numeric = Number(next);
    if (!Number.isFinite(numeric)) return;
    state.zoom = Math.min(1.8, Math.max(0.55, Number(numeric.toFixed(2))));
    applyTransform();
  }

  function renderLegend() {
    const entries = Object.entries(state.data.palette).map(([token, description]) => {
      const swatch = node('span', {
        className: `swatch status-${safeToken(token)}`,
        attributes: { 'aria-hidden': 'true' }
      });
      const text = node('span', {
        children: [node('b', { text: token }), node('br'), document.createTextNode(String(description))]
      });
      return node('div', { className: 'legend-item', children: [swatch, text] });
    });
    replaceChildren($('#legend'), entries);
  }

  function renderWorlds() {
    const elements = state.data.worlds.map((world, index) => {
      const [x, y] = worldPositions[index] || [50, 50];
      const button = node('button', {
        className: `world status-${safeToken(world.status)}`,
        attributes: {
          'data-world': world.id,
          'aria-label': `${world.label}, ${world.status}`
        },
        children: [
          node('b', { text: world.label }),
          node('small', { text: `${world.score}/100 • ${world.evidence}` })
        ]
      });
      position(button, x, y, true);
      return button;
    });
    replaceChildren($('#worldLayer'), elements);
  }

  function renderNodes() {
    const elements = state.data.nodes.map((record, index) => {
      const [x, y] = nodePositions[index % nodePositions.length] || [50, 50];
      const button = node('button', {
        className: `node status-${safeToken(record.status)}`,
        text: record.shortcut,
        title: record.label,
        attributes: {
          'data-node': record.id,
          'aria-label': `${record.label}, ${record.status}`
        }
      });
      position(button, x, y, true);
      return button;
    });
    replaceChildren($('#nodeLayer'), elements);
  }

  function renderPresence() {
    const elements = state.data.presence_clusters.map((cluster) => {
      const button = node('button', {
        className: `presence status-${safeToken(cluster.status)}`,
        attributes: {
          'data-presence': cluster.id,
          'data-label': cluster.label,
          'aria-label': `${cluster.label}; simulated; count zero`
        }
      });
      position(button, cluster.x, cluster.y);
      return button;
    });
    replaceChildren($('#presenceLayer'), elements);
  }

  function renderWidgets() {
    const treasury = state.data.treasury;
    replaceChildren($('#treasuryWidget'), [
      labelledParagraph('Status', treasury.status),
      node('p', { text: treasury.notice }),
      labelledParagraph('Networks', treasury.networks.join(', ')),
      node('p', {
        children: [
          node('b', { text: 'Balances: ' }), document.createTextNode('hidden / unavailable'),
          node('br'), node('b', { text: 'Signing: ' }), document.createTextNode('disabled')
        ]
      })
    ]);
    replaceChildren($('#suggestions'), state.data.suggestions.map((item) => node('li', { text: item })));
  }

  function addFact(fragment, label, value) {
    if (value === undefined || value === null || value === '') return;
    fragment.append(node('dt', { text: label }), node('dd', { text: value }));
  }

  function inspect(item, kind) {
    if (!item || typeof item !== 'object') return;
    state.selected = { item, kind };
    $('#detailTitle').textContent = item.label || item.id || 'Unknown record';
    $('#detailSummary').textContent = item.summary || item.description || item.help || 'Public-safe record.';
    const fragment = document.createDocumentFragment();
    addFact(fragment, 'Type', item.type || String(kind).toUpperCase());
    addFact(fragment, 'Status', item.status);
    addFact(fragment, 'Evidence', item.evidence);
    addFact(fragment, 'Score', item.score !== undefined ? `${item.score}/100` : null);
    addFact(fragment, 'World', item.world);
    addFact(fragment, 'Mode', item.mode);
    addFact(fragment, 'Region', item.region);
    addFact(fragment, 'Count', item.count);
    $('#detailFacts').replaceChildren(fragment);
    $('#showEvidence').disabled = false;
  }

  function showModal(title, children) {
    $('#modalTitle').textContent = title;
    replaceChildren($('#modalBody'), children);
    $('#modal').showModal();
  }

  function showEvidence() {
    if (!state.selected) return;
    const { item, kind } = state.selected;
    showModal('Public evidence record', [
      labelledParagraph('Record class', kind),
      node('pre', { text: JSON.stringify(item, null, 2) }),
      node('p', { text: 'This is public fixture evidence only. It does not expose or prove private runtime state.' })
    ]);
  }

  function showSuggestion() {
    const suggestions = Array.isArray(state.data.suggestions) ? state.data.suggestions : [];
    const suggestion = suggestions.length
      ? suggestions[Math.floor(Math.random() * suggestions.length)]
      : 'No public suggestion is available.';
    showModal('8x8 suggestion', [node('p', { text: suggestion })]);
  }

  function filterNodes(query) {
    const term = String(query ?? '').trim().toLowerCase();
    $$('.node').forEach((element) => {
      const record = state.data.nodes.find((entry) => entry.id === element.dataset.node);
      const haystack = JSON.stringify(record ?? {}).toLowerCase();
      element.hidden = Boolean(term && !haystack.includes(term));
    });
    $$('.world').forEach((element) => {
      const record = state.data.worlds.find((entry) => entry.id === element.dataset.world);
      const haystack = JSON.stringify(record ?? {}).toLowerCase();
      element.hidden = Boolean(term && !haystack.includes(term));
    });
  }

  function focusWorld(id) {
    const element = $(`[data-world="${CSS.escape(String(id))}"]`);
    if (!element) return;
    state.mapMode = false;
    $('#mapLayer').hidden = true;
    $('#worldLayer').hidden = false;
    $('#nodeLayer').hidden = false;
    $('#toggleMap').setAttribute('aria-pressed', 'false');
    $('#modeReadout').textContent = 'ART BOARD';
    setZoom(1.35);
    inspect(state.data.worlds.find((world) => world.id === id), 'world');
    element.focus({ preventScroll: true });
  }

  function toggleMap() {
    state.mapMode = !state.mapMode;
    $('#mapLayer').hidden = !state.mapMode;
    $('#worldLayer').hidden = state.mapMode;
    $('#nodeLayer').hidden = state.mapMode;
    $('#toggleMap').setAttribute('aria-pressed', String(state.mapMode));
    $('#modeReadout').textContent = state.mapMode ? 'GLOBAL MAP' : 'ART BOARD';
    state.panX = 0;
    state.panY = 0;
    setZoom(state.mapMode ? 0.88 : 1);
  }

  function helpContent() {
    const items = [
      'Green means complete only inside the displayed release-unit scope.',
      'Red is down or blocked; orange is degraded; yellow is incomplete; black is unknown or hidden.',
      'Use zoom, drag, filters, shortcuts and bubbles to inspect public evidence.',
      'The map contains simulated regional markers with zero users and no tracking.'
    ];
    return [node('ul', { children: items.map((item) => node('li', { text: item })) })];
  }

  function bindEvents() {
    $('#zoomIn').addEventListener('click', () => setZoom(state.zoom + 0.1));
    $('#zoomOut').addEventListener('click', () => setZoom(state.zoom - 0.1));
    $('#zoomReset').addEventListener('click', () => { state.panX = 0; state.panY = 0; setZoom(1); });
    $('#toggleMap').addEventListener('click', toggleMap);
    $('#togglePanels').addEventListener('click', (event) => {
      const minimized = $('#widgets').classList.toggle('minimized');
      event.currentTarget.setAttribute('aria-pressed', String(minimized));
      event.currentTarget.textContent = minimized ? 'Expand panels' : 'Minimize panels';
    });
    $('#openHelp').addEventListener('click', () => showModal('How to use the Art Board', helpContent()));
    $('#closeModal').addEventListener('click', () => $('#modal').close());
    $('#showEvidence').addEventListener('click', showEvidence);
    $('#showSuggestion').addEventListener('click', showSuggestion);
    $('#nodeFilter').addEventListener('input', (event) => filterNodes(event.target.value));
    $$('.quick-links button').forEach((button) => button.addEventListener('click', () => focusWorld(button.dataset.focus)));
    $$('.widget-toggle').forEach((button) => button.addEventListener('click', () => {
      const widget = button.closest('.widget');
      const collapsed = widget.classList.toggle('collapsed');
      button.textContent = collapsed ? '+' : '−';
      button.setAttribute('aria-expanded', String(!collapsed));
    }));
    $('#board').addEventListener('click', (event) => {
      const worldButton = event.target.closest('[data-world]');
      const nodeButton = event.target.closest('[data-node]');
      const presenceButton = event.target.closest('[data-presence]');
      if (worldButton) inspect(state.data.worlds.find((world) => world.id === worldButton.dataset.world), 'world');
      if (nodeButton) inspect(state.data.nodes.find((entry) => entry.id === nodeButton.dataset.node), 'node');
      if (presenceButton) inspect(state.data.presence_clusters.find((cluster) => cluster.id === presenceButton.dataset.presence), 'presence');
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
      state.panX += event.clientX - state.pointerX;
      state.panY += event.clientY - state.pointerY;
      state.pointerX = event.clientX;
      state.pointerY = event.clientY;
      applyTransform();
    });
    viewport.addEventListener('pointerup', stopDragging);
    viewport.addEventListener('pointercancel', stopDragging);
    viewport.addEventListener('lostpointercapture', stopDragging);
    viewport.addEventListener('wheel', (event) => {
      event.preventDefault();
      setZoom(state.zoom + (event.deltaY < 0 ? 0.08 : -0.08));
    }, { passive: false });
    window.addEventListener('keydown', (event) => {
      if (event.target instanceof HTMLInputElement) return;
      const shortcut = event.key.toUpperCase();
      const record = state.data.nodes.find((item) => item.shortcut === shortcut);
      if (record) inspect(record, 'node');
      if (event.key === '+' || event.key === '=') setZoom(state.zoom + 0.1);
      if (event.key === '-') setZoom(state.zoom - 0.1);
      if (event.key === '0') { state.panX = 0; state.panY = 0; setZoom(1); }
      if (event.key.toLowerCase() === 'm') toggleMap();
      if (event.key === 'Escape' && $('#modal').open) $('#modal').close();
    });
  }

  function renderFailure(error) {
    const panel = node('main', {
      className: 'panel glass',
      children: [
        node('h1', { text: 'Art Board blocked' }),
        node('p', { text: 'The public state failed validation. Nothing was rendered.' }),
        node('pre', { text: error instanceof Error ? error.message : 'Unknown error' })
      ]
    });
    panel.style.margin = '2rem';
    document.body.replaceChildren(panel);
  }

  async function start() {
    try {
      const response = await fetch('./state.json', { cache: 'no-store', credentials: 'same-origin', redirect: 'error' });
      if (!response.ok) throw new Error(`State request failed: ${response.status}`);
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('json')) throw new Error('State response is not JSON');
      state.data = await response.json();
      if (state.data.schema_version !== '8x8.public-art-board.v1') throw new Error('Unsupported state schema');
      if (state.data.mode !== 'PUBLIC_SAFE_FIXTURE') throw new Error('Only public-safe fixture mode is accepted');
      if (state.data.score.earned !== 100 || state.data.score.possible !== 100) throw new Error('Release-unit score is not complete');
      $('#truthBanner').textContent = state.data.truth_banner;
      $('#sliceScore').textContent = `${state.data.score.earned}/${state.data.score.possible}`;
      renderLegend();
      renderWorlds();
      renderNodes();
      renderPresence();
      renderWidgets();
      bindEvents();
      applyTransform();
    } catch (error) {
      renderFailure(error);
    }
  }

  start();
})();
