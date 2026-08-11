from decimal import Decimal
import json
import math
import unittest

from trading.paper_engine import (
    DEFAULT_SEED,
    MarketConfig,
    Order,
    concentration_hhi,
    deterministic_fixture,
    execute_order,
    funding_cost,
    liquidation_price,
    manipulation_stress,
    model_drift,
    risk_of_ruin_bootstrap,
    sha256_obj,
    summarize_equity,
    walk_forward,
)


class PaperEngineTests(unittest.TestCase):
    def test_order_fill_costs_are_deterministic(self):
        m = MarketConfig(fee_bps=10, half_spread_bps=2, slippage_bps_per_unit=0.5, max_fill_units=100)
        fill = execute_order(Order("BUY", 20, 100), m)
        self.assertEqual(fill.status, "FILLED")
        self.assertEqual(fill.filled_quantity, 20)
        self.assertAlmostEqual(fill.fill_price, 100.12)
        self.assertAlmostEqual(fill.spread_cost, 0.4)
        self.assertAlmostEqual(fill.slippage_cost, 2.0)
        self.assertAlmostEqual(fill.fee, 2.0024)

    def test_partial_fill_and_outage_are_explicit(self):
        m = MarketConfig(max_fill_units=100, partial_fill_fraction=0.5)
        partial = execute_order(Order("SELL", 300, 100), m)
        outage = execute_order(Order("BUY", 1, 100), m, outage=True)
        self.assertEqual(partial.status, "PARTIAL")
        self.assertEqual(partial.filled_quantity, 100)
        self.assertEqual(outage.status, "REJECTED_OUTAGE")
        self.assertEqual(outage.filled_quantity, 0)

    def test_invalid_market_config_is_rejected_without_negative_or_nonfinite_fill(self):
        invalid_markets = [
            MarketConfig(fee_bps=-1),
            MarketConfig(half_spread_bps=-1),
            MarketConfig(slippage_bps_per_unit=-1),
            MarketConfig(max_fill_units=-10),
            MarketConfig(partial_fill_fraction=0),
            MarketConfig(partial_fill_fraction=1.1),
            MarketConfig(maintenance_margin_fraction=-0.1),
            MarketConfig(maintenance_margin_fraction=1.0),
            MarketConfig(fee_bps=math.inf),
            MarketConfig(max_fill_units=math.nan),
        ]
        for market in invalid_markets:
            with self.subTest(market=market):
                fill = execute_order(Order("BUY", 20, 100), market)
                self.assertEqual(fill.status, "REJECTED_INVALID")
                self.assertEqual(fill.filled_quantity, 0.0)
                self.assertTrue(math.isfinite(fill.fill_price))

    def test_float_convertible_order_inputs_are_normalized_once(self):
        fill = execute_order(
            Order("BUY", Decimal("20"), "100", leverage=Decimal("2")),
            MarketConfig(fee_bps=Decimal("10")),
        )
        self.assertEqual(fill.status, "FILLED")
        self.assertEqual(fill.filled_quantity, 20.0)
        self.assertTrue(math.isfinite(fill.fill_price))

    def test_liquidation_examples(self):
        self.assertAlmostEqual(liquidation_price(100, "LONG", 5, 0.10), 90)
        self.assertAlmostEqual(liquidation_price(100, "SHORT", 5, 0.10), 110)
        with self.assertRaises(ValueError):
            liquidation_price(100, "LONG", 5, 1.0)

    def test_funding_cost_rejects_invalid_market_or_steps(self):
        with self.assertRaises(ValueError):
            funding_cost(1000, MarketConfig(max_fill_units=-1), 1)
        with self.assertRaises(ValueError):
            funding_cost(1000, MarketConfig(), -1)

    def test_drawdown(self):
        s = summarize_equity(1000, [0.10, -0.20, 0.05])
        self.assertGreater(s.max_drawdown_fraction, 0.19)
        self.assertLess(s.max_drawdown_fraction, 0.21)

    def test_monte_carlo_is_seed_reproducible(self):
        returns = [0.01, -0.005, 0.002, -0.01]
        a = risk_of_ruin_bootstrap(returns, 1000, paths=200, horizon=50, seed=DEFAULT_SEED)
        b = risk_of_ruin_bootstrap(returns, 1000, paths=200, horizon=50, seed=DEFAULT_SEED)
        self.assertEqual(a, b)
        self.assertEqual(a["sampler"], "SHA256_COUNTER_V1")
        self.assertTrue(0 <= a["risk_of_ruin"] <= 1)

    def test_monte_carlo_normalizes_float_convertible_returns_before_arithmetic(self):
        result = risk_of_ruin_bootstrap(
            [Decimal("0.01"), "-0.005", Decimal("0.002")],
            Decimal("1000"),
            paths=20,
            horizon=10,
        )
        self.assertTrue(0 <= result["risk_of_ruin"] <= 1)
        self.assertTrue(math.isfinite(result["final_equity_quantiles"]["q50"]))

    def test_monte_carlo_rejects_invalid_parameters(self):
        returns = [0.01, -0.005]
        for kwargs in ({"paths": 0}, {"paths": -1}, {"horizon": 0}, {"ruin_fraction": 1.1}, {"ruin_fraction": -0.1}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    risk_of_ruin_bootstrap(returns, 1000, **kwargs)
        with self.assertRaises(ValueError):
            risk_of_ruin_bootstrap([-1.0], 1000)
        with self.assertRaises(ValueError):
            risk_of_ruin_bootstrap(returns, 0)
        with self.assertRaises(ValueError):
            risk_of_ruin_bootstrap(returns, 1000, seed="8888")

    def test_walk_forward_keeps_out_of_sample_separate(self):
        folds = walk_forward([0.01, -0.01] * 20, train=10, test=5)
        self.assertGreater(len(folds), 0)
        for fold in folds:
            self.assertNotEqual(fold["train_digest"], "")
            self.assertNotEqual(fold["test_digest"], "")
            self.assertEqual(set(fold), {"fold", "train", "test", "train_digest", "test_digest"})

    def test_manipulation_shock_degrades_equity(self):
        returns = [0.001] * 20
        stress = manipulation_stress(returns, shock_fraction=-0.20)
        self.assertLess(stress["stressed"]["final_equity"], stress["baseline"]["final_equity"])

    def test_manipulation_stress_rejects_invalid_index_or_ruinous_single_period_return(self):
        with self.assertRaises(ValueError):
            manipulation_stress([0.001] * 5, index=5)
        with self.assertRaises(ValueError):
            manipulation_stress([0.001] * 5, index=-1)
        with self.assertRaises(ValueError):
            manipulation_stress([0.001] * 5, shock_fraction=-1.1)

    def test_concentration_hhi(self):
        self.assertAlmostEqual(concentration_hhi([25, 25, 25, 25]), 0.25)
        self.assertGreater(concentration_hhi([90, 10]), 0.8)
        with self.assertRaises(ValueError):
            concentration_hhi([1, -0.5])
        with self.assertRaises(ValueError):
            concentration_hhi([1, math.inf])

    def test_model_drift_flags_large_shift(self):
        drift = model_drift([0.001, 0.002, 0.0, 0.001] * 10, [-0.04, -0.05, -0.03, -0.04] * 10)
        self.assertTrue(drift["drift_flag"])

    def test_model_drift_flags_zero_volatility_mean_shift(self):
        drift = model_drift([0.01] * 20, [-0.01] * 20)
        self.assertTrue(drift["drift_flag"])
        self.assertTrue(math.isinf(drift["standardized_mean_shift"]))

    def test_model_drift_flags_volatility_emerging_from_zero(self):
        drift = model_drift([0.01] * 20, [0.0, 0.02] * 10)
        self.assertAlmostEqual(drift["reference_mean"], drift["recent_mean"])
        self.assertEqual(drift["reference_volatility"], 0.0)
        self.assertGreater(drift["recent_volatility"], 0.0)
        self.assertFalse(drift["mean_shift_flag"])
        self.assertTrue(drift["volatility_shift_flag"])
        self.assertTrue(drift["drift_flag"])

    def test_model_drift_normalizes_decimal_and_string_inputs(self):
        drift = model_drift([Decimal("0.01")] * 5, ["0.01", "0.02", "0.00", "0.01", "0.01"])
        self.assertTrue(math.isfinite(drift["recent_volatility"]))

    def test_model_drift_flat_equal_series_is_stable(self):
        drift = model_drift([0.01] * 20, [0.01] * 20)
        self.assertFalse(drift["drift_flag"])
        self.assertEqual(drift["standardized_mean_shift"], 0.0)
        self.assertFalse(drift["volatility_shift_flag"])

    def test_receipt_is_digest_bound_and_paper_only(self):
        receipt = deterministic_fixture()
        digest = receipt.pop("receipt_sha256")
        self.assertEqual(digest, sha256_obj(receipt))
        self.assertTrue(receipt["truth"]["paper_only"])
        self.assertFalse(receipt["truth"]["live_execution"])
        self.assertFalse(receipt["truth"]["wallet_access"])
        self.assertFalse(receipt["truth"]["exchange_access"])
        self.assertEqual(receipt["risk_of_ruin"]["sampler"], "SHA256_COUNTER_V1")

    def test_fixture_is_json_serializable(self):
        json.dumps(deterministic_fixture(), sort_keys=True)


if __name__ == "__main__":
    unittest.main()
