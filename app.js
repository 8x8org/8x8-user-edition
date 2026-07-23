const AGENTS = {
  FlashTM8: {symbol:'⚡', role:'Owner intent and final authority', color:'#ffd166', body:'The human owner remains at the center of the operating model. High-impact actions require exact, current and target-specific approval.', facts:{Class:'OWNER', Public_status:'ROLE DESCRIPTION', Private_runtime:'NOT EXPOSED'}},
  Hermes: {symbol:'☿', role:'Orchestration and bounded tool planning', color:'#76f7ff', body:'Hermes represents mission decomposition, tool routing and receipt-oriented orchestration. This public card does not claim a live provider session.', facts:{Class:'ORCHESTRATOR', Public_status:'ARCHETYPE', Credentials:'NOT INCLUDED'}},
  Seraphim: {symbol:'✦', role:'Security, policy and adversarial review', color:'#ff6685', body:'Seraphim challenges unsafe claims and protects the public/private boundary. It never receives wallet keys or hidden owner authority from this interface.', facts:{Class:'SECURITY', Public_status:'ARCHETYPE', Shell_access:'NONE'}},
  SOMA: {symbol:'◉', role:'Health, continuity and operational sensing', color:'#53f6a7', body:'SOMA describes the health and continuity role: evidence freshness, storage pressure, service stability and recovery signals.', facts:{Class:'OPERATIONS', Public_status:'ARCHETYPE', Telemetry:'DEMO ONLY'}},
  Atlas: {symbol:'◇', role:'Architecture, maps and dependency intelligence', color:'#5c82ff', body:'Atlas maps systems, dependencies and plans. The public beta shows conceptual relationships without revealing private topology.', facts:{Class:'ARCHITECTURE', Public_status:'ARCHETYPE', Private_topology:'REDACTED'}},
  Omnivore: {symbol:'∞', role:'Cross-source research and evidence retrieval', color:'#a76dff', body:'Omnivore represents broad retrieval and evidence normalization. Private messages, owner files and credentials remain excluded.', facts:{Class:'RESEARCH', Public_status:'ARCHETYPE', Private_sources:'NOT CONNECTED'}},
  OpenClaw: {symbol:'C', role:'Bounded computer-use and interface assistance', color:'#ff9d66', body:'OpenClaw represents user-visible, policy-bounded interaction. This beta contains no remote-control channel and no device administration.', facts:{Class:'INTERACTION', Public_status:'ARCHETYPE', Remote_control:'DISABLED'}}
};

const TRUTH = {
  CLAIMED:'A statement exists in public documentation. No implementation is implied.',
  DESIGNED:'Architecture, interfaces or contracts have been specified.',
  IMPLEMENTED:'Source code exists for the specific capability.',
  TESTED:'A defined test passed against a known revision.',
  RECEIPT_VERIFIED:'A hash-linked receipt verifies the exact result and assertions.',
  RUNNING:'Fresh evidence shows an active runtime process or service.',
  DEPLOYED:'The verified revision is running on a named target.',
  RELEASED:'A public, versioned release exists with provenance.',
  ADOPTED:'Independent users or systems have verified use of the release.'
};

const agentOrder=['FlashTM8','Hermes','Seraphim','SOMA','Atlas','Omnivore','OpenClaw'];
const views=[...document.querySelectorAll('.view')];
const navButtons=[...document.querySelectorAll('[data-view]')];
const drawer=document.getElementById('drawer');

function setView(id){
  views.forEach(view=>view.classList.toggle('active',view.id===id));
  navButtons.forEach(button=>button.classList.toggle('active',button.dataset.view===id));
  window.scrollTo({top:0,behavior:'smooth'});
  history.replaceState(null,'',`#${id}`);
}

navButtons.forEach(button=>button.addEventListener('click',()=>setView(button.dataset.view)));

document.getElementById('enterCockpit').addEventListener('click',()=>{
  document.getElementById('metricsGrid').scrollIntoView({behavior:'smooth',block:'center'});
});

document.getElementById('coreButton').addEventListener('click',()=>openAgent('FlashTM8','SYSTEM SUMMARY'));

document.getElementById('closeDrawer').addEventListener('click',closeDrawer);
document.addEventListener('keydown',event=>{
  if(event.key==='Escape') closeDrawer();
  if(['1','2','3','4','5'].includes(event.key) && !/input|textarea/i.test(document.activeElement.tagName)) setView(['overview','agents','map','roadmap','security'][Number(event.key)-1]);
});

function openAgent(name,label='AGENT ARCHETYPE'){
  const agent=AGENTS[name];
  if(!agent) return;
  document.getElementById('drawerLabel').textContent=label;
  document.getElementById('drawerTitle').textContent=`${agent.symbol} ${name}`;
  document.getElementById('drawerTitle').style.color=agent.color;
  document.getElementById('drawerBody').textContent=agent.body;
  document.getElementById('drawerFacts').innerHTML=Object.entries(agent.facts).map(([key,value])=>`<dt>${key.replaceAll('_',' ')}</dt><dd>${value}</dd>`).join('');
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden','false');
}
function closeDrawer(){drawer.classList.remove('open');drawer.setAttribute('aria-hidden','true')}

document.querySelectorAll('[data-agent]').forEach(button=>button.addEventListener('click',()=>openAgent(button.dataset.agent)));

document.querySelectorAll('[data-truth]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('[data-truth]').forEach(item=>item.classList.remove('active'));
  button.classList.add('active');
  document.getElementById('truthDescription').textContent=TRUTH[button.dataset.truth];
}));

const grid=document.getElementById('agentGrid');
grid.innerHTML=agentOrder.map(name=>{
  const a=AGENTS[name];
  return `<article class="agent-card glass" data-agent-card="${name}" style="--agent-color:${a.color}" tabindex="0" role="button" aria-label="Inspect ${name}"><div class="agent-symbol">${a.symbol}</div><h2>${name}</h2><p class="agent-role">${a.role}</p><p>${a.body}</p><div class="agent-meta"><span>PUBLIC ROLE</span><span>NO UPTIME CLAIM</span></div></article>`;
}).join('');

document.querySelectorAll('[data-agent-card]').forEach(card=>{
  const show=()=>openAgent(card.dataset.agentCard);
  card.addEventListener('click',show);
  card.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();show()}});
});

const canvas=document.getElementById('space');
const ctx=canvas.getContext('2d',{alpha:true});
let stars=[];
let width=0,height=0,dpr=1;
function resize(){
  dpr=Math.min(window.devicePixelRatio||1,2);
  width=window.innerWidth;height=window.innerHeight;
  canvas.width=width*dpr;canvas.height=height*dpr;
  canvas.style.width=`${width}px`;canvas.style.height=`${height}px`;
  ctx.setTransform(dpr,0,0,dpr,0,0);
  const count=Math.max(60,Math.min(190,Math.floor(width*height/9000)));
  stars=Array.from({length:count},()=>({x:Math.random()*width,y:Math.random()*height,r:Math.random()*1.35+.15,v:Math.random()*.12+.025,a:Math.random()*.55+.16}));
}
function frame(){
  ctx.clearRect(0,0,width,height);
  for(const s of stars){
    s.y+=s.v;
    if(s.y>height+2){s.y=-2;s.x=Math.random()*width}
    ctx.beginPath();ctx.fillStyle=`rgba(188,234,255,${s.a})`;ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
  }
  requestAnimationFrame(frame);
}
window.addEventListener('resize',resize,{passive:true});resize();frame();

const initial=location.hash.slice(1);
if(['overview','agents','map','roadmap','security'].includes(initial)) setView(initial);

if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}));}
