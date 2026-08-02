import http from 'node:http';
import crypto from 'node:crypto';

const PORT = Number(process.env.PORT || 8080);
const HOST = '0.0.0.0';
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const PUBLIC_ORIGIN = process.env.PUBLIC_ORIGIN || '';
const MAX_BODY_BYTES = 64 * 1024;
const REQUEST_TIMEOUT_MS = Number(process.env.REQUEST_TIMEOUT_MS || 30000);
const SERVICE_REVISION = process.env.K_REVISION || 'local-unverified';

const templates = [
  {id:'launch-business', name:'Launch a business', world:'Studio, Builder & Creation'},
  {id:'build-product', name:'Build and test a product', world:'Agent Council & Automation'},
  {id:'research-problem', name:'Research a market or technical problem', world:'Workspaces, Memory & Knowledge'},
  {id:'content-campaign', name:'Create a content campaign', world:'Studio, Builder & Creation'},
  {id:'system-audit', name:'Audit a system with evidence', world:'Quality, Security & Release'}
];

function json(res, status, body, extraHeaders = {}) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
    'referrer-policy': 'no-referrer',
    ...corsHeaders(),
    ...extraHeaders
  });
  res.end(payload);
}

function corsHeaders() {
  if (!PUBLIC_ORIGIN) return {};
  return {
    'access-control-allow-origin': PUBLIC_ORIGIN,
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'access-control-allow-headers': 'content-type',
    'vary': 'origin'
  };
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function cleanText(value, max) {
  return typeof value === 'string' ? value.trim().replace(/[\u0000-\u001f]/g, ' ').slice(0, max) : '';
}

async function readJson(req) {
  let bytes = 0;
  const chunks = [];
  for await (const chunk of req) {
    bytes += chunk.length;
    if (bytes > MAX_BODY_BYTES) throw Object.assign(new Error('BODY_TOO_LARGE'), {status: 413});
    chunks.push(chunk);
  }
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
  } catch {
    throw Object.assign(new Error('INVALID_JSON'), {status: 400});
  }
}

function extractGeminiText(payload) {
  return payload?.candidates?.[0]?.content?.parts?.map(part => part.text || '').join('').trim() || '';
}

function parseModelJson(text) {
  const normalized = text.replace(/^```json\s*/i, '').replace(/\s*```$/i, '').trim();
  const parsed = JSON.parse(normalized);
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('MODEL_SCHEMA_INVALID');
  return parsed;
}

async function callGemini({goal, template, context}) {
  if (!GEMINI_API_KEY) throw Object.assign(new Error('GEMINI_NOT_CONFIGURED'), {status: 503});

  const prompt = `You are the bounded mission planner for 8x8 OS Competition Edition.\n\nCreate a practical plan for the user goal below. Do not claim that actions were executed. Do not propose wallet movement, trading, token/NFT issuance, credential changes, destructive cleanup, unrestricted shell access, surveillance, or hidden telemetry. Mark owner-gated actions clearly.\n\nReturn JSON only with this schema:\n{\n  "summary": "string",\n  "diagnosis": ["string"],\n  "tasks": [{"title":"string","agent":"string","world":"string","authority":"L0|L1|L2|L3|L4","owner_gate":true,"evidence":"string"}],\n  "deliverables": ["string"],\n  "risks": ["string"],\n  "success_metrics": ["string"]\n}\n\nTemplate: ${template}\nGoal: ${goal}\nAdditional context: ${context || 'none'}`;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(GEMINI_MODEL)}:generateContent`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-goog-api-key': GEMINI_API_KEY
      },
      signal: controller.signal,
      body: JSON.stringify({
        contents: [{role:'user', parts:[{text: prompt}]}],
        generationConfig: {responseMimeType: 'application/json'}
      })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error('GEMINI_REQUEST_FAILED');
      error.status = 502;
      error.publicDetail = payload?.error?.status || `HTTP_${response.status}`;
      throw error;
    }
    const text = extractGeminiText(payload);
    if (!text) throw Object.assign(new Error('GEMINI_EMPTY_RESPONSE'), {status: 502});
    return parseModelJson(text);
  } finally {
    clearTimeout(timeout);
  }
}

function receiptFor(input, result) {
  const body = {
    receipt_version: '1.0.0',
    mission_id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
    service_revision: SERVICE_REVISION,
    model: GEMINI_MODEL,
    execution_state: 'PLANNED_NOT_EXECUTED',
    input_digest: sha256(JSON.stringify(input)),
    output_digest: sha256(JSON.stringify(result)),
    protected_actions_executed: false,
    owner_approval_granted: false
  };
  return {...body, receipt_digest: sha256(JSON.stringify(body))};
}

async function route(req, res) {
  if (req.method === 'OPTIONS') return json(res, 204, {});
  const url = new URL(req.url, 'http://localhost');

  if (req.method === 'GET' && url.pathname === '/healthz') {
    return json(res, 200, {
      ok: true,
      service: '8x8-competition-api',
      revision: SERVICE_REVISION,
      gemini_configured: Boolean(GEMINI_API_KEY),
      deployment_truth: SERVICE_REVISION === 'local-unverified' ? 'LOCAL_OR_UNVERIFIED' : 'CLOUD_RUN_REVISION_PRESENT'
    });
  }

  if (req.method === 'GET' && url.pathname === '/api/v1/system') {
    return json(res, 200, {
      product: '8x8 OS Competition Edition',
      worlds: 8,
      sectors: 64,
      authority: {autonomous_ceiling:'L3', owner_gated:'L4', dormant_owner_only:'L5'},
      protected_execution_enabled: false,
      templates
    });
  }

  if (req.method === 'GET' && url.pathname === '/api/v1/missions/templates') {
    return json(res, 200, {templates});
  }

  if (req.method === 'POST' && url.pathname === '/api/v1/missions/plan') {
    const body = await readJson(req);
    const goal = cleanText(body.goal, 3000);
    const context = cleanText(body.context, 3000);
    const template = cleanText(body.template, 80) || 'custom';
    if (body.consent !== true) return json(res, 400, {error:'CONSENT_REQUIRED'});
    if (goal.length < 10) return json(res, 400, {error:'GOAL_TOO_SHORT'});

    const result = await callGemini({goal, template, context});
    const receipt = receiptFor({goal, template, context}, result);
    return json(res, 200, {result, receipt});
  }

  return json(res, 404, {error:'NOT_FOUND'});
}

const server = http.createServer((req, res) => {
  route(req, res).catch(error => {
    const status = Number(error.status || 500);
    console.error(JSON.stringify({event:'request_error', status, code:error.message, revision:SERVICE_REVISION}));
    json(res, status, {error:error.message || 'INTERNAL_ERROR', detail:error.publicDetail || undefined});
  });
});

server.listen(PORT, HOST, () => {
  console.log(JSON.stringify({event:'service_started', host:HOST, port:PORT, revision:SERVICE_REVISION, gemini_configured:Boolean(GEMINI_API_KEY)}));
});
