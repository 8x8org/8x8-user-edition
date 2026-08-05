import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "capabilities"
LEDGER_PATH = ROOT / "research" / "external-capabilities" / "CANDIDATE_STATUS_LEDGER_V3.json"


class CapabilitiesObservatoryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (CAP / "index.html").read_text(encoding="utf-8")
        cls.css = (CAP / "styles.css").read_text(encoding="utf-8")
        cls.js = (CAP / "app.js").read_text(encoding="utf-8")
        cls.release = json.loads((CAP / "release-unit.json").read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))

    def test_required_files_exist(self):
        required = [CAP / name for name in ["index.html", "styles.css", "app.js", "release-unit.json", "README.md"]] + [LEDGER_PATH]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])

    def test_canonical_ledger_truth(self):
        self.assertEqual("3.0.0", self.ledger["schema_version"])
        self.assertEqual(13, len(self.ledger["candidates"]))
        self.assertEqual(13, self.ledger["summary"]["candidate_packets_merged"])
        self.assertEqual(0, self.ledger["summary"]["third_party_candidates_installed_into_8x8"])
        self.assertEqual(1, self.ledger["summary"]["external_measured_benchmarks_complete"])
        self.assertEqual(2, self.ledger["summary"]["external_measured_benchmarks_required"])
        self.assertEqual(0, self.ledger["council"]["valid_votes"])
        self.assertEqual(4, self.ledger["council"]["quorum_required"])
        self.assertFalse(self.ledger["council"]["quorum_reached"])

    def test_candidate_identities_and_pins_are_unique(self):
        ids = [item["id"] for item in self.ledger["candidates"]]
        repos = [item["repository"] for item in self.ledger["candidates"]]
        pins = [item["pin"] for item in self.ledger["candidates"]]
        self.assertEqual(13, len(set(ids)))
        self.assertEqual(13, len(set(repos)))
        self.assertEqual(13, len(set(pins)))
        for pin in pins:
            self.assertRegex(pin, r"^[0-9a-f]{40}$")

    def test_verified_projection_receipt(self):
        score = self.release["scope_score"]
        projection = self.release["protected_projection"]
        self.assertEqual(100, score["earned"])
        self.assertEqual(100, score["possible"])
        self.assertEqual("NOT_INFERRED", score["whole_system_score"])
        self.assertEqual("6b7e5bf8fb13587a2e26f4949ae774a41571cc5f", projection["integration_commit"])
        self.assertEqual("dpl_6k8vV7jYRENNMepCBJMTGuYJEPHB", projection["deployment_id"])
        self.assertEqual("READY", projection["state"])
        self.assertEqual(200, projection["route_http_status"])
        self.assertTrue(projection["truth_markers_verified"])
        self.assertFalse(projection["production_alias_changed"])

    def test_source_branch_is_honestly_pending(self):
        gates = self.release["source_branch_gates"]
        self.assertTrue(gates["current_main_base"])
        self.assertFalse(gates["exact_head_ci"])
        self.assertFalse(gates["codeql"])
        self.assertEqual("PUBLIC_PROJECTION_VERIFIED_SOURCE_BRANCH_AWAITING_EXACT_HEAD_CI", self.release["truth_state"])

    def test_authority_boundary(self):
        authority = self.release["authority"]
        self.assertTrue(authority["read_only"])
        for key, value in authority.items():
            if key != "read_only":
                self.assertFalse(value, key)

    def test_strict_local_resources_and_dom_safety(self):
        self.assertIn("default-src 'self'", self.html)
        self.assertIn("script-src 'self'", self.html)
        self.assertIn("object-src 'none'", self.html)
        self.assertIn('src="./app.js"', self.html)
        self.assertIn('href="./styles.css"', self.html)
        self.assertNotRegex(self.html, r"https?://")
        self.assertNotIn("<script>", self.html.lower())
        for token in ["innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"]:
            self.assertNotIn(token, self.js)
        self.assertIn("textContent", self.js)
        self.assertIn("credentials: 'same-origin'", self.js)
        self.assertIn("FAIL_CLOSED_LEDGER_UNAVAILABLE", self.js)

    def test_no_secret_or_private_material(self):
        corpus = "\n".join([self.html, self.css, self.js, json.dumps(self.release)])
        for pattern in [
            r"/root/", r"/data/data/com\.termux", r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY",
            r"\bgh[opsu]_[A-Za-z0-9]{20,}\b", r"\bsk-[A-Za-z0-9]{20,}\b",
            r"Authorization:\s*Bearer", r"seed phrase", r"wallet address", r"127\.0\.0\.1", r"localhost:\d+",
        ]:
            self.assertIsNone(re.search(pattern, corpus, flags=re.IGNORECASE), pattern)

    def test_accessibility_contract(self):
        self.assertIn("skip-link", self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('for="filter"', self.html)
        self.assertIn('id="main"', self.html)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("forced-colors", self.css)


if __name__ == "__main__":
    unittest.main()
