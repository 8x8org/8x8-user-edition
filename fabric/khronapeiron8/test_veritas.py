import json
import unittest

from fabric.khronapeiron8.veritas import (
    MULTIPLIERS,
    SEED,
    W_ANCHOR,
    calculations,
    canonical_json_bytes,
    digital_root,
    grand_aggregate,
    verify,
)


class VeritasV1Tests(unittest.TestCase):
    def test_exact_chain_and_correct_aggregate(self):
        rows = calculations()
        expected = [
            8_888_888,
            7_901_225_876_544,
            702_324_165_714_243_072,
            6_242_257_184_868_192_423_936,
            5_543_124_380_162_954_872_455_168,
            487_794_945_454_340_028_776_054_784,
            3_902_359_563_634_720_230_208_438_272,
            4_395_703_876_428_740_148_998_380_664,
        ]
        self.assertEqual([row.value for row in rows], expected)

    def test_supplied_legacy_calc8_is_rejected_as_sum(self):
        rows = calculations()
        legacy_calc8 = 499_581_037_244_762_775_498_942_392
        self.assertNotEqual(sum(row.value for row in rows[:7]), legacy_calc8)

    def test_chain_multipliers(self):
        rows = calculations()
        self.assertEqual(rows[0].value, SEED)
        for index, multiplier in enumerate(MULTIPLIERS, start=1):
            self.assertEqual(rows[index].value, rows[index - 1].value * multiplier)

    def test_correct_aggregate_has_digital_root_8(self):
        aggregate = calculations()[-1].value
        self.assertEqual(digital_root(aggregate), 8)
        self.assertEqual(aggregate % 256, 120)

    def test_w_is_explicit_protocol_anchor_not_arithmetic_claim(self):
        self.assertEqual(W_ANCHOR, 87)
        self.assertEqual(format(W_ANCHOR, "08b"), "01010111")
        self.assertEqual(chr(W_ANCHOR), "W")

    def test_truth_boundary_and_receipt_are_deterministic(self):
        first = canonical_json_bytes()
        second = canonical_json_bytes()
        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertFalse(payload["w_anchor"]["derived_from_arithmetic"])
        self.assertEqual(
            payload["truth_boundary"]["phononium_8"],
            "CONCEPTUAL_NOT_EMPIRICALLY_VERIFIED",
        )

    def test_complete_verifier_passes(self):
        result = verify()
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["receipt_sha256"]), 64)

    def test_grand_aggregate_requires_seven_precursors(self):
        with self.assertRaises(ValueError):
            grand_aggregate([1, 2, 3])


if __name__ == "__main__":
    unittest.main()
