#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "competition" / "system-registry.v1.json"
STATE = ROOT / "competition" / "competition-state.v1.json"
INDEX = ROOT / "competition" / "index.html"
APP = ROOT / "competition" / "app.js"
API = ROOT / "services" / "competition-api" / "server.mjs"
DOCKERFILE = ROOT / "services" / "competition-api" / "Dockerfile"

errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

for path in (REGISTRY, STATE, INDEX, APP, API, DOCKERFILE):
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")

if not errors:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8"))
    html = INDEX.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    api = API.read_text(encoding="utf-8")
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")

    worlds = registry.get("worlds", [])
    sectors = [sector for world in worlds for sector in world.get("sectors", [])]
    require(registry.get("world_count") == 8, "world_count must equal 8")
    require(registry.get("sector_count") == 64, "sector_count must equal 64")
    require(len(worlds) == 8, "registry must contain exactly 8 worlds")
    require(len(sectors) == 64, "registry must contain exactly 64 sectors")
    require(all(len(world.get("sectors", [])) == 8 for world in worlds), "each world must contain exactly 8 sectors")
    require(len(set(sectors)) == 64, "sector names must be unique")
    require(state.get("ready_100") is False, "ready_100 must remain false without production evidence")
    require(state.get("public_deployment_authorized") is False, "source branch must not authorize public deployment")
    require(state.get("submission_authorized") is False, "source branch must not authorize final submission")
    require(state.get("openai_build_week_assets_frozen") is True, "OpenAI Build Week assets must remain frozen")
    require("GEMINI_API_KEY" in api, "API must read Gemini configuration from the environment")
    require("process.env.PORT" in api and "0.0.0.0" in api, "API must satisfy the Cloud Run port contract")
    require("PLANNED_NOT_EXECUTED" in api, "mission receipts must distinguish planning from execution")
    require("responseMimeType: 'application/json'" in api, "Gemini request must ask for structured JSON")
    require("USER node" in dockerfile, "container must run as the non-root node user")
    require("8x8 OS Competition Edition" in html, "competition identity missing from cockpit")
    require("64 sectors" in html, "64-sector representation missing from cockpit")
    require("API NOT CONFIGURED" in app, "UI must fail closed when the production API is absent")
    require("innerHTML = payload" not in app, "untrusted payload must not be assigned directly to innerHTML")

    forbidden_live_claims = [
        r"guaranteed first place",
        r"fully deployed",
        r"100/100 complete",
        r"all agents live 24/7"
    ]
    combined = "\n".join([html, app, STATE.read_text(encoding="utf-8")]).lower()
    for pattern in forbidden_live_claims:
        require(re.search(pattern, combined) is None, f"unsupported live claim found: {pattern}")

if errors:
    print("COMPETITION_EDITION_VALIDATION=FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("COMPETITION_EDITION_VALIDATION=PASS")
print("WORLD_COUNT=8")
print("SECTOR_COUNT=64")
print("READY_100=false")
print("PUBLIC_DEPLOYMENT_AUTHORIZED=false")
