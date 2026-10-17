import dataclasses
import unittest
from one_fabric_user_gateway_policy import *

ISS="https://auth.example.test";AUD="https://mcp.example.test/mcp";NOW=10000
T="tenant_alpha";U="8x8_"+"a"*30
BASE=frozenset(FREE_TIER_SCOPES|{"trading.execute","publishing.publish","wallet.sign","devices.connect"})
def who(**kwargs):
    x=dict(user_id="user_a",tenant_id=T,eightx8_id=U,issuer=ISS,audience=AUD,
       scopes=BASE,expires_at=NOW+100,verified_by_server=True)
    x.update(kwargs);return Principal(**x)
def plan(**kwargs):
    x=dict(tenant_id=T,plan=PLAN_FREE,remaining_free_seconds=5280,billing_verified=False,suspended=False)
    x.update(kwargs);return Entitlement(**x)
def auth(action="agents.list",p=None,e=None,tenant=T,evidence=None):
    return authorize(action,who() if p is None else p,tenant,plan() if e is None else e,
                     now=NOW,issuer=ISS,resource=AUD,evidence=evidence)

class PolicyTest(unittest.TestCase):
 def test_public_catalog_without_account(self):
    self.assertTrue(authorize("catalog.read",None,None,None,now=NOW,issuer=ISS,resource=AUD).allowed)
 def test_unknown_action_fails(self):self.assertFalse(auth("owner.shell.exec").allowed)
 def test_valid_tenant(self):self.assertTrue(auth().allowed)
 def test_unverified_principal_rejected(self):self.assertEqual(auth(p=who(verified_by_server=False)).reason,"OAUTH_REQUIRED")
 def test_other_issuer(self):self.assertFalse(auth(p=who(issuer="https://attacker.test")).allowed)
 def test_other_audience(self):self.assertFalse(auth(p=who(audience="https://other.test")).allowed)
 def test_expired(self):self.assertFalse(auth(p=who(expires_at=NOW)).allowed)
 def test_cross_tenant_read_denied(self):self.assertEqual(auth(tenant="tenant_victim").reason,"TENANT_ISOLATION_DENIED")
 def test_cross_tenant_memory_write_denied(self):self.assertFalse(auth("memory.write",tenant="tenant_victim").allowed)
 def test_user_metadata_cannot_be_a_principal(self):
    self.assertFalse(authorize("agents.list",{"verified_by_server":True},T,plan(),now=NOW,issuer=ISS,resource=AUD).allowed)
 def test_wrong_entitlement_tenant(self):self.assertFalse(auth(e=plan(tenant_id="tenant_victim")).allowed)
 def test_unknown_plan_rejected(self):self.assertFalse(auth(e=plan(plan="FAKE_ELITE")).allowed)
 def test_suspended_account_denied(self):self.assertFalse(auth(e=plan(suspended=True)).allowed)
 def test_negative_quota_denied(self):self.assertFalse(auth(e=plan(remaining_free_seconds=-1)).allowed)
 def test_missing_scope_denied(self):self.assertEqual(auth("memory.read",p=who(scopes=frozenset())).reason,"OAUTH_SCOPE_DENIED")
 def test_chatgpt_account_not_magically_granted(self):self.assertNotIn("chatgpt.conversations.read",CAPABILITIES)
 def test_owner_actions_not_present(self):self.assertNotIn("owner.adb.exec",CAPABILITIES)
 def test_no_trading_even_premium(self):
    d=auth("trading.execute",e=plan(plan=PLAN_PLUS,billing_verified=True))
    self.assertFalse(d.allowed);self.assertFalse(d.effect_allowed)
 def test_no_publication_even_premium(self):self.assertFalse(auth("publishing.publish",e=plan(plan=PLAN_PLUS,billing_verified=True)).allowed)
 def test_no_wallet_signing(self):self.assertFalse(auth("wallet.sign").allowed)
 def test_device_mount_needs_more(self):self.assertFalse(auth("devices.storage_request").allowed)
 def test_research_simulation_allowed(self):self.assertTrue(auth("trading.simulate").allowed)
 def test_draft_allowed(self):self.assertTrue(auth("publishing.prepare").allowed)
 def test_free_minutes(self):self.assertEqual(auth("studio.generate").inference_budget_seconds,5280)
 def test_free_exhausted(self):self.assertFalse(auth("agents.converse",e=plan(remaining_free_seconds=0)).allowed)
 def test_plus_requires_billing_proof_for_unlimited(self):
    self.assertEqual(auth("studio.generate",e=plan(plan=PLAN_PLUS,billing_verified=False)).inference_budget_seconds,5280)
 def test_verified_plus_inference_still_provider_gated(self):
    self.assertEqual(auth("agents.converse",e=plan(plan=PLAN_PLUS,billing_verified=True)).reason,"PAID_PLAN_VERIFIED_PROVIDER_QUOTA_STILL_REQUIRED")
 def test_meter_debit_verified(self):
    e,ok=verify_meter_receipt(tenant=T,entitlement=plan(),seconds=60,provider_response_verified=True,
                              request_id="req_abcdefghijk123",prior_ids=frozenset())
    self.assertTrue(ok);self.assertEqual(e.remaining_free_seconds,5220)
 def test_meter_denies_unverified(self):
    e,ok=verify_meter_receipt(tenant=T,entitlement=plan(),seconds=60,provider_response_verified=False,
                              request_id="req_abcdefghijk123",prior_ids=frozenset())
    self.assertFalse(ok)
 def test_meter_blocks_double_charge(self):
    e,ok=verify_meter_receipt(tenant=T,entitlement=plan(),seconds=60,provider_response_verified=True,
                              request_id="req_abcdefghijk123",prior_ids=frozenset({"req_abcdefghijk123"}))
    self.assertFalse(ok)
 def test_meter_refuses_overdraw(self):
    e,ok=verify_meter_receipt(tenant=T,entitlement=plan(remaining_free_seconds=8),seconds=10,provider_response_verified=True,
                              request_id="req_abcdefghijk123",prior_ids=frozenset())
    self.assertFalse(ok)
 def test_meter_blocks_cross_tenant(self):
    e,ok=verify_meter_receipt(tenant="tenant_victim",entitlement=plan(),seconds=5,provider_response_verified=True,
                              request_id="req_abcdefghijk123",prior_ids=frozenset())
    self.assertFalse(ok)
 def test_consent_not_inferred(self):self.assertNotIn("microphone.listen",CAPABILITIES)
 def test_all_product_sectors(self):self.assertEqual(len(CATEGORIES),19)
 def test_one_fabric_onboarding(self):self.assertEqual(len(public_onboarding_steps()),10)

if __name__ == "__main__": unittest.main()
