#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CommercialScenario:
    active_users: int
    subscription_price_monthly: float
    subscription_conversion_fraction: float
    creator_gmv_monthly: float
    marketplace_commission_fraction: float
    services_revenue_monthly: float
    education_revenue_monthly: float
    licensing_revenue_monthly: float
    grants_monthly: float
    fixed_cost_monthly: float
    variable_cost_per_active_user: float


def evaluate(s: CommercialScenario) -> dict:
    subscribers = s.active_users * s.subscription_conversion_fraction
    subscription = subscribers * s.subscription_price_monthly
    marketplace = s.creator_gmv_monthly * s.marketplace_commission_fraction
    gross = subscription + marketplace + s.services_revenue_monthly + s.education_revenue_monthly + s.licensing_revenue_monthly + s.grants_monthly
    variable_cost = s.active_users * s.variable_cost_per_active_user
    total_cost = s.fixed_cost_monthly + variable_cost
    contribution = gross - total_cost
    result = {
        "inputs": asdict(s),
        "derived": {
            "modeled_subscribers": subscribers,
            "subscription_revenue_monthly": subscription,
            "marketplace_commission_monthly": marketplace,
            "modeled_gross_revenue_monthly": gross,
            "modeled_variable_cost_monthly": variable_cost,
            "modeled_total_cost_monthly": total_cost,
            "modeled_contribution_monthly": contribution,
        },
        "truth": {
            "scenario_only": True,
            "actual_users": False,
            "actual_revenue": False,
            "profitability_claim": False,
            "financial_commitment": False,
        },
    }
    result["sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


def sensitivity(base: CommercialScenario, user_multipliers=(0.5, 1.0, 2.0), conversion_multipliers=(0.5, 1.0, 1.5)) -> list[dict]:
    out = []
    for um in user_multipliers:
        for cm in conversion_multipliers:
            s = CommercialScenario(
                active_users=max(0, round(base.active_users * um)),
                subscription_price_monthly=base.subscription_price_monthly,
                subscription_conversion_fraction=min(1.0, max(0.0, base.subscription_conversion_fraction * cm)),
                creator_gmv_monthly=base.creator_gmv_monthly * um,
                marketplace_commission_fraction=base.marketplace_commission_fraction,
                services_revenue_monthly=base.services_revenue_monthly * um,
                education_revenue_monthly=base.education_revenue_monthly * um,
                licensing_revenue_monthly=base.licensing_revenue_monthly * um,
                grants_monthly=base.grants_monthly,
                fixed_cost_monthly=base.fixed_cost_monthly,
                variable_cost_per_active_user=base.variable_cost_per_active_user,
            )
            row = evaluate(s)
            row["sensitivity"] = {"user_multiplier": um, "conversion_multiplier": cm}
            out.append(row)
    return out


if __name__ == "__main__":
    # Purely synthetic fixture. It is deliberately not labeled as an 8x8 forecast.
    fixture = CommercialScenario(1000, 10.0, 0.05, 5000.0, 0.05, 0.0, 0.0, 0.0, 0.0, 2500.0, 0.50)
    print(json.dumps({"base": evaluate(fixture), "sensitivity": sensitivity(fixture)}, indent=2, sort_keys=True))
