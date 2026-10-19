import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,sign} from 'node:crypto';
import {SCHEMA,eventHash,verifyMissionCinemaBatch} from '../server/mission-cinema-event-trust-v1.mjs';
const {publicKey,privateKey}=generateKeyPairSync('ed25519');
const trust={'8x8.test.runtime':{'unit-signer':publicKey.export({format:'jwk'})}};
const now=Date.parse('2026-10-18T14:39:00.000Z');
const mkEvent=(o={})=>{const e={
 event_id:'e001',source_id:'test.agent',observed_utc:'2026-10-18T14:38:45.000Z',sequence:1,
 event_type:'TEST_RESULT',evidence_class:'RUNTIME_RECEIPT',receipt_ref:'',sanitized_summary:'Isolated test completed',
 previous_hash:'GENESIS',hash:'',...o
 };e.hash=eventHash(e);return e};
const mkBatch=(events=[mkEvent()],overrides={})=>{
 const data={schema:SCHEMA,issuer:'8x8.test.runtime',key_id:'unit-signer',tenant_id:'tenant-demo-001',events,...overrides};
 const signature=sign(null,Buffer.from(JSON.stringify(data)),privateKey).toString('base64url');
 return {...data,signature};
};
const verify=(batch,opts={})=>verifyMissionCinemaBatch(batch,{tenantId:'tenant-demo-001',trust,nowMs:now,...opts});
const denied=(batch,error,opts={})=>assert.throws(()=>verify(batch,opts),new RegExp(error));
test('genuine signed event accepted but not labeled live stream',()=>{
 const v=verify(mkBatch());
 assert.equal(v.verified,true);assert.equal(v.events.length,1);
 assert.equal(v.live_stream_connected,false);assert.equal(v.actions_authorized,false);
});
test('untrusted signer is denied',()=>denied(mkBatch([mkEvent()],{issuer:'other.issuer'}),'SIGNER_NOT_ENROLLED'));
test('wrong tenant is denied',()=>denied(mkBatch(), 'TENANT_NOT_AUTHORIZED',{tenantId:'tenant-other'}));
test('signature tampering denied',()=>{
 const b=mkBatch();b.events[0].sanitized_summary='Tampered';denied(b,'SIGNATURE_NOT_VERIFIED');
});
test('missing event signature denied',()=>denied({...mkBatch(),signature:''},'BAD_SIGNATURE_FORMAT'));
test('extra sensitive payload field denied despite valid signature',()=>{
 const e=mkEvent({raw_tool_arguments:'x'});denied(mkBatch([e]),'UNAPPROVED_EVENT_FIELD');
});
test('Bearer tokens in summary denied',()=>{
 const e=mkEvent({sanitized_summary:'Bearer abc.def.xyz'});denied(mkBatch([e]),'UNSAFE_SUMMARY');
});
test('hidden reasoning in summary denied',()=>{
 const e=mkEvent({sanitized_summary:'private chain of thought recorded'});denied(mkBatch([e]),'UNSAFE_SUMMARY');
});
test('mismatched hash chain rejected',()=>denied(mkBatch([mkEvent({previous_hash:'f'.repeat(64)})]),'BROKEN_HASH_CHAIN'));
test('gaps and replay denied',()=>denied(mkBatch([mkEvent({sequence:2})]),'EVENT_SEQUENCE_GAP_OR_REPLAY'));
test('stale runtime evidence denied',()=>{
 const e=mkEvent({observed_utc:'2026-10-17T14:38:45.000Z'});denied(mkBatch([e]),'STALE_RUNTIME_EVENT');
});
test('future timestamp denied',()=>{
 const e=mkEvent({observed_utc:'2026-10-18T14:45:00.000Z'});denied(mkBatch([e]),'FUTURE_EVENT');
});
test('unknown event type denied',()=>{
 const e=mkEvent({event_type:'UNRESTRICTED_DEVICE_CONTROL'});denied(mkBatch([e]),'UNKNOWN_EVENT_TYPE');
});
test('GitHub provenance URL allowed, URL containing tokens denied',()=>{
 const e=mkEvent({receipt_ref:'https://github.com/8x8org/8x8-user-edition/pull/200'});
 assert.equal(verify(mkBatch([e])).verified,true);
 const bad=mkEvent({receipt_ref:'https://evil.example.com/token'});
 denied(mkBatch([bad]),'UNSAFE_RECEIPT_REF');
});
test('two signed ordered and chained events pass',()=>{
 const first=mkEvent();
 const second=mkEvent({event_id:'e002',sequence:2,previous_hash:first.hash});
 const batch=mkBatch([first,second]);
 assert.equal(verify(batch).lastSequence,2);
});
test('wrong key and forged signature fail',()=>{
 const other=generateKeyPairSync('ed25519');
 const d={schema:SCHEMA,issuer:'8x8.test.runtime',key_id:'unit-signer',tenant_id:'tenant-demo-001',events:[mkEvent()]};
 const b={...d,signature:sign(null,Buffer.from(JSON.stringify(d)),other.privateKey).toString('base64url')};
 denied(b,'SIGNATURE_NOT_VERIFIED');
});
test('verified checkpoint enforces monotonic continuation',()=>{
 const a=mkEvent({event_id:'e003',sequence:3,previous_hash:'a'.repeat(64)});
 assert.equal(verify(mkBatch([a]),{lastSequence:2,lastHash:'a'.repeat(64)}).lastSequence,3);
});

test('signed operation lifecycle milestones accepted but do not grant execution',()=>{
 for(const phase of ['OPERATION_STARTED','OPERATION_PROGRESS','OPERATION_SUCCEEDED','OPERATION_FAILED','OPERATION_BLOCKED']){
  const v=verify(mkBatch([mkEvent({event_type:phase})]));
  assert.equal(v.events[0].event_type,phase);
  assert.equal(v.actions_authorized,false);
  assert.equal(v.live_stream_connected,false);
 }
});
test('operation result cannot include hidden reasoning or credentials',()=>{
 for(const summary of ['hidden reasoning transcript','Bearer abc.def.ghi','api_key pasted']){
  denied(mkBatch([mkEvent({event_type:'OPERATION_SUCCEEDED',sanitized_summary:summary})]),'UNSAFE_SUMMARY');
 }
});

test('signed in-progress work is visible without indicating completion or a provider effect',()=>{
 const v=verify(mkBatch([mkEvent({event_type:'OPERATION_PROGRESS',
   sanitized_summary:'Source files reviewed; isolated regression checks running'})]));
 assert.equal(v.verified,true);
 assert.equal(v.events[0].event_type,'OPERATION_PROGRESS');
 assert.equal(v.actions_authorized,false);
 assert.equal(v.live_stream_connected,false);
});
test('in-progress percentage is denied without an independently validated denominator',()=>{
 const e=mkEvent({event_type:'OPERATION_PROGRESS',
  sanitized_summary:'Project 100% complete'});
 denied(mkBatch([e]),'UNATTESTED_PROGRESS_PERCENTAGE');
});
