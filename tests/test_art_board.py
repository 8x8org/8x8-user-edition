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
        cls.positions = (ART / "positions.css").read_text(encoding="utf-8")

    def test_required_files_exist(self):
        for path in ("index.html", "styles.css", "positions.css", "app.js", "state.json", "release-unit.json", "README.md"):
            self.assertTrue((ART / path).is_file(), path)

    def test_bounded_slice_truth(self):
        self.assertEqual(self.state["score"]["earned"], 100)
        self.assertEqual(self.state["score"]["possible"], 100)
        self.assertEqual(self.state["score"]["whole_system_score"], "NOT_INFERRED")
        self.assertEqual(sum(self.release["score"]["categories"].values()), 100)
        self.assertFalse(self.release["whole_system_completion_inferred"])
        self.assertEqual(self.release["truth_state"], "PROTECTED_PREVIEW_DEPLOYED")
        self.assertFalse(self.release["gates"]["public_production_release"])

    def test_preview_remains_nonproduction(self):
        deployment = self.release["deployment"]
        validation = self.release["validation"]
        self.assertEqual(deployment["authorized_class"], "AUTHENTICATED_PREVIEW")
        self.assertEqual(deployment["visibility"], "VERCEL_PROTECTED")
        self.assertEqual(deployment["ready_state"], "READY")
        self.assertFalse(validation["production_alias_changed"])

    def test_worlds_presence_and_treasury_are_public_safe(self):
        self.assertEqual(len(self.state["worlds"]), 8)
        self.assertTrue(all(cluster["count"] == 0 for cluster in self.state["presence_clusters"]))
        treasury = self.state["treasury"]
        self.assertFalse(treasury["public_balances"])
        self.assertFalse(treasury["wallet_addresses"])
        self.assertFalse(treasury["signing_authority"])
        serialized = json.dumps(self.state).lower()
        for field in ("email", "ip_address", "device_id", "precise_location"):
            self.assertNotIn(field, serialized)

    def test_csp_has_no_unsafe_inline_exception(self):
        self.assertIn("default-src 'self'", self.html)
        self.assertIn("script-src 'self'", self.html)
        self.assertIn("style-src 'self'", self.html)
        self.assertNotIn("unsafe-inline", self.html)
        self.assertIn('href="./positions.css"', self.html)
        self.assertNotIn("<iframe", self.html.lower())
        self.assertNotIn("http://", self.html.lower())

    def test_renderer_uses_dom_and_attribute_classes_only(self):
        self.assertNotIn(".innerHTML", self.js)
        self.assertNotIn(".style", self.js)
        self.assertNotIn("Math.random", self.js)
        for token in ("document.createElement", "document.createTextNode", "replaceChildren", "textContent", "boundedPercent", "data-position", "dataset.zoom"):
            self.assertIn(token, self.js)
        for token in ('data-zoom="100"', '.world[data-position="0"]', '.node[data-position="0"]', '.presence[data-position="0"]'):
            self.assertIn(token, self.positions)

    def test_pointer_interruptions_and_accessibility(self):
        for token in ("pointercancel", "lostpointercapture", "stopDragging"):
            self.assertIn(token, self.js)
        self.assertIn("aria-live", self.html)
        self.assertIn("aria-pressed", self.html)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn("forced-colors", self.css)

    def test_javascript_has_no_privileged_browser_paths(self):
        for token in (
            "localStorage.setItem",
            "sessionStorage.setItem",
            "navigator.geolocation",
            "WebSocket(",
            "EventSource(",
            "XMLHttpRequest",
            "eval(",
            "new Function",
            "document.cookie",
        ):
            self.assertNotIn(token, self.js)
        self.assertIn("PUBLIC_SAFE_FIXTURE", self.js)


if __name__ == "__main__":
    unittest.main()
