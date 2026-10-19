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

test('Mission Cinema uses one existing Observatory, with micro/cinema director views',()=>{
 for(const id of ['mc-director','mc-mode-micro','mc-mode-cinema','mc-evidence-filter','mc-scene-title','mc-detail-event','mc-detail-proof','mc-detail-receipt'])
  assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(html,/mission_cinema/);
});
test('director presents selected signed-source provenance without untrusted HTML insertion',()=>{
 assert.match(html,/get\("mc-detail-source"\)\.textContent/);
 assert.match(html,/get\("mc-detail-time"\)\.textContent/);
 assert.match(html,/get\("mc-detail-hash"\)\.textContent/);
 assert.match(html,/receiptPattern\.test\(ref\)/);
 assert.match(html,/link\.removeAttribute\("href"\)/);
 assert.doesNotMatch(html,/innerHTML\s*=\s*e\.summary/);
});
test('cinema mode is presentation only and cannot forge effect confirmation',()=>{
 assert.match(html,/0 effect attestations/);
 assert.match(html,/RECORDED_REPLAY_NOT_LIVE/);
 assert.match(html,/new MutationObserver\(refresh\)\.observe\(feed/);
 assert.match(html,/directorMode=next/);
});
test('live records project observed time and receipt reference without new tool authority',()=>{
 assert.match(html,/li\.dataset\.receiptRef/);
 assert.match(html,/li\.dataset\.observedUtc/);
 assert.match(html,/SIGNED RECORDS RECEIVED · LIVE AUTH NOT ATTESTED/);
});
test('all five inline scripts compile after director integration',()=>{
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 assert.ok(scripts.length>=4);
 for(const [i,s]of scripts.entries())assert.doesNotThrow(()=>new Script(s,{filename:'director-'+i+'.js'}));
});

test('director interaction filters source results and opens only allowlisted evidence URLs',()=>{
 const byId={};
 class El {
  constructor(id){this.id=id;this.dataset={};this.listeners={};this.attrs={};this.hidden=true;this.value='ALL';this.title='';}
  addEventListener(type,fn){this.listeners[type]=fn;}
  setAttribute(k,v){this.attrs[k]=v;}
  removeAttribute(k){delete this.attrs[k];if(k==='href')delete this.href;}
  querySelector(s){return s==='strong'?{textContent:this.title}:null;}
  querySelectorAll(){return this.items||[];}
  contains(el){return (this.items||[]).includes(el);}
 }
 for(const id of ['mission-cinema','mc-events','mc-evidence-filter','mc-mode-micro','mc-mode-cinema','mc-detail-receipt','mc-visible-count','mc-evidence-type','mc-confirmed-effects','mc-detail-event','mc-detail-source','mc-detail-time','mc-detail-proof','mc-detail-sequence','mc-detail-hash','mc-scene-title','mc-scene-caption'])byId[id]=new El(id);
 const replay=new El('replay');
 replay.dataset={sourceId:'source-only',eventType:'REPLAY',evidenceClass:'RECORDED_REPLAY_NOT_LIVE'};
 replay.title='Recorded source milestone';
 const record=new El('signed');
 record.dataset={sourceId:'repo-check',eventType:'SOURCE_COMMIT',evidenceClass:'SOURCE_VERIFIED',sequence:'1',observedUtc:'2026-10-18T13:00:00.000Z',eventHash:'a'.repeat(64),receiptRef:'https://github.com/8x8org/8x8-user-edition/commit/abc123'};
 record.title='Source commit verified';
 byId['mc-events'].items=[replay,record];
 let observer=null;
 class Observer{constructor(cb){observer=cb;}observe(){}}
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 new Script(scripts.at(-1)).runInNewContext({document:{getElementById:id=>byId[id]},MutationObserver:Observer});
 assert.equal(byId['mc-visible-count'].textContent,'2');
 assert.equal(byId['mc-confirmed-effects'].textContent,'0 effect attestations');
 byId['mc-evidence-filter'].value='BUILD';byId['mc-evidence-filter'].listeners.change();
 assert.equal(replay.dataset.hidden,'true');
 assert.equal(record.dataset.hidden,'false');
 assert.equal(byId['mc-detail-source'].textContent,'repo-check');
 assert.equal(byId['mc-detail-receipt'].href,'https://github.com/8x8org/8x8-user-edition/commit/abc123');
 byId['mc-mode-cinema'].listeners.click();
 assert.equal(byId['mission-cinema'].dataset.directorMode,'cinema');
 record.dataset.receiptRef='javascript:alert(1)';
 byId['mc-mode-micro'].listeners.click();
 assert.equal(byId['mc-detail-receipt'].hidden,true);
 assert.equal(byId['mc-detail-receipt'].href,undefined);
 assert.equal(typeof observer,'function');
});

test('operation lifecycle includes four phases but cannot attest a real-world effect',()=>{
 assert.match(html,/value="LIFECYCLE"/);
 for(const t of ['OPERATION_STARTED','OPERATION_PROGRESS','OPERATION_SUCCEEDED','OPERATION_FAILED','OPERATION_BLOCKED'])assert.match(html,new RegExp(t));
 assert.match(html,/id="mc-lifecycle-count"/);
 assert.match(html,/id="mc-detail-phase"/);
 assert.match(html,/external effect must be confirmed separately/);
 assert.match(html,/0 effect attestations/);
 assert.doesNotMatch(html,/innerHTML\s*=\s*e\.summary/);
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 for(const code of scripts)assert.doesNotThrow(()=>new Script(code));
});

test('progress phase appears in micro/cinema inspector without false completion',()=>{
 assert.match(html,/OPERATION_PROGRESS:"IN PROGRESS/);
 assert.match(html,/completion not attested/);
 assert.match(html,/Started · progress · succeeded/);
 assert.match(html,/0 effect attestations/);
 assert.doesNotMatch(html,/__EIGHTX8_AUTHORIZED_OBSERVATORY__\s*=/);
});
