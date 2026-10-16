/* ©8x8 One Fabric reusable in-page bubble. PUBLIC-SAFE preview only.
   No network, secrets, localStorage, service worker, device access, telemetry,
   OS overlay or implicit ChatGPT run tracking. Supported only in active pages. */
(() => {
  "use strict";
  if (typeof document === "undefined" || document.getElementById("eightx8-bubble-root")) return;
  const style = document.createElement("style");
  style.textContent = `
#eightx8-bubble-root{position:fixed;bottom:calc(18px + env(safe-area-inset-bottom,0px));right:calc(14px + env(safe-area-inset-right,0px));z-index:2147483000;font:14px/1.45 system-ui,-apple-system,sans-serif;color:#eef7ff}
#eightx8-bubble-root *{box-sizing:border-box}
#eightx8-bubble-root button,#eightx8-bubble-root a{font:inherit;touch-action:manipulation}
#eightx8-bubble-root .eightx8-orb{display:grid;place-items:center;border:1px solid #8ddbf7;color:#f5fcff;background:linear-gradient(130deg,#155375,#26194c);box-shadow:0 5px 25px #021123bb,0 0 16px #5cbfff76;border-radius:50%;width:56px;height:56px;font-size:14px;font-weight:900;cursor:pointer}
#eightx8-bubble-root .eightx8-panel{width:min(360px,calc(100vw - 28px));max-height:min(520px,calc(100dvh - 110px));display:flex;flex-direction:column;overflow:hidden;border-radius:18px;border:1px solid #477c9e;box-shadow:0 14px 75px #020713dc;background:#071c2df7;color:#e3f5ff;margin-bottom:10px}
#eightx8-bubble-root .eightx8-panel[hidden]{display:none}
#eightx8-bubble-root .eightx8-head{display:flex;align-items:center;justify-content:space-between;padding:12px;background:#11334e;gap:8px;font-weight:800}
#eightx8-bubble-root .eightx8-close{background:transparent;border:1px solid #47687b;color:#e9f6ff;border-radius:8px;padding:3px 10px;cursor:pointer}
#eightx8-bubble-root .eightx8-tabs{display:flex;gap:5px;padding:9px;background:#0d263b}
#eightx8-bubble-root .eightx8-tab{flex:1;background:#153750;color:#d9ecf8;border:1px solid #45617b;border-radius:8px;padding:7px 3px;cursor:pointer;font-size:12px}
#eightx8-bubble-root .eightx8-tab[aria-selected="true"]{border-color:#a3eeff;background:#276285}
#eightx8-bubble-root .eightx8-body{overflow:auto;padding:12px;font-size:12px}
#eightx8-bubble-root .eightx8-body h3{font-size:14px;margin:2px 0 8px;color:#edfaff}
#eightx8-bubble-root .eightx8-body p{margin:6px 0 10px;color:#b7d1e2}
#eightx8-bubble-root .eightx8-row{display:flex;justify-content:space-between;gap:9px;border-bottom:1px solid #2c455a;padding:7px 0}
#eightx8-bubble-root .eightx8-row b{font-size:11px;text-align:right}
#eightx8-bubble-root .eightx8-warning{padding:8px 9px;border:1px solid #856a41;background:#362a1d;border-radius:8px;color:#ffdcac;margin:8px 0}
#eightx8-bubble-root .eightx8-voicebtn{margin:6px 6px 3px 0;padding:9px 10px;border-radius:9px;border:1px solid #58abd5;color:#e8f8ff;background:#16547a;cursor:pointer}
#eightx8-bubble-root .eightx8-voicebtn:disabled{opacity:.46;cursor:not-allowed}
#eightx8-bubble-root .eightx8-voicefeedback{min-height:28px;border:1px solid #31506b;border-radius:8px;padding:8px;background:#0b2133;color:#dcecf6;margin:7px 0}
#eightx8-bubble-root .eightx8-action{display:inline-block;margin:7px 8px 2px 0;padding:7px 10px;color:#eef9ff!important;background:#174f73;border:1px solid #5eabd2;border-radius:8px;text-decoration:none}
#eightx8-bubble-root :focus-visible{outline:2px solid #e3ca7a;outline-offset:3px}
@media(prefers-reduced-motion:reduce){#eightx8-bubble-root *{animation:none!important}}
`;
  document.head.append(style);
  const root=document.createElement("aside");
  root.id="eightx8-bubble-root";
  root.setAttribute("aria-label","8x8 One Fabric assistant preview");
  const panel=document.createElement("section");panel.className="eightx8-panel";panel.hidden=true;
  panel.id="eightx8-bubble-panel";panel.setAttribute("aria-label","8x8 read-only source preview");
  const head=document.createElement("div");head.className="eightx8-head";
  const title=document.createElement("span");title.textContent="⚡ 8x8 · FlashTM8";
  const close=document.createElement("button");close.type="button";close.className="eightx8-close";close.textContent="Close";close.setAttribute("aria-label","Close 8x8 panel");
  head.append(title,close);
  const tabs=document.createElement("div");tabs.className="eightx8-tabs";tabs.setAttribute("role","tablist");
  const body=document.createElement("div");body.className="eightx8-body";body.id="eightx8-bubble-body";body.setAttribute("role","tabpanel");body.setAttribute("aria-live","polite");
  const launch=document.createElement("button");launch.type="button";launch.className="eightx8-orb";launch.textContent="8×8";launch.setAttribute("aria-expanded","false");launch.setAttribute("aria-controls",panel.id);launch.setAttribute("aria-label","Open 8x8 One Fabric bubble");
  let active="status";
  const tabDefs=[["status","Status"],["agents","Agents"],["reports","Reports"],["access","Access"],["voice","Voice"]];
  const tabButtons=new Map();
  // Voice is foreground / explicit tap only. This does not connect a model,
  // accept a secret, start an ambient listener or send events to any 8x8 API.
  let recognition=null;
  let listening=false;
  let statusNote="No microphone or speech operation started.";
  const synth=()=>typeof window!=="undefined" && window.speechSynthesis;
  const recognitionCtor=()=>window.SpeechRecognition||window.webkitSpeechRecognition||null;
  const updateNote=(message)=>{
    statusNote=message;
    const node=document.getElementById("eightx8-voice-state");
    if(node)node.textContent=message;
  };
  function cancelVoice(){
    if(recognition){try{recognition.abort();}catch(_e){} recognition=null;}
    listening=false;
    try{synth()?.cancel();}catch(_e){}
  }
  const utteranceFor=()=>{
    switch(active){
      case "agents":return "8x8 agent roster is source indexed. Verified live model replies and council quorum are not established.";
      case "reports":return "8x8 run reports require a signed, authenticated event feed. No current ChatGPT run is connected to this bubble.";
      case "access":return "Access rescue is read only. Never say or paste private keys or passwords into this demonstration.";
      default:return "8x8 One Fabric voice preview. No private agent event stream or 24 hour runtime is connected here.";
    }
  };
  function speakCurrent(){
    if(!synth()||!window.SpeechSynthesisUtterance){updateNote("Speech output unsupported here. Try Android system TTS in a verified native build.");return;}
    try{
      synth().cancel();
      const u=new window.SpeechSynthesisUtterance(utteranceFor());
      u.lang="en-US";
      u.rate=1.0;
      u.volume=0.9;
      u.onerror=()=>updateNote("Speech output failed or was blocked by this browser.");
      u.onend=()=>updateNote("One spoken interface status completed. No agent conversation took place.");
      synth().speak(u);
      updateNote("Reading verified interface status aloud; this is not a remote FlashTM8 model reply.");
    }catch(_e){updateNote("Speech playback is unavailable in this browser.");}
  }
  function interpretVoiceCommand(raw){
    // No transcript is persisted, echoed or transmitted. Only allowlisted
    // local navigation commands can have effects.
    const command=String(raw||"").toLowerCase().trim().replace(/[.!?]+$/,"");
    let match=command.match(/^(?:show |open |go to )?(status|agents|reports|access|voice)$/);
    if(match){
      active=match[1];render();
      updateNote("Recognized local navigation only. No agent or device command was executed.");
    }else if(/^(help|what can you do)$/.test(command)){
      updateNote("Supported local commands: status, agents, reports, access, voice, read status, stop voice.");
    }else if(/^(read status|speak status|talk to me)$/.test(command)){
      speakCurrent();
    }else if(/^(stop voice|stop speaking|be quiet)$/.test(command)){
      cancelVoice();
      updateNote("Voice playback stopped. This is not the system-wide owner STOP.");
    }else{
      updateNote("Unsupported local voice command. Nothing stored, transmitted, approved or executed.");
    }
  }
  function startListening(){
    const Speech=recognitionCtor();
    if(!Speech){updateNote("Browser speech recognition unavailable. The device needs a separately verified native speech route.");return;}
    if(listening){updateNote("A one-shot listening request is already open.");return;}
    // Stop current TTS to avoid listening to our own synthesized speech.
    try{synth()?.cancel();}catch(_e){}
    let rec;
    try{
      rec=new Speech();
      rec.lang="en-US";
      rec.continuous=false;
      rec.interimResults=false;
      rec.maxAlternatives=1;
      rec.onresult=(event)=>{
        const result=event?.results?.[0]?.[0]?.transcript;
        interpretVoiceCommand(result);
      };
      rec.onerror=()=>{updateNote("Microphone or recognition permission denied, unsupported or interrupted.");};
      rec.onend=()=>{
        listening=false;
        if(recognition===rec)recognition=null;
      };
      rec.start();
      recognition=rec;
      listening=true;
      updateNote("One-shot listening requested. Browser/provider may process audio; no 8x8 recording is saved.");
    }catch(_e){listening=false;recognition=null;updateNote("Speech recognition could not start or requires permission.");}
  }
  const append=(parent,tag,value,cl)=>{const el=document.createElement(tag);if(value!==undefined)el.textContent=value;if(cl)el.className=cl;parent.append(el);return el;};
  const line=(k,v)=>{const row=append(body,"div",undefined,"eightx8-row");append(row,"span",k);append(row,"b",v);};
  const link=(label,href)=>{const a=append(body,"a",label,"eightx8-action");a.href=href;a.rel="noopener";};
  function render(){
    body.replaceChildren();
    for(const [id,b] of tabButtons)b.setAttribute("aria-selected",String(id===active));
    if(active==="status"){
      append(body,"h3","Observatory connection");
      append(body,"p","In-page UI is available. Owner private telemetry, ChatGPT run instrumentation and device mirroring are not connected.");
      line("This page","Interactive preview");line("Owner event stream","Not connected");
      line("Background 24/7","Not established");line("Sync latency","Not measured");
      const w=append(body,"div","No provider-connected LIVE indicator is shown without signed and fresh receipts.","eightx8-warning");
      w.setAttribute("role","status");
      link("Open full Observatory","/observatory/");
    }else if(active==="agents"){
      append(body,"h3","Agent personas");
      line("FlashTM8","Concept persona");line("Research Agent","Inference reply unverified");
      line("Council","No verified quorum");line("Seraphim","UI guide template");
      append(body,"p","Historical agent identities do not imply running or active instances.");
      link("Explore agent theater","/observatory/");
    }else if(active==="reports"){
      append(body,"h3","Run summaries and receipts");
      line("Current ChatGPT run","Not instrumented");
      line("Completed run receipts","No authenticated feed");
      line("Report provenance","Source only");
      append(body,"p","A genuine run report requires recorded actions, receipt IDs, evidence timestamps, gaps, blockers, decisions and next steps. No hidden model thoughts or raw secrets will be exposed.");
      link("Review Observatory","/observatory/");
    }else if(active==="voice"){
      append(body,"h3","Jarvis-style voice interface · local pilot");
      append(body,"p","Tap to speak or listen once. Speech playback is actual browser TTS, not a connected AI model. Microphone recognition depends on device/browser permissions and may use a provider service.");
      line("Speech output",synth() && window.SpeechSynthesisUtterance?"Browser API present · audio unverified":"Unavailable here");
      line("Microphone input",recognitionCtor()?"One-shot API present · consent required":"Unavailable here");
      line("FlashTM8 model conversation","Not connected");
      line("Ambient listening","OFF");
      const play=append(body,"button","🔊 Speak current status","eightx8-voicebtn");
      play.type="button";play.id="eightx8-voice-play";play.addEventListener("click",speakCurrent);
      const mic=append(body,"button","🎙 Listen once","eightx8-voicebtn");
      mic.type="button";mic.id="eightx8-voice-mic";mic.addEventListener("click",startListening);
      const stop=append(body,"button","■ Stop voice","eightx8-voicebtn");
      stop.type="button";stop.id="eightx8-voice-stop";stop.addEventListener("click",()=>{cancelVoice();updateNote("Voice input/output stopped locally. The 8x8 owner STOP remains a separate gate.");});
      const note=append(body,"div",statusNote,"eightx8-voicefeedback");
      note.id="eightx8-voice-state";note.setAttribute("role","status");
      append(body,"p","Say: status, agents, reports, access, voice, read status, stop voice, help. Commands only navigate this visible UI or control TTS. No hidden system or device action.");
    }else{
      append(body,"h3","Access Rescue");
      append(body,"p","This public preview cannot collect credentials. Use an authenticated owner-only broker or provider OAuth flow after connection gates pass.");
      line("Encrypted key intake","Disabled here");
      line("Direct publishing","Provider authorization required");
      line("Device control","Local owner consent required");
      const note=append(body,"div","Do not paste API keys, bot tokens or recovery phrases into this bubble or chat.","eightx8-warning");
      note.setAttribute("role","status");
      link("Universal access guide","/universal/");
    }
  }
  for(const [id,label] of tabDefs){
    const b=document.createElement("button");b.type="button";b.className="eightx8-tab";b.textContent=label;
    b.setAttribute("role","tab");b.setAttribute("aria-selected","false");
    b.addEventListener("click",()=>{active=id;render();});
    tabs.append(b);tabButtons.set(id,b);
  }
  panel.append(head,tabs,body);root.append(panel,launch);
  const setOpen=(v)=>{
    if(!v){cancelVoice();statusNote="Voice paused when bubble closed.";}
    panel.hidden=!v;launch.setAttribute("aria-expanded",String(v));
    if(v){render();close.focus();}else launch.focus();
  };
  launch.addEventListener("click",()=>setOpen(panel.hidden));
  close.addEventListener("click",()=>setOpen(false));
  root.addEventListener("keydown",e=>{if(e.key==="Escape"&&!panel.hidden)setOpen(false);});
  document.addEventListener("visibilitychange",()=>{if(document.hidden){cancelVoice();updateNote("Voice paused when page became hidden.");}});
  window.addEventListener("pagehide",cancelVoice);
  document.body.append(root);
})();
