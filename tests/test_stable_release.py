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

    def test_public_vercel_builder_guards_source_before_dist_cleanup(self):
        build = (ROOT / 'scripts/build-vercel-static.mjs').read_text()
        required_markers = [
            '8X8_PUBLIC_DEPLOY_SOURCE_MISMATCH',
            '8X8_PUBLIC_DEPLOY_CONTRACT_MISMATCH',
            '8X8_PUBLIC_DEPLOY_PRIVATE_SOURCE_PRESENT',
            'state/public-state.json',
            'unexpectedBackendRoots',
        ]
        for marker in required_markers:
            self.assertIn(marker, build)
        # Do not clear a previously functional dist until the guard has
        # inspected public-only inputs. Arbitrary CLI uploads still need
        # a separate owner-deployment release entrypoint gate.
        self.assertLess(build.index('8X8_PUBLIC_DEPLOY_SOURCE_MISMATCH'),
                        build.index('rmSync(out'))
        self.assertLess(build.index('8X8_PUBLIC_DEPLOY_PRIVATE_SOURCE_PRESENT'),
                        build.index('rmSync(out'))

    def test_public_actor_aliases_preserve_client_capabilities(self):
        catalog = json.loads((ROOT / 'catalog/one_fabric_unified_user_mcp_v1.json').read_text())
        archetypes = catalog['protected_defaults']
        self.assertIn('research-relay', archetypes)
        self.assertIn('research-relay', (ROOT / 'protected-beta/one_fabric_user_gateway_policy.py').read_text())

        capabilities = (ROOT / 'one-fabric-capability-estate-v52.js').read_text()
        self.assertIn('agents.research_relay', capabilities)
        self.assertIn('computer.local_terminal', capabilities)
        self.assertIn('presence.local_terminal_body', capabilities)

        providers = (ROOT / 'protected-beta/one_fabric_secure_connection_intents_v1.py').read_text()
        self.assertIn('Provider("local-device-bridge", "devices"', providers)
        self.assertIn('LOCAL_DEVICE_CONSENT', providers)
        self.assertIn('terminal.execute', providers)
        self.assertIn('orders.place', providers)

        theater = (ROOT / 'plugins/one-fabric-world/ui/one-fabric-agent-theater.html').read_text()
        self.assertIn('"id":"RESEARCH_RELAY"', theater)
        self.assertIn('Research Relay', theater)
        self.assertIn('SCRIPTED SCENARIO', theater)
        self.assertIn('Research Relay 9119', (ROOT / 'v50.html').read_text())

    def test_rollback_is_preserved_while_v50_is_root(self):
        self.assertTrue(self.release['rollback']['available'])
        self.assertEqual(self.release['rollback']['projection'], '/r3')
        rewrites = {(r['source'], r['destination']) for r in self.vercel['rewrites']}
        self.assertIn(('/r3', '/index.html'), rewrites)
        self.assertIn(('/stable', '/stable/index.html'), rewrites)
        self.assertIn(('/', '/v50.html'), rewrites)


if __name__ == '__main__':
    unittest.main()
