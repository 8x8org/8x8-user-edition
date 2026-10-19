// Browser controller: only the verified Supabase URL is contacted, no account-provider secrets.
import {createIdentityClient,CONFIG,isValidEmail} from "./identity-client.mjs";
const $=id=>document.getElementById(id);
const info=$("identity-status"),details=$("identity-detail"),idBox=$("verified-id");
let client;
function setStatus(message){info.textContent=message;}
function signedIn(){ $("identity-create").disabled=false;$("identity-check").disabled=false;$("identity-logout").disabled=false; }
async function inspect(){
 const reply=await client.eightx8ID();
 idBox.textContent=reply.state==="8X8_ID_BOOTSTRAP_VERIFIED"?reply.eightx8_id:"Not enrolled yet";
 details.textContent=reply.state==="NOT_ENROLLED"?
  "A verified session exists. Creating a beta sign-in ID does NOT claim legacy 0000000001 (owner) or 0000000002 (iPhone staging).":
  "Beta ID authenticated for this session; 10-digit legacy ID mapping is NOT verified. No owner powers, Vault, provider access, trading, publishing or wallet signing granted.";
 setStatus(reply.state);
}
function report(error){setStatus("Action unavailable: "+String(error?.message||"UNKNOWN").replace(/[^A-Z0-9_]/gi,"").slice(0,70));}
try{
 client=createIdentityClient({fetchImpl:window.fetch.bind(window),storage:window.sessionStorage,
   cryptoImpl:window.crypto,origin:window.location.origin});
 setStatus("Sign in through your own email address. No broker passwords, API keys, or wallet seeds are accepted.");
 $("identity-email-form").addEventListener("submit",async e=>{
   e.preventDefault();
   const email=$("identity-email").value.trim();
   if(!isValidEmail(email)){setStatus("VALID_EMAIL_REQUIRED");return;}
   setStatus("Requesting your email sign-in link…");
   try{await client.emailLink(email);setStatus("Email request accepted. Open the link on this browser, or enter the email OTP code if provided. The account callback URL must be registered in Supabase Auth.");}
   catch(err){report(err);}
 });
 $("identity-otp-form").addEventListener("submit",async e=>{
   e.preventDefault();
   try{await client.verifyEmailCode($("identity-email").value.trim(),$("identity-otp").value.trim());signedIn();await inspect();}
   catch(err){report(err);}
 });
 $("identity-check").addEventListener("click",async()=>{try{await inspect();}catch(err){report(err)}});
 $("identity-create").addEventListener("click",async()=>{
   if(!window.confirm("Create a beta sign-in ID? It does not bind legacy 8x8 public IDs, grant owner powers, connect providers or authorize trades."))return;
   try{await client.eightx8ID({create:true});await inspect();}
   catch(err){report(err)}
 });
 $("identity-logout").addEventListener("click",()=>{client.logout();$("identity-create").disabled=true;$("identity-check").disabled=true;$("identity-logout").disabled=true;idBox.textContent="Not signed in";setStatus("Local session cleared.");});
 const locationUrl=new URL(window.location.href);
 const code=locationUrl.searchParams.get("code");
 if(code){
   locationUrl.searchParams.delete("code");locationUrl.searchParams.delete("sb_flow_id");
   history.replaceState(null,"",locationUrl.pathname+locationUrl.search+locationUrl.hash);
   setStatus("Verifying the one-time authentication code…");
   try{await client.exchangeCode(code);signedIn();await inspect();}
   catch(err){report(err);}
 }
}catch(err){report(err);details.textContent="Identity connection requires HTTPS, a modern browser and a verified Auth redirect allowlist."}
