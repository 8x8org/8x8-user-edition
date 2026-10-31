import test from 'node:test';
import assert from 'node:assert/strict';
import {audit,smoke} from '../scripts/one-fabric-hosted-release-smoke.mjs';
const data={
 '/':['text/html','<title>8x8 OS · Three Gates</title>'],
 '/studio':['text/html','<title>8x8 Studio · Media Inspector</title>'],
 '/agents':['text/html','<title>8x8 Agent Room · Public Preview</title>'],
 '/icon.svg':['image/svg+xml','<svg xmlns="http://www.w3.org/2000/svg"/>'],
 '/manifest.webmanifest':['application/manifest+json',JSON.stringify({shortcuts:[{url:'/studio'},{url:'/agents'}]})],
 '/sw.js':['application/javascript','self.addEventListener("install",()=>{})']
};
const fake=(overrides={})=>async url=>{
 const path=new URL(url).pathname;
 if(typeof overrides[path]==='function') return overrides[path](url);
 if(overrides[path] instanceof Error) throw overrides[path];
 const [mime,body]=overrides[path]||data[path];
 return new Response(body,{status:200,headers:{'content-type':mime}});
};

test('all six distinct hosted route profiles pass in one report',async()=>{
 const r=await audit('https://example.com/',fake());
 assert.equal(r.state,'PRESENT_PROVEN');assert.equal(r.checks.length,6);
 assert.equal(r.failures.length,0);
 assert.ok(r.checks.every(x=>x.verdict==='PASS'&&x.sha256?.length===64));
});
test('independent route failures are all reported after a homepage failure',async()=>{
 let seen=[];
 const f=async url=>{
  const path=new URL(url).pathname;seen.push(path);
  if(path==='/') return new Response('wrong',{status:404});
  return fake({'/studio':['text/html','<html>wrong studio</html>'],'/agents':['text/html','<html>wrong agents</html>']})(url);
 };
 const r=await audit('https://example.com/',f);
 assert.equal(seen.length,6);
 assert.equal(r.state,'FUTURE_GATED');
 assert.equal(r.checks.length,6);
 assert.deepEqual(r.checks.filter(x=>x.verdict==='FAIL').map(x=>x.path).slice(0,3),['/','/studio','/agents']);
 assert.equal(r.checks.find(x=>x.path==='/icon.svg').verdict,'PASS');
 await assert.rejects(smoke('https://example.com/',f),/UNEXPECTED_HTTP/);
});
test('same HTML fallback across page routes is detected even with bad markers',async()=>{
 const body='<title>8x8 OS · Three Gates</title><p>One Fabric</p>';
 const r=await audit('https://example.com/',fake({'/':[ 'text/html',body],'/studio':['text/html',body],'/agents':['text/html',body]}));
 assert.ok(r.failures.some(x=>x.code.startsWith('FALLBACK_SAME_BODY_/')));
 assert.equal(r.checks.find(x=>x.path==='/agents').fallback_duplicate_of,'/');
});
test('an explicit redirect is not followed and later paths are still checked',async()=>{
 let requested=[];
 const request=async url=>{
  requested.push(url);
  if(new URL(url).pathname==='/')return new Response(null,{status:302,headers:{location:'https://evil.example/exfil'}});
  return fake()(url);
 };
 const r=await audit('https://example.com/',request);
 assert.equal(requested.length,6);
 assert.ok(requested.every(s=>new URL(s).origin==='https://example.com'));
 assert.match(r.failures[0].code,/UNEXPECTED_HTTP/);
});
test('cross-origin and unexpected same-origin response URLs are rejected',async()=>{
 const request=async url=>{
  const p=new URL(url).pathname;
  if(p==='/') return {status:200,url:'https://evil.example/',redirected:false,headers:new Headers({'content-type':'text/html'})};
  if(p==='/studio') return {status:200,url:'https://example.com/not-studio',redirected:false,headers:new Headers({'content-type':'text/html'})};
  return fake()(url);
 };
 const r=await audit('https://example.com/',request);
 assert.deepEqual(r.failures.slice(0,2).map(f=>f.code),['CROSS_ORIGIN_REDIRECT_/', 'RESPONSE_URL_MISMATCH_/studio']);
});
test('a wrapper that follows redirects despite manual mode fails closed',async()=>{
 const req=async url=>new Response(data[new URL(url).pathname][1],{status:200,headers:{'content-type':data[new URL(url).pathname][0]}});
 const r=await audit('https://example.com/',async url=>{
  const res=await req(url);
  if(new URL(url).pathname==='/')return {status:res.status,url,redirected:true,headers:res.headers};
  return res;
 });
 assert.match(r.failures[0].code,/AUTO_FOLLOWED_REDIRECT/);
});
test('bad attachment disposition is rejected for route content',async()=>{
 const r=await audit('https://example.com/',async url=>{
  const p=new URL(url).pathname;
  if(p==='/studio')return new Response(data[p][1],{status:200,headers:{'content-type':data[p][0],'content-disposition':'attachment; filename="bad.html"'}});
  return fake()(url);
 });
 assert.equal(r.checks.find(x=>x.path==='/studio').code,'ATTACHMENT_DISPOSITION_/studio');
});
test('one route request failure does not stop remaining routes',async()=>{
 const r=await audit('https://example.com/',fake({'/studio':new Error('network error with https://internal.example/token')}));
 assert.equal(r.checks.length,6);
 assert.equal(r.checks.find(x=>x.path==='/studio').code,'REQUEST_OR_PARSE_FAILED_/studio');
 assert.equal(JSON.stringify(r).includes('internal.example'),false);
});
test('origin validation rejects user-info, path and non-http schemes before any request',async()=>{
 let calls=0;const req=async()=>{calls++;throw Error('must not run')};
 for(const s of ['https://user:secret@example.com/','https://example.com/a','file:///etc/passwd','not an url']){
  await assert.rejects(audit(s,req),/EXPECTED_BASE_ORIGIN/);
 }
 assert.equal(calls,0);
});
test('oversized and empty bodies fail while preserving other checks',async()=>{
 const r=await audit('https://example.com/',async url=>{
  const p=new URL(url).pathname;
  if(p==='/studio')return new Response('bad',{status:200,headers:{'content-type':'text/html','content-length':'2000000'}});
  if(p==='/agents')return new Response('',{status:200,headers:{'content-type':'text/html'}});
  return fake()(url);
 });
 assert.equal(r.checks.length,6);
 assert.match(r.checks.find(x=>x.path==='/studio').code,/OVERSIZED/);
 assert.match(r.checks.find(x=>x.path==='/agents').code,/EMPTY_OR_OVERSIZED/);
});
