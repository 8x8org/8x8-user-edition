import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const base = new URL('../', import.meta.url);
const doc = JSON.parse(readFileSync(new URL('docs/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2.json',base), 'utf8'));
const prose = readFileSync(new URL('docs/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2.md',base), 'utf8');
const readme = readFileSync(new URL('README.md',base), 'utf8');
const role = readFileSync(new URL('ONE_FABRIC_ROLE.md',base), 'utf8');

test('one root, public audience, unpromoted',()=>{
 assert.equal(doc.canonical_root,'fabric://8x8/core');
 assert.equal(doc.audience,'PUBLIC_SAFE');
 assert.equal(doc.source_state,'DRAFT_REVIEW_NOT_RELEASED');
 assert.equal(doc.public_bootstrap_is_not_authorization,true);
});
test('six release gates cannot be silently excluded',()=>{
 assert.equal(doc.public_release_scope.v1_required_gates.length,6);
 assert.equal(new Set(doc.public_release_scope.v1_required_gates).size,6);
});
test('user scope and economic effects remain gated',()=>{
 assert.equal(doc.identity.private_owner_core,'NOT_PUBLIC');
 assert.equal(doc.no_secrets,true);
 assert.equal(doc.roadmap_product_targets.billing_status,'NOT_ESTABLISHED');
 assert.equal(doc.roadmap_product_targets.mainnet,'NOT_ESTABLISHED');
});
test('public document excludes private topology and credentials',()=>{
 for (const forbidden of [/horbolsi\/8x8(?:\/|\b)/i,/\/data\/data\/com\.termux/i,/\b(?:sk-proj-|ghp_|xoxb-)[A-Za-z0-9]+/i,/BEGIN (?:RSA|OPENSSH) PRIVATE KEY/]){
  assert.doesNotMatch(prose,forbidden);
  assert.doesNotMatch(JSON.stringify(doc),forbidden);
 }
 assert.match(prose,/private.*not.*shared|not shared tenant authority/is);
});
test('existing public entrypoints reference this bootstrap',()=>{
 assert.match(readme,/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2\.md/);
 assert.match(role,/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2\.md/);
});
test('agent and AI discovery entrypoints stay public-safe',()=>{
 const agents = readFileSync(new URL('AGENTS.md',base),'utf8');
 const discover = readFileSync(new URL('llms.txt',base),'utf8');
 assert.match(agents,/ONE_FABRIC_PUBLIC_BOOTSTRAP_V2\.md/);
 assert.match(discover,/Public AI\/user bootstrap V2/);
 assert.doesNotMatch(agents,/\/data\/data\/com\.termux|BEGIN (?:RSA|OPENSSH) PRIVATE KEY/i);
 assert.match(discover,/not proof of a hosted llms\.txt endpoint/i);
});

test('public bootstrapping never grants live authority',()=>{
 assert.match(prose,/not a newly accepted release|not a new release/i);
 assert.match(prose,/No production deployment is performed/i);
});
