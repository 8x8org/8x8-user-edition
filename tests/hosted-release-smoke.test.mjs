import test from 'node:test';
import assert from 'node:assert/strict';
import {smoke} from '../scripts/one-fabric-hosted-release-smoke.mjs';
const routes={
'/':['text/html','<title>8x8 OS · Three Gates</title>'],
'/studio':['text/html','<title>8x8 Studio · Media Inspector</title>'],
'/agents':['text/html','<title>8x8 Agent Room · Public Preview</title>'],
'/icon.svg':['image/svg+xml','<svg viewBox="0 0 1 1"></svg>'],
'/manifest.webmanifest':['application/manifest+json',JSON.stringify({shortcuts:[{url:'/studio'},{url:'/agents'}]})],
'/sw.js':['application/javascript','self.addEventListener("install",()=>{})']
};
function fake(overrides={}){
return async url=>{
  const [mime,body]=overrides[new URL(url).pathname]||routes[new URL(url).pathname];
  return new Response(body,{status:200,headers:{'content-type':mime}});
}}
test('distinct public app/studio/agent pages and asset MIME pass',async()=>{const r=await smoke('https://8x8.example/',fake());assert.equal(r.checks.length,6);assert.equal(r.state,'PRESENT_PROVEN')});
test('wrong studio page still HTTP 200 is rejected',async()=>await assert.rejects(smoke('https://8x8.example/',fake({'/studio':routes['/']})),/WRONG_PAGE/));
test('wrong agent page still HTTP 200 is rejected',async()=>await assert.rejects(smoke('https://8x8.example/',fake({'/agents':routes['/']})),/WRONG_PAGE/));
test('HTML-as-SVG is rejected',async()=>await assert.rejects(smoke('https://8x8.example/',fake({'/icon.svg':['text/html','<html>fallback</html>']})),/WRONG_MEDIA_TYPE/));
test('manifest missing Agent Room shortcut is rejected',async()=>await assert.rejects(smoke('https://8x8.example/',fake({'/manifest.webmanifest':['application/json','{"shortcuts":[{"url":"/studio"}]}']})),/MANIFEST_SHORTCUT_MISSING/));
test('redirect and URL credentials are rejected',async()=>{await assert.rejects(smoke('https://user:pw@8x8.example/',fake()),/EXPECTED_BASE_ORIGIN/); await assert.rejects(smoke('https://8x8.example/',async()=>new Response('',{status:302})),/UNEXPECTED_HTTP/)});
