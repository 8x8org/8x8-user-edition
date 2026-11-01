/* ©8x8 One Fabric — public, read-only capability projection.
   One catalog for Web/PWA/Android/Telegram/public skill navigation.
   No owner runtime, internal connector tokens or private hostnames. */
(function (root) {
  'use strict';
  const modules = [
    {id:'entry',name:'One Fabric Portal',family:'Experience',icon:'◈',route:'/',state:'SOURCE_PREVIEW',summary:'Gate 1 entry and access to the unified public experience'},
    {id:'world',name:'8x8 World',family:'Experience',icon:'◉',route:'/world',state:'SOURCE_PREVIEW',summary:'Gate 3 scenes, public spatial interface and mission entry'},
    {id:'atlas',name:'Capability Atlas',family:'Experience',icon:'▦',route:'/atlas',state:'SOURCE_PREVIEW',summary:'One searchable map of services, readiness, products and skills'},
    {id:'observatory',name:'One Fabric Observatory',family:'Experience',icon:'◫',route:'/observatory',state:'SOURCE_PREVIEW',summary:'Five-lane read-only preview; owner telemetry requires Gate 2, verified receipt stream and access grants'},
    {id:'studio',name:'8x8 Studio',family:'Creation',icon:'▶',route:'/studio',state:'LOCAL_SOURCE_PREVIEW',summary:'User-selected images, video, audio preview and evidence receipts'},
    {id:'agents',name:'Agent Room',family:'Intelligence',icon:'♧',route:'/agents',state:'CONCEPT_PREVIEW',summary:'Illustrative talking figures; live agent replies require the authenticated gateway'},
    {id:'updates',name:'Verified Updates',family:'Platforms',icon:'↻',route:null,state:'DEVICE_ACCEPTANCE_PENDING',summary:'Native package-aware signed updates; platform approval is separate'},
    {id:'telegram',name:'Telegram Mini App',family:'Platforms',icon:'✈',route:'/telegram',state:'ROUTE_SOURCE_ONLY',summary:'Shared public carrier; Telegram live-launch acceptance pending'},
    {id:'android',name:'Android',family:'Platforms',icon:'▣',route:'/android',state:'OFFLINE_CANDIDATE',summary:'One Fabric offline bundle and Android development carriers'},
    {id:'desktop',name:'iOS / Windows / Linux',family:'Platforms',icon:'▤',route:null,state:'FUTURE_GATED',summary:'PWA access; distinct native installers are not released'},
    {id:'mcp',name:'8x8 All-in-One MCP',family:'Intelligence',icon:'◇',route:null,state:'OAUTH_AND_PUBLIC_RELEASE_PENDING',summary:'Single tenant-scoped tool gateway; ChatGPT app discoverability not yet verified'},
    {id:'skills',name:'8x8 Skill Federation',family:'Intelligence',icon:'✧',route:null,state:'SOURCE_SKILLS_AVAILABLE',summary:'Public skill source, private skills and external providers require separate discovery'},
    {id:'models',name:'Models and A2A',family:'Intelligence',icon:'⋈',route:null,state:'AUTHENTICATED_REPLIES_PENDING',summary:'Model routing, approved work queues, signed agent exchanges'},
    {id:'research',name:'Research and Repositories',family:'Knowledge',icon:'⌕',route:null,state:'RECONCILIATION_IN_PROGRESS',summary:'URL, repository, model, tool and capability evidence with provenance'},
    {id:'memory',name:'Knowledge and Memory',family:'Knowledge',icon:'▤',route:null,state:'TENANT_AUTH_REQUIRED',summary:'Personal and shared knowledge with rights, retention and user controls'},
    {id:'science',name:'Science and Planet Earth',family:'Knowledge',icon:'⊕',route:null,state:'RESEARCH',summary:'Scientific tools, climate, simulations, education and civic evidence'},
    {id:'books',name:'Books, Education and Languages',family:'Knowledge',icon:'▣',route:null,state:'PARTIAL',summary:'Multilingual books, lessons, narration and accessibility'},
    {id:'trading',name:'Trading and Markets',family:'Economy',icon:'↗',route:null,state:'PROVIDER_AND_ORDER_AUTH_REQUIRED',summary:'Market research, analytics, account linkage and scoped order workflows'},
    {id:'wallet',name:'Wallet, Blockchain and NFTs',family:'Economy',icon:'⬡',route:null,state:'TENANT_AND_PROVIDER_AUTH_REQUIRED',summary:'Blockchain research, wallets, asset catalogs, digital collectibles'},
    {id:'publishing',name:'Social Publishing',family:'Creation',icon:'↗',route:null,state:'PROVIDER_PUBLISH_AUTH_REQUIRED',summary:'Original content creation, platform-specific rights and verified posting'},
    {id:'entertainment',name:'Games, Radio and Streaming',family:'Creation',icon:'♫',route:null,state:'ROADMAP',summary:'Games, live media, film episodes, interactive shows and broadcasts'},
    {id:'business',name:'Partners and Commerce',family:'Economy',icon:'◎',route:'/presale',state:'PRELAUNCH',summary:'Business, partnerships, creator services and commerce flows'},
    {id:'projects',name:'Public Projects',family:'Experience',icon:'⌘',route:'/projects',state:'SOURCE_PREVIEW',summary:'Public-safe project and roadmap surfaces'}
  ];
  const skills = [
    {id:'one-fabric-public-media-review',name:'Media review',state:'SOURCE_ONLY',path:'skills/one-fabric-public-media-review/SKILL.md'},
    {id:'one-fabric-verified-upgrade',name:'Verified upgrade',state:'SOURCE_ONLY',path:'skills/one-fabric-verified-upgrade/SKILL.md'},
    {id:'one-fabric-unified-navigation',name:'Unified navigation',state:'SOURCE_ONLY',path:'skills/one-fabric-unified-navigation/SKILL.md'}
  ];
  const allowedStates = new Set(['SOURCE_PREVIEW','LOCAL_SOURCE_PREVIEW','CONCEPT_PREVIEW','DEVICE_ACCEPTANCE_PENDING','ROUTE_SOURCE_ONLY','OFFLINE_CANDIDATE','FUTURE_GATED','OAUTH_AND_PUBLIC_RELEASE_PENDING','SOURCE_SKILLS_AVAILABLE','AUTHENTICATED_REPLIES_PENDING','RECONCILIATION_IN_PROGRESS','TENANT_AUTH_REQUIRED','RESEARCH','PARTIAL','PROVIDER_AND_ORDER_AUTH_REQUIRED','TENANT_AND_PROVIDER_AUTH_REQUIRED','PROVIDER_PUBLISH_AUTH_REQUIRED','ROADMAP','PRELAUNCH']);
  const seen = new Set();
  for (const m of modules) {
    if (seen.has(m.id) || !allowedStates.has(m.state) || (m.route && !/^\/[a-z0-9/-]*$/.test(m.route))) throw new Error('INVALID_PUBLIC_CATALOG');
    seen.add(m.id);
  }
  const catalog = Object.freeze({
    version: '1.0.0-source',canonicalRoot:'fabric://8x8/core',
    userEditionSource:'8x8org/8x8-user-edition',classification:'PUBLIC_PROJECTION_NOT_LIVE_INTEGRATION',
    modules:Object.freeze(modules.map(x=>Object.freeze(x))),
    skills:Object.freeze(skills.map(x=>Object.freeze(x)))
  });
  Object.defineProperty(root,'EIGHTX8_PUBLIC_CATALOG',{value:catalog,writable:false,configurable:false});
})(typeof window !== 'undefined' ? window : globalThis);
