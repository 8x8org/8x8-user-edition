#!/usr/bin/env python3
"""Generate a CycloneDX 1.5 SBOM for the public 8x8 User Edition release."""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_VERSION = "0.0.1"
RELEASE = "0.0.1-beta"
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


def sha256_hex(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    missing = [asset for asset in STATIC_ASSETS if not (root / asset).is_file()]
    if missing:
        print(f"ERROR: missing release assets: {missing}", file=sys.stderr)
        raise SystemExit(1)

    components = []
    for asset in STATIC_ASSETS:
        path = root / asset
        components.append(
            {
                "type": "file",
                "name": asset,
                "version": PRODUCT_VERSION,
                "hashes": [{"alg": "SHA-256", "content": sha256_hex(path)}],
                "properties": [
                    {"name": "8x8:reality", "value": "PUBLIC_PRESENT"},
                    {"name": "8x8:release", "value": RELEASE},
                ],
            }
        )

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": [{"vendor": "8x8org", "name": "generate-sbom.py", "version": PRODUCT_VERSION}],
            "component": {
                "type": "application",
                "name": "8x8-user-edition",
                "version": PRODUCT_VERSION,
                "description": "8x8 OS 0.0.1 Beta public-safe Omniversal Command Atlas",
                "licenses": [{"license": {"id": "Apache-2.0"}}],
                "properties": [
                    {"name": "8x8:truth_class", "value": "PUBLIC_PRESENT"},
                    {"name": "8x8:promotion_state", "value": "PROTECTED_BETA"},
                ],
            },
        },
        "components": components,
    }

    output = root / "sbom.cdx.json"
    output.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(f"SBOM_GENERATED=PASS path={output} components={len(components)}")


if __name__ == "__main__":
    main()
