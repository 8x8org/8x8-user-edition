// ©️8x8 by FlashTM8 — public User Edition source admission before build.
// Converges PR #200's private-source veto with PR #201's public-only Agent Room.
// No credentials, network calls, runtime authority or user/device action.
import {existsSync,readFileSync,readdirSync} from 'node:fs';

const REQUIRED=['package.json','vercel.json','state/public-state.json','v50.html',
  'studio/index.html','studio/media-core.mjs','agents/index.html','atlas/index.html',
  'observatory/index.html','projects/world-atlas/index.html'];
const PRIVATE_ROOTS=['core','auth.py','background_loop.py','agent.py','private','server',
  'agents/__init__.py','agents/server','agents/runtime','agents/private'];
const FLAGS=['credentials_included','wallet_material_included','remote_shell_enabled',
  'live_trading_enabled','public_billing_enabled','private_control_plane_connected'];
// Only the explicitly reviewed public character-room file is admitted at this stage.
// Any additional public agent asset must get a provenance-reviewed policy update first.
const PUBLIC_AGENT_FILES=new Set(['index.html']);

export function assertPublicBuildSource({exists=existsSync,read=p=>readFileSync(p,'utf8'),
  list=p=>readdirSync(p,{withFileTypes:true})}={}) {
  const missing=REQUIRED.filter(p=>!exists(p));
  if(missing.length)throw Error('8X8_PUBLIC_REQUIRED_SOURCE_MISSING:'+missing.join(','));
  let pkg,vercel,state;
  try {
    pkg=JSON.parse(read('package.json'));
    vercel=JSON.parse(read('vercel.json'));
    state=JSON.parse(read('state/public-state.json'));
  }catch {throw Error('8X8_PUBLIC_METADATA_INVALID')}
  if(pkg.name!=='8x8-user-edition-quality-gates' ||
    vercel.buildCommand!=='npm run build:vercel' ||
    vercel.outputDirectory!=='dist' ||
    state.promotion_state!=='PROTECTED_BETA' ||
    FLAGS.some(key=>state[key]!==false))
    throw Error('8X8_PUBLIC_SOURCE_POLICY_MISMATCH');
  const prohibited=PRIVATE_ROOTS.filter(p=>exists(p));
  if(prohibited.length)throw Error('8X8_PUBLIC_PRIVATE_SOURCE_PRESENT:'+prohibited.join(','));
  const agentFiles=list('agents').map(entry=>entry.name).sort();
  if(agentFiles.some(name=>!PUBLIC_AGENT_FILES.has(name)))
    throw Error('8X8_PUBLIC_AGENT_DIRECTORY_NOT_ALLOWLISTED');
  return {state:'PUBLIC_SOURCE_ONLY',required:REQUIRED.length,
    public_agent_files:agentFiles,private_source_admitted:false,
    tenant_grants:false,verified_deployment:false};
}
