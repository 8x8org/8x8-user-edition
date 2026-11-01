import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync,existsSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
const policy=JSON.parse(read('projects/open-world-2026/event-policy.v1.json'));
const html=read('projects/open-world-2026/index.html');
test('free public-preview event has exact 2026 period and never grants provider quota',()=>{
 assert.equal(policy.root,'fabric://8x8/core');
 assert.equal(policy.event.start,'2026-11-01');
 assert.equal(policy.event.end_inclusive,'2026-12-31');
 assert.equal(policy.event.state,'PROPOSED_EVENT_POLICY_SOURCE_ONLY');
 assert.equal(policy.truth.release_deployed,false);
 assert.equal(policy.truth.all_products_free,false);
 assert.equal(policy.pricing.automatic_reactivation,false);
 assert.match(policy.event.free_scope,/does not include unverified premium AI calls/i);
});
test('live voluntary support is separate from disabled subscriptions and unlaunched NFTs',()=>{
 assert.equal(policy.support.one_time_usd,8.88);
 assert.match(policy.support.optional_fiat_tip,/^https:\/\/buy\.stripe\.com\//);
 assert.equal(policy.support.no_product_entitlement,true);
 assert.equal(policy.reservations.enabled_payment,false);
 assert.equal(policy.web3.crypto_asset_packages,'NOT_FOR_SALE');
 assert.equal(policy.web3.wallet_addresses_published,false);
 assert.match(html,/not a paid subscription/i);
 assert.match(html,/No paid subscription will be automatically started/i);
});
test('human-facing event is crawlable and linked from existing public routes',()=>{
 assert.match(html,/<h1>8x8 <em>Open World<\/em> 2026<\/h1>/);
 assert.match(html,/November 1 – December 31, 2026/);
 assert.match(html,/available on an independently verified deployment/i);
 assert.match(read('projects/index.html'),/href="\/open-world-2026"/);
 const v=JSON.parse(read('vercel.json'));
 assert.ok(v.rewrites.some(r=>r.source==='/open-world-2026'&&r.destination==='/projects/open-world-2026/index.html'));
 assert.ok(read('scripts/build-vercel-static.mjs').includes("'projects'"));
});
test('event page and policy included in actual built output with no false live tokens',()=>{
 assert.ok(existsSync(new URL('../dist/projects/open-world-2026/index.html',import.meta.url)));
 assert.ok(existsSync(new URL('../dist/projects/open-world-2026/event-policy.v1.json',import.meta.url)));
 const built=read('dist/projects/open-world-2026/index.html');
 assert.match(built,/not a verified live production launch/i);
});
