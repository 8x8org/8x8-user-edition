"""8x8 User Edition: tenant-bound MCP capability and entitlement policy, v1.

NOT an authentication implementation. The caller MUST verify an OAuth 2.1
access token's signature, issuer, audience/resource, expiry and scopes
via an audited server-side verifier BEFORE constructing Principal.
A client supplied JSON Principal is never authentication.
Public-safe, pure Python. No payments, device access or trades occur here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet
import re

# Canonical public target; private founder authority deliberately absent.
PLAN_FREE = "FREE"
PLAN_PLUS = "PLUS_8_88"
FREE_MINUTES_TOTAL = 88
PRICE_USD_CENTS_MONTH = 888
CATEGORIES = (
    "agents", "models", "memory", "world", "studio", "publishing", "finance",
    "trading", "wallet", "blockchain", "games", "radio", "books", "research",
    "planet", "security", "devices", "community", "settings",
)

# The tool registry is a public contract. A listed action is not a deployed tool.
# All action scopes require user OAuth unless explicitly public.
CAPABILITIES = {
    "catalog.read": ("public", None, "read"),
    "plans.read": ("public", None, "read"),
    "account.profile": ("identity.read", "account", "read"),
    "account.connections": ("connectors.read", "connectors", "read"),
    "account.connection_suggest": ("connectors.read", "connectors", "suggest"),
    "agents.list": ("agents.read", "agents", "read"),
    "agents.create_custom": ("agents.write", "agents", "write"),
    "agents.converse": ("agents.interact", "agents", "inference"),
    "memory.read": ("memory.read", "memory", "read"),
    "memory.write": ("memory.write", "memory", "write"),
    "studio.projects": ("studio.read", "studio", "read"),
    "studio.generate": ("studio.generate", "studio", "inference"),
    "publishing.drafts": ("publishing.read", "publishing", "read"),
    "publishing.prepare": ("publishing.write", "publishing", "write"),
    "publishing.publish": ("publishing.publish", "publishing", "effect"),
    "finance.research": ("finance.read", "finance", "read"),
    "trading.simulate": ("trading.research", "trading", "simulation"),
    "trading.order_preview": ("trading.research", "trading", "simulation"),
    "trading.execute": ("trading.execute", "trading", "effect"),
    "wallet.addresses": ("wallet.read", "wallet", "read"),
    "wallet.sign": ("wallet.sign", "wallet", "effect"),
    "devices.list": ("devices.read", "devices", "read"),
    "devices.storage_request": ("devices.connect", "devices", "sensitive"),
    "books.read": ("books.read", "books", "read"),
    "research.search": ("research.read", "research", "read"),
    "planet.public_sources": ("planet.read", "planet", "read"),
    "games.list": ("games.read", "games", "read"),
    "radio.list": ("radio.read", "radio", "read"),
    "community.posts": ("community.read", "community", "read"),
}

FREE_TIER_SCOPES = frozenset({
    "identity.read", "connectors.read", "agents.read", "agents.write",
    "agents.interact", "memory.read", "memory.write",
    "studio.read", "studio.generate", "publishing.read", "publishing.write",
    "finance.read", "trading.research", "wallet.read", "devices.read",
    "books.read", "research.read", "planet.read", "games.read",
    "radio.read", "community.read"
})

SAFE_DEFAULT_ARCHETYPES = (
    "seraphim-guide", "flash-assistant", "aegis-security",
    "jarvis-interface", "research-relay", "anvil-builder",
)
DENIED_CORE_PREFIXES = ("owner:", "founder:", "core-private:", "vault-root:")

@dataclass(frozen=True)
class Principal:
    # VERIFIED BY SERVER MIDDLEWARE, not from tool arguments.
    user_id: str
    tenant_id: str
    eightx8_id: str
    issuer: str
    audience: str
    scopes: FrozenSet[str]
    expires_at: int
    verified_by_server: bool = False

@dataclass(frozen=True)
class Entitlement:
    # Server-side Stripe webhook / internal meter source only.
    tenant_id: str
    plan: str = PLAN_FREE
    remaining_free_seconds: int = FREE_MINUTES_TOTAL * 60
    billing_verified: bool = False
    suspended: bool = False

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    category: str = ""
    effect_allowed: bool = False
    inference_budget_seconds: int = 0

def _tenant(value: str) -> bool:
    return bool(isinstance(value,str) and re.fullmatch(r"[0-9a-z][0-9a-z_-]{2,79}",value))

def valid_principal(p: Principal | None, now: int, *, issuer: str, resource: str) -> bool:
    if not isinstance(p, Principal) or p.verified_by_server is not True:
        return False
    if not (p.user_id and _tenant(p.tenant_id)
        and re.fullmatch(r"8x8_[0-9a-z]{20,40}",p.eightx8_id)
        and p.issuer == issuer and p.audience == resource
        and isinstance(p.expires_at,int) and p.expires_at > now
        and isinstance(p.scopes,frozenset)
        and all(isinstance(s,str) for s in p.scopes)):
        return False
    return True

def authorize(action: str, principal: Principal | None,
              resource_tenant: str | None, entitlement: Entitlement | None,
              *, now: int, issuer: str, resource: str,
              evidence: dict | None = None) -> Decision:
    """Request-time defense in depth; auth middleware and RLS are also mandatory.

    Trading/publication/signing/device effects cannot be unlocked by subscription.
    A positive 'ready' result is not itself a completed external action.
    """
    if action not in CAPABILITIES:
        return Decision(False,"UNKNOWN_ACTION")
    scope, category, operation = CAPABILITIES[action]
    if scope == "public":
        return Decision(True,"PUBLIC_INFORMATION_ONLY",category or "")
    if not valid_principal(principal,now,issuer=issuer,resource=resource):
        return Decision(False,"OAUTH_REQUIRED",category or "")
    if (not isinstance(resource_tenant,str)
        or resource_tenant != principal.tenant_id
        or not _tenant(resource_tenant)
        or resource_tenant.startswith(DENIED_CORE_PREFIXES)):
        return Decision(False,"TENANT_ISOLATION_DENIED",category or "")
    if (not isinstance(entitlement,Entitlement)
        or entitlement.tenant_id != principal.tenant_id or entitlement.suspended
        or entitlement.plan not in (PLAN_FREE,PLAN_PLUS)
        or not isinstance(entitlement.remaining_free_seconds,int)
        or entitlement.remaining_free_seconds < 0):
        return Decision(False,"ENTITLEMENT_NOT_VERIFIED",category or "")
    if scope not in principal.scopes:
        return Decision(False,"OAUTH_SCOPE_DENIED",category or "")
    if operation=="effect":
        # Disallow by default: separate signed execution grant is not implemented.
        return Decision(False,"EXTERNAL_EFFECT_REQUIRES_SEPARATE_GRANT",category or "")
    if operation=="sensitive":
        return Decision(False,"DEVICE_PRESENCE_AND_CONSENT_NOT_VERIFIED",category or "")
    if operation=="inference":
        if entitlement.plan == PLAN_PLUS and entitlement.billing_verified:
            return Decision(True,"PAID_PLAN_VERIFIED_PROVIDER_QUOTA_STILL_REQUIRED",
                            category or "",False,0)
        if entitlement.remaining_free_seconds <= 0:
            return Decision(False,"FREE_ALLOWANCE_EXHAUSTED",category or "")
        return Decision(True,"FREE_ALLOWANCE_AVAILABLE_PROVIDER_NOT_GUARANTEED",
                        category or "",False,entitlement.remaining_free_seconds)
    return Decision(True,"TENANT_SCOPED_NON_EFFECT_ONLY",category or "")

def verify_meter_receipt(*, tenant: str, entitlement: Entitlement,
                         seconds: int, provider_response_verified: bool,
                         request_id: str, prior_ids: FrozenSet[str]) -> tuple[Entitlement, bool]:
    """Pure quota accounting: caller MUST persist atomic unique request IDs server-side."""
    if (not _tenant(tenant) or tenant != entitlement.tenant_id
        or not isinstance(seconds,int) or isinstance(seconds,bool)
        or seconds <= 0 or seconds > 3600 or not provider_response_verified
        or not isinstance(request_id,str) or not re.fullmatch(r"[A-Za-z0-9_-]{12,128}",request_id)
        or request_id in prior_ids or entitlement.suspended):
        return entitlement, False
    if entitlement.plan == PLAN_PLUS and entitlement.billing_verified:
        return entitlement, True  # Plan-specific abuse/provider limits remain independent.
    if seconds > entitlement.remaining_free_seconds:
        return entitlement,False
    return Entitlement(entitlement.tenant_id, entitlement.plan,
                       entitlement.remaining_free_seconds-seconds,
                       entitlement.billing_verified,entitlement.suspended), True

def public_onboarding_steps() -> tuple[str,...]:
    return (
        "Sign in to 8x8 ID using an implemented, verified identity-provider flow.",
        "Connect this 8x8 MCP using OAuth 2.1 + S256 PKCE and resource-bound scopes.",
        "Link ChatGPT identity via Sign in with ChatGPT only if the app is approved for it.",
        "Connect each external app through that provider's own user consent.",
        "Select protected default agent templates or create tenant-owned custom agents.",
        "Grant memory and voice permissions separately; no implicit conversation import.",
        "Connect financial accounts for read-only research, then separately approve any trade.",
        "Review publishing destinations, content rights and each external publication approval.",
        "Install optional on-device bridge with explicit local presence and revocable leases.",
        "Review 88-minute free proposal or an actual verified $8.88/month subscription."
    )
