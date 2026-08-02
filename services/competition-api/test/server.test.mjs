import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';

const port = 18080 + Math.floor(Math.random() * 1000);
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

test.before(async () => {
  child = spawn(process.execPath, ['server.mjs'], {
    cwd: new URL('..', import.meta.url),
    env: {...process.env, PORT:String(port), GEMINI_API_KEY:'', PUBLIC_ORIGIN:'https://example.test'},
    stdio: ['ignore', 'pipe', 'pipe']
  });
  await waitForHealth();
});

test.after(() => child?.kill('SIGTERM'));

test('health reports missing Gemini configuration', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/healthz`);
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.equal(body.gemini_configured, false);
  assert.equal(body.deployment_truth, 'LOCAL_OR_UNVERIFIED');
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

test('mission planning requires explicit consent', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/api/v1/missions/plan`, {
    method:'POST',
    headers:{'content-type':'application/json'},
    body:JSON.stringify({goal:'Create a launch plan for a neighborhood bakery', consent:false})
  });
  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, 'CONSENT_REQUIRED');
});

test('mission planning fails closed without Gemini configuration', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/api/v1/missions/plan`, {
    method:'POST',
    headers:{'content-type':'application/json'},
    body:JSON.stringify({goal:'Create a launch plan for a neighborhood bakery', consent:true})
  });
  assert.equal(response.status, 503);
  assert.equal((await response.json()).error, 'GEMINI_NOT_CONFIGURED');
});

test('unknown routes return a minimal response', async () => {
  const response = await fetch(`http://127.0.0.1:${port}/missing`);
  assert.equal(response.status, 404);
  assert.deepEqual(await response.json(), {error:'NOT_FOUND'});
});
