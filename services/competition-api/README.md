# 8x8 Competition API

Dependency-free Node.js service for the 8x8 OS Competition Edition. It exposes public system metadata, mission templates and a Gemini-backed planning endpoint.

## Truth boundary

The service creates plans and receipts. It does not execute plans or grant owner authority. Source presence is not proof of deployment, Gemini configuration, production traffic or competition eligibility.

## Endpoints

- `GET /healthz`
- `GET /api/v1/system`
- `GET /api/v1/missions/templates`
- `POST /api/v1/missions/plan`

Mission planning requires `consent: true`, a goal of at least ten characters and a configured Gemini secret.

## Local validation

```bash
npm test
PORT=8080 node server.mjs
curl -fsS http://127.0.0.1:8080/healthz
```

Without `GEMINI_API_KEY`, health remains available while mission planning fails closed with `GEMINI_NOT_CONFIGURED`.

## Required configuration

- `GEMINI_API_KEY`: supplied from a secret store, never committed.
- `GEMINI_MODEL`: defaults to `gemini-2.5-flash`.
- `PUBLIC_ORIGIN`: exact public cockpit origin for CORS.
- `REQUEST_TIMEOUT_MS`: defaults to 30000.
- `PORT`: injected by Cloud Run.

## Owner-gated Cloud Run deployment template

Do not run this until the owner explicitly approves the named project, region, public access and revision.

```bash
PROJECT_ID="REPLACE_WITH_APPROVED_PROJECT"
REGION="us-east1"
SERVICE="eightx8-competition-api"
PUBLIC_ORIGIN="https://REPLACE_WITH_APPROVED_PUBLIC_ORIGIN"

gcloud config set project "$PROJECT_ID"

gcloud run deploy "$SERVICE" \
  --source services/competition-api \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "PUBLIC_ORIGIN=$PUBLIC_ORIGIN,GEMINI_MODEL=gemini-2.5-flash" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
```

The secret must already exist in Google Secret Manager and the Cloud Run service identity must have only the required secret-access permission.

## Required deployment receipt

Record without exposing secrets:

- repository and exact commit SHA;
- Google Cloud project identifier;
- Cloud Run service, region and revision;
- deployment timestamp;
- image digest;
- configured model name;
- health response;
- one consented Gemini mission response;
- receipt digest;
- public origin;
- rollback revision;
- error and latency sample;
- confirmation that no secret value appears in logs or source.

## Cockpit connection

The static cockpit accepts a deployment-specific API base through the `api` query parameter and stores it locally in the browser:

```text
/competition/?api=https://APPROVED_CLOUD_RUN_URL
```

A production release should inject the approved API base during deployment rather than relying on a user-edited query parameter.
