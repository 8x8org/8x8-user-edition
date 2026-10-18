// ©️8x8 One Fabric protected-beta browser identity client.
// Only a public Supabase publishable key is embedded. Never send provider credentials here.
export const CONFIG=Object.freeze({
  authOrigin:"https://kjvmagncyednwfezbjww.supabase.co",
  publishableKey:"sb_publishable_N1to5h-EWYkMefO3WodBhA_Bkyr0LxH",
  idFunction:"one-fabric-id",
  fabricRoot:"fabric://8x8/core",
});
export function isValidEmail(email) {
  return typeof email==="string" && email.length<=254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
export function safeOrigin(origin) {
  if(typeof origin!=="string") return false;
  try { const u=new URL(origin);
    return !u.username&&!u.password&&!u.search&&!u.hash&&u.pathname==="/"&&
      (u.protocol==="https:"||((u.hostname==="localhost"||u.hostname==="127.0.0.1")&&u.protocol==="http:"));
  } catch {return false;}
}
export function base64url(bytes) {
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
}
export function createIdentityClient({fetchImpl,storage,cryptoImpl,origin,config=CONFIG}={}) {
  if(typeof fetchImpl!=="function"||!storage||!cryptoImpl?.getRandomValues||!cryptoImpl?.subtle||!safeOrigin(origin))
    throw new Error("SECURE_BROWSER_ENVIRONMENT_REQUIRED");
  if(!/^https:\/\/[a-z0-9.-]+$/.test(config.authOrigin)||!/^sb_publishable_/.test(config.publishableKey))
    throw new Error("INVALID_PUBLIC_IDENTITY_ORIGIN");
  const headers=()=>({"apikey":config.publishableKey,"Content-Type":"application/json"});
  let accessToken=null,expiresAt=0;
  async function jsonRequest(path,body,token) {
    if(!path.startsWith("/auth/v1/")&&!path.startsWith("/functions/v1/"))throw Error("INVALID_IDENTITY_ENDPOINT");
    const method=body===undefined?"GET":"POST";
    const response=await fetchImpl(config.authOrigin+path,{
      method,headers:{...headers(),...(token?{"Authorization":"Bearer "+token}:{})},
      ...(body===undefined?{}:{body:body===null?undefined:JSON.stringify(body)}),
      cache:"no-store",redirect:"error",credentials:"omit"});
    let data={};
    try{data=await response.json();}catch{data={};}
    if(!response.ok&&!(response.status===404&&path==="/functions/v1/"+config.idFunction))
      throw new Error("IDENTITY_SERVICE_"+String(response.status));
    return {status:response.status,data};
  }
  function sessionReady(){
    return typeof accessToken==="string"&&accessToken.length>32&&expiresAt>Date.now()+30000;
  }
  function consumeSession(data) {
    if(typeof data?.access_token!=="string"||data.access_token.length<33||
       !Number.isFinite(data.expires_in)||data.expires_in<31||data.expires_in>86400)
      throw new Error("INVALID_AUTHENTICATED_SESSION");
    accessToken=data.access_token;
    expiresAt=Date.now()+data.expires_in*1000;
    return true;
  }
  async function emailLink(email) {
    email=email?.trim();
    if(!isValidEmail(email))throw Error("VALID_EMAIL_REQUIRED");
    const random=new Uint8Array(48); cryptoImpl.getRandomValues(random);
    const verifier=base64url(random);
    const digest=new Uint8Array(await cryptoImpl.subtle.digest("SHA-256",new TextEncoder().encode(verifier)));
    storage.setItem("8x8.id.pkce.verifier",verifier);
    try{
      await jsonRequest("/auth/v1/otp?redirect_to="+encodeURIComponent(origin+"/account"),{
        email,create_user:true,code_challenge:base64url(digest),code_challenge_method:"s256"
      });
      return {state:"EMAIL_SENT_OR_ACCEPTED",redirect:origin+"/account"};
    }catch(e){storage.removeItem("8x8.id.pkce.verifier");throw e;}
  }
  async function exchangeCode(code){
    if(typeof code!=="string"||!/[a-f0-9-]{30,64}/i.test(code)||code.length>128)
      throw Error("AUTH_CODE_INVALID");
    const verifier=storage.getItem("8x8.id.pkce.verifier");
    if(!verifier||verifier.length<43||verifier.length>128)throw Error("PKCE_VERIFIER_NOT_FOUND");
    storage.removeItem("8x8.id.pkce.verifier");
    const r=await jsonRequest("/auth/v1/token?grant_type=pkce",{auth_code:code,code_verifier:verifier});
    consumeSession(r.data);
    return {state:"SIGNED_IN",sessionExpiresAt:expiresAt};
  }
  async function verifyEmailCode(email,code){
    if(!isValidEmail(email)||typeof code!=="string"||!/^[0-9]{6,8}$/.test(code))
      throw Error("EMAIL_OTP_INVALID");
    const r=await jsonRequest("/auth/v1/verify",{email,token:code,type:"email"});
    consumeSession(r.data);storage.removeItem("8x8.id.pkce.verifier");
    return {state:"SIGNED_IN",sessionExpiresAt:expiresAt};
  }
  async function eightx8ID({create=false}={}){
    if(!sessionReady())throw Error("SESSION_EXPIRED_OR_MISSING");
    const path="/functions/v1/"+config.idFunction;
    const r=await jsonRequest(path,create?null:undefined,accessToken);
    if(r.status===404)return {state:"NOT_ENROLLED"};
    if(r.data?.state!=="8X8_ID_BOOTSTRAP_VERIFIED"||
       typeof r.data?.eightx8_id!=="string"||!/^8x8_[a-f0-9]{32}$/.test(r.data.eightx8_id))
      throw Error("UNVERIFIED_ID_RESPONSE");
    return {state:"8X8_ID_BOOTSTRAP_VERIFIED",eightx8_id:r.data.eightx8_id};
  }
  function logout(){accessToken=null;expiresAt=0;storage.removeItem("8x8.id.pkce.verifier");}
  return {emailLink,exchangeCode,verifyEmailCode,eightx8ID,sessionReady,logout};
}
