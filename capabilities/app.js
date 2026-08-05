(() => {
  'use strict';
  const LEDGER_URL = '../research/external-capabilities/CANDIDATE_STATUS_LEDGER_V4.json';
  const state = { ledger: null, filter: 'ALL' };
  const byId = (id) => document.getElementById(id);

  function textNode(tag, text, className) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = String(text ?? '');
    return element;
  }

  function classify(candidate) {
    const decision = String(candidate.decision || '');
    const packet = String(candidate.packet || '');
    const runtime = String(candidate.runtime || '');
    if (packet.includes('DISABLED_ADAPTER_CONTRACT') && runtime.includes('NOT_INSTALLED')) return { key: 'ADAPTER_CONTRACT_MERGED', label: 'Disabled adapter contract', className: 'ready' };
    if (decision.includes('NARROW_SUBSET_ELIGIBLE') && packet.includes('CANARY_PASS')) return { key: 'READY_FOR_ADAPTER_DESIGN', label: 'Adapter design eligible', className: 'ready' };
    if (decision.includes('REJECT') || packet.includes('BLOCKED') || runtime.includes('BLOCKED')) return { key: 'BLOCKED', label: 'Blocked', className: 'blocked' };
    if (decision.includes('DEFER')) return { key: 'DEFERRED', label: 'Deferred', className: 'deferred' };
    if (decision.includes('PATTERN') || decision.includes('SCHEMA') || decision.includes('IDEAS') || decision.includes('KNOWLEDGE') || decision.includes('TAXONOMY')) return { key: 'PATTERNS_ONLY', label: 'Patterns only', className: 'patterns' };
    return { key: 'PATTERNS_ONLY', label: 'Reviewed', className: 'unknown' };
  }

  function displayEvidence(value) {
    if (Array.isArray(value)) return value.join(', ');
    if (value && typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  function candidateCard(candidate) {
    const status = classify(candidate);
    const article = document.createElement('article');
    article.className = 'candidate';
    article.dataset.status = status.key;
    const header = document.createElement('header');
    const identity = document.createElement('div');
    identity.append(textNode('h3', candidate.id), textNode('div', candidate.repository, 'repo'));
    header.append(identity, textNode('span', status.label, `status ${status.className}`));
    article.append(header, textNode('div', candidate.pin, 'pin'), textNode('div', candidate.decision, 'decision'), textNode('div', candidate.runtime, 'runtime'));
    if (candidate.evidence && typeof candidate.evidence === 'object') {
      const evidence = document.createElement('div');
      evidence.className = 'evidence-list';
      for (const [key, value] of Object.entries(candidate.evidence)) evidence.append(textNode('span', `${key}: ${displayEvidence(value)}`));
      article.append(evidence);
    }
    return article;
  }

  function renderCandidates() {
    const candidates = state.ledger.candidates.filter((candidate) => state.filter === 'ALL' || classify(candidate).key === state.filter);
    const grid = byId('candidateGrid');
    grid.replaceChildren(...candidates.map(candidateCard));
    if (!candidates.length) grid.append(textNode('p', 'No candidates match this filter.', 'error'));
  }

  function describeDependency(record) {
    if (record.id === 'AIRLLM_CUDA_BENCHMARK') return 'Requires a dedicated owner-approved NVIDIA CUDA node, an approved model license, storage and cost authority, measured performance evidence, and verified cleanup. It is explicitly rejected on Samsung Termux and the active Ubuntu PRoot.';
    if (record.id === 'REAL_RESEARCH_COUNCIL') return 'Requires four real identity-, lease-, input-digest-, output-digest- and receipt-bound votes. ChatGPT advisory output does not count toward quorum.';
    return String(record.state || 'Evidence remains incomplete.');
  }

  function renderRemaining() {
    const articles = (state.ledger.remaining_dependencies || []).map((dependency) => {
      const article = document.createElement('article');
      article.append(textNode('h3', dependency.id), textNode('div', dependency.state, 'pin'), textNode('p', describeDependency(dependency)));
      return article;
    });
    byId('remainingGrid').replaceChildren(...articles);
  }

  function renderSummary() {
    const summary = state.ledger.summary;
    byId('packetCount').textContent = `${summary.candidate_packets_merged}/${summary.candidate_count}`;
    byId('benchmarkCount').textContent = `${summary.external_measured_benchmarks_complete}/${summary.external_measured_benchmarks_required}`;
    byId('adapterCount').textContent = String(summary.disabled_adapter_contracts_merged);
    byId('installedCount').textContent = String(summary.third_party_candidates_installed_into_8x8);
    byId('councilCount').textContent = `${summary.real_council_votes}/${state.ledger.council.quorum_required}`;
    byId('truthState').textContent = state.ledger.truth_state;
  }

  function validateLedger(ledger) {
    if (!ledger || ledger.schema_version !== '4.0.0') throw new Error('Unsupported or missing ledger schema.');
    if (!Array.isArray(ledger.candidates) || ledger.candidates.length !== 13) throw new Error('Expected exactly thirteen candidates.');
    if (ledger.summary.disabled_adapter_contracts_merged !== 1) throw new Error('Expected exactly one merged disabled adapter contract.');
    if (ledger.summary.third_party_candidates_installed_into_8x8 !== 0) throw new Error('Public observatory refuses a ledger claiming runtime installation without a new release contract.');
    if (ledger.absolute_boundaries.production_deployment_performed !== false) throw new Error('Unexpected production deployment boundary.');
    const vision = ledger.candidates.find((candidate) => candidate.id === 'MSG197-VISION-001');
    const contract = vision && vision.evidence && vision.evidence.adapter_contract;
    if (!contract || contract.enabled !== false || contract.install_state !== 'NOT_INSTALLED' || contract.runtime_authority !== 'NONE' || contract.production_ready !== false) {
      throw new Error('Supervision adapter contract must remain disabled and uninstalled.');
    }
  }

  async function load() {
    try {
      const response = await fetch(LEDGER_URL, { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) throw new Error(`Ledger request failed with ${response.status}.`);
      const ledger = await response.json();
      validateLedger(ledger);
      state.ledger = ledger;
      renderSummary();
      renderCandidates();
      renderRemaining();
    } catch (error) {
      byId('truthState').textContent = 'FAIL_CLOSED_LEDGER_UNAVAILABLE';
      byId('candidateGrid').replaceChildren(textNode('p', `The canonical ledger could not be rendered: ${error.message}`, 'error'));
      byId('remainingGrid').replaceChildren();
    }
  }

  byId('filter').addEventListener('change', (event) => {
    state.filter = event.target.value;
    if (state.ledger) renderCandidates();
  });
  load();
})();
