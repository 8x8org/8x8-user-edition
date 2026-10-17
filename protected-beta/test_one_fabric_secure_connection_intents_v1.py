import dataclasses, json, unittest
from one_fabric_secure_connection_intents_v1 import *
A=Actor("member_001","user_tenant_001","8x8_"+"a"*30,True,frozenset({"connections.create"}))
NOW=10000
class PolicyTests(unittest.TestCase):
 def i(self,provider="bitget",slot=1,scopes=frozenset({"account.read"}),**kwargs):
  return propose_connection(A,provider,slot=slot,scopes=scopes,now=NOW,**kwargs)
 def test_all_provider_names_unique(self):self.assertEqual(len(PROVIDERS),16)
 def test_bitget_read_only_intent(self):
  x=self.i();self.assertEqual((x.provider,x.slot,x.state),("bitget",1,"PREPARED_NOT_CONNECTED"))
 def test_bitget_five_slots(self):
  for n in range(1,6):self.assertEqual(self.i(slot=n).slot,n)
 def test_bitget_sixth_slot_rejected(self):
  with self.assertRaises(ConnectionDenied):self.i(slot=6)
 def test_bitget_zero_slot_rejected(self):
  with self.assertRaises(ConnectionDenied):self.i(slot=0)
 def test_bitget_bool_slot_rejected(self):
  with self.assertRaises(ConnectionDenied):self.i(slot=True)
 def test_external_effect_cannot_be_requested(self):
  for s in ["orders.place","withdraw","transfer","publisher.post","terminal.execute","wallet.sign"]:
   with self.subTest(s=s),self.assertRaises(ConnectionDenied):self.i(scopes=frozenset({s}))
 def test_social_post_scope_denied(self):
  with self.assertRaises(ConnectionDenied):self.i(provider="youtube",slot=None,scopes=frozenset({"publisher.post"}))
 def test_telegram_bot_guidance(self):
  g=agent_guidance("telegram");self.assertTrue(g["secret_form_required"]);self.assertTrue(g["no_secret_in_chat"])
 def test_bitget_passphrase_not_in_response(self):
  x=self.i();self.assertNotIn("passphrase",json.dumps(dataclasses.asdict(x)).lower())
 def test_no_user_password(self):
  with self.assertRaises(SecretInChatRejected):self.i(submitted_fields={"password":"do-not-store"})
 def test_no_bot_token(self):
  with self.assertRaises(SecretInChatRejected):self.i(provider="telegram",slot=None,scopes=frozenset({"channel.read"}),submitted_fields={"bot_token":"secret"})
 def test_nested_api_key_rejected(self):
  with self.assertRaises(SecretInChatRejected):self.i(submitted_fields={"field":{"Api_Key":"secret"}})
 def test_empty_extra_fields_allowed(self):self.assertEqual(self.i(submitted_fields={}).provider,"bitget")
 def test_unknown_extra_fields_rejected(self):
  with self.assertRaises(ConnectionDenied):self.i(submitted_fields={"unsafe":1})
 def test_cross_tenant_denied(self):
  x=self.i();b=dataclasses.replace(A,tenant_id="tenant_victim")
  self.assertFalse(validate_intent_owner(b,x,now=NOW))
 def test_account_cross_8x8_id_denied(self):
  x=self.i();b=dataclasses.replace(A,eightx8_id="8x8_"+"b"*30)
  self.assertFalse(validate_intent_owner(b,x,now=NOW))
 def test_expired_denied(self):self.assertFalse(validate_intent_owner(A,self.i(),now=NOW+300))
 def test_valid_owner(self):self.assertTrue(validate_intent_owner(A,self.i(),now=NOW+50))
 def test_unverified_actor_denied(self):
  with self.assertRaises(ConnectionDenied):propose_connection(dataclasses.replace(A,server_authenticated=False),"bitget",slot=1,scopes=frozenset({"account.read"}),now=NOW)
 def test_actor_missing_scope_denied(self):
  with self.assertRaises(ConnectionDenied):propose_connection(dataclasses.replace(A,scopes=frozenset()),"bitget",slot=1,scopes=frozenset({"account.read"}),now=NOW)
 def test_owner_tenant_not_auto_authorized(self):
  with self.assertRaises(ConnectionDenied):propose_connection(dataclasses.replace(A,tenant_id="owner:root"),"bitget",slot=1,scopes=frozenset({"account.read"}),now=NOW)
 def test_account_slot_not_allowed_for_youtube(self):
  with self.assertRaises(ConnectionDenied):self.i(provider="youtube",slot=1,scopes=frozenset({"channel.read"}))
 def test_youtube_read_only(self):self.assertEqual(self.i(provider="youtube",slot=None,scopes=frozenset({"channel.read"})).provider,"youtube")
 def test_wallet_watch_only(self):self.assertEqual(self.i(provider="wallet-watch",slot=None,scopes=frozenset({"wallet.address.read"})).provider,"wallet-watch")
 def test_wallet_seed_denied(self):
  with self.assertRaises(SecretInChatRejected):self.i(provider="wallet-watch",slot=None,scopes=frozenset({"wallet.address.read"}),submitted_fields={"seed_phrase":"never"})
 def test_direct_local_device_shell_denied(self):
  with self.assertRaises(ConnectionDenied):self.i(provider="local-device-bridge",slot=None,scopes=frozenset({"terminal.execute"}))
 def test_local_device_bridge_alias_is_read_only(self):
  g=agent_guidance("local-device-bridge")
  self.assertEqual(g["domain"],"devices")
  self.assertEqual(g["approved_initial_scopes"],["device.status.read"])
  self.assertFalse(g["secret_form_required"])
  self.assertEqual(g["state"],"GUIDE_ONLY_NO_LIVE_VAULT_LINK")
 def test_unknown_provider(self):
  with self.assertRaises(ConnectionDenied):self.i(provider="fake")
 def test_nonce_unique(self):self.assertNotEqual(self.i().nonce_digest,self.i().nonce_digest)
 def test_nonce_is_digest_only(self):self.assertEqual(len(self.i().nonce_digest),64)
 def test_no_password_collected_anywhere(self):self.assertNotIn("password",dataclasses.asdict(self.i()))
 def test_free_not_active(self):self.assertFalse(plan_truth()["free_grant_active"])
 def test_paid_not_active(self):self.assertFalse(plan_truth()["paid_entitlement_active"])
 def test_platform_not_unlimited(self):self.assertFalse(plan_truth()["external_social_api_unlimited"])
 def test_crypto_not_live(self):self.assertFalse(plan_truth()["tokenomics_8x8_coin_payments_live_verified"])
 def test_bitget_initial_order_read_allowed(self):self.assertEqual(self.i(scopes=frozenset({"orders.read"})).provider,"bitget")
 def test_bitget_not_live_order(self):self.assertNotIn("orders.place",PROVIDERS["bitget"].scopes)
 def test_telegram_scope_read_only(self):self.assertNotIn("publisher.post",PROVIDERS["telegram"].scopes)
 def test_bitget_cloud_credential_form_not_offered(self):
  g=agent_guidance("bitget")
  self.assertFalse(g["secret_form_required"])
  self.assertTrue(g["bitget_local_broker_required"])
 def test_bitget_us_is_prohibited(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="US",jurisdiction_verified_by_server=True,
      local_broker_security_accepted=True,provider_access_policy_accepted=True)
  self.assertEqual(r["state"],"PROVIDER_PROHIBITS_US_ACCESS")
  self.assertFalse(r["credential_intake_allowed"])
 def test_bitget_unverified_location_fails_closed(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="FR",jurisdiction_verified_by_server=False)
  self.assertEqual(r["state"],"JURISDICTION_VERIFICATION_REQUIRED")
 def test_bitget_missing_location_fails_closed(self):
  r=provider_enrollment_preflight("bitget",jurisdiction=None,jurisdiction_verified_by_server=True)
  self.assertEqual(r["state"],"JURISDICTION_VERIFICATION_REQUIRED")
 def test_bitget_local_broker_required_even_if_policy_cleared(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="TEST_ELIGIBLE",
      jurisdiction_verified_by_server=True,provider_access_policy_accepted=True)
  self.assertEqual(r["state"],"USER_LOCAL_BROKER_SECURITY_PENDING")
 def test_bitget_provider_terms_required_even_with_local_broker(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="TEST_ELIGIBLE",
      jurisdiction_verified_by_server=True,local_broker_security_accepted=True)
  self.assertEqual(r["state"],"PROVIDER_TERMS_AND_ELIGIBILITY_REVIEW_REQUIRED")
 def test_all_pass_still_not_secret_intake_or_trade(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="TEST_ELIGIBLE",jurisdiction_verified_by_server=True,
      local_broker_security_accepted=True,provider_access_policy_accepted=True)
  self.assertEqual(r["state"],"LOCAL_READ_ONLY_BROKER_REVIEW_ONLY")
  self.assertFalse(r["credential_intake_allowed"])
  self.assertFalse(r["authorized_trading"])
 def test_social_oauth_not_credential_capture(self):
  r=provider_enrollment_preflight("youtube",jurisdiction=None,jurisdiction_verified_by_server=False)
  self.assertEqual(r["state"],"SEPARATE_PROVIDER_OAUTH_OR_CUSTODY_FLOW_NOT_DEPLOYED")
  self.assertFalse(r["credential_intake_allowed"])
 def test_unknown_provider_rejected_by_preflight(self):
  with self.assertRaises(ConnectionDenied):
   provider_enrollment_preflight("attacker",jurisdiction="US",jurisdiction_verified_by_server=True)
 def test_bitget_unapproved_cloud_storage_never_allowed(self):
  r=provider_enrollment_preflight("bitget",jurisdiction="TEST_ELIGIBLE",jurisdiction_verified_by_server=True)
  self.assertIs(r["remote_cloud_bitget_key_storage_allowed"],False)
 def test_original_intent_remains_metadata_only(self):
  intent=self.i()
  self.assertEqual(intent.state,"PREPARED_NOT_CONNECTED")
  self.assertNotIn("secret_key",json.dumps(dataclasses.asdict(intent)))

 def test_invalid_time_rejected(self):
  with self.assertRaises(ConnectionDenied):propose_connection(A,"bitget",slot=1,scopes=frozenset({"account.read"}),now=-1)
 def test_invalid_scope_type_rejected(self):
  with self.assertRaises(ConnectionDenied):propose_connection(A,"bitget",slot=1,scopes={"account.read"},now=NOW)
 def test_generated_id_not_equal(self):self.assertNotEqual(self.i().intent_id,self.i().intent_id)

if __name__=="__main__":unittest.main()
