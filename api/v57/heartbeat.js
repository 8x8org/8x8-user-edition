import { ensureSchema, requireSubject, heartbeat } from '../../lib/v57-db.js';

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
  try{
    await ensureSchema();
    const subject=await requireSubject(req);
    if(!subject) return res.status(401).json({state:'AUTH_REQUIRED'});
    const carrier=String(req.body?.carrier||'web').slice(0,24);
    const state=await heartbeat(subject,carrier);
    return res.status(200).json({schema:'8x8.heartbeat.v57',...state,truth:'SERVER_AUTHORITATIVE'});
  }catch(e){return res.status(503).json({state:'AUTHORITY_UNAVAILABLE',truth:'FAIL_CLOSED',detail:String(e?.message||e)})}
}
