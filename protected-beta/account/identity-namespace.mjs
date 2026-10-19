// ©️8x8 One Fabric — read-only legacy/public-ID namespace reconciliation.
// Canonical source: horbolsi/8x8/docs/architecture/ACCOUNT_AGENT_FLEET_AND_IMPORT_MODEL_V1.md
// This projection never authenticates a human, links an account, or reserves an ID.
export const LEGACY_PUBLIC_ID_CONTRACT = Object.freeze({
  root:"fabric://8x8/core",
  ownerPublicId:"0000000001",
  iphoneAcceptancePublicId:"0000000002",
  source:"horbolsi/8x8:docs/architecture/ACCOUNT_AGENT_FLEET_AND_IMPORT_MODEL_V1.md",
  ownerState:"HISTORICAL_RESERVED_NOT_NEW_BETA_AUTHENTICATION",
  iphoneState:"HISTORICAL_STAGING_ACCEPTANCE_NOT_PRODUCTION_CUSTOMER",
  betaToLegacyBinding:"NOT_VERIFIED",
  tenantMembershipVerified:false,
  deviceBindingVerified:false,
  signingAuthorityGranted:false,
  brokerAuthorityGranted:false
});
const BETA_ID=/^8x8_[a-f0-9]{32}$/;
const PUBLIC_ID=/^[0-9]{10}$/;
export function inspectIdentityNamespace(value){
  if(typeof value!=="string")return {classification:"INVALID",grant_authority:false};
  if(value===LEGACY_PUBLIC_ID_CONTRACT.ownerPublicId)
    return {classification:"LEGACY_OWNER_RESERVED",grant_authority:false,authentication:"NOT_PROVEN"};
  if(value===LEGACY_PUBLIC_ID_CONTRACT.iphoneAcceptancePublicId)
    return {classification:"LEGACY_IPHONE_STAGING_RESERVED",grant_authority:false,authentication:"NOT_PROVEN"};
  if(PUBLIC_ID.test(value))
    return {classification:"LEGACY_PUBLIC_UNMAPPED",grant_authority:false,authentication:"NOT_PROVEN"};
  if(BETA_ID.test(value))
    return {classification:"BETA_AUTH_USER_ID",grant_authority:false,
      public_legacy_id:null,legacy_binding_verified:false,owner_root_authorized:false,
      user_tenant_membership_verified:false,account_connections_authorized:false,
      wallet_signing_authorized:false,live_trading_authorized:false,
      publishing_authorized:false};
  return {classification:"INVALID",grant_authority:false};
}
export function verifiedBetaIdentityProjection(value){
  const identity=inspectIdentityNamespace(value);
  if(identity.classification!=="BETA_AUTH_USER_ID")throw new Error("LEGACY_ID_BRIDGE_NOT_VERIFIED");
  return {id_namespace:"BETA_AUTH_USER_ID_NOT_LEGACY_PUBLIC_ID",
    legacy_public_id:null,legacy_binding_verified:false,
    owner_root_authorized:false,user_tenant_membership_verified:false,
    provider_connections_authorized:false,wallet_signing_authorized:false,
    live_trading_authorized:false,publishing_authorized:false};
}
