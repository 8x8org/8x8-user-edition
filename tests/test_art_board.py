from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "art-board"


class ArtBoardReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = json.loads((ART / "state.json").read_text(encoding="utf-8"))
        cls.release = json.loads((ART / "release-unit.json").read_text(encoding="utf-8"))
        cls.html = (ART / "index.html").read_text(encoding="utf-8")
        cls.js = (ART / "app.js").read_text(encoding="utf-8")
        cls.css = (ART / "styles.css").read_text(encoding="utf-8")

    def test_required_art_board_files_exist(self):
        for path in ("index.html", "styles.css", "app.js", "state.json", "release-unit.json", "README.md"):
            self.assertTrue((ART / path).is_file(), path)

    def test_slice_score_is_exact_and_does_not_claim_whole_system(self):
        self.assertEqual(self.state["score"]["earned"], 100)
        self.assertEqual(self.state["score"]["possible"], 100)
        self.assertEqual(self.state["score"]["whole_system_score"], "NOT_INFERRED")
        self.assertEqual(sum(self.release["score"]["categories"].values()), 100)
        self.assertFalse(self.release["whole_system_completion_inferred"])
        self.assertEqual(self.release["truth_state"], "PROTECTED_PREVIEW_DEPLOYED")
        self.assertTrue(self.release["gates"]["exact_deployment_target"])
        self.assertTrue(self.release["gates"]["deployment_receipt"])
        self.assertFalse(self.release["gates"]["public_production_release"])

    def test_preview_deployment_is_exact_and_nonproduction(self):
        deployment = self.release["deployment"]
        validation = self.release["validation"]
        self.assertEqual(deployment["authorized_class"], "AUTHENTICATED_PREVIEW")
        self.assertEqual(deployment["visibility"], "VERCEL_PROTECTED")
        self.assertEqual(deployment["ready_state"], "READY")
        self.assertTrue(deployment["url"].startswith("https://"))
        self.assertEqual(validation["github_actions_conclusion"], "SUCCESS")
        self.assertEqual(validation["vercel_build"], "READY")
        self.assertFalse(validation["production_alias_changed"])

    def test_eight_worlds_and_status_palette(self):
        self.assertEqual(len(self.state["worlds"]), 8)
        required = {"GREEN", "CYAN", "YELLOW", "ORANGE", "RED", "BLACK", "PURPLE", "GRAY"}
        self.assertEqual(set(self.state["palette"]), required)
        for world in self.state["worlds"]:
            self.assertIn(world["status"], required)
            self.assertGreaterEqual(world["score"], 0)
            self.assertLessEqual(world["score"], 100)

    def test_presence_is_simulated_and_contains_no_people(self):
        for cluster in self.state["presence_clusters"]:
            self.assertEqual(cluster["count"], 0)
            self.assertTrue(cluster["mode"].startswith("SIMULATED_"))
        serialized = json.dumps(self.state).lower()
        for field in ("email", "ip_address", "device_id", "precise_location"):
            self.assertNotIn(field, serialized)

    def test_treasury_exposes_no_active_values(self):
        treasury = self.state["treasury"]
        self.assertFalse(treasury["public_balances"])
        self.assertFalse(treasury["wallet_addresses"])
        self.assertFalse(treasury["signing_authority"])

    def test_html_has_strict_but_functional_security_policy(self):
        self.assertIn("default-src 'self'", self.html)
        self.assertIn("script-src 'self'", self.html)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", self.html)
        self.assertIn("style-src-elem 'self'", self.html)
        self.assertIn("style-src-attr 'unsafe-inline'", self.html)
        self.assertIn("connect-src 'self'", self.html)
        self.assertIn("object-src 'none'", self.html)
        self.assertIn("form-action 'none'", self.html)
        self.assertIn("frame-ancestors 'none'", self.html)
        self.assertNotIn("<iframe", self.html.lower())
        self.assertNotIn("http://", self.html.lower())

    def test_interface_has_zoom_map_help_and_accessibility(self):
        for identifier in ("zoomOut", "zoomReset", "zoomIn", "toggleMap", "togglePanels", "openHelp"):
            self.assertIn(f'id="{identifier}"', self.html)
        self.assertIn("aria-live", self.html)
        self.assertIn("aria-pressed", self.html)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("forced-colors", self.css)

    def test_dynamic_content_uses_dom_apis_not_html_sinks(self):
        self.assertNotIn(".innerHTML", self.js)
        self.assertIn("document.createElement", self.js)
        self.assertIn("document.createTextNode", self.js)
        self.assertIn("replaceChildren", self.js)
        self.assertIn("textContent", self.js)
        self.assertIn("function boundedPercent", self.js)
        self.assertIn("Number.isFinite", self.js)
        self.assertIn("record ?? {}", self.js)

    def test_pointer_interruptions_end_dragging(self):
        self.assertIn("pointercancel", self.js)
        self.assertIn("lostpointercapture", self.js)
        self.assertIn("stopDragging", self.js)

    def test_javascript_is_local_fixture_only(self):
        self.assertIn("PUBLIC_SAFE_FIXTURE", self.js)
        self.assertIn("whole_system_score", json.dumps(self.state))
        self.assertNotIn("localStorage.setItem", self.js)
        self.assertNotIn("sessionStorage.setItem", self.js)
        self.assertNotIn("navigator.geolocation", self.js)


if __name__ == "__main__":
    unittest.main()
