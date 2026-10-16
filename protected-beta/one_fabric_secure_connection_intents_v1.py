"""8x8 One Fabric User Edition: fail-closed cross-domain connection intents.

Public-safe policy component, NOT a deployed Vault, OAuth server or trade executor.
The verified `actor` MUST come from server-authenticated 8x8 middleware, never the
ChatGPT tool arguments, user-editable metadata, Telegram username or browser ID.
No API key, secret, passphrase, user password or wallet seed is accepted, logged,
returned or stored by this module.  Never paste secrets into a ChatGPT message.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
import secrets
from typing import FrozenSet, Optional

VERSION = "8x8.secure_connection_intents.v1"
FABRIC_ROOT = "fabric://8x8/core"
MAX_ACCOUNT_SLOTS = 5
DEFAULT_LIFETIME_SECONDS = 300
TRADING_API_PROVIDER = "bitget"
NO_EXTERNAL_UNLIMITED = "PROVIDER_QUOTAS_AND_TERMS_STILL_APPLY"

@dataclass(frozen=True)
class Provider:
    id: str
    domain: str
    auth_mode: str
    scopes: FrozenSet[str]
    user_onboarding: str
    secret_form_required: bool = False

# No credentials or live endpoint URLs are included. The actual provider OAuth
# config and callback allowlists belong in a verified private deployment.
_PROVIDERS = [
    Provider("bitget", "trading", "SECURE_VAULT_API_KEY_FORM", frozenset({"account.read", "positions.read", "orders.read"}),
             "Generate a dedicated Bitget API key with read-only permissions and IP restrictions; securely enter key, secret and API passphrase in the separate verified 8x8 Vault site. Disable transfers/withdrawals.", True),
    Provider("telegram", "publishing", "PROVIDER_BOT_ADMIN_AND_SECURE_VAULT", frozenset({"channel.read", "draft.prepare"}),
             "Create or manage a bot through Telegram, grant only required channel privileges, and enter its token in the verified 8x8 Vault site, never in chat.", True),
    Provider("discord", "publishing", "OAUTH_OR_VERIFIED_BOT_INSTALL", frozenset({"channel.read", "draft.prepare"}), "Authorize the minimal server/channel permissions in the provider flow."),
    Provider("bluesky", "publishing", "PROVIDER_AUTH_REVIEW", frozenset({"profile.read", "draft.prepare"}), "Use a supported provider authentication method; store any credential only in the verified 8x8 Vault."),
    Provider("youtube", "publishing", "OAUTH_USER_CONSENT", frozenset({"channel.read", "draft.prepare"}), "Use Google's official OAuth consent flow."),
    Provider("instagram", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use the supported Meta professional-account authorization path."),
    Provider("facebook", "publishing", "OAUTH_USER_CONSENT", frozenset({"page.read", "draft.prepare"}), "Use the supported Meta Page permissions and review."),
    Provider("threads", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use the supported Threads official authorization flow."),
    Provider("tiktok", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use supported TikTok login/Content Posting API access and app review."),
    Provider("x", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use X official authorization and applicable API access."),
    Provider("pinterest", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use Pinterest developer authorization."),
    Provider("linkedin", "publishing", "OAUTH_USER_CONSENT", frozenset({"profile.read", "draft.prepare"}), "Use the LinkedIn approved product scopes and authorization flow."),
    Provider("stripe", "billing", "HOSTED_STRIPE_CHECKOUT", frozenset({"billing.read"}), "Use hosted checkout and verify signed server-side webhooks; never collect card numbers in 8x8 chat."),
    Provider("crypto-checkout", "billing", "NETWORK_SPECIFIC_INVOICE", frozenset({"invoice.read"}), "Use only supported verified network/asset invoices and confirmations. Do not request a seed phrase."),
    Provider("wallet-watch", "wallet", "SIGNED_ADDRESS_CHALLENGE", frozenset({"wallet.address.read"}), "Start with watch-only addresses and signed ownership challenges, not imported seed phrases."),
    Provider("termux", "devices", "LOCAL_DEVICE_CONSENT", frozenset({"device.status.read"}), "Use an opt-in local installer; owner-visible stop, revocation and short capability leases."),
]
PROVIDERS = {p.id:p for p in _PROVIDERS}

# Future trade, account transfer, public-post, signer, and terminal-exec effects
# are NOT obtainable from any account-link intent or a paid subscription.
FORBIDDEN_DELEGATIONS = frozenset({
    "orders.place", "orders.cancel", "trade.execute", "withdraw", "transfer",
    "publisher.post", "publisher.delete", "wallet.sign", "seed.export",
    "terminal.execute", "device.control", "adb.pair", "mining.execute",
    "stake.execute", "owner.admin", "owner.memory", "owner.vault",
})
SECRET_KEYS = frozenset({
    "api_key", "apikey", "access_key", "secret", "secret_key", "secretkey",
    "passphrase", "password", "bot_token", "token", "private_key",
    "seed", "seed_phrase", "mnemonic", "wallet_seed", "credential",
})

@dataclass(frozen=True)
class Actor:
    # Construct ONLY after trusted server-side signature, issuer, audience,
    # expiry, resource, scope, tenant membership and session checks.
    user_id: str
    tenant_id: str
    eightx8_id: str
    server_authenticated: bool
    scopes: FrozenSet[str]

@dataclass(frozen=True)
class Intent:
    intent_id: str
    nonce_digest: str
    tenant_id: str
    eightx8_id: str
    provider: str
    slot: Optional[int]
    scopes: tuple[str, ...]
    issued_at: int
    expires_at: int
    state: str = "PREPARED_NOT_CONNECTED"

class ConnectionDenied(ValueError):
    pass

class SecretInChatRejected(ConnectionDenied):
    pass

def _validate_actor(actor: Actor) -> None:
    if (not isinstance(actor, Actor) or actor.server_authenticated is not True
        or not isinstance(actor.user_id, str) or len(actor.user_id) < 3
        or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,79}",actor.tenant_id)
        or not re.fullmatch(r"8x8_[a-z0-9]{20,40}",actor.eightx8_id)
        or not isinstance(actor.scopes,frozenset)):
        raise ConnectionDenied("VERIFIED_8X8_SESSION_REQUIRED")
    if "connections.create" not in actor.scopes:
        raise ConnectionDenied("CONNECTION_SCOPE_REQUIRED")

def assert_no_secret_fields(values: object) -> None:
    """Reject potential secret names anywhere in nested caller input.

    This is defense-in-depth for MCP tool argument schemas. Raw message content
    must NEVER be sent to this API; it might contain an unlabelled secret.
    """
    if isinstance(values,dict):
        for key,value in values.items():
            normalized=re.sub(r"[^a-z0-9]","",str(key).lower())
            if normalized in {re.sub(r"[^a-z0-9]","",k) for k in SECRET_KEYS}:
                raise SecretInChatRejected("OPEN_SEPARATE_SECURE_VAULT_FORM")
            assert_no_secret_fields(value)
    elif isinstance(values,(list,tuple)):
        for element in values:assert_no_secret_fields(element)

def propose_connection(actor: Actor, provider: str, *, slot: Optional[int],
                       scopes: FrozenSet[str], now: int,
                       submitted_fields: Optional[dict] = None) -> Intent:
    """Generate a metadata-only, tenant-bound proposal; NO secret capture.

    The backend MUST persist the one-use nonce hash atomically and implement
    a separate authenticated vault-origin callback before an intent may become
    connected. No endpoint URL is generated by this function.
    """
    _validate_actor(actor)
    if submitted_fields is not None:
        assert_no_secret_fields(submitted_fields)
        if submitted_fields:
            raise ConnectionDenied("NO_EXTRA_CREDENTIAL_OR_UNREVIEWED_FIELDS")
    spec=PROVIDERS.get(provider)
    if not spec:raise ConnectionDenied("UNSUPPORTED_PROVIDER")
    if not isinstance(scopes,frozenset) or not scopes or not all(isinstance(x,str) for x in scopes):
        raise ConnectionDenied("INVALID_SCOPES")
    if scopes & FORBIDDEN_DELEGATIONS or not scopes.issubset(spec.scopes):
        raise ConnectionDenied("UNAPPROVED_ACTION_SCOPE")
    if provider == TRADING_API_PROVIDER:
        if type(slot) is not int or not 1<=slot<=MAX_ACCOUNT_SLOTS:
            raise ConnectionDenied("BITGET_SLOT_MUST_BE_1_TO_5")
    elif slot is not None:
        raise ConnectionDenied("SLOT_IS_ONLY_FOR_EXCHANGE_ACCOUNT")
    if type(now) is not int or now <= 0:
        raise ConnectionDenied("INVALID_TIME")
    # Distinct opaque nonce provides correlation to the backend, never auth.
    nonce=secrets.token_urlsafe(32)
    return Intent(intent_id="intent_"+secrets.token_hex(16),
          nonce_digest=sha256(nonce.encode()).hexdigest(),
          tenant_id=actor.tenant_id,eightx8_id=actor.eightx8_id,
          provider=provider,slot=slot,scopes=tuple(sorted(scopes)),
          issued_at=now,expires_at=now+DEFAULT_LIFETIME_SECONDS)

def validate_intent_owner(actor: Actor, intent: Intent, *, now: int) -> bool:
    _validate_actor(actor)
    return (isinstance(intent,Intent) and intent.tenant_id == actor.tenant_id
       and intent.eightx8_id == actor.eightx8_id
       and type(now) is int and intent.issued_at <= now < intent.expires_at
       and intent.state == "PREPARED_NOT_CONNECTED")

def agent_guidance(provider: str) -> dict:
    """Safe MCP read-only response. No credentials, no fictitious link."""
    p=PROVIDERS.get(provider)
    if p is None:raise ConnectionDenied("UNSUPPORTED_PROVIDER")
    return {"root":FABRIC_ROOT,"provider":p.id,"domain":p.domain,
            "authentication_route":p.auth_mode,
            "approved_initial_scopes":sorted(p.scopes),
            "secret_form_required":p.secret_form_required,
            "guidance":p.user_onboarding,
            "state":"GUIDE_ONLY_NO_LIVE_VAULT_LINK",
            "provider_permissions_not_granted":True,
            "official_platform_limits_still_apply":True,
            "no_secret_in_chat":True,
            "next_step":"AWAIT_VERIFIED_8X8_ID_AND_SECURE_VAULT_HOST_DEPLOYMENT"}

def plan_truth() -> dict:
    return {"free_target_seconds_per_day":88*60,
            "free_grant_active":False,"plus_target_usd_cents_per_month":888,
            "paid_entitlement_active":False,
            "paid_infinite_throughput_guaranteed":False,
            "external_social_api_unlimited":False,
            "user_authorization_required_per_provider":True,
            "budget_ledger_and_billing_webhook_required":True,
            "tokenomics_8x8_coin_payments_live_verified":False}
