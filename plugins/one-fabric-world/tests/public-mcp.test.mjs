import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,sign} from 'node:crypto';
import {makeHandler} from '../server/public-mcp.mjs';
const {privateKey,publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});
const key=publicKey.export({format:'jwk'});key.kid='good';key.alg='RS256';
const env={PUBLIC_OAUTH_ISSUER:'https://id.test',PUBLIC_OAUTH_AUDIENCE:'https://mcp.test/mcp',PUBLIC_JWKS_URL:'https://id.test/jwks',PUBLIC_MCP_RESOURCE_URL:'https://mcp.test/mcp',PUBLIC_ALLOWED_ORIGINS:'https://chatgpt.com'};
const fakeFetch=async()=>new Response(JSON.stringify({keys:[key]}));
const now=()=>1730000000000;
const b=x=>Buffer.from(JSON.stringify(x)).toString('base64url');
const jwt=(c={},pk=privateKey)=>{let h=b({alg:'RS256',kid:'good'}),p=b({iss:env.PUBLIC_OAUTH_ISSUER,aud:env.PUBLIC_OAUTH_AUDIENCE,sub:'user1',iat:1729999900,exp:1730000100,scope:'8x8.public.read',...c});return `${h}.${p}.${sign('RSA-SHA256',Buffer.from(h+'.'+p),pk).toString('base64url')}`};
async function post(method,params,token=jwt(),override=env,origin=null){const req=new Request('https://mcp.test/mcp',{method:'POST',headers:{authorization:token?'Bearer '+token:'',...(origin?{origin}:{})},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})});let r=await makeHandler(override,fakeFetch,now)(req);return [r,await r.json().catch(()=>null)]}
const toolName='one_fabric.unified_modules';
test('without configured issuer and JWKS fails closed',async()=>assert.equal((await post('tools/list',{},jwt(),{}))[0].status,503));
test('missing bearer fails',async()=>assert.equal((await post('tools/list',{},''))[0].status,401));
test('wrong audience fails',async()=>assert.equal((await post('tools/list',{},jwt({aud:'https://attacker.test'})))[0].status,401));
test('wrong issuer fails',async()=>assert.equal((await post('tools/list',{},jwt({iss:'https://attacker.test'})))[0].status,401));
test('expired JWT fails',async()=>assert.equal((await post('tools/list',{},jwt({exp:1729999999})))[0].status,401));
test('wrong scopes fails',async()=>assert.equal((await post('tools/list',{},jwt({scope:'8x8.owner.read'})))[0].status,401));
test('tampered signatures fail',async()=>{const other=generateKeyPairSync('rsa',{modulusLength:2048});assert.equal((await post('tools/list',{},jwt({},other.privateKey)))[0].status,401)});
test('external origins rejected',async()=>assert.equal((await post('tools/list',{},jwt(),env,'https://evil.test'))[0].status,403));
test('protected resource metadata matches issuer and public scope',async()=>{let r=await makeHandler(env,fakeFetch)(new Request('https://mcp.test/.well-known/oauth-protected-resource'));assert.deepEqual((await r.json()).scopes_supported,['8x8.public.read'])});
test('all 21 tools are read only with one scope',async()=>{const [,x]=await post('tools/list',{});assert.equal(x.result.tools.length,21);assert.ok(x.result.tools.every(t=>t.annotations.readOnlyHint===true&&t.securitySchemes[0].scopes[0]==='8x8.public.read'))});
test('historical tool identifiers retained',async()=>{const [,x]=await post('tools/list',{});for(const n of ['one_fabric.capability_catalog','one_fabric.agent_catalog','one_fabric.world_status','one_fabric.studio_status','one_fabric.release_status'])assert.ok(x.result.tools.some(t=>t.name===n))});
test('owner shell denied',async()=>{const [,x]=await post('tools/call',{name:'owner.adb.exec',arguments:{}});assert.equal(x.error.code,-32602)});
test('trading execute denied',async()=>{const [,x]=await post('tools/call',{name:'trading.execute',arguments:{}});assert.equal(x.error.code,-32602)});
test('publishing action denied',async()=>{const [,x]=await post('tools/call',{name:'publishing.publish',arguments:{}});assert.equal(x.error.code,-32602)});
test('every tool returns no public external effect permission',async()=>{const [,l]=await post('tools/list',{});for(const tool of l.result.tools){const [,x]=await post('tools/call',{name:tool.name,arguments:{}});assert.equal(x.result.structuredContent.effect_count,0);assert.equal(x.result.structuredContent.live_user_backend_connected,false)}});
test('19 domain catalog',async()=>{const [,x]=await post('tools/call',{name:toolName,arguments:{}});assert.equal(x.result.structuredContent.domains.length,19)});
test('88 minute target not live',async()=>{const [,x]=await post('tools/call',{name:'one_fabric.usage_plans',arguments:{}});assert.equal(x.result.structuredContent.plans.free.target_minutes,88);assert.equal(x.result.structuredContent.plans.free.active,false)});
test('8.88 dollars is target not live',async()=>{const [,x]=await post('tools/call',{name:'one_fabric.usage_plans',arguments:{}});assert.equal(x.result.structuredContent.plans.plus.usd_cents_month,888);assert.equal(x.result.structuredContent.plans.plus.active,false)});
test('identity-only does not imply ChatGPT memory access',async()=>{const [,x]=await post('tools/call',{name:'one_fabric.identity_connection_guide',arguments:{}});assert.equal(x.result.structuredContent.authentication.chatgpt_history_or_memory_import,false)});
test('default templates lack founder memory',async()=>{const [,x]=await post('tools/call',{name:'one_fabric.user_agent_templates',arguments:{}});assert.equal(x.result.structuredContent.owner_private_tools_exposed,false);assert.equal(x.result.structuredContent.templates.length,6)});
test('connector suggestions do not install connectors',async()=>{const [,x]=await post('tools/call',{name:'one_fabric.connector_guidance',arguments:{}});assert.equal(x.result.structuredContent.auto_install,false)});
test('UI resource includes actual hub with 19 domain renderer',async()=>{const [,l]=await post('resources/list',{});assert.equal(l.result.resources.length,3);const [,r]=await post('resources/read',{uri:l.result.resources[0].uri});assert.match(r.result.contents[0].text,/Your 8x8 World/);assert.match(r.result.contents[0].text,/catalog only/i)});
test('not registered resource denied',async()=>{const [,x]=await post('resources/read',{uri:'ui://8x8/owner-secret'});assert.equal(x.error.code,-32602)});
test('no host config implies not production ready',async()=>{const r=await makeHandler(env,fakeFetch)(new Request('https://mcp.test/health'));assert.equal((await r.json()).production_ready,false)});
test('tool arguments must be empty to avoid implicit authority',async()=>{const [,x]=await post('tools/call',{name:toolName,arguments:{tenant:'other'}});assert.equal(x.error.code,-32602)});

test('universal atlas retains all domains as extensible subfamily projection',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.experience_atlas',arguments:{}});
 const a=x.result.structuredContent;
 assert.equal(a.effect_count,0);
 assert.equal(a.legacy_domains.length,19);
 assert.equal(a.experience_atlas.families.length,20);
 assert.equal(new Set(a.experience_atlas.families.map(f=>f.id)).size,20);
 assert.ok(a.experience_atlas.families.reduce((n,f)=>n+f.features.length,0)>=230);
 assert.ok(a.experience_atlas.families.every(f=>a.legacy_domains.includes(f.domain)));
});
test('market/media readiness never invents a live count or grants orders',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.market_media_readiness',arguments:{}});
 const xdata=x.result.structuredContent;
 assert.equal(xdata.effect_count,0);
 assert.equal(xdata.market_media_readiness.market_feed.connected,false);
 assert.equal(xdata.market_media_readiness.market_feed.market_trades_count,null);
 assert.equal(xdata.market_media_readiness.market_feed.account_fills_count,null);
 assert.equal(xdata.market_media_readiness.market_feed.orders_enabled,false);
 assert.equal(xdata.market_media_readiness.spotify.connection_state,'NOT_VERIFIED');
 assert.equal(xdata.market_media_readiness.spotify.content_sync_to_video_allowed,false);
});
test('UI renders canonical atlas and non-autoplay media preview',async()=>{
 const [,l]=await post('resources/list',{});
 const [,r]=await post('resources/read',{uri:l.result.resources[0].uri});
 const html=r.result.contents[0].text;
 assert.ok(html.includes('Universal One Fabric Atlas'));
 assert.ok(html.includes('Markets · Charts · Trade Counts'));
 assert.ok(html.includes('Music · Spotify · Radio'));
 assert.ok(html.includes('8x8 World &amp; Spatial Experience'));
 assert.ok(html.includes('233'));
 assert.ok(html.includes('Local 8x8 video preview'));
 assert.ok(!html.includes('<!-- EXPERIENCE_ATLAS_ITEMS -->'));
 assert.ok(!html.includes('<video autoplay'));
});

test('market snapshot contract is local unverified only and no account fills',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.market_snapshot_contract',arguments:{}});
 const v=x.result.structuredContent;
 assert.equal(v.effect_count,0);
 assert.equal(v.contract.classification,'LOCAL_IMPORT_UNVERIFIED');
 assert.equal(v.contract.live_status,'NEVER_LIVE_FROM_FILE_IMPORT');
 assert.ok(!v.contract.allowed_top_level_fields.includes('account_fill_count'));
 assert.equal(v.live_feed_connected,false);
});
test('connector census 6105 actions is explicitly historical, not authorization',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.connector_inventory_status',arguments:{}});
 const c=x.result.structuredContent.connector_census;
 assert.equal(c.advertised_mcp_actions_at_snapshot,6105);
 assert.equal(c.authenticated_connections_verified,false);
 assert.equal(c.global_provider_catalog_exhaustive,false);
 assert.equal(c.public_user_tools_obtainable_by_8x8_automatically,false);
});
test('market renderer is included in the MCP Apps resource, no fabricated live bar content',async()=>{
 const [,l]=await post('resources/list',{});
 const [,r]=await post('resources/read',{uri:l.result.resources[0].uri});
 const html=r.result.contents[0].text;
 assert.ok(html.includes('function validateLocalMarketSnapshot'));
 assert.ok(html.includes('function marketClosePath'));
 assert.ok(html.includes('id="market-json"'));
 assert.ok(html.includes('id="market-chart-path"'));
 assert.ok(html.includes('Search all source-backed experience entries'));
 assert.ok(!html.includes('<!-- MARKET_VALIDATOR_JS -->'));
 assert.ok(!html.includes('LIVE_PROVIDER_VERIFIED · ACTIVE'));
 assert.ok(!html.includes('account_fill_count='));
});

test('source-backed access rescue offers no-secret recovery for eight conditions',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.access_rescue',arguments:{}});
 const v=x.result.structuredContent;
 assert.equal(v.effect_count,0);assert.equal(v.external_connection_performed,false);
 assert.equal(v.access_states.length,8);
 for(const state of v.access_states)assert.ok(state.id&&state.remedy);
 assert.ok(v.privacy.never_collect.includes('api key'));
});
test('eight scenarios preserve distinct execution and proof gates',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.scenario_catalog',arguments:{}});
 const v=x.result.structuredContent;
 assert.equal(v.effect_count,0);assert.equal(v.automatic_execution,false);
 assert.equal(v.scenarios.length,8);assert.equal(new Set(v.scenarios.map(x=>x.id)).size,8);
 for(const x of v.scenarios){assert.ok(x.steps.length>1&&x.missing.length>0&&x.receipt.length>0)}
});
test('UI includes source-backed assistance dialog and local draft export',async()=>{
 const [,l]=await post('resources/list',{});const [,r]=await post('resources/read',{uri:l.result.resources[0].uri});
 const html=r.result.contents[0].text;
 assert.ok(html.includes('id="access-dialog"'));
 assert.ok(html.includes('id="access-launch"'));
 assert.ok(html.includes('id="studio-draft"'));
 assert.ok(html.includes('LOCAL_DRAFT_NOT_RENDERED'));
 assert.ok(html.includes('"id":"QUOTA_BLOCKED"'));
 assert.ok(!html.includes('<!-- SCENARIO_CATALOG_JSON -->'));
 assert.ok(!html.includes('create live order'));
});

test('observatory contract is read-only and refuses fake live users or hidden reasoning',async()=>{
 const [,x]=await post('tools/call',{name:'one_fabric.observatory_contract',arguments:{}});
 const v=x.result.structuredContent;
 assert.equal(v.effect_count,0);
 assert.equal(v.owner_live_stream_connected,false);
 assert.equal(v.verified_live_agents,null);
 assert.equal(v.world_domains,24);
 assert.equal(v.all_files_covered,false);
 assert.equal(v.raw_hidden_model_reasoning_exposed,false);
 assert.ok(v.event_fields.includes('receipt_ref'));
 assert.equal(x.result._meta['ui/resourceUri'],'ui://8x8/one-fabric-observatory.html');
});
test('observatory MCP resource is public-safe animation and has no owner secrets',async()=>{
 const [,l]=await post('resources/list',{});
 const resource=l.result.resources.find(x=>x.uri==='ui://8x8/one-fabric-observatory.html');
 assert.ok(resource);
 const [,r]=await post('resources/read',{uri:resource.uri});
 const html=r.result.contents[0].text;
 assert.ok(html.includes('The Living Observatory'));
 assert.ok(html.includes('id="scene"'));
 assert.ok(html.includes('id="domains"'));
 assert.ok(html.includes('PUBLIC DEMO'));
 assert.ok(html.includes('No live owner event stream'));
 assert.ok(!html.includes('PRIVATE_KEY'));
 assert.ok(!html.includes('localStorage.'));
 assert.ok(!html.includes('fetch('));
});

test('original cinematic agent theater is a public-safe read-only MCP resource',async()=>{
 const [,list]=await post('resources/list',{});
 const uri='ui://8x8/one-fabric-agent-theater.html';
 assert.ok(list.result.resources.some(x=>x.uri===uri));
 const [,read]=await post('resources/read',{uri});
 const html=read.result.contents[0].text;
 assert.match(html,/Cinematic Agent Theater/);
 assert.match(html,/SERAPHIM/);
 assert.match(html,/FLASHTM8_ASSISTANT/);
 assert.match(html,/CHATGPT_BRIDGE/);
 assert.match(html,/212 historical source identities/);
 assert.ok((html.match(/data:image\/webp;base64,/g)||[]).length>=7);
 assert.doesNotMatch(html,/github_pat_|-----BEGIN PRIVATE KEY-----|sk-proj-/);
});
test('agent theater tool reports actual source-only state, not verified real voices',async()=>{
 const [,r]=await post('tools/call',{name:'one_fabric.agent_theater',arguments:{}});
 const d=r.result.structuredContent;
 assert.equal(d.effect_count,0);
 assert.equal(d.historical_agent_identities,212);
 assert.equal(d.cinematic_character_sources,7);
 assert.equal(d.verified_simultaneously_active_agent_sessions,0);
 assert.equal(d.live_model_dialogue,false);
 assert.equal(d.chatgpt_bridge_display_only,true);
 assert.equal(r.result._meta['ui/resourceUri'],'ui://8x8/one-fabric-agent-theater.html');
});

test('MCP preserves owner/iPhone historical IDs without impersonating either principal',async()=>{
 const [,res]=await post('tools/call',{name:'one_fabric.identity_lineage',arguments:{}});
 const p=res.result.structuredContent;
 assert.equal(p.identity_lineage.owner_public_id,'0000000001');
 assert.equal(p.identity_lineage.iphone_public_id,'0000000002');
 assert.equal(p.identity_lineage.protected_beta_legacy_account_mapping_verified,false);
 assert.equal(p.identity_lineage.tenant_membership_verified,false);
 assert.equal(p.authenticated_legacy_mapping,false);
 assert.equal(p.owner_root_grant,false);
 assert.equal(p.credential_intake_enabled,false);
 assert.equal(p.effect_count,0);
});
test('MCP identity lineage rejects owner grants or secret payloads',async()=>{
 const [,r]=await post('tools/call',{name:'one_fabric.identity_lineage',
  arguments:{owner_root:true,api_key:'do-not-log'}});
 assert.equal(r.error.code,-32602);
});
test('lineage projection is read only and has no owner-private MCP capabilities',async()=>{
 const [,l]=await post('tools/list',{});
 const t=l.result.tools.find(x=>x.name==='one_fabric.identity_lineage');
 assert.ok(t);assert.equal(t.annotations.readOnlyHint,true);
 assert.deepEqual(t.inputSchema.properties,{});
 assert.deepEqual(t.securitySchemes[0].scopes,['8x8.public.read']);
});

test('public finder is advertised as read-only and has bounded search schema',async()=>{
 const [,r]=await post('tools/list',{});
 const f=r.result.tools.find(x=>x.name==='one_fabric.capability_finder');
 assert.ok(f);assert.equal(f.annotations.readOnlyHint,true);
 assert.equal(f.securitySchemes[0].scopes[0],'8x8.public.read');
 assert.equal(f.inputSchema.properties.max_results.maximum,20);
});
test('public finder preserves complete 20-family denominator without manufacturing uptime',async()=>{
 const [,r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:{}});
 const v=r.result.structuredContent;
 assert.equal(v.searched_family_denominator,20);
 assert.equal(v.matches.length,20);
 assert.ok(v.searched_feature_denominator>=240);
 assert.equal(v.finder_grants_no_account_access,true);
 assert.equal(v.effect_count,0);
 assert.ok(v.matches.every(f=>!f.live_runtime_verified_by_this_tool));
});
test('finder can locate historical SOMA, Omni, Atlas, GG and Quran donors',async()=>{
 const cases=[['SOMA','devices'],['Omni','intelligence'],['Atlas','intelligence'],
              ['GG BTC','markets'],['Quran','knowledge'],['Planet Earth','planet']];
 for(const [q,id] of cases){
   const [,r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:{query:q}});
   assert.ok(r.result.structuredContent.matches.some(x=>x.id===id),q);
 }
});
test('finder searches user topics across multiple domains',async()=>{
 const [,r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:{query:'trading studio',max_results:8}});
 assert.ok(r.result.structuredContent.matched_family_count>=2);
 assert.ok(r.result.structuredContent.matches.length<=8);
 assert.equal(r.result.structuredContent.effect_count,0);
});
test('finder cannot accept credential or authority fields',async()=>{
 for(const args of [{query:'SOMA',api_key:'fake'},{query:'world',owner_root:true},
                    {query:'world',tenant_id:'private'}]){
   const [,r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:args});
   assert.equal(r.error.code,-32602);
 }
});
test('finder rejects credential-like, control-character and unbounded queries',async()=>{
 for(const args of [{query:'A'.repeat(42)},{query:'test@sample.com'},
     {query:'abcd=abcd'},{query:'world\\nprivate'},{query:'x'.repeat(81)},
     {query:10},{query:'world',max_results:21},{query:'world',max_results:0}]){
   const [,r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:args});
   assert.equal(r.error.code,-32602);
 }
});
test('public catalog search rejects unauthorized calls before lookup',async()=>{
 const [r]=await post('tools/call',{name:'one_fabric.capability_finder',arguments:{query:'SOMA'}},'');
 assert.equal(r.status,401);
});

test('v0.4.4 server identity consistent across health and initialize',async()=>{
 const h=await makeHandler(env,fakeFetch,now)(new Request('https://mcp.test/health'));
 assert.equal(h.status,200);
 const health=await h.json();
 assert.equal(health.version,'0.4.4');
 assert.equal(health.production_ready,false);
 const [response,payload]=await post('initialize',{});
 assert.equal(response.status,200);
 assert.equal(payload.result.serverInfo.version,'0.4.4');
});
test('OAuth missing cannot be bypassed by public metadata or initialize',async()=>{
 const handler=makeHandler({},fakeFetch,now);
 const discovery=await handler(new Request('https://mcp.test/.well-known/oauth-protected-resource'));
 assert.equal(discovery.status,503);
 assert.deepEqual(await discovery.json(),{error:'AUTH_CONFIGURATION_REQUIRED'});
 const request=new Request('https://mcp.test/mcp',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({jsonrpc:'2.0',id:77,method:'initialize',params:{}})});
 const response=await handler(request);
 assert.equal(response.status,503);
 assert.deepEqual(await response.json(),{error:'AUTH_CONFIGURATION_REQUIRED'});
});
