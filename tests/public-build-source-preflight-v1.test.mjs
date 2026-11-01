import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync,readdirSync} from 'node:fs';
import {assertPublicBuildSource} from '../scripts/public-build-source-preflight-v1.mjs';
const read=p=>readFileSync(p,'utf8');
test('actual current public source is admitted without production authority',()=>{
 const r=assertPublicBuildSource();
 assert.equal(r.state,'PUBLIC_SOURCE_ONLY');
 assert.deepEqual(r.public_agent_files,['index.html']);
 assert.equal(r.tenant_grants,false);
 assert.equal(r.verified_deployment,false);
});
test('an additional agent backend is refused rather than silently copied',()=>{
 const list=p=>p==='agents'?[{name:'index.html'},{name:'controller.py'}]:readdirSync(p,{withFileTypes:true});
 assert.throws(()=>assertPublicBuildSource({list}),/AGENT_DIRECTORY_NOT_ALLOWLISTED/);
});
test('a private server root is rejected even with a legitimate public Agent Room',()=>{
 const exists=p=>p==='core'||existsSync(p);
 assert.throws(()=>assertPublicBuildSource({exists}),/PRIVATE_SOURCE_PRESENT/);
});
test('missing release source is not treated as successful',()=>{
 const exists=p=>p==='v50.html'?false:existsSync(p);
 assert.throws(()=>assertPublicBuildSource({exists}),/REQUIRED_SOURCE_MISSING/);
});
test('broad runtime or credential enablement is rejected',()=>{
 const readBad=p=>{
   if(p!=='state/public-state.json')return read(p);
   const j=JSON.parse(read(p));
   j.remote_shell_enabled=true;
   return JSON.stringify(j);
 };
 assert.throws(()=>assertPublicBuildSource({read:readBad}),/SOURCE_POLICY_MISMATCH/);
});
test('metadata changes cannot switch the build output destination',()=>{
 const readBad=p=>{
   if(p!=='vercel.json')return read(p);
   const j=JSON.parse(read(p));
   j.outputDirectory='private';
   return JSON.stringify(j);
 };
 assert.throws(()=>assertPublicBuildSource({read:readBad}),/SOURCE_POLICY_MISMATCH/);
});
