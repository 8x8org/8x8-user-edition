from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.validate_public_information_boundary import PATTERNS

ROOT = Path(__file__).resolve().parents[1]


class PublicInformationBoundaryTests(unittest.TestCase):
    def test_validator_passes_current_public_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/validate_public_information_boundary.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PUBLIC_INFORMATION_BOUNDARY=PASS", result.stdout)

    def test_private_research_projection_is_absent(self) -> None:
        self.assertFalse((ROOT / "research" / "external-capabilities").exists())
        self.assertFalse((ROOT / "adapters" / "supervision").exists())
        self.assertFalse((ROOT / "capabilities").exists())

    def test_boundary_document_exists(self) -> None:
        text = (ROOT / "PUBLIC_INFORMATION_BOUNDARY.md").read_text(encoding="utf-8")
        self.assertIn("Private Past", text)
        self.assertIn("Future Lab", text)
        self.assertIn("Public Present", text)

    def test_external_research_tracker_policy_is_documented(self) -> None:
        text = (ROOT / "PUBLIC_INFORMATION_BOUNDARY.md").read_text(encoding="utf-8")
        self.assertIn("Public tracker rule for external capability research", text)
        self.assertIn("private branch names", text)

    def test_validator_blocks_msg197_program_markers(self) -> None:
        program_marker = "".join(("MSG", "197"))
        stale_branch = "".join(
            ("feature/", "msg", "197", "-external-capability-intake-v1")
        )
        self.assertIsNotNone(
            PATTERNS["private_research_program_identifier"].search(program_marker)
        )
        self.assertIsNotNone(
            PATTERNS["stale_private_research_branch"].search(stale_branch)
        )


if __name__ == "__main__":
    unittest.main()
