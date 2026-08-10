import pathlib
import unittest

from fabric.external_capability_registry.registry import Coverage, FAMILIES, load, metrics, normalize, receipt_sha256

HERE = pathlib.Path(__file__).parent


class RegistryV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load(str(HERE / "seed_registry.json"))

    def test_seed_registry_validates(self):
        for record in self.records:
            record.validate()

    def test_eight_families_are_canonical(self):
        self.assertEqual(len(FAMILIES), 8)
        self.assertEqual(FAMILIES[0], "CHRONOS")
        self.assertEqual(FAMILIES[-1], "VERITAS")

    def test_normalization_is_deterministic(self):
        a = normalize(self.records)
        b = normalize(reversed(self.records))
        self.assertEqual(a, b)

    def test_metrics_do_not_fake_global_100(self):
        result = metrics(self.records)
        self.assertFalse(result["global_100_claim_allowed"])
        self.assertFalse(result["w_state"])
        self.assertGreater(result["denominator"], 0)
        self.assertLess(result["coverage_C"], 1.0)

    def test_only_receipted_states_can_score_parity_or_superior(self):
        for record in self.records:
            if record.score >= Coverage.PARITY:
                self.assertTrue(record.receipt.strip())
                self.assertTrue(record.test.strip())

    def test_receipt_hash_is_stable(self):
        first = receipt_sha256(self.records)
        second = receipt_sha256(self.records)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


if __name__ == "__main__":
    unittest.main()
