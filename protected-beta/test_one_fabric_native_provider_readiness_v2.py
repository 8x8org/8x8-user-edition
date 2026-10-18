import dataclasses
import unittest
from one_fabric_native_provider_readiness_v2 import *

A = Admission("alpaca", "trading", 1, True, True, True, True, True,
              "US", True, False, frozenset({"account.read"}))

class Gate(unittest.TestCase):
    def test_all_eleven_eligible_provider_candidates(self):
        self.assertEqual(len(TRADING_CANDIDATES), 11)
        for name in TRADING_CANDIDATES:
            with self.subTest(name=name):
                self.assertEqual(evaluate(dataclasses.replace(A, provider=name)).verdict, "READ_ONLY_CONNECTION_VERIFIED")
    def test_all_twelve_publishing_candidates(self):
        self.assertEqual(len(PUBLICATION_CANDIDATES), 12)
        for name in PUBLICATION_CANDIDATES:
            with self.subTest(name=name):
                v = evaluate(dataclasses.replace(A, provider=name, domain="publishing", account_slot=None, requested_scopes=frozenset({"profile.read"})))
                self.assertTrue(v.connected)
                self.assertFalse(v.public_post_authorized)
    def test_rejects_bitget_us(self):
        self.assertEqual(evaluate(dataclasses.replace(A, provider="bitget")).reason,"PROVIDER_RESTRICTED_IN_US")
    def test_rejects_unknown_exchange(self):
        self.assertEqual(evaluate(dataclasses.replace(A, provider="unknown")).reason,"UNKNOWN_TRADING_PROVIDER")
    def test_eight_distinct_slots_not_historical_five_cap(self):
        for n in range(1,9):
            self.assertTrue(evaluate(dataclasses.replace(A, account_slot=n)).connected)
    def test_zero_slot_rejected(self):
        self.assertEqual(evaluate(dataclasses.replace(A, account_slot=0)).verdict,"BLOCKED")
    def test_bool_slot_rejected(self):
        self.assertEqual(evaluate(dataclasses.replace(A, account_slot=True)).verdict,"BLOCKED")
    def test_tenant_missing_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, authenticated_tenant=False)).verdict,"BLOCKED")
    def test_consent_missing_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, owner_consent=False)).verdict,"BLOCKED")
    def test_vault_not_ready_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, vault_origin_verified=False)).verdict,"BLOCKED")
    def test_unenrolled_is_not_connected(self):
        x=evaluate(dataclasses.replace(A, vault_handle_present=False))
        self.assertEqual(x.verdict,"READY_FOR_PROTECTED_ENROLLMENT");self.assertFalse(x.connected)
    def test_canary_missing_is_not_connected(self):
        x=evaluate(dataclasses.replace(A, provider_canary_verified=False))
        self.assertEqual(x.verdict,"BOUND_PENDING_CANARY");self.assertFalse(x.connected)
    def test_jurisdiction_not_verified(self):
        self.assertEqual(evaluate(dataclasses.replace(A, jurisdiction_verified=False)).verdict,"BLOCKED")
    def test_owner_stop_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, owner_stop_active=True)).verdict,"BLOCKED")
    def test_trade_requested_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, live_order_requested=True)).verdict,"BLOCKED")
    def test_trading_scope_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, requested_scopes=frozenset({"orders.place"}))).verdict,"BLOCKED")
    def test_publishing_scope_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, requested_scopes=frozenset({"publisher.post"}))).verdict,"BLOCKED")
    def test_raw_secret_never_accepted(self):
        self.assertEqual(evaluate(dataclasses.replace(A, raw_credential_submitted=True)).verdict,"BLOCKED")
    def test_connected_never_grants_live_effect(self):
        x=evaluate(A)
        self.assertTrue(x.connected);self.assertFalse(x.live_trading_authorized);self.assertFalse(x.public_post_authorized)
    def test_invalid_input_denied(self):
        self.assertEqual(evaluate({}).verdict,"BLOCKED")
        self.assertEqual(evaluate(dataclasses.replace(A, requested_scopes=set(["account.read"]))).verdict,"BLOCKED")
    def test_empty_scopes_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A,requested_scopes=frozenset())).verdict,"BLOCKED")
    def test_forged_string_auth_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A, authenticated_tenant="true")).verdict,"BLOCKED")
    def test_cross_domain_scope_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A,requested_scopes=frozenset({"profile.read"}))).verdict,"BLOCKED")
    def test_missing_jurisdiction_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A,jurisdiction=None)).verdict,"BLOCKED")
    def test_publication_slot_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A,domain="publishing",provider="youtube")).verdict,"BLOCKED")
    def test_unknown_domain_denied(self):
        self.assertEqual(evaluate(dataclasses.replace(A,domain="wallet")).verdict,"BLOCKED")

if __name__ == '__main__':unittest.main()
