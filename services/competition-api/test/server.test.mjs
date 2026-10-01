import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';

const port = 18080 + Math.floor(Math.random() * 1000);
const allowedOrigin = 'https://example.test';
let child;

async function waitForHealth() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/healthz`);
      if (response.ok) return;
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('server did not start');
}

function missionRequest(body, {origin = allowedOrigin, contentType = 'application/json'} = {}) {
  const headers = {origin};
  if (contentType) headers['content-type'] = contentType;
  return fetch(`http://127.0.0.1:${port}/api/v1/missions/plan`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });
}

test.before(async () => {
  child = spawn(process.execPath, ['server.mjs'], {
    cwd: new URL('..', import.meta.url),
    env: {
      ...process.env,
      PORT: String(port),
      GEMINI_API_KEY: '',
      PUBLIC_ORIGIN: allowedOrigin,
      RATE_LIMIT_PER_MINUTE: '50'
    },
    stdio: ['ignore', 'pipe', 'pipe']
  });
  await waitForHealth();
});

test.after(() => child?.kill('SIGTERM'));

test('health reports missing Gemini configuration and configured origin', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/healthz`);
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.equal(body.gemini_configured, false);
  assert.equal(body.public_origin_configured, true);
  assert.equal(body.deployment_truth, 'LOCAL_OR_UNVERIFIED');
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(response.headers.get('x-frame-options'), 'DENY');
});

test('system exposes bounded authority and 64 sectors', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/api/v1/system`);
  const body = await response.json();
  assert.equal(body.worlds, 8);
  assert.equal(body.sectors, 64);
  assert.equal(body.authority.autonomous_ceiling, 'L3');
  assert.equal(body.authority.dormant_owner_only, 'L5');
  assert.equal(body.protected_execution_enabled, false);
});

test('mission planning rejects foreign browser origins before processing', async () => {
  const response = await missionRequest(
    {goal: 'Create a launch plan for a neighborhood bakery', template: 'launch-business', consent: true},
    {origin: 'https://attacker.invalid'}
  );
  assert.equal(response.status, 403);
  assert.deepEqual(await response.json(), {error: 'ORIGIN_NOT_ALLOWED'});
});

test('preflight allows only the configured origin', async () => {
  const allowed = await fetch(`http://127.0.0.1:${port}/api/v1/missions/plan`, {
    method: 'OPTIONS',
    headers: {origin: allowedOrigin}
  });
  assert.equal(allowed.status, 204);
  assert.equal(allowed.headers.get('access-control-allow-origin'), allowedOrigin);

  const rejected = await fetch(`http://127.0.0.1:${port}/api/v1/missions/plan`, {
    method: 'OPTIONS',
    headers: {origin: 'https://attacker.invalid'}
  });
  assert.equal(rejected.status, 403);
});

test('mission planning requires JSON content type', async () => {
  const response = await missionRequest(
    {goal: 'Create a launch plan for a neighborhood bakery', template: 'launch-business', consent: true},
    {contentType: 'text/plain'}
  );
  assert.equal(response.status, 415);
  assert.equal((await response.json()).error, 'CONTENT_TYPE_REQUIRED');
});

test('mission planning requires explicit consent', async () => {
  const response = await missionRequest({
    goal: 'Create a launch plan for a neighborhood bakery',
    template: 'launch-business',
    consent: false
  });
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, 'CONSENT_REQUIRED');
});

test('mission planning rejects unknown templates', async () => {
  const response = await missionRequest({
    goal: 'Create a launch plan for a neighborhood bakery',
    template: 'unbounded-mystery-mode',
    consent: true
  });
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, 'TEMPLATE_NOT_ALLOWED');
});

test('mission planning fails closed without Gemini configuration', async () => {
  const response = await missionRequest({
    goal: 'Create a launch plan for a neighborhood bakery',
    template: 'launch-business',
    consent: true
  });
  assert.equal(response.status, 503);
  const body = await response.json();
  assert.equal(body.error, 'GEMINI_NOT_CONFIGURED');
  assert.equal(typeof body.request_id, 'string');
  assert.equal(Object.hasOwn(body, 'detail'), false);
});

test('unknown routes return a minimal response', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/missing`);
  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), {error: 'NOT_FOUND'});
});
