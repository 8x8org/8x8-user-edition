import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DELTA = ROOT / "donor_delta_2026-08-11.json"
ALLOWED_PRIMARY_DOMAINS = {
    "google.github.io",
    "a2a-protocol.org",
    "docs.letta.com",
    "mastra.ai",
    "ai.pydantic.dev",
}


class ExternalDonorDeltaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DELTA.read_text(encoding="utf-8"))

    def test_schema_and_closed_score_boundary(self):
        self.assertEqual(self.data["schema"], "8x8.one-fabric.external-donor-delta.v1")
        self.assertEqual(self.data["base_score"], 75)
        self.assertEqual(self.data["uncertainty_points"], 3)
        self.assertFalse(self.data["score_changed"])
        self.assertFalse(self.data["global_100_claim_allowed"])
        self.assertIn("No benchmark point moves", self.data["reason_no_score_change"])

    def test_five_unique_donors_and_capability_families(self):
        donors = self.data["donors"]
        self.assertEqual(len(donors), 5)
        ids = [d["id"] for d in donors]
        self.assertEqual(len(ids), len(set(ids)))
        families = [d["capability_family"] for d in donors]
        self.assertEqual(len(families), len(set(families)))

    def test_every_donor_has_primary_sources_and_one_parity_gate(self):
        for donor in self.data["donors"]:
            self.assertTrue(donor["project"].strip())
            self.assertTrue(donor["evidence_summary"].strip())
            self.assertTrue(donor["single_extra_feature"].strip())
            self.assertTrue(donor["8x8_parity_gate"].strip())
            self.assertGreaterEqual(len(donor["primary_sources"]), 1)
            for source in donor["primary_sources"]:
                parsed = urlparse(source)
                self.assertEqual(parsed.scheme, "https")
                self.assertIn(parsed.netloc, ALLOWED_PRIMARY_DOMAINS)

    def test_no_donor_is_treated_as_implemented_8x8_capability(self):
        forbidden = {"PASS", "VERIFIED", "IMPLEMENTED", "SUPERIOR"}
        for donor in self.data["donors"]:
            gate_tokens = set(re.findall(r"\b[A-Z]+\b", donor["8x8_parity_gate"].upper()))
            self.assertFalse(
                forbidden & gate_tokens,
                f"parity gate for {donor['id']} contains forbidden implementation claim(s): {sorted(forbidden & gate_tokens)}",
            )

    def test_forbidden_claim_guard_handles_punctuation(self):
        sample = "This would be IMPLEMENTED, VERIFIED. and SUPERIOR! only after evidence PASS."
        tokens = set(re.findall(r"\b[A-Z]+\b", sample.upper()))
        self.assertTrue({"IMPLEMENTED", "VERIFIED", "SUPERIOR", "PASS"}.issubset(tokens))


if __name__ == "__main__":
    unittest.main()
