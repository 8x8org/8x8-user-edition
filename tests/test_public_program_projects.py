import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PublicProgramProjectsContract(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / "public/projects/races.json").read_text(encoding="utf-8"))
        self.projects_html = (ROOT / "projects/index.html").read_text(encoding="utf-8")
        self.vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))

    def test_one_fabric_and_public_program_identity(self):
        self.assertEqual(self.registry["root"], "fabric://8x8/core")
        self.assertEqual(self.registry["program"], "8x8 OS Public Program")
        self.assertEqual(self.registry["policy"]["architecture_priority"], "ONE_FABRIC_FIRST")
        self.assertEqual(self.registry["policy"]["deadline_priority"], "INFORMATIONAL_NOT_GOVERNING")

    def test_exactly_eight_fair_race_rules(self):
        rules = self.registry["policy"]["fair_race_rules"]
        self.assertEqual(len(rules), 8)
        self.assertEqual(len(set(rules)), 8)

    def test_build_week_is_submitted_but_unranked(self):
        race = next(item for item in self.registry["races"] if item["id"] == "openai-build-week-2026")
        self.assertEqual(race["participation"], "SUBMITTED")
        self.assertEqual(race["status"], "SUBMITTED_OUTCOME_PENDING")
        self.assertEqual(race["result_receipt"], "NOT_AVAILABLE")
        self.assertEqual(race["official_timeline"]["conflict_state"], "AUTHORITATIVE_PUBLIC_SOURCES_CURRENTLY_DIFFER")

    def test_xprize_is_not_claimed_submitted(self):
        race = next(item for item in self.registry["races"] if item["id"] == "build-with-gemini-xprize-2026")
        self.assertEqual(race["participation"], "BUILDING_NOT_SUBMITTED")
        self.assertEqual(race["status"], "ACTIVE_BUILD_FUTURE_GATED_SUBMISSION")
        self.assertEqual(len(race["pending"]), 8)

    def test_watchlist_does_not_claim_entry(self):
        watch = [item for item in self.registry["races"] if item["lane"] == "WATCHLIST"]
        self.assertGreaterEqual(len(watch), 1)
        for race in watch:
            self.assertEqual(race["participation"], "NOT_ENTERED")
            self.assertEqual(race["truth_class"], "FUTURE_GATED")

    def test_projects_route_precedes_generic_fallback(self):
        rewrites = self.vercel["rewrites"]
        projects_index = next(i for i, item in enumerate(rewrites) if item["source"] == "/projects")
        fallback_index = next(i for i, item in enumerate(rewrites) if item["source"] == "/((?!.*\\.).*)")
        self.assertLess(projects_index, fallback_index)
        self.assertEqual(rewrites[projects_index]["destination"], "/projects/index.html")

    def test_ui_reads_machine_registry_and_fails_closed(self):
        self.assertIn("/public/projects/races.json", self.projects_html)
        self.assertIn("No fallback status is invented", self.projects_html)
        self.assertIn("Eight fair-race rules", self.projects_html)
        self.assertIn("8x8 OS PUBLIC PROGRAM", self.projects_html)


if __name__ == "__main__":
    unittest.main()
