from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "adapters" / "supervision"


def load(name: str) -> dict:
    return json.loads((ADAPTER / name).read_text(encoding="utf-8"))


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class SupervisionAdapterContractTests(unittest.TestCase):
    def test_manifest_fails_closed(self) -> None:
        manifest = load("manifest.json")
        self.assertEqual(manifest["adapter_id"], "8x8.supervision.adapter.v1")
        self.assertEqual(manifest["upstream"]["commit"], "bc20dd19fbc7b6cceaec447f1182346ca9158523")
        self.assertFalse(manifest["enabled"])
        self.assertEqual(manifest["install_state"], "NOT_INSTALLED")
        self.assertEqual(manifest["runtime_authority"], "NONE")
        self.assertFalse(manifest["production_ready"])
        denied = set(manifest["authority_denies"])
        required_denies = {
            "NETWORK", "MODEL_DOWNLOAD", "CAMERA", "MICROPHONE",
            "PRIVATE_FILESYSTEM", "DATABASE_WRITE", "SERVICE_CONTROL",
            "SCHEDULER_CONTROL", "PUBLIC_DEPLOYMENT", "WALLET", "FINANCIAL_ACTION",
        }
        self.assertTrue(required_denies.issubset(denied))
        self.assertLessEqual(manifest["resource_limits"]["cpu_cores"], 1)
        self.assertLessEqual(manifest["resource_limits"]["memory_mib"], 768)
        self.assertLessEqual(manifest["resource_limits"]["wall_time_seconds"], 30)

    def test_schemas_are_closed_and_bounded(self) -> None:
        request = load("request.schema.json")
        response = load("response.schema.json")
        self.assertFalse(request["additionalProperties"])
        self.assertFalse(response["additionalProperties"])
        self.assertEqual(request["properties"]["detections"]["maxItems"], 1000)
        self.assertEqual(response["properties"]["evidence"]["properties"]["network_used"]["const"], False)
        self.assertEqual(response["properties"]["evidence"]["properties"]["private_data_used"]["const"], False)
        self.assertEqual(response["properties"]["evidence"]["properties"]["model_used"]["const"], False)

    def test_synthetic_fixture_hashes_are_deterministic(self) -> None:
        fixture = load("synthetic-fixture.json")
        request = fixture["request"]
        response = fixture["response"]
        self.assertEqual(response["evidence"]["input_sha256"], canonical_sha256(request))
        self.assertEqual(response["evidence"]["output_sha256"], canonical_sha256(response["result"]))
        threshold = request["parameters"]["confidence_threshold"]
        selected = [index for index, item in enumerate(request["detections"]) if item["confidence"] >= threshold]
        self.assertEqual(selected, response["result"]["selected_indices"])
        self.assertEqual(len(request["detections"]), response["result"]["input_count"])
        self.assertEqual(len(selected), response["result"]["output_count"])
        self.assertFalse(response["evidence"]["network_used"])
        self.assertFalse(response["evidence"]["private_data_used"])
        self.assertFalse(response["evidence"]["model_used"])
        self.assertTrue(response["evidence"]["cleanup_complete"])

    def test_no_runtime_or_install_commands_in_adapter(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in ADAPTER.rglob("*") if path.is_file())
        forbidden = [
            "pip install", "npm install", "docker run", "systemctl", "sv restart",
            "vercel deploy", "gh pr merge", "camera.open", "wallet.connect",
        ]
        for token in forbidden:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
