"""Read-only provider connection admission for existing 8x8 User Edition.

This is a policy helper, NOT a second vault/credential collector, executor,
OAuth client, or a statement that any broker account is connected. The existing
one_fabric_secure_connection_intents_v1.py remains the intent authority.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet

ROOT = "fabric://8x8/core"
TRADING_CANDIDATES = frozenset({
    "alpaca", "tradier", "tastytrade", "tradestation", "schwab",
    "coinbase-advanced", "kraken", "gemini", "interactive-brokers",
    "robinhood-crypto", "oanda-us",
})
PUBLICATION_CANDIDATES = frozenset({
    "tiktok", "youtube", "instagram", "facebook", "threads", "x",
    "telegram", "discord", "pinterest", "bluesky", "linkedin",
    "google-business",
})
RESTRICTED_US = frozenset({"bitget"})
SENSITIVE_SCOPES = frozenset({
    "orders.place", "trade.execute", "order.write", "withdraw", "transfer",
    "wallet.sign", "seed.export", "publisher.post", "publisher.delete",
    "credentials.read", "vault.decrypt", "owner.admin", "terminal.execute",
})
TRADING_READ = frozenset({"account.read", "positions.read", "orders.read", "market.read"})
PUBLISHING_READ = frozenset({"profile.read", "channel.read", "page.read", "draft.prepare"})

@dataclass(frozen=True)
class Admission:
    provider: str
    domain: str
    account_slot: int | None
    authenticated_tenant: bool
    owner_consent: bool
    vault_origin_verified: bool
    vault_handle_present: bool
    provider_canary_verified: bool
    jurisdiction: str
    jurisdiction_verified: bool
    owner_stop_active: bool
    requested_scopes: FrozenSet[str]
    live_order_requested: bool = False
    raw_credential_submitted: bool = False

@dataclass(frozen=True)
class Decision:
    verdict: str
    reason: str
    connected: bool = False
    live_trading_authorized: bool = False
    public_post_authorized: bool = False

def evaluate(a: Admission) -> Decision:
    """Fail closed. Decision cannot authorize funds movement or public posts."""
    def deny(code: str) -> Decision:
        return Decision("BLOCKED", code)
    if not isinstance(a, Admission):
        return deny("INVALID_ADMISSION_TYPE")
    if a.raw_credential_submitted:
        return deny("DO_NOT_PASS_CREDENTIALS_TO_CHAT_OR_MCP")
    if not isinstance(a.provider, str) or not isinstance(a.requested_scopes, frozenset):
        return deny("INVALID_INPUT")
    if a.domain == "trading":
        if a.provider in RESTRICTED_US and isinstance(a.jurisdiction, str) and a.jurisdiction.upper() in {"US", "USA", "UNITED STATES"}:
            return deny("PROVIDER_RESTRICTED_IN_US")
        if a.provider not in TRADING_CANDIDATES:
            return deny("UNKNOWN_TRADING_PROVIDER")
        if type(a.account_slot) is not int or not (1 <= a.account_slot <= 100):
            return deny("INVALID_ACCOUNT_SLOT")
        if a.jurisdiction_verified is not True or not isinstance(a.jurisdiction, str) or not a.jurisdiction.strip():
            return deny("JURISDICTION_NOT_VERIFIED")
    elif a.domain == "publishing":
        if a.provider not in PUBLICATION_CANDIDATES or a.account_slot is not None:
            return deny("UNKNOWN_PUBLISHER_OR_SLOT")
    else:
        return deny("UNKNOWN_DOMAIN")
    scopes_allowed = TRADING_READ if a.domain == "trading" else PUBLISHING_READ
    if a.live_order_requested is not False or not a.requested_scopes or not a.requested_scopes <= scopes_allowed:
        return deny("EFFECT_SCOPE_NOT_AUTHORIZED")
    if a.requested_scopes & SENSITIVE_SCOPES:
        return deny("EFFECT_SCOPE_NOT_AUTHORIZED")
    if a.owner_stop_active is not False:
        return deny("OWNER_STOP_OR_ACTIVITY")
    if a.authenticated_tenant is not True or a.owner_consent is not True:
        return deny("OWNER_SESSION_AND_CONSENT_REQUIRED")
    if a.vault_origin_verified is not True:
        return deny("VERIFIED_VAULT_ORIGIN_REQUIRED")
    if a.vault_handle_present is not True:
        return Decision("READY_FOR_PROTECTED_ENROLLMENT", "SECURE_PROVIDER_FLOW_REQUIRED")
    if a.provider_canary_verified is not True:
        return Decision("BOUND_PENDING_CANARY", "READ_ONLY_CANARY_REQUIRED")
    return Decision("READ_ONLY_CONNECTION_VERIFIED", "LIVE_EFFECTS_NOT_GRANTED", connected=True)
