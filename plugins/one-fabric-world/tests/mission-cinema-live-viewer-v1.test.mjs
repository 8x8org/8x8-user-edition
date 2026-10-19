import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Script} from 'node:vm';
const html=readFileSync(new URL('../ui/one-fabric-observatory.html',import.meta.url),'utf8');
test('existing replay and media popup remain intact',()=>{
 for(const id of ['mc-replay','mc-halt','mc-video','mc-player','mc-dialog','mc-approval'])
  assert.match(html,new RegExp('id="'+id+'"'));
});
test('new explicit read-only event connect and disconnect controls appear',()=>{
 assert.match(html,/id="mc-live-connect"/);assert.match(html,/id="mc-live-disconnect"/);
 assert.match(html,/eightx8\.verified_record/);
});
test('live transport must be independently enabled; disabled by default',()=>{
 assert.match(html,/if\(!cfg\|\|cfg\.enabled!==true/);
 assert.match(html,/LIVE FEED NOT CONNECTED/);
 assert.doesNotMatch(html,/__EIGHTX8_AUTHORIZED_OBSERVATORY__\s*=/);
});
test('same-origin HTTPS only, no token or URL guessing',()=>{
 assert.match(html,/target\.origin!==location\.origin/);
 assert.match(html,/target\.protocol!=="https:"/);
 assert.match(html,/cfg\.path!=="\/v1\/observatory\/events"/);
 assert.doesNotMatch(html,/new EventSource\("https:/);
});
test('fails closed for recorded and unsigned messages',()=>{
 assert.match(html,/SIGNED_EVENTS_VERIFIED_TRANSPORT_NOT_PROVEN/);
 assert.match(html,/UNVERIFIED_FRAME/);assert.match(html,/INVALID_CHECKPOINT/);
});
test('viewer never displays raw args, tokens or hidden thoughts',()=>{
 assert.match(html,/textContent=e\.event_type/);
 assert.match(html,/hidden reasoning/);
 assert.match(html,/authorization:/);
 assert.doesNotMatch(html,/innerHTML\s*=\s*e\.summary/);
});
test('read-only subscription has no effect or stream forgery',()=>{
 assert.match(html,/frame\.execution_authorized!==false/);
 assert.match(html,/frame\.live_stream_connected!==false/);
 assert.match(html,/stream\.close\(\)/);
});
test('all inline JavaScript parses under Node VM',()=>{
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 assert.ok(scripts.length>=3);
 for(const [i,s]of scripts.entries())
  assert.doesNotThrow(()=>new Script(s,{filename:'observatory-inline-'+i+'.js'}));
});

test('browser rejects cross-tenant frames even when a stream is configured',()=>{
 assert.match(html,/frame\.tenant_id!==cfg\.tenant_id/);
 assert.match(html,/!safe\(cfg\.tenant_id,80\)/);
});
