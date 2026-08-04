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

  function safeText(value) {
    return String(value ?? '').replace(/[<>]/g, '');
  }

  function applyTransform() {
    const board = $('#board');
    board.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
    $('#zoomReadout').textContent = `${Math.round(state.zoom * 100)}%`;
    $('#zoomReset').textContent = `${Math.round(state.zoom * 100)}%`;
  }

  function setZoom(next) {
    state.zoom = Math.min(1.8, Math.max(0.55, Number(next.toFixed(2))));
    applyTransform();
  }

  function renderLegend() {
    $('#legend').innerHTML = Object.entries(state.data.palette)
      .map(([token, description]) => `
        <div class="legend-item">
          <span class="swatch status-${safeText(token)}" aria-hidden="true"></span>
          <span><b>${safeText(token)}</b><br>${safeText(description)}</span>
        </div>`)
      .join('');
  }

  function renderWorlds() {
    $('#worldLayer').innerHTML = state.data.worlds.map((world, index) => {
      const [x, y] = worldPositions[index];
      return `<button class="world status-${safeText(world.status)}" style="left:${x}%;top:${y}%;transform:translate(-50%,-50%)" data-world="${safeText(world.id)}" aria-label="${safeText(world.label)}, ${safeText(world.status)}">
        <b>${safeText(world.label)}</b><small>${safeText(world.score)}/100 • ${safeText(world.evidence)}</small>
      </button>`;
    }).join('');
  }

  function renderNodes() {
    $('#nodeLayer').innerHTML = state.data.nodes.map((node, index) => {
      const [x, y] = nodePositions[index % nodePositions.length];
      return `<button class="node status-${safeText(node.status)}" style="left:${x}%;top:${y}%;transform:translate(-50%,-50%)" data-node="${safeText(node.id)}" title="${safeText(node.label)}" aria-label="${safeText(node.label)}, ${safeText(node.status)}">${safeText(node.shortcut)}</button>`;
    }).join('');
  }

  function renderPresence() {
    $('#presenceLayer').innerHTML = state.data.presence_clusters.map((cluster) => `
      <button class="presence status-${safeText(cluster.status)}" style="left:${cluster.x}%;top:${cluster.y}%" data-presence="${safeText(cluster.id)}" data-label="${safeText(cluster.label)}" aria-label="${safeText(cluster.label)}; simulated; count zero"></button>
    `).join('');
  }

  function renderWidgets() {
    $('#treasuryWidget').innerHTML = `
      <p><b>Status:</b> ${safeText(state.data.treasury.status)}</p>
      <p>${safeText(state.data.treasury.notice)}</p>
      <p><b>Networks:</b> ${state.data.treasury.networks.map(safeText).join(', ')}</p>
      <p><b>Balances:</b> hidden / unavailable<br><b>Signing:</b> disabled</p>`;
    $('#suggestions').innerHTML = state.data.suggestions.map((item) => `<li>${safeText(item)}</li>`).join('');
  }

  function inspect(item, kind) {
    state.selected = { item, kind };
    $('#detailTitle').textContent = item.label || item.id;
    $('#detailSummary').textContent = item.summary || item.description || item.help || 'Public-safe record.';
    const facts = [];
    const add = (label, value) => {
      if (value !== undefined && value !== null && value !== '') facts.push(`<dt>${safeText(label)}</dt><dd>${safeText(value)}</dd>`);
    };
    add('Type', item.type || kind.toUpperCase());
    add('Status', item.status);
    add('Evidence', item.evidence);
    add('Score', item.score !== undefined ? `${item.score}/100` : null);
    add('World', item.world);
    add('Mode', item.mode);
    add('Region', item.region);
    add('Count', item.count);
    $('#detailFacts').innerHTML = facts.join('');
    $('#showEvidence').disabled = false;
  }

  function showModal(title, html) {
    $('#modalTitle').textContent = title;
    $('#modalBody').innerHTML = html;
    $('#modal').showModal();
  }

  function showEvidence() {
    if (!state.selected) return;
    const { item, kind } = state.selected;
    showModal('Public evidence record', `
      <p><b>Record class:</b> ${safeText(kind)}</p>
      <pre>${safeText(JSON.stringify(item, null, 2))}</pre>
      <p>This is public fixture evidence only. It does not expose or prove private runtime state.</p>`);
  }

  function showSuggestion() {
    const suggestion = state.data.suggestions[Math.floor(Math.random() * state.data.suggestions.length)];
    showModal('8x8 suggestion', `<p>${safeText(suggestion)}</p>`);
  }

  function filterNodes(query) {
    const term = query.trim().toLowerCase();
    $$('.node').forEach((element) => {
      const record = state.data.nodes.find((node) => node.id === element.dataset.node);
      const haystack = JSON.stringify(record).toLowerCase();
      element.hidden = term && !haystack.includes(term);
    });
    $$('.world').forEach((element) => {
      const record = state.data.worlds.find((world) => world.id === element.dataset.world);
      const haystack = JSON.stringify(record).toLowerCase();
      element.hidden = term && !haystack.includes(term);
    });
  }

  function focusWorld(id) {
    const element = $(`[data-world="${CSS.escape(id)}"]`);
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
    $('#openHelp').addEventListener('click', () => showModal('How to use the Art Board', `
      <ul>
        <li>Green means complete only inside the displayed release-unit scope.</li>
        <li>Red is down or blocked; orange is degraded; yellow is incomplete; black is unknown or hidden.</li>
        <li>Use zoom, drag, filters, shortcuts and bubbles to inspect public evidence.</li>
        <li>The map contains simulated regional markers with zero users and no tracking.</li>
      </ul>`));
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
      if (nodeButton) inspect(state.data.nodes.find((node) => node.id === nodeButton.dataset.node), 'node');
      if (presenceButton) inspect(state.data.presence_clusters.find((cluster) => cluster.id === presenceButton.dataset.presence), 'presence');
    });

    const viewport = $('#boardViewport');
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
    viewport.addEventListener('pointerup', () => { state.dragging = false; });
    viewport.addEventListener('wheel', (event) => {
      event.preventDefault();
      setZoom(state.zoom + (event.deltaY < 0 ? 0.08 : -0.08));
    }, { passive: false });
    window.addEventListener('keydown', (event) => {
      if (event.target instanceof HTMLInputElement) return;
      const shortcut = event.key.toUpperCase();
      const node = state.data.nodes.find((item) => item.shortcut === shortcut);
      if (node) inspect(node, 'node');
      if (event.key === '+' || event.key === '=') setZoom(state.zoom + 0.1);
      if (event.key === '-') setZoom(state.zoom - 0.1);
      if (event.key === '0') { state.panX = 0; state.panY = 0; setZoom(1); }
      if (event.key.toLowerCase() === 'm') toggleMap();
      if (event.key === 'Escape' && $('#modal').open) $('#modal').close();
    });
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
      document.body.innerHTML = `<main class="panel glass" style="margin:2rem"><h1>Art Board blocked</h1><p>The public state failed validation. Nothing was rendered.</p><pre>${safeText(error.message)}</pre></main>`;
    }
  }

  start();
})();
