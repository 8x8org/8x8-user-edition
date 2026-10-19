// ©8x8 Mission Cinema — verified, tenant-scoped source-to-viewer event projection.
// This is a pure, source-only bridge; it does NOT enroll signers, establish
// Gate 2 sessions, open a network port, or authorize effects.
import {verifyMissionCinemaBatch} from './mission-cinema-event-trust-v1.mjs';
const BRAND=Symbol('8x8.source_verified_event_frame');
const TENANT=/^[a-z0-9][a-z0-9_-]{2,79}$/;
const SCOPE='8x8.events.read';
export const FRAME_SCHEMA='8x8.mission_cinema.verified_observation_frame.v1';
function requireTrustContext(ctx){
 // verifyReader must be an injected, trusted, server-side authentication
 // callback; NEVER a model argument, client JSON claim or browser assertion.
 if(!ctx||typeof ctx.verifyReader!=='function'||typeof ctx.ownerPreempted!=='function'
    ||typeof ctx.now!=='function'||!ctx.trust||typeof ctx.trust!=='object')
   throw Error('TRUSTED_BACKEND_CONTEXT_REQUIRED');
 return ctx;
}
export class SignedCinemaObservationChannel{
 #ctx;#sequence=0;#hash='GENESIS';
 constructor(ctx){this.#ctx=requireTrustContext(ctx);}
 checkpoint(){return Object.freeze({lastSequence:this.#sequence,lastHash:this.#hash});}
 accept(batch){
  const gate=this.#ctx.verifyReader();
  if(!gate||gate.authenticated!==true||!TENANT.test(gate.tenantId||'')
     ||!Array.isArray(gate.scopes)||!gate.scopes.includes(SCOPE))
    throw Error('GATE2_TENANT_SCOPE_REQUIRED');
  // Paused, stopped, unknown and exceptions fail closed. Historical local
  // replay remains available through the separate offline viewer.
  if(this.#ctx.ownerPreempted()!==false)throw Error('OWNER_STOP_OR_PAUSE');
  const verified=verifyMissionCinemaBatch(batch,{
   tenantId:gate.tenantId,trust:this.#ctx.trust,nowMs:this.#ctx.now(),
   lastSequence:this.#sequence,lastHash:this.#hash
  });
  // No state change before the entire signature/chain is validated.
  const projected=verified.events.map(e=>Object.freeze({
   event_id:e.event_id,sequence:e.sequence,source_id:e.source_id,
   observed_utc:e.observed_utc,event_type:e.event_type,
   evidence_class:e.evidence_class,receipt_ref:e.receipt_ref,
   summary:e.sanitized_summary,hash:e.hash
  }));
  this.#sequence=verified.lastSequence;this.#hash=verified.lastHash;
  const frame={
   schema:FRAME_SCHEMA,tenant_id:gate.tenantId,classification:
    'SIGNED_EVENTS_VERIFIED_TRANSPORT_NOT_PROVEN',
   live_stream_connected:false,execution_authorized:false,
   lastSequence:this.#sequence,lastHash:this.#hash,events:projected
  };
  Object.defineProperty(frame,BRAND,{value:true,enumerable:false});
  return Object.freeze(frame);
 }
}
// Framing helper for a FUTURE authenticated, bounded, same-origin SSE route.
// It has no listener; caller must implement Gate2 session + transport auth.
export function serializeVerifiedSseFrame(frame){
 if(!frame||frame[BRAND]!==true||frame.live_stream_connected!==false)
  throw Error('ONLY_SIGNED_VERIFIED_FRAME_ALLOWED');
 const out=JSON.stringify(frame);
 if(out.length>65536||/[\r\n]/.test(out))throw Error('UNSAFE_EVENT_FRAME');
 return 'id: '+frame.lastSequence+'\nevent: eightx8.verified_record\ndata: '+out+'\n\n';
}
