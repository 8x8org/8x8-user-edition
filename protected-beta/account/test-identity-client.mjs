import {test} from "node:test";
import assert from "node:assert/strict";
import {webcrypto} from "node:crypto";
import {createIdentityClient,isValidEmail,safeOrigin,base64url} from "./identity-client.mjs";
import {inspectIdentityNamespace,verifiedBetaIdentityProjection,LEGACY_PUBLIC_ID_CONTRACT} from "./identity-namespace.mjs";

const ORIGIN="https://8x8-user-8888-8x8-team-url.vercel.app";
const UID="8x8_"+"a".repeat(32);
const NOW_SESSION={access_token:"z".repeat(60),expires_in:900};
function harness(overrides={}){
 const requests=[];
 const cells=new Map();
 const storage={getItem:k=>cells.get(k)||null,setItem:(k,v)=>cells.set(k,v),removeItem:k=>cells.delete(k)};
 const fetchImpl=async (url,config)=>{
   requests.push({url,config});
   if(overrides.reject)throw new Error("EXPECTED_NETWORK_FAILURE");
   let status=200,data={};
   if(url.includes("/token?grant_type=pkce")||url.endsWith("/verify"))data=NOW_SESSION;
   if(url.endsWith("/one-fabric-id")){
     if(config.method==="GET"){status=404;data={state:"NOT_ENROLLED",authenticated:true,secret_collection:false};}
     else data={state:"8X8_ID_BOOTSTRAP_VERIFIED",eightx8_id:UID};
   }
   if(overrides.reply)({status,data}=overrides.reply(url,config,{status,data})||{status,data});
   return {ok:status<400,status,json:async()=>data};
 };
 const client=createIdentityClient({fetchImpl,storage,cryptoImpl:webcrypto,origin:ORIGIN});
 return {client,requests,cells,storage};
}

test("email validation excludes malformed addresses and oversize payloads",()=>{
 assert.equal(isValidEmail("user@example.com"),true);
 assert.equal(isValidEmail("oops"),false);
 assert.equal(isValidEmail("x@"+("a".repeat(250))+".com"),false);
});
test("identity origin requires HTTPS unless loopback",()=>{
 assert.equal(safeOrigin("https://8x8-user-8888-8x8-team-url.vercel.app"),true);
 assert.equal(safeOrigin("http://malicious.example"),false);
 assert.equal(safeOrigin("https://8x8-user-8888-8x8-team-url.vercel.app/path"),false);
 assert.equal(safeOrigin("http://127.0.0.1"),true);
});
test("unsafe web origin fails before any network",()=>{
 assert.throws(()=>createIdentityClient({fetchImpl:async()=>{},storage:{},cryptoImpl:webcrypto,origin:"http://evil.example"}),/SECURE_BROWSER/);
});
test("PKCE email OTP request uses verified origin and S256 challenge",async()=>{
 const h=harness();await h.client.emailLink(" user@example.com ");
 const r=h.requests[0];
 assert.match(r.url,/\/auth\/v1\/otp\?redirect_to=/);
 assert.ok(r.url.includes(encodeURIComponent(ORIGIN+"/account")));
 const b=JSON.parse(r.config.body);
 assert.equal(b.code_challenge_method,"s256");
 assert.equal(b.email,"user@example.com");
 assert.match(b.code_challenge,/^[A-Za-z0-9_-]{43}$/);
 assert.equal(r.config.credentials,"omit");
 assert.equal(r.config.redirect,"error");
 assert.ok(h.storage.getItem("8x8.id.pkce.verifier").length>=43);
 assert.equal(r.config.headers.Authorization,undefined);
});
test("credentials never sent with an identity email request",async()=>{
 const h=harness();await h.client.emailLink("hello@example.com");
 const payload=JSON.stringify(h.requests);
 assert.equal(payload.includes("service_role"),false);
 assert.equal(payload.includes("private_key"),false);
 assert.equal(payload.includes("wallet_seed"),false);
});
test("network failure removes PKCE verifier and does not authenticate",async()=>{
 const h=harness({reject:true});
 await assert.rejects(h.client.emailLink("hello@example.com"));
 assert.equal(h.storage.getItem("8x8.id.pkce.verifier"),null);
 assert.equal(h.client.sessionReady(),false);
});
test("auth code exchange is one-use and validates bound verifier",async()=>{
 const h=harness();await h.client.emailLink("hello@example.com");
 const code="11111111-2222-3333-4444-555555555555";
 const result=await h.client.exchangeCode(code);
 assert.equal(result.state,"SIGNED_IN");assert.equal(h.client.sessionReady(),true);
 assert.equal(h.storage.getItem("8x8.id.pkce.verifier"),null);
 const body=JSON.parse(h.requests[1].config.body);
 assert.equal(body.auth_code,code);
 assert.ok(body.code_verifier.length>=43);
 await assert.rejects(h.client.exchangeCode(code),/PKCE_VERIFIER_NOT_FOUND/);
});
test("substrings and oversized auth codes fail closed",async()=>{
 const h=harness();await h.client.emailLink("hello@example.com");
 await assert.rejects(h.client.exchangeCode("X"+"1".repeat(36)+"X"),/AUTH_CODE_INVALID/);
});
test("OTP verifies user email code and uses short-lived bearer",async()=>{
 const h=harness();await h.client.verifyEmailCode("hello@example.com","123456");
 assert.equal(h.client.sessionReady(),true);
 assert.equal(JSON.parse(h.requests[0].config.body).type,"email");
 await assert.rejects(h.client.verifyEmailCode("hello@example.com","never-raw-secrets"),/EMAIL_OTP_INVALID/);
});
test("no 8x8 ID request before authenticated session",async()=>{
 const h=harness();
 await assert.rejects(h.client.eightx8ID({create:true}),/SESSION_EXPIRED_OR_MISSING/);
 assert.equal(h.requests.length,0);
});
test("read-only GET says not enrolled, does not fabricate an ID",async()=>{
 const h=harness();await h.client.verifyEmailCode("hello@example.com","123456");
 const r=await h.client.eightx8ID();
 assert.deepEqual(r,{state:"NOT_ENROLLED"});
 assert.equal(h.requests[1].config.method,"GET");
 assert.match(h.requests[1].config.headers.Authorization,/^Bearer /);
});
test("ID issuance requires a separately requested POST, not email login",async()=>{
 const h=harness();await h.client.verifyEmailCode("hello@example.com","123456");
 const r=await h.client.eightx8ID({create:true});
 assert.equal(r.eightx8_id,UID);
 assert.equal(h.requests[1].config.method,"POST");
 assert.equal(h.requests[1].config.body,undefined);
});
test("forged backend ID response cannot become an ID",async()=>{
 const h=harness({reply:(url,config,res)=>{
   if(url.endsWith("/one-fabric-id")&&config.method==="POST")
     return {status:200,data:{state:"8X8_ID_BOOTSTRAP_VERIFIED",eightx8_id:"8x8_malicious"}};
   return res;
 }});
 await h.client.verifyEmailCode("hello@example.com","123456");
 await assert.rejects(h.client.eightx8ID({create:true}),/UNVERIFIED_ID_RESPONSE/);
});
test("bad auth session does not grant ID access",async()=>{
 const h=harness({reply:(url,config,res)=>{
   if(url.endsWith("/verify"))return {status:200,data:{access_token:"fake",expires_in:900}};
   return res;
 }});
 await assert.rejects(h.client.verifyEmailCode("hello@example.com","123456"),/INVALID_AUTHENTICATED_SESSION/);
 assert.equal(h.client.sessionReady(),false);
});
test("clearing browser session revokes local ability to make ID calls",async()=>{
 const h=harness();await h.client.verifyEmailCode("hello@example.com","123456");
 h.client.logout();assert.equal(h.client.sessionReady(),false);
 await assert.rejects(h.client.eightx8ID(),/SESSION_EXPIRED_OR_MISSING/);
});
test("no wallet, trade or publishing tool exists on identity client",()=>{
 const names=Object.keys(harness().client);
 for(const forbidden of ["trade","post","withdraw","seed","sign","vault","apikey"])assert.ok(!names.includes(forbidden));
});

test("historical ten-digit identifiers remain distinct and non-authenticating",()=>{
 assert.equal(LEGACY_PUBLIC_ID_CONTRACT.root,"fabric://8x8/core");
 assert.equal(inspectIdentityNamespace("0000000001").classification,"LEGACY_OWNER_RESERVED");
 assert.equal(inspectIdentityNamespace("0000000002").classification,"LEGACY_IPHONE_STAGING_RESERVED");
 for(const id of ["0000000001","0000000002","0000000003"]){
   const v=inspectIdentityNamespace(id);assert.equal(v.grant_authority,false);
   assert.equal(v.authentication,"NOT_PROVEN");
 }
});
test("beta sign-in ID cannot authenticate an OWNER_ROOT, iPhone, or any tenant binding",()=>{
 const r=verifiedBetaIdentityProjection(UID);
 assert.equal(r.id_namespace,"BETA_AUTH_USER_ID_NOT_LEGACY_PUBLIC_ID");
 assert.equal(r.legacy_public_id,null);assert.equal(r.legacy_binding_verified,false);
 assert.equal(r.owner_root_authorized,false);assert.equal(r.user_tenant_membership_verified,false);
 assert.equal(r.provider_connections_authorized,false);assert.equal(r.wallet_signing_authorized,false);
 assert.equal(r.live_trading_authorized,false);assert.equal(r.publishing_authorized,false);
});
test("reserved legacy ID submitted as a beta identity is denied, not migrated",()=>{
 for(const id of ["0000000001","0000000002","0000000003","8x8_invalid"]){
   assert.throws(()=>verifiedBetaIdentityProjection(id),/LEGACY_ID_BRIDGE_NOT_VERIFIED/);
 }
});
test("login and identity creation produce only the non-authoritative beta projection",async()=>{
 const h=harness();await h.client.verifyEmailCode("hello@example.com","123456");
 const r=await h.client.eightx8ID({create:true});
 assert.equal(r.eightx8_id,UID);
 assert.equal(r.legacy_public_id,null);
 assert.equal(r.owner_root_authorized,false);
 assert.equal(r.live_trading_authorized,false);
});
test("unexpected legacy owner ID from backend does not grant identity",async()=>{
 const h=harness({reply:(url,config,res)=>{
   if(url.endsWith("/one-fabric-id"))return {status:200,data:{
      state:"8X8_ID_BOOTSTRAP_VERIFIED",eightx8_id:"0000000001",
      owner_root_authorized:true}};
   return res;
 }});
 await h.client.verifyEmailCode("hello@example.com","123456");
 await assert.rejects(h.client.eightx8ID({create:true}),/UNVERIFIED_ID_RESPONSE/);
});

test("arbitrary 404 cannot impersonate authenticated not-enrolled status",async()=>{
 const h=harness({reply:(url,config,res)=>url.endsWith("/one-fabric-id")
  ?{status:404,data:{error:"missing deployment"}}:res});
 await h.client.verifyEmailCode("hello@example.com","123456");
 await assert.rejects(h.client.eightx8ID(),/UNVERIFIED_ID_ABSENCE/);
});
test("unauthenticated 404 or 404 bearing owner authority cannot become not-enrolled",async()=>{
 for(const body of [
  {state:"NOT_ENROLLED",authenticated:false,secret_collection:false},
  {state:"NOT_ENROLLED",authenticated:true},
  {state:"NOT_ENROLLED",secret_collection:false},
  {state:"NOT_ENROLLED",authenticated:true,secret_collection:true}
 ]){
 const h=harness({reply:(url,config,res)=>url.endsWith("/one-fabric-id")
 ?{status:404,data:body}:res});
 await h.client.verifyEmailCode("hello@example.com","123456");
 await assert.rejects(h.client.eightx8ID(),/UNVERIFIED_ID_ABSENCE/);
 }
});
test("404 on explicit ID creation is never treated as completed enrollment",async()=>{
 const h=harness({reply:(url,config,res)=>url.endsWith("/one-fabric-id") && config.method==="POST"
 ?{status:404,data:{state:"NOT_ENROLLED",authenticated:true,secret_collection:false}}:res});
 await h.client.verifyEmailCode("hello@example.com","123456");
 await assert.rejects(h.client.eightx8ID({create:true}),/ID_CREATION_NOT_CONFIRMED/);
});
