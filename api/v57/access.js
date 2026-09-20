import { ensureSchema, requireSubject, getAccessState } from '../../lib/v57-db.js';

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='GET') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
  try{
    await ensureSchema();
    const subject=await requireSubject(req);
    if(!subject) return res.status(401).json({schema:'8x8.access.v57',state:'AUTH_REQUIRED',truth:'SERVER_AUTHORITATIVE'});
    const state=await getAccessState(subject);
    return res.status(200).json({schema:'8x8.access.v57',canonical_root:'fabric://8x8/core',authority:'SERVER',...state,truth:'SERVER_AUTHORITATIVE'});
  }catch(e){
    return res.status(503).json({schema:'8x8.access.v57',state:'AUTHORITY_UNAVAILABLE',truth:'FAIL_CLOSED',detail:String(e?.message||e)});
  }
}
