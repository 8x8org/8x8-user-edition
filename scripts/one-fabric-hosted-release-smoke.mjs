#!/usr/bin/env node
// 8x8 public User Edition hosted-route acceptance. Non-mutating.
// HTTP 200 does not prove /studio or /agents is the correct resource.
import {createHash} from 'node:crypto';
const profiles=[
  ['/', 'text/html', /8x8 OS|Three Gates|One Fabric/i],
  ['/studio','text/html',/8x8 Studio.*Media Inspector/i],
  ['/agents','text/html',/Agent Room.*Public Preview|8x8.*Agent Room/i],
  ['/icon.svg','image/svg+xml',/<svg\b/i],
  ['/manifest.webmanifest','application/(?:manifest\+json|json)', null],
  ['/sw.js','(?:application|text)/javascript',/addEventListener|self\./]
];
export async function smoke(base, request=fetch) {
  const origin=new URL(base);
  if(!['http:','https:'].includes(origin.protocol)||origin.pathname!=='/'||origin.search||origin.hash||origin.username||origin.password) throw Error('EXPECTED_BASE_ORIGIN');
  const results=[];const unique=new Map();
  for(const [path,expectedType,expectedContent] of profiles){
    const target=new URL(path,origin);
    const res=await request(target.href,{redirect:'manual',cache:'no-store',signal:AbortSignal.timeout(8000)});
    if(res.status!==200) throw Error('UNEXPECTED_HTTP_'+path+'_'+res.status);
    const resolved=new URL(res.url||target.href);
    if(resolved.origin!==origin.origin) throw Error('CROSS_ORIGIN_REDIRECT_'+path);
    const mime=res.headers.get('content-type')||'';
    if(!(new RegExp('^'+expectedType,'i')).test(mime)) throw Error('WRONG_MEDIA_TYPE_'+path+'_'+mime);
    if(Number(res.headers.get('content-length')||'0')>1048576) throw Error('OVERSIZED_'+path);
    const bytes=Buffer.from(await res.arrayBuffer());
    if(!bytes.length||bytes.length>1048576) throw Error('EMPTY_OR_OVERSIZED_'+path);
    const body=bytes.toString('utf8');
    if(expectedContent&&!expectedContent.test(body)) throw Error('WRONG_PAGE_'+path);
    if(path==='/manifest.webmanifest'){
      let doc;try{doc=JSON.parse(body)}catch{throw Error('BAD_MANIFEST_JSON')}
      if(!Array.isArray(doc.shortcuts)||!['/agents','/studio'].every(p=>doc.shortcuts.some(x=>x.url===p))) throw Error('MANIFEST_SHORTCUT_MISSING');
    }
    const hash=createHash('sha256').update(bytes).digest('hex');
    if(['/', '/agents','/studio'].includes(path)){
      if(unique.has(hash)) throw Error('FALLBACK_SAME_BODY_'+unique.get(hash)+'_'+path);
      unique.set(hash,path);
    }
    results.push({path,sha256:hash,media_type:mime,bytes:bytes.length});
  }
  return {state:'PRESENT_PROVEN',scope:'hosted public assets only',origin:origin.origin,checks:results};
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 if(!process.argv[2]){console.error('Usage: node scripts/one-fabric-hosted-release-smoke.mjs https://HOST/');process.exitCode=2}
 else try{console.log(JSON.stringify(await smoke(process.argv[2]),null,2))}
 catch(e){console.error('HOSTED_USER_EDITION_GATE=FAIL',e.message);process.exitCode=1}
}
