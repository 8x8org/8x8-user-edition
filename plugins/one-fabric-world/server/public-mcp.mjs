// ©️8x8 User Edition — protected public directory; NO owner controls or writes.
// Source release: requires deployment + OAuth before ChatGPT can connect.
import {createServer} from 'node:http';
import {readFileSync} from 'node:fs';
import {createPublicKey,verify} from 'node:crypto';
const DATA=JSON.parse(readFileSync(new URL('../data/unified_public_catalog.json',import.meta.url),'utf8'));
const SCENARIOS=JSON.parse(readFileSync(new URL('../data/access_scenarios_v1.json',import.meta.url),'utf8'));
const SCENARIO_EMBED=JSON.stringify(SCENARIOS).replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/&/g,'\\u0026');
// Reuse the original, source-preserved Agent Theater portraits; never invent live
// agent presence or clone a second avatar registry. Embed only four bounded
// public concept thumbnails into the same MCP Apps resource (no remote fetch).
const THEATER_SOURCE=readFileSync(new URL('../ui/one-fabric-agent-theater.html',import.meta.url),'utf8');
const theaterCastMatch=THEATER_SOURCE.match(/const PEOPLE=(\\[[^\\r\\n]*\\]);/);
if(!theaterCastMatch)throw new Error('ORIGINAL_AGENT_THEATER_SOURCE_NOT_FOUND');
const theaterCast=JSON.parse(theaterCastMatch[1]);
if(!Array.isArray(theaterCast)||theaterCast.length<4)throw new Error('AGENT_THEATER_CAST_TOO_SMALL');
const PUBLIC_CONCEPT_AVATARS=theaterCast.slice(0,4).map(person=>{
 if(!/^[A-Z0-9_-]{2,40}$/.test(person.id)||
    typeof person.name!=='string'||person.name.length>80||
    typeof person.role!=='string'||person.role.length>90||
    typeof person.portrait!=='string'||
    !/^data:image\\/webp;base64,[A-Za-z0-9+/=]+$/.test(person.portrait)||
    person.portrait.length>55000)throw new Error('UNTRUSTED_AGENT_CONCEPT_ART');
 return {id:person.id,name:person.name,role:person.role,portrait:person.portrait,
         evidence_state:'ORIGINAL_CONCEPT_NOT_AUTHENTICATED'};
});
export function getPublicConceptAvatarSummary(){
 return PUBLIC_CONCEPT_AVATARS.map(({id,name,role,evidence_state})=>({id,name,role,evidence_state}));
}
const AVATAR_BOOTSTRAP='window.__EIGHTX8_PUBLIC_CONCEPT_AVATARS__='+
 JSON.stringify(PUBLIC_CONCEPT_AVATARS).replace(/</g,'\\u003c').replace(/>/g,'\\u003e')+';\\n';
const BUBBLE_SCRIPT=AVATAR_BOOTSTRAP+readFileSync(new URL('../ui/one-fabric-bubble.js',import.meta.url),'utf8');
const withBubble=html=>html.replace('</body>','<script>'+BUBBLE_SCRIPT+'</script></body>');
// Source-backed atlas projection: render from ONE catalog; no duplicate UI authority.
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const MARKET_CLIENT=readFileSync(new URL('../ui/market-evidence.mjs',import.meta.url),'utf8').replace(/^export /gm,'');
const atlas=DATA.experience_atlas;
const ATLAS_ITEMS=atlas.families.map(f=>'<details class="family"><summary>'+esc(f.title)+' <span class="state">SOURCE ONLY</span></summary><ul>'+f.features.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></details>').join('');
const UI=withBubble(readFileSync(new URL('../ui/one-fabric-hub.html',import.meta.url),'utf8')
 .replace('<!-- EXPERIENCE_ATLAS_ITEMS -->',ATLAS_ITEMS)
 .replace('<!-- EXPERIENCE_TOTAL -->',String(atlas.families.length))
 .replace('<!-- CAPABILITY_TOTAL -->',String(atlas.families.reduce((n,f)=>n+f.features.length,0)))
 .replace('<!-- MARKET_VALIDATOR_JS -->',MARKET_CLIENT)
 .replace('<!-- SCENARIO_CATALOG_JSON -->',SCENARIO_EMBED));

// Pure source renderer for offline/browser contract testing. This is not a network endpoint.
export function renderPublicUI(){return UI;}
const OBSERVATORY_UI=withBubble(readFileSync(new URL('../ui/one-fabric-observatory.html',import.meta.url),'utf8'));
export function renderObservatoryUI(){return OBSERVATORY_UI;}
const AGENT_THEATER_UI=withBubble(readFileSync(new URL('../ui/one-fabric-agent-theater.html',import.meta.url),'utf8'));
export function renderAgentTheaterUI(){return AGENT_THEATER_UI;}
const SCOPE='8x8.public.read';
const UI_URI='ui://8x8/one-fabric-user-edition-hub.html';
const OBSERVATORY_URI='ui://8x8/one-fabric-observatory.html';
const AGENT_THEATER_URI='ui://8x8/one-fabric-agent-theater.html';
const TOOLS=Object.freeze({
 'one_fabric.capability_catalog':'Explore source-backed public capabilities and maturity',
 'one_fabric.world_status':'Inspect World and Three Gates readiness',
 'one_fabric.agent_catalog':'Inspect public agent archetypes; no live presence claims',
 'one_fabric.studio_status':'Inspect Studio and permitted distribution roadmap',
 'one_fabric.release_status':'Inspect independently accepted release status',
 'one_fabric.unified_modules':'Explore all 19 One Fabric product domains from a single catalog',
 'one_fabric.identity_connection_guide':'How a user safely links 8x8 ID and ChatGPT MCP using OAuth',
 'one_fabric.identity_lineage':'Inspect reserved historical 10-digit 8x8 identities versus protected-beta Auth IDs (no owner grants)',
 'one_fabric.user_agent_templates':'Explore default non-owner agent templates and custom agents',
 'one_fabric.usage_plans':'Review proposed 88 free minutes and $8.88/month limits',
 'one_fabric.connector_guidance':'Recommend optional connections, with consent required separately',
 'one_fabric.platform_surfaces':'Review one 8x8 World projection across web, ChatGPT, APK and Telegram',
 'one_fabric.experience_atlas':'Explore the extensible 8x8 universal experience atlas, including all 20 source-classified families',
 'one_fabric.market_media_readiness':'Inspect market-feed provenance, chart readiness, Spotify and multimedia restrictions; no invented live data',
 'one_fabric.market_snapshot_contract':'Inspect the fail-closed local market chart import schema and explicitly unverified provenance',
 'one_fabric.connector_inventory_status':'Inspect time-stamped advertised tool census without claims of installation or account access',
 'one_fabric.access_rescue':'Explore missing-access states and safe reversible connection guidance without collecting secrets',
 'one_fabric.scenario_catalog':'Explore eight source-classified cross-domain scenarios, agent role templates and acceptance receipts',
 'one_fabric.observatory_contract':'Explore agent avatar and whole-estate event observation requirements without accessing private telemetry',
 'one_fabric.capability_finder':'Search all publicly classified One Fabric families, including preserved historical donor capabilities (source-only, no account access)',
 'one_fabric.agent_theater':'Explore restored 8x8 character portraits, source-indexed personas and voice-demo boundary without live agent claims'
});
const json=(body,status=200,headers={})=>new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json','cache-control':'no-store',...headers}});
const https=x=>{try{return new URL(x).protocol==='https:'}catch{return false}};
const configured=e=>['PUBLIC_OAUTH_ISSUER','PUBLIC_OAUTH_AUDIENCE','PUBLIC_JWKS_URL','PUBLIC_MCP_RESOURCE_URL'].every(k=>https(e[k]));
const decode=s=>Buffer.from(s.replace(/-/g,'+').replace(/_/g,'/'),'base64');
async function verifyIdentity(req,env,fetcher,now){
 const auth=req.headers.get('authorization')||'';
 if(!/^Bearer [\w.-]+$/.test(auth)||auth.length>8192)throw Error('UNAUTHORIZED');
 const parts=auth.slice(7).split('.');if(parts.length!==3)throw Error('INVALID_TOKEN');
 let hd,claims;try{hd=JSON.parse(decode(parts[0]));claims=JSON.parse(decode(parts[1]));}catch{throw Error('FORMAT')}
 if(hd.alg!=='RS256'||typeof hd.kid!=='string'||!hd.kid||hd.kid.length>200)throw Error('ALGORITHM');
 if(claims.iss!==env.PUBLIC_OAUTH_ISSUER||!(claims.aud===env.PUBLIC_OAUTH_AUDIENCE||Array.isArray(claims.aud)&&claims.aud.includes(env.PUBLIC_OAUTH_AUDIENCE)))throw Error('ISSUER_AUDIENCE');
 const nowSec=Math.floor(now()/1000);
 if(!Number.isSafeInteger(claims.exp)||claims.exp<=nowSec||!Number.isSafeInteger(claims.iat)||claims.iat>nowSec+30||claims.nbf!==undefined&&claims.nbf>nowSec+30)throw Error('EXPIRED');
 if(typeof claims.sub!=='string'||!claims.sub||claims.sub.length>300)throw Error('SUBJECT');
 const scopes=new Set(typeof claims.scope==='string'?claims.scope.split(/\s+/):Array.isArray(claims.scp)?claims.scp:[]);
 if(!scopes.has(SCOPE))throw Error('SCOPE');
 const rsp=await fetcher(env.PUBLIC_JWKS_URL,{redirect:'error',headers:{accept:'application/json'},signal:AbortSignal.timeout(3500)});
 if(!rsp.ok)throw Error('JWKS');const keyset=await rsp.json();
 const jwk=Array.isArray(keyset.keys)?keyset.keys.find(k=>k.kid===hd.kid&&k.kty==='RSA'&&(!k.alg||k.alg==='RS256')&&(!k.use||k.use==='sig')):null;
 if(!jwk||!verify('RSA-SHA256',Buffer.from(parts[0]+'.'+parts[1]),createPublicKey({key:jwk,format:'jwk'}),decode(parts[2])))throw Error('SIGNATURE');
 // JWT signature validates public catalog access only. Tenant membership must be verified
 // separately against 8x8 account data before any user-owned resource action is added.
 return {subject:claims.sub};
}
const COMMON={root:'fabric://8x8/core',access:'OAUTH_PUBLIC_USER_READ_ONLY',status:'PRELAUNCH_SOURCE_ONLY',effect_count:0,live_user_backend_connected:false,owner_private_tools_exposed:false};
// Public catalog discovery uses existing Atlas data; it is not a private-estate
// index, browser agent, remote model or authority channel.
function discoverPublic(args={}){
 const keys=Object.keys(args);
 if(keys.some(k=>!['query','max_results'].includes(k)))throw Error('INVALID_DISCOVERY_ARGUMENTS');
 const q=args.query===undefined?'':args.query;
 const max=args.max_results===undefined?20:args.max_results;
 if(typeof q!=='string'||q.length>80||q.includes(String.fromCharCode(92))||/[\x00-\x1f\x7f@=]/.test(q)||
    /[A-Za-z0-9_-]{32,}/.test(q)||!Number.isInteger(max)||max<1||max>20)
   throw Error('INVALID_DISCOVERY_QUERY');
 const text=q.trim().toLowerCase();
 const words=text.split(/\s+/).filter(x=>x.length>1&&!['find','show','give','about','what','with','from','please','the','and'].includes(x));
 const matched=DATA.experience_atlas.families.filter(f=>{
   if(!text)return true;
   const hay=[f.title,f.id,f.domain,...f.features].join(' ').toLowerCase();
   return hay.includes(text)||(words.length>0&&words.some(w=>hay.includes(w)));
 });
 return {...COMMON,classification:'PUBLIC_SOURCE_DISCOVERY_ONLY',
   catalog_source:'unified_public_catalog.json',
   searched_family_denominator:DATA.experience_atlas.families.length,
   searched_feature_denominator:DATA.experience_atlas.families.reduce((n,f)=>n+f.features.length,0),
   matched_family_count:matched.length,returned_family_count:Math.min(matched.length,max),
   next_action:'USE_EXISTING_8X8_ID_ONBOARDING_AND_SEPARATE_PROVIDER_CONSENT',
   verified_live_capabilities:'NOT_EVALUATED_BY_CATALOG_LOOKUP',
   finder_grants_no_account_access:true,
   matches:matched.slice(0,max).map(f=>({
     id:f.id,title:f.title,domain:f.domain,
     evidence_state:'CATALOG_OR_HISTORICAL_SOURCE_ONLY',
     features:f.features.filter(v=>!text||words.length===0||words.some(w=>v.toLowerCase().includes(w))).slice(0,10),
     catalog_feature_count:f.features.length,
     live_runtime_verified_by_this_tool:false
   }))
 };
}
function value(name,args={}){

 switch(name){
  case 'one_fabric.capability_catalog':return {...COMMON,capabilities:DATA.capabilities};
  case 'one_fabric.world_status':return {...COMMON,gates:['Seraphim welcome','Verified 8x8 ID / tenant','Authorized 8x8 World'],production_login_verified:false};
  case 'one_fabric.agent_catalog':return {...COMMON,agent_templates:DATA.agent_templates,live_model_agents_verified:0,owner_agent_memory_available:false};
  case 'one_fabric.studio_status':return {...COMMON,studio:'SOURCE_CANDIDATE',published_items_verified:0,approval_required:true};
  case 'one_fabric.release_status':return {...COMMON,public_mcp_deployed_verified:false,authenticated_user_flow_verified:false,signed_apk_verified:false,stripe_webhooks_verified:false};
  case 'one_fabric.unified_modules':return {...COMMON,domains:DATA.domains,protection:'TENANT_ISOLATION_REQUIRED_FOR_ALL_USER_DATA'};
  case 'one_fabric.identity_connection_guide':return {...COMMON,authentication:DATA.authentication,onboarding:DATA.onboarding};
  case 'one_fabric.identity_lineage':return {...COMMON,identity_lineage:DATA.identity_lineage,authenticated_legacy_mapping:false,owner_root_grant:false,credential_intake_enabled:false};
  case 'one_fabric.user_agent_templates':return {...COMMON,templates:DATA.agent_templates,custom_agent_creation:'NOT_DEPLOYED',individual_memory:'USER_TENANT_OWNED_TARGET'};
  case 'one_fabric.usage_plans':return {...COMMON,plans:DATA.plans,billing_status:'NOT_CONNECTED_NO_PAYMENT_AUTHORIZED'};
  case 'one_fabric.connector_guidance':return {...COMMON,provider_connections:DATA.connector_guidance,auto_install:false,auto_token_import:false};
  case 'one_fabric.platform_surfaces':return {...COMMON,surfaces:DATA.surfaces};
  case 'one_fabric.experience_atlas':return {...COMMON,experience_atlas:DATA.experience_atlas,legacy_domains:DATA.domains};
  case 'one_fabric.market_media_readiness':return {...COMMON,market_media_readiness:DATA.market_media_readiness};
  case 'one_fabric.market_snapshot_contract':return {...COMMON,contract:DATA.market_media_readiness.local_market_snapshot_contract,live_feed_connected:false,execution_authority:false};
  case 'one_fabric.connector_inventory_status':return {...COMMON,connector_census:DATA.connector_census};
  case 'one_fabric.access_rescue':return {...COMMON,access_states:SCENARIOS.missing_access_states,privacy:SCENARIOS.privacy,external_connection_performed:false};
  case 'one_fabric.scenario_catalog':return {...COMMON,scenarios:SCENARIOS.flows,classification:SCENARIOS.classification,automatic_execution:false};
  case 'one_fabric.observatory_contract':return {...COMMON,visualization:'PUBLIC_SAFE_ANIMATED_ILLUSTRATION',owner_live_stream_connected:false,verified_live_agents:null,world_domains:24,all_files_covered:false,event_fields:['event_id','source_id','observed_utc','evidence_class','receipt_ref','tenant_scope'],sequence_gap_detection_required:true,transport:'FUTURE_AUTHENTICATED_OWNER_SSE',raw_hidden_model_reasoning_exposed:false,owner_secrets_exposed:false};
  case 'one_fabric.capability_finder':return discoverPublic(args);
  case 'one_fabric.agent_theater':return {...COMMON,cinematic_character_sources:7,chatgpt_bridge_display_only:true,historical_agent_identities:212,verified_simultaneously_active_agent_sessions:0,live_model_dialogue:false,source_art_recovered:true,voice_preview:'USER_GESTURE_BROWSER_TTS_ONLY',mic_preview:'ONE_SHOT_BROWSER_RECOGNIZER_CONSENT',chatgpt_private_reasoning_exposed:false,external_effects:0};
  default:throw Error('UNKNOWN_TOOL');
 }
}
function toolList(){return Object.entries(TOOLS).map(([name,description])=>({name,description,inputSchema:name==='one_fabric.capability_finder'?{type:'object',properties:{query:{type:'string',maxLength:80},max_results:{type:'integer',minimum:1,maximum:20}},additionalProperties:false}:{type:'object',properties:{},additionalProperties:false},securitySchemes:[{type:'oauth2',scopes:[SCOPE]}],annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{'ui/resourceUri':name==='one_fabric.agent_theater'?AGENT_THEATER_URI:name==='one_fabric.observatory_contract'?OBSERVATORY_URI:UI_URI}}))}
export function makeHandler(env=process.env,fetcher=fetch,now=Date.now){
 return async request=>{
  const url=new URL(request.url);
  if(request.method==='GET'&&url.pathname==='/health')return json({service:'8x8-one-fabric-user-world',version:'0.2.0',configured:configured(env),production_ready:false,private_effects:false});
  if(request.method==='GET'&&url.pathname==='/.well-known/oauth-protected-resource')return configured(env)?json({resource:env.PUBLIC_MCP_RESOURCE_URL,authorization_servers:[env.PUBLIC_OAUTH_ISSUER],scopes_supported:[SCOPE]}):json({error:'AUTH_CONFIGURATION_REQUIRED'},503);
  if(url.pathname!=='/mcp')return json({error:'NOT_FOUND'},404);
  if(request.method!=='POST')return json({error:'METHOD_NOT_ALLOWED'},405);
  if(!configured(env))return json({error:'AUTH_CONFIGURATION_REQUIRED'},503);
  const origin=request.headers.get('origin');
  if(origin&&!(env.PUBLIC_ALLOWED_ORIGINS||'').split(',').map(s=>s.trim()).includes(origin))return json({error:'ORIGIN_DENIED'},403);
  try{await verifyIdentity(request,env,fetcher,now)}catch{return json({error:'UNAUTHENTICATED'},401,{'www-authenticate':`Bearer resource_metadata="${new URL('/.well-known/oauth-protected-resource',env.PUBLIC_MCP_RESOURCE_URL).href}"`})}
  if(Number(request.headers.get('content-length')||0)>32768)return json({error:'REQUEST_TOO_LARGE'},413);
  let body;try{let txt=await request.text();if(Buffer.byteLength(txt)>32768)throw Error('large');body=JSON.parse(txt)}catch{return json({error:'BAD_JSON'},400)}
  if(!body||Array.isArray(body)||body.jsonrpc!=='2.0'||typeof body.method!=='string')return json({error:'BAD_JSONRPC'},400);
  if(body.method==='notifications/initialized')return new Response(null,{status:202});
  const id=body.id??null;
  let result;
  if(body.method==='initialize')result={protocolVersion:'2025-06-18',serverInfo:{name:'8x8-one-fabric-user-world',version:'0.2.0'},capabilities:{tools:{listChanged:false},resources:{listChanged:false}},instructions:'Public prelaunch user directory only. No founder/owner resource, broker action, payment, signer, device command or automatic social post.'};
  else if(body.method==='ping')result={};
  else if(body.method==='tools/list')result={tools:toolList()};
  else if(body.method==='resources/list')result={resources:[{uri:UI_URI,name:'One Fabric User Hub',mimeType:'text/html;profile=mcp-app'},{uri:OBSERVATORY_URI,name:'One Fabric Observatory (Public Preview)',mimeType:'text/html;profile=mcp-app'},{uri:AGENT_THEATER_URI,name:'One Fabric Agent Theater (Cinematic Source Preview)',mimeType:'text/html;profile=mcp-app'}]};
  else if(body.method==='resources/read'){
    if(body.params?.uri!==UI_URI&&body.params?.uri!==OBSERVATORY_URI&&body.params?.uri!==AGENT_THEATER_URI)return json({jsonrpc:'2.0',id,error:{code:-32602,message:'UNKNOWN_RESOURCE'}});
    const stage=body.params.uri===AGENT_THEATER_URI;
    const obs=body.params.uri===OBSERVATORY_URI;
    result={contents:[{uri:body.params.uri,mimeType:'text/html;profile=mcp-app',text:stage?AGENT_THEATER_UI:obs?OBSERVATORY_UI:UI}]};
  }
  else if(body.method==='tools/call'){
   const name=body.params?.name,args=body.params?.arguments||{};
   if(typeof name!=='string'||!Object.hasOwn(TOOLS,name)||!args||typeof args!=='object'||Array.isArray(args)||
      (name!=='one_fabric.capability_finder'&&Object.keys(args).length))
       return json({jsonrpc:'2.0',id,error:{code:-32602,message:'INVALID_TOOL_OR_ARGUMENTS'}});
   let data;try{data=value(name,args)}catch{return json({jsonrpc:'2.0',id,error:{code:-32602,message:'INVALID_TOOL_OR_ARGUMENTS'}})}
   result={content:[{type:'text',text:JSON.stringify(data)}],structuredContent:data,isError:false,_meta:{'ui/resourceUri':name==='one_fabric.agent_theater'?AGENT_THEATER_URI:name==='one_fabric.observatory_contract'?OBSERVATORY_URI:UI_URI}};
  }else return json({jsonrpc:'2.0',id,error:{code:-32601,message:'METHOD_NOT_FOUND'}});
  return json({jsonrpc:'2.0',id,result});
 }
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const handler=makeHandler();createServer(async(req,res)=>{
  try{let data='';for await(const chunk of req){data+=chunk;if(Buffer.byteLength(data)>32768)throw Error('large')}
   const x=new Request(new URL(req.url,'https://'+(req.headers.host||'localhost')),{method:req.method,headers:req.headers,body:req.method==='POST'?data:undefined});
   const out=await handler(x);res.writeHead(out.status,Object.fromEntries(out.headers));res.end(await out.text());
  }catch{res.writeHead(400,{'content-type':'application/json'});res.end('{"error":"BAD_REQUEST"}')}
 }).listen(Number(process.env.PORT||10000),'0.0.0.0',()=>console.log('8x8 PUBLIC MCP PRELAUNCH'));}
