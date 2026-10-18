import dataclasses
import unittest
from one_fabric_native_provider_readiness_v2 import Admission
from one_fabric_oauth_launch_gate_v3 import *

BASE=Admission("alpaca","trading",1,True,True,True,False,False,"US",True,False,frozenset({"account.read"}))
P=LaunchPrerequisites(BASE,True,True,True,True,True,True,True,True,True)
class TestNativeLaunch(unittest.TestCase):
 def test_positive_prerequisites_never_create_token_or_url(self):
  d=assess_alpaca_launch(P)
  self.assertEqual(d.verdict,"READY_FOR_BACKEND_OAUTH_START")
  self.assertIsNone(d.user_authorization_url)
  self.assertFalse(d.connected)
  self.assertFalse(d.live_order_authorized)
 def test_every_precondition_fails_separately(self):
  for key in ["verified_8x8_tenant_binding","oauth_app_registered","oauth_app_approved_for_use","client_id_server_configured","exact_redirect_registered","oauth_callback_server_ready","one_time_state_server_persistent","encrypted_token_storage_ready","paper_environment_only"]:
   with self.subTest(key=key):self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,**{key:False})).verdict,"BLOCKED")
 def test_no_secrets_accepted(self):
  d=assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,raw_credential_submitted=True)))
  self.assertEqual(d.reason,"CREDENTIALS_MUST_NOT_ENTER_MCP_OR_CHAT")
 def test_no_direct_effects(self):
  for f in ["orders.place","withdraw","transfer","publisher.post"]:
   with self.subTest(f=f):self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,requested_scopes=frozenset({f})))).verdict,"BLOCKED")
 def test_unverified_actor_cannot_link(self):
  for key in ["authenticated_tenant","owner_consent","vault_origin_verified","jurisdiction_verified"]:
   with self.subTest(key=key):self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,**{key:False}))).verdict,"BLOCKED")
 def test_stop_blocks(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,owner_stop_active=True))).verdict,"BLOCKED")
 def test_existing_handle_is_not_a_new_link(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,vault_handle_present=True))).reason,"USE_EXISTING_CONNECTION_RECONCILIATION")
 def test_canary_is_not_launch(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,provider_canary_verified=True))).verdict,"BLOCKED")
 def test_other_provider_blocked(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,provider="kraken"))).verdict,"BLOCKED")
 def test_live_env_blocked(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,paper_environment_only=False)).reason,"PAPER_ONLY_FOR_FIRST_CONNECTION")
 def test_bogus_input(self):
  self.assertEqual(assess_alpaca_launch(None).verdict,"BLOCKED")
 def test_blank_or_unverified_jurisdiction_blocked(self):
  self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,jurisdiction="",jurisdiction_verified=False))).verdict,"BLOCKED")
 def test_no_slot_or_bool(self):
  for slot in [None,False,0,101]:
   with self.subTest(slot=slot):self.assertEqual(assess_alpaca_launch(dataclasses.replace(P,admission=dataclasses.replace(BASE,account_slot=slot))).verdict,"BLOCKED")
if __name__=='__main__':unittest.main()
