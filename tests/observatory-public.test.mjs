import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const read = path => readFileSync(new URL('../'+path, import.meta.url),'utf8');
const page=read('observatory/index.html');
const build=read('scripts/build-vercel-static.mjs');
const android=read('android-app/app/src/main/java/world/eightx8/user/PublicAssetHandler.java');
const gradle=read('android-app/app/build.gradle');
const vercel=JSON.parse(read('vercel.json'));
const worker=read('sw.js');

test('five existing lanes are recognizable but not deceptively LIVE',()=>{
  const labels=['Execute','Research','Verify','Create','Improve'];
  const times=[':00',':12',':24',':36',':48'];
  for(const x of labels) assert.match(page,new RegExp('<h3>'+x+'</h3>'));
  for(const x of times) assert.ok(page.includes(x+' EASTERN'), x);
  assert.equal((page.match(/STATUS UNKNOWN/g)||[]).length,5);
  assert.match(page,/LIVE VERIFICATION: NOT CONNECTED/);
  assert.match(page,/No owner session, authorized signed telemetry/);
  assert.match(page,/fabric:\/\/8x8\/core/);
});
test('preview cannot act as owner scheduler, broker or private event feed',()=>{
  assert.doesNotMatch(page,/<script|<form|<input|<button|fetch\(|XMLHttpRequest|WebSocket|EventSource|localStorage|sessionStorage|navigator\.mediaDevices/i);
  for(const privateField of ['6aa4fc51','6ab4df1f','BEGIN PRIVATE KEY','auth_user_id','api_key=','OWNER_PRIVATE_RUNTIME'])
    assert.ok(!page.includes(privateField),privateField);
  assert.match(page,/NOT CONNECTED/);
  assert.match(page,/STOP\/PAUSE/);
});
test('same Observatory route is built and packaged for web, APK and bounded offline cache',()=>{
  assert.match(build,/'observatory'/);
  assert.match(build,/data-eightx8-observatory-link/);
  assert.match(android,/case "observatory": case "observatory\/": return "observatory\/index.html";/);
  assert.match(gradle,/'observatory\/index.html'/);
  assert.ok(vercel.rewrites.some(x=>x.source==='/observatory'&&x.destination==='/observatory/index.html'));
  assert.match(worker,/\['\/observatory\/index.html', \/\^text/);
  assert.match(worker,/\['\/observatory', '\/observatory\/index.html'/);
  assert.match(worker,/if \(req.method !== 'GET'/);
  assert.match(android,/case "studio"/);
});
