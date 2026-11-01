import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync,existsSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
const policy=JSON.parse(read('projects/open-world-2026/genesis-launch-readiness.v1.json'));
const page=read('projects/open-world-2026/genesis.html');
test('preserves source 8x8 candidate identities without calling proposed price market value',()=>{
 assert.equal(policy.root,'fabric://8x8/core');
 assert.equal(policy.genesis.max_native_coin_units,'8888888');
 assert.equal(policy.genesis.owner_reference_usd,'8.88');
 assert.equal(policy.genesis.market_price_usd,null);
 assert.equal(policy.genesis.launch_price_guarantee,false);
 assert.equal(policy.genesis.genesis_vault_backing,'88888');
 assert.match(page,/not<.strong> market price/i);
});
test('no crypto receipt, treasury deposit, token allocation or reward is enabled',()=>{
 assert.equal(policy.payment.crypto_settlement_enabled,false);
 assert.equal(policy.payment.treasury_collection_enabled,false);
 assert.equal(policy.payment.reservations_paid_enabled,false);
 assert.equal(policy.payment.airdrop_enabled,false);
 assert.deepEqual(policy.payment.accepted_crypto_assets,[]);
 assert.equal(policy.payment.treasury_deposit_address,null);
 assert.equal(policy.referral.rewards_live,false);
 assert.equal(policy.referral.purchaser_commissions_enabled,false);
 assert.match(page,/No token sale or reservation checkout is open/i);
});
test('wallet access is user clicked, account-only, and never requests signing or transfer',()=>{
 assert.match(page,/connect\.addEventListener\('click'/);
 assert.match(page,/method:'eth_requestAccounts'/);
 assert.doesNotMatch(page,/eth_sendTransaction|personal_sign|eth_sign|wallet_addEthereumChain|wallet_switchEthereumChain/);
 assert.match(page,/No 8x8 ID association or payment has occurred/);
});
test('verified public help and support channels never imply sale or custody',()=>{
 assert.match(page,/https:\/\/github\.com\/8x8org\/8x8-user-edition\/issues\/new/);
 assert.match(page,/https:\/\/buy\.stripe\.com\/bJe4gz0aUcOD7N93Fr4Rq01/);
 assert.match(page,/no referral rewards are active/i);
 assert.match(read('projects/open-world-2026/index.html'),/href="\/projects\/open-world-2026\/genesis.html"/);
 assert.ok(existsSync(new URL('../dist/projects/open-world-2026/genesis.html',import.meta.url)));
 assert.ok(existsSync(new URL('../dist/projects/open-world-2026/genesis-launch-readiness.v1.json',import.meta.url)));
});

test('public founder invitation links only to nonbinding interest, not a token sale',()=>{
 const invite=read('projects/genesis-invite/index.html');
 assert.match(invite,/href="https:\/\/form\.jotform\.com\/263041117453044"/);
 assert.match(invite,/Join the free community interest list/);
 assert.match(invite,/does not create an 8x8 account or wallet/);
 assert.match(invite,/not live or for sale/);
 assert.match(invite,/https:\/\/github\.com\/8x8org\/8x8-user-edition\/issues\/205/);
 assert.match(invite,/https:\/\/buy\.stripe\.com\/bJe4gz0aUcOD7N93Fr4Rq01/);
 assert.ok(existsSync(new URL('../dist/projects/genesis-invite/index.html',import.meta.url)));
});
