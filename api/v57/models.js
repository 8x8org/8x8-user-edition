import { ensureSchema, requireSubject } from '../../lib/v57-db.js';
import { getCredential, setCredentialStatus } from '../../lib/v57-vault.js';

async function fetchModels(base,key){
  const r=await fetch(`${base.replace(/\/$/,'')}/models`,{headers:{Authorization:`Bearer ${key}`,'Accept':'application/json'},signal:AbortSignal.timeout(10000)});
  if(!r.ok) throw new Error(`MODEL_PROVIDER_HTTP_${r.status}`);
  const d=await r.json();
  const rows=Array.isArray(d?.data)?d.data:Array.isArray(d)?d:[];
  return rows.map(x=>({id:String(x?.id||x?.name||''),name:String(x?.name||x?.id||'')})).filter(x=>x.id);
}

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='GET') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
  try{
    await ensureSchema();
    const subject=await requireSubject(req);
    if(!subject) return res.status(401).json({error:'AUTH_REQUIRED'});
    const provider=String(req.query?.provider||'OPENROUTER').toUpperCase();
    if(!['OPENROUTER','9ROUTER'].includes(provider)) return res.status(400).json({error:'PROVIDER_NOT_ALLOWED'});
    const cred=await getCredential(subject,provider);
    if(!cred) return res.status(404).json({provider,status:'NOT_CONFIGURED',models:[]});
    const base=provider==='OPENROUTER'?'https://openrouter.ai/api/v1':cred.payload.base_url;
    if(!base) return res.status(503).json({provider,status:'ROUTER_BASE_NOT_CONFIGURED',models:[]});
    try{
      const models=await fetchModels(base,cred.payload.api_key);
      await setCredentialStatus(subject,provider,'VERIFIED');
      return res.status(200).json({provider,status:'VERIFIED',model_count:models.length,models,claim_500_plus:models.length>=500});
    }catch(e){
      await setCredentialStatus(subject,provider,'VERIFICATION_FAILED');
      return res.status(502).json({provider,status:'VERIFICATION_FAILED',models:[],detail:String(e?.message||e)});
    }
  }catch(e){return res.status(503).json({error:'MODEL_ROUTER_UNAVAILABLE',detail:String(e?.message||e)})}
}
