import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,sign} from 'node:crypto';
import {SCHEMA,eventHash} from '../server/mission-cinema-event-trust-v1.mjs';
import {SignedCinemaObservationChannel,serializeVerifiedSseFrame,FRAME_SCHEMA} from '../server/mission-cinema-observation-channel-v1.mjs';
const keypair=generateKeyPairSync('ed25519');
const trust={'8x8.test.signer':{'unit-01':keypair.publicKey.export({format:'jwk'})}};
const now=Date.parse('2026-10-18T23:20:00.000Z');
const mkEvent=(seq=1,prev='GENESIS',overrides={})=>{
 const event={event_id:'test-'+seq,source_id:'8x8.unit',observed_utc:'2026-10-18T23:19:50.000Z',
 sequence:seq,event_type:'TEST_RESULT',evidence_class:'RUNTIME_RECEIPT',
 receipt_ref:'',sanitized_summary:'Observed isolated test result',previous_hash:prev,hash:'',...overrides};
 event.hash=eventHash(event);return event;
};
const mkBatch=(events,tenant='tenant_001')=>{
 const unsigned={schema:SCHEMA,issuer:'8x8.test.signer',key_id:'unit-01',tenant_id:tenant,events};
 return {...unsigned,signature:sign(null,Buffer.from(JSON.stringify(unsigned)),keypair.privateKey).toString('base64url')};
};
function makeChannel(overrides={}){
 let stopped=false;
 return new SignedCinemaObservationChannel({
  verifyReader:()=>({authenticated:true,tenantId:'tenant_001',scopes:['8x8.events.read']}),
  ownerPreempted:()=>stopped,now:()=>now,trust,...overrides
 });
}
test('signed batch produces source-verified frame, not live claim',()=>{
 const c=makeChannel(),f=c.accept(mkBatch([mkEvent()]));
 assert.equal(f.schema,FRAME_SCHEMA);assert.equal(f.live_stream_connected,false);
 assert.equal(f.execution_authorized,false);assert.equal(f.events.length,1);
 assert.equal(f.events[0].summary,'Observed isolated test result');
 assert.equal(c.checkpoint().lastSequence,1);
});
test('SSE framing contains signed sanitized outcome only',()=>{
 const f=makeChannel().accept(mkBatch([mkEvent()]));
 const s=serializeVerifiedSseFrame(f);
 assert.match(s,/event: eightx8.verified_record/);assert.match(s,/id: 1/);
 assert.ok(!s.includes('secret'));assert.ok(!s.includes('token'));
 assert.deepEqual(JSON.parse(s.split('data: ')[1]).events[0].sequence,1);
});
test('arbitrary client-constructed frames are rejected',()=>{
 assert.throws(()=>serializeVerifiedSseFrame({schema:FRAME_SCHEMA,lastSequence:1}),/ONLY_SIGNED/);
});
test('missing backend verifier denied',()=>{
 assert.throws(()=>new SignedCinemaObservationChannel({trust,now:()=>now,ownerPreempted:()=>false}),/TRUSTED_BACKEND/);
});
test('missing Gate2 authentication denied',()=>{
 const c=makeChannel({verifyReader:()=>({authenticated:false,tenantId:'tenant_001',scopes:['8x8.events.read']})});
 assert.throws(()=>c.accept(mkBatch([mkEvent()])),/GATE2/);
});
test('missing read permission denied',()=>{
 const c=makeChannel({verifyReader:()=>({authenticated:true,tenantId:'tenant_001',scopes:['8x8.public.read']})});
 assert.throws(()=>c.accept(mkBatch([mkEvent()])),/GATE2/);
});
test('wrong tenant denied',()=>{
 const c=makeChannel();assert.throws(()=>c.accept(mkBatch([mkEvent()],'other_tenant')),/TENANT/);
});
test('owner stop denies signed event projection',()=>{
 const c=makeChannel({ownerPreempted:()=>true});
 assert.throws(()=>c.accept(mkBatch([mkEvent()])),/OWNER_STOP/);
});
test('unknown owner state fails closed',()=>{
 const c=makeChannel({ownerPreempted:()=>undefined});
 assert.throws(()=>c.accept(mkBatch([mkEvent()])),/OWNER_STOP/);
});
test('missing signer enrollment denies',()=>{
 const c=makeChannel({trust:{}});
 assert.throws(()=>c.accept(mkBatch([mkEvent()])),/SIGNER_NOT_ENROLLED/);
});
test('invalid signature denies and preserves checkpoint',()=>{
 const c=makeChannel(),b=mkBatch([mkEvent()]);b.events[0].sanitized_summary='Modified';
 assert.throws(()=>c.accept(b),/SIGNATURE/);
 assert.deepEqual(c.checkpoint(),{lastSequence:0,lastHash:'GENESIS'});
});
test('gap denies and preserves checkpoint',()=>{
 const c=makeChannel();
 assert.throws(()=>c.accept(mkBatch([mkEvent(2)])),/EVENT_SEQUENCE_GAP/);
 assert.equal(c.checkpoint().lastSequence,0);
});
test('replay denies and preserves accepted checkpoint',()=>{
 const c=makeChannel(),b=mkBatch([mkEvent()]);c.accept(b);
 assert.throws(()=>c.accept(b),/EVENT_SEQUENCE_GAP/);assert.equal(c.checkpoint().lastSequence,1);
});
test('successive batches reconcile checkpoint and hash chain',()=>{
 const c=makeChannel(),first=mkEvent(),second=mkEvent(2,first.hash);
 c.accept(mkBatch([first]));const f=c.accept(mkBatch([second]));
 assert.equal(f.lastSequence,2);assert.equal(c.checkpoint().lastHash,second.hash);
});
test('secret-bearing signed fields denied even from enrolled signer',()=>{
 const c=makeChannel(),event=mkEvent(1,'GENESIS',{sanitized_summary:'Bearer abc.def.ghi'});
 assert.throws(()=>c.accept(mkBatch([event])),/UNSAFE_SUMMARY/);
});
test('private internal reasoning cannot be mirrored',()=>{
 const c=makeChannel(),event=mkEvent(1,'GENESIS',{sanitized_summary:'Hidden reasoning transcript'});
 assert.throws(()=>c.accept(mkBatch([event])),/UNSAFE_SUMMARY/);
});
test('unapproved raw arguments cannot pass',()=>{
 const c=makeChannel(),event=mkEvent(1,'GENESIS',{raw_tool_arguments:'injected'});
 assert.throws(()=>c.accept(mkBatch([event])),/UNAPPROVED_EVENT_FIELD/);
});
test('stale runtime event denied',()=>{
 const c=makeChannel(),event=mkEvent(1,'GENESIS',{observed_utc:'2026-10-17T23:19:50.000Z'});
 assert.throws(()=>c.accept(mkBatch([event])),/STALE_RUNTIME_EVENT/);
});
test('batch with poisoned second event is atomic',()=>{
 const c=makeChannel(),e1=mkEvent(),e2=mkEvent(2,e1.hash,{sanitized_summary:'API_KEY copied'});
 assert.throws(()=>c.accept(mkBatch([e1,e2])),/UNSAFE_SUMMARY/);
 assert.equal(c.checkpoint().lastSequence,0);
});
test('no external listener or signing material comes from module',()=>{
 assert.equal(typeof SignedCinemaObservationChannel,'function');
 assert.equal(Object.getOwnPropertyNames(SignedCinemaObservationChannel.prototype).includes('listen'),false);
});
