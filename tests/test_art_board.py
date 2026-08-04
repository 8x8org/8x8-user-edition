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
        self.assertEqual(deployment["deployment_id"], "dpl_5MYCNY9eYNMauJp2c2KXcnLofD2z")
        self.assertEqual(deployment["commit"], "dba1ec6ce6ccb729e4c1d71b9d604f21aa767beb")
        self.assertEqual(deployment["ready_state"], "READY")
        self.assertTrue(deployment["url"].startswith("https://"))
        self.assertIn("github-actions:30945374071", deployment["receipt_id"])
        self.assertEqual(validation["github_actions_conclusion"], "SUCCESS")
        self.assertEqual(validation["vercel_build"], "READY")
        self.assertFalse(validation["production_alias_changed"])
        self.assertEqual(validation["direct_unauthenticated_fetch"], "BLOCKED_BY_VERCEL_PROTECTION")

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
        self.assertNotIn("email", serialized)
        self.assertNotIn("ip_address", serialized)
        self.assertNotIn("device_id", serialized)
        self.assertNotIn("precise_location", serialized)

    def test_treasury_exposes_no_addresses_balances_or_signing(self):
        treasury = self.state["treasury"]
        self.assertFalse(treasury["public_balances"])
        self.assertFalse(treasury["wallet_addresses"])
        self.assertFalse(treasury["signing_authority"])
        serialized = json.dumps(treasury).lower()
        self.assertNotRegex(serialized, r"\b(0x[a-f0-9]{40}|bc1[a-z0-9]{20,}|4[0-9ab][1-9a-hj-np-z]{90,})\b")

    def test_html_has_strict_local_security_policy(self):
        self.assertIn("default-src 'self'", self.html)
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

    def test_javascript_is_local_read_only(self):
        forbidden = (
            "localStorage.setItem",
            "sessionStorage.setItem",
            "navigator.geolocation",
            "WebSocket(",
            "EventSource(",
            "XMLHttpRequest",
            "eval(",
            "new Function",
            "document.cookie",
        )
        for token in forbidden:
            self.assertNotIn(token, self.js)
        self.assertIn("PUBLIC_SAFE_FIXTURE", self.js)
        self.assertIn("whole_system_score", json.dumps(self.state))


if __name__ == "__main__":
    unittest.main()
