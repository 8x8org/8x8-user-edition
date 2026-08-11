from __future__ import annotations

import subprocess
import sys
import unittest

from scripts.validate_public_information_boundary import FORBIDDEN_PATH_PATTERNS, ROOT


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

    def test_public_state_contains_no_operational_run_receipt(self) -> None:
        forbidden: list[str] = []
        for path in sorted((ROOT / "state").rglob("*.json")):
            rel = path.relative_to(ROOT).as_posix()
            if any(pattern.fullmatch(rel) for pattern in FORBIDDEN_PATH_PATTERNS):
                forbidden.append(rel)
            text = path.read_text(encoding="utf-8").lower()
            if '"vnext_drive_id"' in text or '"rights_matrix_drive_id"' in text:
                forbidden.append(rel)
        self.assertEqual(
            forbidden,
            [],
            f"public state contains operational/private artifact receipt data: {forbidden}",
        )

    def test_boundary_document_exists(self) -> None:
        text = (ROOT / "PUBLIC_INFORMATION_BOUNDARY.md").read_text(encoding="utf-8")
        self.assertIn("Private Past", text)
        self.assertIn("Future Lab", text)
        self.assertIn("Public Present", text)


if __name__ == "__main__":
    unittest.main()
