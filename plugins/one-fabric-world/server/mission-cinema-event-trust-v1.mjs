// ©8x8 One Fabric Mission Cinema — signed, public-safe event verification.
// Pure validation library. NO trusted keys enrolled, network listener or
// owner/private event access installed by importing this module.
import { createHash, createPublicKey, verify } from 'node:crypto';
export const SCHEMA='8x8.mission_cinema.signed_event_batch.v1';
export const EVENT_TYPES=Object.freeze([
  'RESEARCH_SOURCE','TOOL_RESULT','SOURCE_COMMIT','TEST_RESULT',
  'DEPLOYMENT_RESULT','PROVIDER_CANARY','MEDIA_RENDER',
  'DEVICE_CONTROL_STATUS','APPROVAL_STATUS','INCIDENT'
]);
const hex64=/^[a-f0-9]{64}$/;
const ident=/^[a-zA-Z0-9_.:-]{2,100}$/;
const forbidden=/bearer\s+[a-z0-9_.-]+|api[_ -]?key|secret|password|passphrase|private[_ -]?key|seed phrase|mnemonic|access[_ -]?token|authorization\s*:|owner[_ -]?route|chain[_ -]?of[_ -]?thought|hidden reasoning/i;
const badChars=/[\x00-\x1f\x7f<>]/;
const exact=(obj,required)=>obj&&typeof obj==='object'&&!Array.isArray(obj)&&
  Object.keys(obj).length===required.length&&required.every(key=>Object.hasOwn(obj,key));
const EVENT_FIELDS=['event_id','source_id','observed_utc','sequence','event_type','evidence_class','receipt_ref','sanitized_summary','previous_hash','hash'];
const BATCH_FIELDS=['schema','issuer','key_id','tenant_id','events','signature'];
const CONTENT_FIELDS=EVENT_FIELDS.filter(x=>x!=='hash');
const canonical=value=>JSON.stringify(value); // Source-specified canonical field ordering below.
function content(e){return Object.fromEntries(CONTENT_FIELDS.map(k=>[k,e[k]]))}
export function eventHash(event){
  return createHash('sha256').update(canonical(content(event)),'utf8').digest('hex');
}
function str(s,max=160){
 return typeof s==='string'&&s.length>0&&s.length<=max&&!badChars.test(s)&&!forbidden.test(s);
}
function assert(x,message){if(!x)throw new Error(message)}
export function verifyMissionCinemaBatch(batch,options={}){
 const {tenantId,trust,nowMs=Date.now(),lastSequence=0,lastHash='GENESIS'}=options;
 assert(exact(batch,BATCH_FIELDS),'INVALID_BATCH_SHAPE');
 assert(batch.schema===SCHEMA,'INVALID_BATCH_SCHEMA');
 assert(str(tenantId,96)&&batch.tenant_id===tenantId,'TENANT_NOT_AUTHORIZED');
 assert(ident.test(batch.issuer)&&ident.test(batch.key_id),'INVALID_ISSUER');
 assert(Array.isArray(batch.events)&&batch.events.length>0&&batch.events.length<=80,'INVALID_EVENT_COUNT');
 assert(Number.isSafeInteger(lastSequence)&&lastSequence>=0,'BAD_SEQUENCE_CHECKPOINT');
 assert(lastHash==='GENESIS'||hex64.test(lastHash),'BAD_HASH_CHECKPOINT');
 assert(typeof trust==='object'&&trust!==null,'NO_TRUSTED_SIGNER');
 const jwk=trust[batch.issuer]?.[batch.key_id];
 assert(jwk&&typeof jwk==='object'&&jwk.kty==='OKP'&&jwk.crv==='Ed25519','SIGNER_NOT_ENROLLED');
 assert(typeof batch.signature==='string'&&/^[A-Za-z0-9_-]{60,140}$/.test(batch.signature),'BAD_SIGNATURE_FORMAT');
 const signedData=Object.fromEntries(BATCH_FIELDS.filter(k=>k!=='signature').map(k=>[k,batch[k]]));
 let ok=false;
 try{
  const key=createPublicKey({key:jwk,format:'jwk'});
  ok=verify(null,Buffer.from(canonical(signedData),'utf8'),key,Buffer.from(batch.signature,'base64url'));
 }catch{ok=false}
 assert(ok,'SIGNATURE_NOT_VERIFIED');
 const out=[];let seq=lastSequence,prev=lastHash;
 for(const e of batch.events){
   assert(exact(e,EVENT_FIELDS),'UNAPPROVED_EVENT_FIELD');
   assert(str(e.event_id,80)&&str(e.source_id,80)&&ident.test(e.source_id),'INVALID_EVENT_IDENTITIES');
   assert(str(e.sanitized_summary,240),'UNSAFE_SUMMARY');
   assert(EVENT_TYPES.includes(e.event_type),'UNKNOWN_EVENT_TYPE');
   assert(['SOURCE_VERIFIED','RUNTIME_RECEIPT'].includes(e.evidence_class),'BAD_EVIDENCE_CLASS');
   assert(typeof e.receipt_ref==='string'&&
     (e.receipt_ref===''||(/^https:\/\/github\.com\/[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+\/(commit|pull|blob)\/[A-Za-z0-9._\/-]+$/.test(e.receipt_ref)
         &&!forbidden.test(e.receipt_ref))),'UNSAFE_RECEIPT_REF');
   assert(Number.isSafeInteger(e.sequence)&&e.sequence===seq+1,'EVENT_SEQUENCE_GAP_OR_REPLAY');
   assert(e.previous_hash===prev,'BROKEN_HASH_CHAIN');
   assert(hex64.test(e.hash)&&eventHash(e)===e.hash,'EVENT_HASH_MISMATCH');
   const observed=Date.parse(e.observed_utc);
   assert(Number.isFinite(observed)&&new Date(observed).toISOString()===e.observed_utc,'INVALID_EVENT_TIME');
   assert(observed<=nowMs+30000,'FUTURE_EVENT');
   assert(e.evidence_class!=='RUNTIME_RECEIPT'||observed>=nowMs-120000,'STALE_RUNTIME_EVENT');
   seq=e.sequence;prev=e.hash;out.push(Object.freeze({...e}));
 }
 return Object.freeze({
  verified:true,classification:'SIGNED_EVENTS_VERIFIED_NOT_LIVE_TRANSPORT',
  source:batch.issuer,tenant_id:tenantId,lastSequence:seq,lastHash:prev,
  live_stream_connected:false,actions_authorized:false,events:Object.freeze(out)
 });
}
