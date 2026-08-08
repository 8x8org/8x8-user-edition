#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from statistics import mean, pstdev
from typing import Iterable, Sequence

ENGINE_VERSION = "1.0.0"
DEFAULT_SEED = 8888888


@dataclass(frozen=True)
class MarketConfig:
    fee_bps: float = 10.0
    half_spread_bps: float = 2.0
    slippage_bps_per_unit: float = 0.5
    max_fill_units: float = 100.0
    partial_fill_fraction: float = 0.5
    funding_bps_per_step: float = 0.0
    maintenance_margin_fraction: float = 0.10


@dataclass(frozen=True)
class Order:
    side: str
    quantity: float
    reference_price: float
    leverage: float = 1.0


@dataclass(frozen=True)
class Fill:
    status: str
    requested_quantity: float
    filled_quantity: float
    fill_price: float
    gross_notional: float
    fee: float
    spread_cost: float
    slippage_cost: float


@dataclass(frozen=True)
class EquityStats:
    final_equity: float
    max_drawdown_fraction: float
    mean_return: float
    volatility: float
    sharpe_like: float


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_obj(obj: object) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def execute_order(order: Order, market: MarketConfig, outage: bool = False) -> Fill:
    if outage:
        return Fill("REJECTED_OUTAGE", order.quantity, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    if order.side not in {"BUY", "SELL"} or order.quantity <= 0 or order.reference_price <= 0 or order.leverage <= 0:
        return Fill("REJECTED_INVALID", order.quantity, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    requested = order.quantity
    if requested > market.max_fill_units:
        filled = min(market.max_fill_units, requested * market.partial_fill_fraction)
        status = "PARTIAL"
    else:
        filled = requested
        status = "FILLED"

    direction = 1 if order.side == "BUY" else -1
    spread_rate = market.half_spread_bps / 10_000.0
    slippage_bps = market.slippage_bps_per_unit * filled
    slippage_rate = slippage_bps / 10_000.0
    fill_price = order.reference_price * (1.0 + direction * (spread_rate + slippage_rate))
    gross = filled * fill_price
    fee = abs(gross) * market.fee_bps / 10_000.0
    spread_cost = filled * order.reference_price * spread_rate
    slippage_cost = filled * order.reference_price * slippage_rate
    return Fill(status, requested, filled, fill_price, gross, fee, spread_cost, slippage_cost)


def funding_cost(position_notional: float, market: MarketConfig, steps: int) -> float:
    return abs(position_notional) * (market.funding_bps_per_step / 10_000.0) * steps


def liquidation_price(entry_price: float, side: str, leverage: float, maintenance_margin_fraction: float) -> float:
    if entry_price <= 0 or leverage <= 0 or side not in {"LONG", "SHORT"}:
        raise ValueError("invalid liquidation inputs")
    initial_margin_fraction = 1.0 / leverage
    buffer = max(0.0, initial_margin_fraction - maintenance_margin_fraction)
    if side == "LONG":
        return entry_price * (1.0 - buffer)
    return entry_price * (1.0 + buffer)


def equity_curve(initial_equity: float, returns: Sequence[float]) -> list[float]:
    eq = [float(initial_equity)]
    for r in returns:
        eq.append(eq[-1] * (1.0 + r))
    return eq


def max_drawdown_fraction(curve: Sequence[float]) -> float:
    peak = curve[0]
    worst = 0.0
    for value in curve:
        peak = max(peak, value)
        if peak > 0:
            worst = max(worst, (peak - value) / peak)
    return worst


def summarize_equity(initial_equity: float, returns: Sequence[float]) -> EquityStats:
    curve = equity_curve(initial_equity, returns)
    mu = mean(returns) if returns else 0.0
    vol = pstdev(returns) if len(returns) > 1 else 0.0
    sharpe_like = mu / vol * math.sqrt(len(returns)) if vol > 0 else 0.0
    return EquityStats(curve[-1], max_drawdown_fraction(curve), mu, vol, sharpe_like)


def risk_of_ruin_bootstrap(
    returns: Sequence[float],
    initial_equity: float,
    ruin_fraction: float = 0.5,
    paths: int = 2000,
    horizon: int = 250,
    seed: int = DEFAULT_SEED,
) -> dict:
    if not returns:
        raise ValueError("returns required")
    rng = random.Random(seed)
    ruined = 0
    finals: list[float] = []
    for _ in range(paths):
        eq = initial_equity
        floor = initial_equity * ruin_fraction
        hit = False
        for _ in range(horizon):
            eq *= 1.0 + returns[rng.randrange(len(returns))]
            if eq <= floor:
                hit = True
                break
        ruined += int(hit)
        finals.append(eq)
    finals_sorted = sorted(finals)
    q05 = finals_sorted[max(0, int(0.05 * (len(finals_sorted) - 1)))]
    q50 = finals_sorted[int(0.50 * (len(finals_sorted) - 1))]
    q95 = finals_sorted[int(0.95 * (len(finals_sorted) - 1))]
    p = ruined / paths
    se = math.sqrt(max(p * (1 - p), 0.0) / paths)
    return {
        "seed": seed,
        "paths": paths,
        "horizon": horizon,
        "ruin_fraction": ruin_fraction,
        "risk_of_ruin": p,
        "approx_95ci": [max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se)],
        "final_equity_quantiles": {"q05": q05, "q50": q50, "q95": q95},
    }


def regime_stats(regimes: Sequence[str], returns: Sequence[float]) -> dict:
    if len(regimes) != len(returns):
        raise ValueError("regime/return length mismatch")
    result: dict[str, dict] = {}
    for regime in sorted(set(regimes)):
        vals = [r for rg, r in zip(regimes, returns) if rg == regime]
        result[regime] = asdict(summarize_equity(1.0, vals)) | {"observations": len(vals)}
    return result


def walk_forward(returns: Sequence[float], train: int, test: int) -> list[dict]:
    if train <= 0 or test <= 0:
        raise ValueError("train/test must be positive")
    out: list[dict] = []
    cursor = 0
    fold = 0
    while cursor + train + test <= len(returns):
        tr = list(returns[cursor: cursor + train])
        te = list(returns[cursor + train: cursor + train + test])
        out.append({
            "fold": fold,
            "train": asdict(summarize_equity(1.0, tr)),
            "test": asdict(summarize_equity(1.0, te)),
            "train_digest": sha256_obj(tr),
            "test_digest": sha256_obj(te),
        })
        cursor += test
        fold += 1
    return out


def manipulation_stress(returns: Sequence[float], shock_fraction: float = -0.20, index: int | None = None) -> dict:
    vals = list(returns)
    if not vals:
        raise ValueError("returns required")
    i = len(vals) // 2 if index is None else index
    vals[i] += shock_fraction
    return {
        "shock_index": i,
        "shock_fraction": shock_fraction,
        "baseline": asdict(summarize_equity(1.0, returns)),
        "stressed": asdict(summarize_equity(1.0, vals)),
        "stressed_returns_digest": sha256_obj(vals),
    }


def concentration_hhi(weights: Iterable[float]) -> float:
    vals = [float(w) for w in weights]
    total = sum(vals)
    if total <= 0:
        raise ValueError("positive weights required")
    normalized = [w / total for w in vals]
    return sum(w * w for w in normalized)


def model_drift(reference: Sequence[float], recent: Sequence[float]) -> dict:
    if not reference or not recent:
        raise ValueError("reference and recent required")
    ref_mu, new_mu = mean(reference), mean(recent)
    ref_vol = pstdev(reference) if len(reference) > 1 else 0.0
    new_vol = pstdev(recent) if len(recent) > 1 else 0.0
    pooled = math.sqrt((ref_vol * ref_vol + new_vol * new_vol) / 2.0)
    standardized_mean_shift = (new_mu - ref_mu) / pooled if pooled > 0 else 0.0
    return {
        "reference_mean": ref_mu,
        "recent_mean": new_mu,
        "reference_volatility": ref_vol,
        "recent_volatility": new_vol,
        "standardized_mean_shift": standardized_mean_shift,
        "drift_flag": abs(standardized_mean_shift) >= 1.0 or (ref_vol > 0 and new_vol / ref_vol >= 1.5),
    }


def deterministic_fixture() -> dict:
    returns = [0.012, -0.006, 0.004, -0.018, 0.009, 0.003, -0.011, 0.015, -0.004, 0.007] * 6
    regimes = (["TREND"] * 20) + (["RANGE"] * 20) + (["STRESS"] * 20)
    market = MarketConfig(funding_bps_per_step=0.75)
    buy = execute_order(Order("BUY", 25, 100.0, leverage=2.0), market)
    partial = execute_order(Order("SELL", 300, 100.0, leverage=2.0), market)
    receipt = {
        "task_id": "MSG326_DETERMINISTIC_PAPER_RISK_ENGINE_V1",
        "engine_version": ENGINE_VERSION,
        "reality": "PROTECTED_BETA_PAPER_ONLY",
        "seed": DEFAULT_SEED,
        "orders": {"buy": asdict(buy), "partial": asdict(partial), "outage": asdict(execute_order(Order("BUY", 1, 100), market, outage=True))},
        "funding_cost_example": funding_cost(25 * buy.fill_price, market, 8),
        "liquidation_examples": {
            "long_5x": liquidation_price(100.0, "LONG", 5.0, market.maintenance_margin_fraction),
            "short_5x": liquidation_price(100.0, "SHORT", 5.0, market.maintenance_margin_fraction),
        },
        "equity": asdict(summarize_equity(10_000.0, returns)),
        "risk_of_ruin": risk_of_ruin_bootstrap(returns, 10_000.0),
        "regimes": regime_stats(regimes, returns),
        "walk_forward": walk_forward(returns, 20, 10),
        "manipulation": manipulation_stress(returns),
        "concentration_hhi": concentration_hhi([40, 30, 20, 10]),
        "model_drift": model_drift(returns[:30], returns[30:]),
        "truth": {
            "live_execution": False,
            "exchange_access": False,
            "wallet_access": False,
            "profit_claim": False,
            "paper_only": True,
        },
    }
    receipt["receipt_sha256"] = sha256_obj(receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(deterministic_fixture(), indent=2, sort_keys=True))
