import { ensureSchema, requireSubject, getAccessState } from '../../lib/v57-db.js';
import { getCredential } from '../../lib/v57-vault.js';

const AGENTS={JARVIS:'You are Jarvis, concise, capable and user-controlled.',SERAPHIM:'You are Seraphim, the guardian and routing layer. Preserve user agency and safety.',FLASHTM8:'You are FlashTM8, the user companion persona. Be proactive but never invent completed actions.'};

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
  try{
    await ensureSchema();
    const subject=await requireSubject(req);
    if(!subject) return res.status(401).json({error:'AUTH_REQUIRED'});
    const access=await getAccessState(subject);
    if(access.locked) return res.status(402).json({error:'FREE_QUOTA_LOCKED',unlock_at:access.unlock_at});
    const agent=String(req.body?.agent||'JARVIS').toUpperCase();
    if(!AGENTS[agent]) return res.status(400).json({error:'AGENT_NOT_ALLOWED'});
    const provider=String(req.body?.provider||'OPENROUTER').toUpperCase();
    if(!['OPENROUTER','9ROUTER'].includes(provider)) return res.status(400).json({error:'PROVIDER_NOT_ALLOWED'});
    const model=String(req.body?.model||'').trim();
    const message=String(req.body?.message||'').trim();
    if(!model||!message) return res.status(400).json({error:'MODEL_AND_MESSAGE_REQUIRED'});
    const cred=await getCredential(subject,provider);
    if(!cred) return res.status(409).json({error:'PROVIDER_CREDENTIAL_NOT_CONFIGURED',provider});
    const base=provider==='OPENROUTER'?'https://openrouter.ai/api/v1':process.env.EIGHTX8_9ROUTER_BASE_URL;
    if(!base) return res.status(503).json({error:'ROUTER_BASE_NOT_CONFIGURED',provider});
    const r=await fetch(`${base.replace(/\/$/,'')}/chat/completions`,{method:'POST',headers:{Authorization:`Bearer ${cred.payload.api_key}`,'Content-Type':'application/json'},body:JSON.stringify({model,messages:[{role:'system',content:AGENTS[agent]},{role:'user',content:message}],stream:false}),signal:AbortSignal.timeout(45000)});
    const body=await r.json().catch(()=>({}));
    if(!r.ok) return res.status(502).json({error:'MODEL_PROVIDER_FAILED',provider,status:r.status});
    const text=body?.choices?.[0]?.message?.content;
    if(typeof text!=='string') return res.status(502).json({error:'MODEL_PROVIDER_RESPONSE_INVALID'});
    return res.status(200).json({schema:'8x8.agent.turn.v57',agent,provider,model,text,voice_hint:true,raw_secret_returned:false});
  }catch(e){return res.status(503).json({error:'AGENT_RUNTIME_UNAVAILABLE',detail:String(e?.message||e)})}
}
