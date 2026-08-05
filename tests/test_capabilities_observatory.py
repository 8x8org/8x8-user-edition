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
        required = [
            CAP / "index.html",
            CAP / "styles.css",
            CAP / "app.js",
            CAP / "release-unit.json",
            CAP / "README.md",
            LEDGER_PATH,
        ]
        self.assertEqual([], [str(path) for path in required if not path.is_file()])

    def test_ledger_is_canonical_v3_with_thirteen_candidates(self):
        self.assertEqual("3.0.0", self.ledger["schema_version"])
        self.assertEqual(13, len(self.ledger["candidates"]))
        self.assertEqual(13, self.ledger["summary"]["candidate_packets_merged"])
        self.assertEqual(0, self.ledger["summary"]["third_party_candidates_installed_into_8x8"])
        self.assertEqual(1, self.ledger["summary"]["external_measured_benchmarks_complete"])
        self.assertEqual(2, self.ledger["summary"]["external_measured_benchmarks_required"])
        self.assertEqual(0, self.ledger["council"]["valid_votes"])
        self.assertEqual(4, self.ledger["council"]["quorum_required"])
        self.assertFalse(self.ledger["council"]["quorum_reached"])

    def test_release_is_read_only_and_not_deployed(self):
        authority = self.release["authority"]
        self.assertTrue(authority["read_only"])
        for key, value in authority.items():
            if key != "read_only":
                self.assertFalse(value, key)
        self.assertEqual("NOT_DEPLOYED", self.release["visibility"])
        self.assertEqual("NOT_INFERRED", self.release["score"]["whole_system_score"])
        self.assertEqual(0, self.release["score"]["earned"])

    def test_html_has_strict_local_resource_policy(self):
        self.assertIn("default-src 'self'", self.html)
        self.assertIn("script-src 'self'", self.html)
        self.assertIn("object-src 'none'", self.html)
        self.assertIn("frame-ancestors 'none'", self.html)
        self.assertIn('src="./app.js"', self.html)
        self.assertIn('href="./styles.css"', self.html)
        self.assertNotRegex(self.html, r"https?://")
        self.assertNotIn("<script>", self.html.lower())

    def test_dom_rendering_is_text_only(self):
        forbidden = ["innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"]
        for token in forbidden:
            self.assertNotIn(token, self.js)
        self.assertIn("textContent", self.js)
        self.assertIn("createElement", self.js)
        self.assertIn("credentials: 'same-origin'", self.js)

    def test_ledger_validation_fails_closed(self):
        self.assertIn("FAIL_CLOSED_LEDGER_UNAVAILABLE", self.js)
        self.assertIn("Expected exactly thirteen candidates", self.js)
        self.assertIn("refuses a ledger claiming runtime installation", self.js)

    def test_no_private_or_secret_shaped_material(self):
        corpus = "\n".join([self.html, self.css, self.js, json.dumps(self.release)])
        forbidden_patterns = [
            r"/root/",
            r"/data/data/com\.termux",
            r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY",
            r"\bgh[opsu]_[A-Za-z0-9]{20,}\b",
            r"\bsk-[A-Za-z0-9]{20,}\b",
            r"Authorization:\s*Bearer",
            r"seed phrase",
            r"private key",
            r"wallet address",
            r"127\.0\.0\.1",
            r"localhost:\d+",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(re.search(pattern, corpus, flags=re.IGNORECASE), pattern)

    def test_candidate_ids_and_pins_are_unique(self):
        ids = [candidate["id"] for candidate in self.ledger["candidates"]]
        pins = [candidate["pin"] for candidate in self.ledger["candidates"]]
        repos = [candidate["repository"] for candidate in self.ledger["candidates"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(pins), len(set(pins)))
        self.assertEqual(len(repos), len(set(repos)))
        for pin in pins:
            self.assertRegex(pin, r"^[0-9a-f]{40}$")

    def test_accessibility_contract(self):
        self.assertIn("skip-link", self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('for="filter"', self.html)
        self.assertIn('id="main"', self.html)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("forced-colors", self.css)


if __name__ == "__main__":
    unittest.main()
