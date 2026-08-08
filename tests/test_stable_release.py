import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StableReleaseContract(unittest.TestCase):
    def setUp(self):
        self.release = json.loads((ROOT / 'stable/release-unit.json').read_text())
        self.state = json.loads((ROOT / 'state/public-state.json').read_text())
        self.reality = json.loads((ROOT / 'public/reality-snapshot.json').read_text())
        self.html = (ROOT / 'stable/index.html').read_text()
        self.vercel = json.loads((ROOT / 'vercel.json').read_text())

    def test_version_and_scope_are_exact(self):
        self.assertEqual(self.release['version'], '0.1.0')
        self.assertEqual(self.release['release'], '0.1.0-stable')
        self.assertEqual(self.release['scope'], 'PUBLIC_WEB_CLIENT')
        self.assertEqual(self.state['product_version'], '0.1.0')
        self.assertEqual(self.state['release'], '0.1.0-stable')
        self.assertEqual(self.reality['release'], '0.1.0-stable')

    def test_bounded_100_score_never_infers_whole_system(self):
        score = self.release['bounded_acceptance_score']
        self.assertEqual(score['earned'], 100)
        self.assertEqual(score['possible'], 100)
        self.assertEqual(score['whole_system_score'], 'NOT_INFERRED')
        self.assertFalse(self.release['claims']['whole_system_complete'])
        self.assertFalse(self.state['whole_system_complete'])
        self.assertEqual(self.state['whole_system_score'], 'NOT_INFERRED')

    def test_eight_acceptance_gates_are_unique(self):
        gates = self.release['acceptance_gates']
        self.assertEqual(len(gates), 8)
        self.assertEqual(len(set(gates)), 8)

    def test_dimensions_and_spatial_contract_exist(self):
        dims = self.release['dimensions']
        for key in ['1d','2d','3d','4d','5d','6d','7d','8d','360','8k']:
            self.assertIn(key, dims)
        for dim in range(1, 9):
            self.assertIn(f'data-dim="{dim}"', self.html)
        self.assertIn('360°', self.html)
        self.assertIn('8K', self.html)

    def test_zero_latency_and_financial_execution_are_not_claimed(self):
        self.assertFalse(self.release['claims']['zero_latency'])
        self.assertFalse(self.release['claims']['live_wallet_execution'])
        self.assertFalse(self.release['claims']['live_trading'])
        self.assertFalse(self.release['claims']['mainnet_asset_actions'])
        self.assertFalse(self.state['live_trading_enabled'])
        self.assertFalse(self.state['wallet_material_included'])

    def test_rollback_is_preserved(self):
        self.assertTrue(self.release['rollback']['available'])
        self.assertEqual(self.release['rollback']['projection'], '/r3')
        rewrites = {(r['source'], r['destination']) for r in self.vercel['rewrites']}
        self.assertIn(('/r3', '/index.html'), rewrites)
        self.assertIn(('/', '/stable/index.html'), rewrites)


if __name__ == '__main__':
    unittest.main()
