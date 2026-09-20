import { ensureSchema, requireSubject } from '../../lib/v57-db.js';
import { putCredential, listCredentialStatus } from '../../lib/v57-vault.js';

const ALLOWED = new Set(['OPENROUTER','9ROUTER']);

function validBaseUrl(v){
  if(!v) return null;
  try{
    const u=new URL(String(v));
    if(u.protocol!=='https:') return null;
    return u.toString().replace(/\/$/,'');
  }catch{return null}
}

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  try{
    await ensureSchema();
    const subject = await requireSubject(req);
    if(!subject) return res.status(401).json({error:'AUTH_REQUIRED'});
    if(req.method==='GET'){
      const providers=await listCredentialStatus(subject);
      return res.status(200).json({schema:'8x8.vault.v57',providers,raw_secrets_returned:false});
    }
    if(req.method!=='POST') return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
    const provider=String(req.body?.provider||'').toUpperCase();
    if(!ALLOWED.has(provider)) return res.status(400).json({error:'PROVIDER_NOT_ALLOWED'});
    const apiKey=String(req.body?.api_key||'').trim();
    if(apiKey.length<8) return res.status(400).json({error:'API_KEY_REQUIRED'});
    const payload={api_key:apiKey};
    if(provider==='9ROUTER'){
      const base=validBaseUrl(req.body?.base_url);
      if(!base) return res.status(400).json({error:'HTTPS_9ROUTER_BASE_URL_REQUIRED'});
      payload.base_url=base;
    }
    await putCredential(subject,provider,payload);
    return res.status(201).json({provider,status:'STORED_UNVERIFIED',raw_secret_returned:false});
  }catch(e){
    return res.status(503).json({error:'VAULT_AUTHORITY_UNAVAILABLE',detail:String(e?.message||e)});
  }
}
