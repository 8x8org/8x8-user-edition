#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from statistics import mean, pstdev
from typing import Iterable, Sequence

ENGINE_VERSION = "1.0.2"
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


def _finite_float(value: object, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be numeric and finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be numeric and finite")
    return result


def _normalized_returns(values: Sequence[float], *, label: str = "returns", require_gt_minus_one: bool = False) -> list[float]:
    out = [_finite_float(value, label) for value in values]
    if require_gt_minus_one and any(value <= -1.0 for value in out):
        raise ValueError(f"{label} must be finite and greater than -1")
    return out


def _validated_market(market: MarketConfig) -> MarketConfig:
    fee_bps = _finite_float(market.fee_bps, "fee_bps")
    half_spread_bps = _finite_float(market.half_spread_bps, "half_spread_bps")
    slippage_bps_per_unit = _finite_float(market.slippage_bps_per_unit, "slippage_bps_per_unit")
    max_fill_units = _finite_float(market.max_fill_units, "max_fill_units")
    partial_fill_fraction = _finite_float(market.partial_fill_fraction, "partial_fill_fraction")
    funding_bps_per_step = _finite_float(market.funding_bps_per_step, "funding_bps_per_step")
    maintenance_margin_fraction = _finite_float(market.maintenance_margin_fraction, "maintenance_margin_fraction")

    if fee_bps < 0 or half_spread_bps < 0 or slippage_bps_per_unit < 0:
        raise ValueError("market execution costs must be non-negative")
    if max_fill_units <= 0:
        raise ValueError("max_fill_units must be positive")
    if not 0.0 < partial_fill_fraction <= 1.0:
        raise ValueError("partial_fill_fraction must be within (0, 1]")
    if not 0.0 <= maintenance_margin_fraction < 1.0:
        raise ValueError("maintenance_margin_fraction must be within [0, 1)")

    return MarketConfig(
        fee_bps=fee_bps,
        half_spread_bps=half_spread_bps,
        slippage_bps_per_unit=slippage_bps_per_unit,
        max_fill_units=max_fill_units,
        partial_fill_fraction=partial_fill_fraction,
        funding_bps_per_step=funding_bps_per_step,
        maintenance_margin_fraction=maintenance_margin_fraction,
    )


def _rejected_invalid(order: Order) -> Fill:
    try:
        requested = float(order.quantity)
    except (TypeError, ValueError, OverflowError):
        requested = 0.0
    if not math.isfinite(requested):
        requested = 0.0
    return Fill("REJECTED_INVALID", requested, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def execute_order(order: Order, market: MarketConfig, outage: bool = False) -> Fill:
    try:
        quantity = _finite_float(order.quantity, "quantity")
        reference_price = _finite_float(order.reference_price, "reference_price")
        leverage = _finite_float(order.leverage, "leverage")
        validated_market = _validated_market(market)
    except ValueError:
        return _rejected_invalid(order)

    normalized_order = Order(order.side, quantity, reference_price, leverage)
    if outage:
        return Fill("REJECTED_OUTAGE", quantity, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    if normalized_order.side not in {"BUY", "SELL"} or quantity <= 0 or reference_price <= 0 or leverage <= 0:
        return _rejected_invalid(normalized_order)

    requested = quantity
    if requested > validated_market.max_fill_units:
        filled = min(validated_market.max_fill_units, requested * validated_market.partial_fill_fraction)
        status = "PARTIAL"
    else:
        filled = requested
        status = "FILLED"

    direction = 1 if normalized_order.side == "BUY" else -1
    spread_rate = validated_market.half_spread_bps / 10_000.0
    slippage_bps = validated_market.slippage_bps_per_unit * filled
    slippage_rate = slippage_bps / 10_000.0
    fill_price = reference_price * (1.0 + direction * (spread_rate + slippage_rate))
    gross = filled * fill_price
    fee = abs(gross) * validated_market.fee_bps / 10_000.0
    spread_cost = filled * reference_price * spread_rate
    slippage_cost = filled * reference_price * slippage_rate
    if any(not math.isfinite(value) or value < 0 for value in (filled, abs(gross), fee, spread_cost, slippage_cost)):
        return _rejected_invalid(normalized_order)
    if not math.isfinite(fill_price) or fill_price <= 0:
        return _rejected_invalid(normalized_order)
    return Fill(status, requested, filled, fill_price, gross, fee, spread_cost, slippage_cost)


def funding_cost(position_notional: float, market: MarketConfig, steps: int) -> float:
    notional = _finite_float(position_notional, "position_notional")
    validated_market = _validated_market(market)
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    result = abs(notional) * (validated_market.funding_bps_per_step / 10_000.0) * steps
    if not math.isfinite(result):
        raise ValueError("funding result must be finite")
    return result


def liquidation_price(entry_price: float, side: str, leverage: float, maintenance_margin_fraction: float) -> float:
    entry = _finite_float(entry_price, "entry_price")
    leverage_value = _finite_float(leverage, "leverage")
    maintenance = _finite_float(maintenance_margin_fraction, "maintenance_margin_fraction")
    if entry <= 0 or leverage_value <= 0 or side not in {"LONG", "SHORT"}:
        raise ValueError("invalid liquidation inputs")
    if not 0.0 <= maintenance < 1.0:
        raise ValueError("maintenance_margin_fraction must be within [0, 1)")
    initial_margin_fraction = 1.0 / leverage_value
    buffer = max(0.0, initial_margin_fraction - maintenance)
    if side == "LONG":
        return entry * (1.0 - buffer)
    return entry * (1.0 + buffer)


def equity_curve(initial_equity: float, returns: Sequence[float]) -> list[float]:
    initial = _finite_float(initial_equity, "initial_equity")
    if initial <= 0:
        raise ValueError("initial_equity must be positive")
    normalized = _normalized_returns(returns, require_gt_minus_one=True)
    eq = [initial]
    for value in normalized:
        next_equity = eq[-1] * (1.0 + value)
        if not math.isfinite(next_equity):
            raise ValueError("equity curve became non-finite")
        eq.append(next_equity)
    return eq


def max_drawdown_fraction(curve: Sequence[float]) -> float:
    vals = _normalized_returns(curve, label="curve")
    if not vals:
        raise ValueError("curve required")
    peak = vals[0]
    worst = 0.0
    for value in vals:
        peak = max(peak, value)
        if peak > 0:
            worst = max(worst, (peak - value) / peak)
    return worst


def summarize_equity(initial_equity: float, returns: Sequence[float]) -> EquityStats:
    normalized = _normalized_returns(returns, require_gt_minus_one=True)
    curve = equity_curve(initial_equity, normalized)
    mu = mean(normalized) if normalized else 0.0
    vol = pstdev(normalized) if len(normalized) > 1 else 0.0
    sharpe_like = mu / vol * math.sqrt(len(normalized)) if vol > 0 else 0.0
    return EquityStats(curve[-1], max_drawdown_fraction(curve), mu, vol, sharpe_like)


def _deterministic_sample_index(seed: int, draw_index: int, population_size: int) -> int:
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    if population_size <= 0:
        raise ValueError("population_size must be positive")
    material = f"8x8-paper-bootstrap-v1:{seed}:{draw_index}".encode("utf-8")
    digest = hashlib.sha256(material).digest()
    return int.from_bytes(digest[:8], "big") % population_size


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
    normalized = _normalized_returns(returns, require_gt_minus_one=True)
    initial = _finite_float(initial_equity, "initial_equity")
    ruin = _finite_float(ruin_fraction, "ruin_fraction")
    if initial <= 0:
        raise ValueError("initial_equity must be positive and finite")
    if not isinstance(paths, int) or isinstance(paths, bool) or paths <= 0:
        raise ValueError("paths must be a positive integer")
    if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon <= 0:
        raise ValueError("horizon must be a positive integer")
    if not 0.0 <= ruin <= 1.0:
        raise ValueError("ruin_fraction must be within [0, 1]")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")

    ruined = 0
    finals: list[float] = []
    draw_index = 0
    for _ in range(paths):
        eq = initial
        floor = initial * ruin
        hit = False
        for _ in range(horizon):
            sample = normalized[_deterministic_sample_index(seed, draw_index, len(normalized))]
            draw_index += 1
            eq *= 1.0 + sample
            if not math.isfinite(eq):
                raise ValueError("bootstrap equity became non-finite")
            if eq <= floor:
                hit = True
                break
        ruined += int(hit)
        finals.append(eq)
    finals_sorted = sorted(finals)
    q05 = finals_sorted[max(0, int(0.05 * (len(finals_sorted) - 1)))]
    q50 = finals_sorted[int(0.50 * (len(finals_sorted) - 1))]
    q95 = finals_sorted[int(0.95 * (len(finals_sorted) - 1))]
    probability = ruined / paths
    se = math.sqrt(max(probability * (1 - probability), 0.0) / paths)
    return {
        "seed": seed,
        "sampler": "SHA256_COUNTER_V1",
        "paths": paths,
        "horizon": horizon,
        "ruin_fraction": ruin,
        "risk_of_ruin": probability,
        "approx_95ci": [max(0.0, probability - 1.96 * se), min(1.0, probability + 1.96 * se)],
        "final_equity_quantiles": {"q05": q05, "q50": q50, "q95": q95},
    }


def regime_stats(regimes: Sequence[str], returns: Sequence[float]) -> dict:
    normalized = _normalized_returns(returns, require_gt_minus_one=True)
    if len(regimes) != len(normalized):
        raise ValueError("regime/return length mismatch")
    result: dict[str, dict] = {}
    for regime in sorted(set(regimes)):
        vals = [value for rg, value in zip(regimes, normalized) if rg == regime]
        result[regime] = asdict(summarize_equity(1.0, vals)) | {"observations": len(vals)}
    return result


def walk_forward(returns: Sequence[float], train: int, test: int) -> list[dict]:
    normalized = _normalized_returns(returns, require_gt_minus_one=True)
    if not isinstance(train, int) or isinstance(train, bool) or not isinstance(test, int) or isinstance(test, bool) or train <= 0 or test <= 0:
        raise ValueError("train/test must be positive integers")
    out: list[dict] = []
    cursor = 0
    fold = 0
    while cursor + train + test <= len(normalized):
        tr = normalized[cursor: cursor + train]
        te = normalized[cursor + train: cursor + train + test]
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
    vals = _normalized_returns(returns, require_gt_minus_one=True)
    if not vals:
        raise ValueError("returns required")
    i = len(vals) // 2 if index is None else index
    if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(vals):
        raise ValueError("index out of range")
    shock = _finite_float(shock_fraction, "shock_fraction")
    stressed_value = vals[i] + shock
    if stressed_value <= -1.0:
        raise ValueError("stressed return must remain greater than -1")
    vals[i] = stressed_value
    baseline_values = _normalized_returns(returns, require_gt_minus_one=True)
    return {
        "shock_index": i,
        "shock_fraction": shock,
        "baseline": asdict(summarize_equity(1.0, baseline_values)),
        "stressed": asdict(summarize_equity(1.0, vals)),
        "stressed_returns_digest": sha256_obj(vals),
    }


def concentration_hhi(weights: Iterable[float]) -> float:
    vals = [_finite_float(weight, "weight") for weight in weights]
    if not vals:
        raise ValueError("weights required")
    if any(weight < 0 for weight in vals):
        raise ValueError("non-negative weights required")
    total = sum(vals)
    if total <= 0:
        raise ValueError("positive total weight required")
    normalized = [weight / total for weight in vals]
    return sum(weight * weight for weight in normalized)


def model_drift(reference: Sequence[float], recent: Sequence[float]) -> dict:
    if not reference or not recent:
        raise ValueError("reference and recent required")
    reference_values = _normalized_returns(reference, label="reference")
    recent_values = _normalized_returns(recent, label="recent")
    ref_mu, new_mu = mean(reference_values), mean(recent_values)
    ref_vol = pstdev(reference_values) if len(reference_values) > 1 else 0.0
    new_vol = pstdev(recent_values) if len(recent_values) > 1 else 0.0
    pooled = math.sqrt((ref_vol * ref_vol + new_vol * new_vol) / 2.0)
    mean_delta = new_mu - ref_mu
    if pooled > 0.0:
        standardized_mean_shift = mean_delta / pooled
        mean_shift_flag = abs(standardized_mean_shift) >= 1.0
    elif mean_delta > 0.0:
        standardized_mean_shift = math.inf
        mean_shift_flag = True
    elif mean_delta < 0.0:
        standardized_mean_shift = -math.inf
        mean_shift_flag = True
    else:
        standardized_mean_shift = 0.0
        mean_shift_flag = False

    # pstdev() is non-negative. Avoid direct floating-point equality while
    # preserving the important zero-reference case: any positive recent
    # volatility emerging from a non-positive reference is a shift.
    if ref_vol <= 0.0:
        volatility_shift_flag = new_vol > 0.0
    else:
        volatility_shift_flag = new_vol / ref_vol >= 1.5
    return {
        "reference_mean": ref_mu,
        "recent_mean": new_mu,
        "reference_volatility": ref_vol,
        "recent_volatility": new_vol,
        "standardized_mean_shift": standardized_mean_shift,
        "mean_shift_flag": mean_shift_flag,
        "volatility_shift_flag": volatility_shift_flag,
        "drift_flag": mean_shift_flag or volatility_shift_flag,
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
