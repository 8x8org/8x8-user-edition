import json
import unittest
from pathlib import Path
from scripts.validate_protected_beta_economy import validate

ROOT = Path(__file__).resolve().parents[1]

class ProtectedBetaEconomyTests(unittest.TestCase):
    def test_current_contract_passes(self):
        self.assertEqual(validate(), [])

    def test_market_assets_exclude_srp(self):
        state = json.loads((ROOT / 'protected-beta/account-economy-state.json').read_text())
        self.assertNotIn('SRP', state['market_asset_family'])
        self.assertEqual(len(state['market_asset_family']), 9)

    def test_cap_and_initial_owner_mint_request_are_exact(self):
        policy = json.loads((ROOT / 'protected-beta/economy-policy.json').read_text())
        self.assertEqual(policy['canonical_supply_rule']['max_live_total_supply_per_market_asset'], 8_888_888)
        for asset in policy['market_assets']:
            self.assertEqual(asset['requested_cap'], 8_888_888)
            self.assertEqual(asset['requested_initial_mint'], 8_888_888)
            self.assertEqual(asset['initial_destination_role'], 'OWNER_TREASURY')

    def test_no_live_financial_state_is_fabricated(self):
        state = json.loads((ROOT / 'protected-beta/account-economy-state.json').read_text())
        for key in ['owner_wallet_verified','mainnet_assets_deployed','testnet_assets_deployed','tokens_minted','primary_sale_live']:
            self.assertFalse(state['truth'][key])

    def test_secondary_market_price_is_not_admin_claim(self):
        policy = json.loads((ROOT / 'protected-beta/economy-policy.json').read_text())
        self.assertFalse(policy['pricing_truth']['secondary_market_price_can_be_directly_set_by_admin'])

if __name__ == '__main__':
    unittest.main()
