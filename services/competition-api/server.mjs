import http from 'node:http';
import crypto from 'node:crypto';

const PORT = Number(process.env.PORT || 8080);
const HOST = '0.0.0.0';
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const MAX_BODY_BYTES = 64 * 1024;
const REQUEST_TIMEOUT_MS = Math.min(Math.max(Number(process.env.REQUEST_TIMEOUT_MS || 30000), 1000), 60000);
const SERVICE_REVISION = process.env.K_REVISION || 'local-unverified';
const RATE_LIMIT_PER_MINUTE = Math.min(Math.max(Number(process.env.RATE_LIMIT_PER_MINUTE || 12), 1), 120);

function normalizedOrigin(raw) {
  if (!raw) return '';
  const parsed = new URL(raw);
  const localDevelopment = ['localhost', '127.0.0.1'].includes(parsed.hostname);
  if (parsed.protocol !== 'https:' && !(localDevelopment && parsed.protocol === 'http:')) {
    throw new Error('PUBLIC_ORIGIN_REQUIRES_HTTPS');
  }
  if (parsed.username || parsed.password || parsed.pathname !== '/' || parsed.search || parsed.hash) {
    throw new Error('PUBLIC_ORIGIN_MUST_BE_ORIGIN_ONLY');
  }
  return parsed.origin;
}

const PUBLIC_ORIGIN = normalizedOrigin(process.env.PUBLIC_ORIGIN || '');
const templates = [
  {id: 'launch-business', name: 'Launch a business', world: 'Studio, Builder & Creation'},
  {id: 'build-product', name: 'Build and test a product', world: 'Agent Council & Automation'},
  {id: 'research-problem', name: 'Research a market or technical problem', world: 'Workspaces, Memory & Knowledge'},
  {id: 'content-campaign', name: 'Create a content campaign', world: 'Studio, Builder & Creation'},
  {id: 'system-audit', name: 'Audit a system with evidence', world: 'Quality, Security & Release'}
];
const allowedTemplates = new Set(templates.map(template => template.id));
const allowedAuthorities = new Set(['L0', 'L1', 'L2', 'L3', 'L4']);
const publicErrors = new Set([
  'BODY_TOO_LARGE',
  'CONSENT_REQUIRED',
  'CONTENT_TYPE_REQUIRED',
  'GEMINI_EMPTY_RESPONSE',
  'GEMINI_NOT_CONFIGURED',
  'GEMINI_REQUEST_FAILED',
  'GOAL_TOO_SHORT',
  'INVALID_JSON',
  'MODEL_SCHEMA_INVALID',
  'ORIGIN_NOT_ALLOWED',
  'RATE_LIMITED',
  'TEMPLATE_NOT_ALLOWED'
]);
const rateWindows = new Map();

function requestOrigin(req) {
  return typeof req.headers.origin === 'string' ? req.headers.origin : '';
}

function isAllowedOrigin(req) {
  const origin = requestOrigin(req);
  return !origin || Boolean(PUBLIC_ORIGIN && origin === PUBLIC_ORIGIN);
}

function corsHeaders(req) {
  const origin = requestOrigin(req);
  if (!origin || !PUBLIC_ORIGIN || origin !== PUBLIC_ORIGIN) return {};
  return {
    'access-control-allow-origin': PUBLIC_ORIGIN,
    'access-control-allow-methods': 'GET,POST,OPTIONS',
    'access-control-allow-headers': 'content-type',
    'access-control-max-age': '600',
    'vary': 'origin'
  };
}

function json(req, res, status, body, extraHeaders = {}) {
  const payload = status === 204 ? '' : JSON.stringify(body);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'content-security-policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    'cross-origin-resource-policy': 'same-site',
    'permissions-policy': 'camera=(), microphone=(), geolocation=()',
    'referrer-policy': 'no-referrer',
    'x-content-type-options': 'nosniff',
    'x-frame-options': 'DENY',
    ...corsHeaders(req),
    ...extraHeaders
  });
  res.end(payload);
}

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function cleanText(value, max) {
  return typeof value === 'string' ? value.trim().replace(/[\u0000-\u001f\u007f]/g, ' ').slice(0, max) : '';
}

function clientKey(req) {
  const forwarded = typeof req.headers['x-forwarded-for'] === 'string' ? req.headers['x-forwarded-for'].split(',')[0].trim() : '';
  return forwarded || req.socket.remoteAddress || 'unknown';
}

function consumeRateLimit(req) {
  const now = Date.now();
  const key = sha256(clientKey(req));
  const current = rateWindows.get(key);
  if (!current || now - current.startedAt >= 60000) {
    rateWindows.set(key, {startedAt: now, count: 1});
    return true;
  }
  if (current.count >= RATE_LIMIT_PER_MINUTE) return false;
  current.count += 1;
  return true;
}

const cleanupTimer = setInterval(() => {
  const cutoff = Date.now() - 120000;
  for (const [key, value] of rateWindows.entries()) {
    if (value.startedAt < cutoff) rateWindows.delete(key);
  }
}, 60000);
cleanupTimer.unref();

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

function boundedString(value, max) {
  const cleaned = cleanText(value, max);
  if (!cleaned) throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
  return cleaned;
}

function boundedStringArray(value, maxItems = 12, maxLength = 500) {
  if (!Array.isArray(value) || value.length > maxItems) throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
  return value.map(item => boundedString(item, maxLength));
}

function parseModelJson(text) {
  const normalized = text.replace(/^```json\s*/i, '').replace(/\s*```$/i, '').trim();
  let parsed;
  try {
    parsed = JSON.parse(normalized);
  } catch {
    throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
  }

  if (!Array.isArray(parsed.tasks) || parsed.tasks.length > 16) {
    throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
  }

  const tasks = parsed.tasks.map(task => {
    if (!task || typeof task !== 'object' || Array.isArray(task)) {
      throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
    }
    const authority = cleanText(task.authority, 2);
    if (!allowedAuthorities.has(authority)) {
      throw Object.assign(new Error('MODEL_SCHEMA_INVALID'), {status: 502});
    }
    return {
      title: boundedString(task.title, 240),
      agent: boundedString(task.agent, 80),
      world: boundedString(task.world, 120),
      authority,
      owner_gate: task.owner_gate === true,
      evidence: boundedString(task.evidence, 500)
    };
  });

  return {
    summary: boundedString(parsed.summary, 1200),
    diagnosis: boundedStringArray(parsed.diagnosis),
    tasks,
    deliverables: boundedStringArray(parsed.deliverables),
    risks: boundedStringArray(parsed.risks),
    success_metrics: boundedStringArray(parsed.success_metrics)
  };
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
        contents: [{role: 'user', parts: [{text: prompt}]}],
        generationConfig: {responseMimeType: 'application/json'}
      })
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw Object.assign(new Error('GEMINI_REQUEST_FAILED'), {status: 502});
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
  if (req.method === 'OPTIONS') {
    if (!isAllowedOrigin(req)) return json(req, res, 403, {error: 'ORIGIN_NOT_ALLOWED'});
    return json(req, res, 204, {});
  }

  const url = new URL(req.url, 'http://service.local');

  if (req.method === 'GET' && url.pathname === '/healthz') {
    return json(req, res, 200, {
      ok: true,
      service: '8x8-competition-api',
      revision: SERVICE_REVISION,
      gemini_configured: Boolean(GEMINI_API_KEY),
      public_origin_configured: Boolean(PUBLIC_ORIGIN),
      deployment_truth: SERVICE_REVISION === 'local-unverified' ? 'LOCAL_OR_UNVERIFIED' : 'CLOUD_RUN_REVISION_PRESENT'
    });
  }

  if (req.method === 'GET' && url.pathname === '/api/v1/system') {
    return json(req, res, 200, {
      product: '8x8 OS Competition Edition',
      worlds: 8,
      sectors: 64,
      authority: {autonomous_ceiling: 'L3', owner_gated: 'L4', dormant_owner_only: 'L5'},
      protected_execution_enabled: false,
      templates
    });
  }

  if (req.method === 'GET' && url.pathname === '/api/v1/missions/templates') {
    return json(req, res, 200, {templates});
  }

  if (req.method === 'POST' && url.pathname === '/api/v1/missions/plan') {
    if (!isAllowedOrigin(req)) return json(req, res, 403, {error: 'ORIGIN_NOT_ALLOWED'});
    if (!consumeRateLimit(req)) return json(req, res, 429, {error: 'RATE_LIMITED'}, {'retry-after': '60'});
    if (!String(req.headers['content-type'] || '').toLowerCase().startsWith('application/json')) {
      return json(req, res, 415, {error: 'CONTENT_TYPE_REQUIRED'});
    }

    const body = await readJson(req);
    const goal = cleanText(body.goal, 3000);
    const context = cleanText(body.context, 3000);
    const template = cleanText(body.template, 80) || 'launch-business';
    if (body.consent !== true) return json(req, res, 400, {error: 'CONSENT_REQUIRED'});
    if (goal.length < 10) return json(req, res, 400, {error: 'GOAL_TOO_SHORT'});
    if (!allowedTemplates.has(template)) return json(req, res, 400, {error: 'TEMPLATE_NOT_ALLOWED'});

    const result = await callGemini({goal, template, context});
    const receipt = receiptFor({goal, template, context}, result);
    return json(req, res, 200, {result, receipt});
  }

  return json(req, res, 404, {error: 'NOT_FOUND'});
}

function publicError(error) {
  const candidate = error instanceof Error ? error.message : '';
  return publicErrors.has(candidate) ? candidate : 'INTERNAL_ERROR';
}

const server = http.createServer((req, res) => {
  const requestId = crypto.randomUUID();
  route(req, res).catch(error => {
    const rawStatus = Number(error?.status || 500);
    const status = rawStatus >= 400 && rawStatus <= 599 ? rawStatus : 500;
    const code = publicError(error);
    console.error(JSON.stringify({event: 'request_error', request_id: requestId, status, code, revision: SERVICE_REVISION}));
    json(req, res, status, {error: code, request_id: requestId});
  });
});

server.listen(PORT, HOST, () => {
  console.log(JSON.stringify({
    event: 'service_started',
    host: HOST,
    port: PORT,
    revision: SERVICE_REVISION,
    gemini_configured: Boolean(GEMINI_API_KEY),
    public_origin_configured: Boolean(PUBLIC_ORIGIN)
  }));
});
