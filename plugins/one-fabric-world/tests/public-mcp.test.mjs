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
test('all 17 tools are read only with one scope',async()=>{const [,x]=await post('tools/list',{});assert.equal(x.result.tools.length,17);assert.ok(x.result.tools.every(t=>t.annotations.readOnlyHint===true&&t.securitySchemes[0].scopes[0]==='8x8.public.read'))});
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
test('UI resource includes actual hub with 19 domain renderer',async()=>{const [,l]=await post('resources/list',{});assert.equal(l.result.resources.length,1);const [,r]=await post('resources/read',{uri:l.result.resources[0].uri});assert.match(r.result.contents[0].text,/Your 8x8 World/);assert.match(r.result.contents[0].text,/catalog only/i)});
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
