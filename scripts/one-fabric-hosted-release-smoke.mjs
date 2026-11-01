#!/usr/bin/env node
// ©️8x8 One Fabric User Edition V50 — bounded hosted acceptance.
// Source-only review candidate, derived from PR #201 exact-head blob 2e2a577e... .
// Independent route results prevent a failure at '/' from hiding failures elsewhere.
// No credentials, cookies, writes, deploys, device actions, or implicit redirects.
import {createHash} from 'node:crypto';

const profiles=[
  ['/', 'text/html', /8x8 OS|Three Gates|One Fabric/i],
  ['/studio','text/html',/8x8 Studio.*Media Inspector/i],
  ['/agents','text/html',/Agent Room.*Public Preview|8x8.*Agent Room/i],
  ['/icon.svg','image/svg+xml',/<svg\b/i],
  ['/manifest.webmanifest','application/manifest+json', null],
  ['/sw.js','application/javascript',/addEventListener|self\./]
];
const MAX_BYTES=1048576;

function expectedOrigin(base){
  let origin;
  try { origin=new URL(base); } catch { throw Error('EXPECTED_BASE_ORIGIN'); }
  if(!['http:','https:'].includes(origin.protocol)||origin.pathname!=='/'||origin.search||origin.hash||origin.username||origin.password)
    throw Error('EXPECTED_BASE_ORIGIN');
  return origin;
}
function safeError(e,path){
  const msg=String(e?.message||'');
  // An error message can contain attacker-controlled headers/URLs. Emit only an allow-listed code.
  const patterns=['UNEXPECTED_HTTP','AUTO_FOLLOWED_REDIRECT','RESPONSE_URL_MISMATCH','CROSS_ORIGIN_REDIRECT',
    'WRONG_MEDIA_TYPE','ATTACHMENT_DISPOSITION','OVERSIZED','EMPTY_OR_OVERSIZED','WRONG_PAGE',
    'BAD_MANIFEST_JSON','MANIFEST_SHORTCUT_MISSING'];
  const prefix=patterns.find(p=>msg.startsWith(p+'_'));
  return prefix ? prefix+'_'+path : 'REQUEST_OR_PARSE_FAILED_'+path;
}

/** Non-mutating, six-route diagnostic. Never treats a partial result as production acceptance. */
export async function audit(base,request=fetch){
  const origin=expectedOrigin(base);
  const checks=[];
  const failures=[];
  for(const [path,expectedType,expectedContent] of profiles){
    const target=new URL(path,origin);
    const check={path,verdict:'UNKNOWN'};
    try {
      const res=await request(target.href,{redirect:'manual',cache:'no-store',signal:AbortSignal.timeout(8000)});
      check.status=res.status;
      if(res.status!==200) throw Error('UNEXPECTED_HTTP_'+path+'_'+res.status);
      // Check both the final URL and redirected flag: a client wrapper may ignore redirect:'manual'.
      if(res.redirected) throw Error('AUTO_FOLLOWED_REDIRECT_'+path);
      const resolved=new URL(res.url||target.href);
      if(resolved.origin!==origin.origin) throw Error('CROSS_ORIGIN_REDIRECT_'+path);
      if(resolved.href!==target.href) throw Error('RESPONSE_URL_MISMATCH_'+path);
      const mime=res.headers.get('content-type')||'';
      check.media_type=mime;
      const disposition=res.headers.get('content-disposition')||'';
      if(/\battachment\b/i.test(disposition)) throw Error('ATTACHMENT_DISPOSITION_'+path);
      const normalizedMime=mime.split(';',1)[0].trim().toLowerCase();
      const acceptedTypes=path==='/manifest.webmanifest' ? ['application/manifest+json','application/json'] :
        path==='/sw.js' ? ['application/javascript','text/javascript'] : [expectedType];
      if(!acceptedTypes.includes(normalizedMime)) throw Error('WRONG_MEDIA_TYPE_'+path+'_'+mime);
      const declared=Number(res.headers.get('content-length')||'0');
      if(!Number.isFinite(declared)||declared<0||declared>MAX_BYTES) throw Error('OVERSIZED_'+path);
      const bytes=Buffer.from(await res.arrayBuffer());
      if(!bytes.length||bytes.length>MAX_BYTES) throw Error('EMPTY_OR_OVERSIZED_'+path);
      check.bytes=bytes.length;
      check.sha256=createHash('sha256').update(bytes).digest('hex');
      const body=bytes.toString('utf8');
      if(expectedContent&&!expectedContent.test(body)) throw Error('WRONG_PAGE_'+path);
      if(path==='/manifest.webmanifest'){
        let doc;try{doc=JSON.parse(body)}catch{throw Error('BAD_MANIFEST_JSON_'+path)}
        if(!Array.isArray(doc.shortcuts)||!['/agents','/studio'].every(p=>doc.shortcuts.some(x=>x.url===p)))
          throw Error('MANIFEST_SHORTCUT_MISSING_'+path);
      }
      check.verdict='PASS';
    } catch(e){
      check.verdict='FAIL';
      check.code=safeError(e,path);
      failures.push({path,code:check.code});
    }
    checks.push(check);
  }
  // Identify identical HTML fallback content even when a marker check already failed.
  const seen=new Map();
  for(const check of checks){
    if(!['/', '/studio','/agents'].includes(check.path)||!check.sha256) continue;
    if(seen.has(check.sha256)){
      const code='FALLBACK_SAME_BODY_'+seen.get(check.sha256)+'_'+check.path;
      failures.push({path:check.path,code});
      check.verdict='FAIL';
      check.fallback_duplicate_of=seen.get(check.sha256);
    } else seen.set(check.sha256,check.path);
  }
  return {
    state:failures.length?'FUTURE_GATED':'PRESENT_PROVEN',
    scope:'hosted public assets only',
    origin:origin.origin,
    checks,
    failures
  };
}

/** Preserve PR #201's fail-closed smoke() API and successful check shape. */
export async function smoke(base,request=fetch){
  const result=await audit(base,request);
  if(result.failures.length) throw Error(result.failures[0].code);
  return {state:result.state,scope:result.scope,origin:result.origin,
    checks:result.checks.map(({path,sha256,media_type,bytes})=>({path,sha256,media_type,bytes}))};
}

if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
  if(!process.argv[2]){
    console.error('Usage: node scripts/one-fabric-hosted-release-smoke.mjs https://HOST/');process.exitCode=2;
  } else {
    try {
      const result=await audit(process.argv[2]);
      console.log(JSON.stringify(result,null,2));
      if(result.failures.length) process.exitCode=1;
    } catch(e){
      console.error('HOSTED_USER_EDITION_GATE=FAIL',e.message);process.exitCode=1;
    }
  }
}
