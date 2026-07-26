#!/usr/bin/env python3
"""Generate a CycloneDX 1.5 SBOM for the 8x8-user-edition static assets.

Run from the repository root or from the scripts/ sub-directory:

    python3 scripts/generate-sbom.py

Output: sbom.cdx.json in the repository root.
"""

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Canonical list of public static assets included in each release.
STATIC_ASSETS = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.webmanifest",
    "icon.svg",
    "sw.js",
    "state/public-state.json",
    "vercel.json",
]

COMPONENT_VERSION = "0.1.0-beta"


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    # Support running from either the repo root or the scripts/ directory.
    here = Path(__file__).resolve().parent
    root = here.parent if here.name == "scripts" else here

    components = []
    missing = []
    for asset in STATIC_ASSETS:
        p = root / asset
        if not p.is_file():
            missing.append(asset)
            continue
        digest = sha256_hex(p)
        components.append(
            {
                "type": "file",
                "name": asset,
                "version": COMPONENT_VERSION,
                "hashes": [{"alg": "SHA-256", "content": digest}],
            }
        )

    if missing:
        print(f"ERROR: missing static assets: {missing}", file=sys.stderr)
        sys.exit(1)

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": [
                {
                    "vendor": "8x8org",
                    "name": "generate-sbom.py",
                    "version": "1.0",
                }
            ],
            "component": {
                "type": "application",
                "name": "8x8-user-edition",
                "version": COMPONENT_VERSION,
                "description": "8x8 User Edition public beta static cockpit",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
            },
        },
        "components": components,
    }

    out = root / "sbom.cdx.json"
    out.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(f"SBOM_GENERATED=PASS  path={out}  components={len(components)}")


if __name__ == "__main__":
    main()
