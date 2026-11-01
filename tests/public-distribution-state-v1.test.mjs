import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
import test from 'node:test';
const state = JSON.parse(readFileSync(new URL('../docs/data/ONE_FABRIC_PUBLIC_DISTRIBUTION_STATE_V1.json', import.meta.url)));
const ids = new Set();
const acceptedStates = new Set(['PUBLISHED_SHELL','PREVIEW_DEPLOYED','SOURCE_PRESENT','CANDIDATE','UNKNOWN']);
for (const carrier of state.carriers) {
  assert.ok(/^[a-z0-9_]+$/.test(carrier.id));
  assert.equal(ids.has(carrier.id), false, `duplicate ${carrier.id}`);
  ids.add(carrier.id);
}
test('canonical root and source are public-safe', () => {
  assert.equal(state.canonical_root, 'fabric://8x8/core');
  assert.equal(state.classification, 'PUBLIC_SAFE_RELEASE_REVIEW');
  assert.equal(state.owner_private_access_from_public, false);
  assert.equal(state.automatic_public_release, false);
});
test('all nine carriers have bounded and separate identities', () => {
  assert.equal(ids.size, 9);
  assert.equal(new Set(state.carriers.map(c=>c.display_name)).size, 9);
  for (const c of state.carriers) {
    assert.ok(acceptedStates.has(c.claim_state));
    assert.ok(c.source_reference && c.not_proven.length>=1);
    assert.ok(c.public_url === null || c.public_url.startsWith('https://'));
    if(c.claim_state!=='PREVIEW_DEPLOYED'&&c.claim_state!=='PUBLISHED_SHELL') assert.equal(c.public_url,null);
  }
});
test('no registered app or preview is credited as a production 8x8 task', () => {
  assert.equal(state.cross_surface_gate.shared_identity_server_proven, false);
  assert.equal(state.cross_surface_gate.release_promotion_allowed, false);
  assert.equal(state.cross_surface_gate.cross_tenant_denial_proven, false);
});
test('ChatGPT distribution is not declared approved or installed', () => {
  const m=state.carriers.find(c=>c.id==='chatgpt_mcp');
  assert.equal(m.claim_state,'CANDIDATE');
  assert.equal(m.public_url,null);
  assert.equal(state.cross_surface_gate.production_8x8_mcp_proven,false);
});
test('APK and local device consent remain unverified and segregated', () => {
  assert.equal(state.carriers.find(c=>c.id==='android_apk').claim_state,'SOURCE_PRESENT');
  assert.equal(state.cross_surface_gate.public_signed_apk_verified,false);
  assert.equal(state.cross_surface_gate.public_device_pairing_proven,false);
  assert.match(state.policy.optional_adb,/no public ADB exposure/);
});
test('pricing is target-only and no unlimited or charged service is misrepresented', () => {
  assert.equal(state.entitlement.free_minutes_proposed,88);
  assert.equal(state.entitlement.subscription_price_usd_proposed,'8.88');
  assert.equal(state.entitlement.billing_live,false);
  assert.equal(state.entitlement.unlimited_usage_guaranteed,false);
});
test('historical donor ledger is preserved without falsely closing census',()=>{
  assert.equal(state.archive.overlapping_preserved_ledger_rows,1269);
  assert.equal(state.archive.archive_exhaustively_reviewed,false);
  assert.equal(state.archive.public_exposure_of_private_source,false);
});
test('marketing and code distribution do not bypass privacy or spam protections',()=>{
  assert.match(state.policy.marketing,/no mass unsolicited/);
  assert.match(state.policy.source_code_privacy,/browser JavaScript cannot be secret/);
});