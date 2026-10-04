import unittest
from datetime import datetime, time, timedelta

from zoh import backtest, review
from zoh.strategy import (ET, bs_delta, bs_price, check_exit, contracts_for, current_phase,
                          parse_occ, round_limit, select_contract, signal_momentum, signal_orb)


def make_bars(closes, day=datetime(2026, 10, 2)):
    start = datetime.combine(day.date(), time(9, 30), ET)
    bars = []
    prev = closes[0]
    for i, c in enumerate(closes):
        bars.append({"t": start + timedelta(minutes=i), "o": prev, "h": max(prev, c),
                     "l": min(prev, c), "c": c})
        prev = c
    return bars


class SignalTests(unittest.TestCase):
    def test_orb_breakout_up_and_down(self):
        flat = [100 + (0.1 if i % 2 else -0.1) for i in range(30)]
        self.assertIsNone(signal_orb(make_bars(flat + [100.05]), {"or_minutes": 30}))
        self.assertEqual(signal_orb(make_bars(flat + [100.5]), {"or_minutes": 30}), "call")
        self.assertEqual(signal_orb(make_bars(flat + [99.5]), {"or_minutes": 30}), "put")

    def test_orb_fade_flips(self):
        flat = [100.0] * 30
        self.assertEqual(signal_orb(make_bars(flat + [101]), {"or_minutes": 30, "fade": True}),
                         "put")

    def test_orb_waits_for_range(self):
        self.assertIsNone(signal_orb(make_bars([100, 105, 106]), {"or_minutes": 30}))

    def test_momentum(self):
        up = [100 + i * 0.01 for i in range(61)]  # +0.6% after 60 minutes
        self.assertEqual(signal_momentum(make_bars(up), {"after_minutes": 60}), "call")
        self.assertIsNone(signal_momentum(make_bars(up[:30]), {"after_minutes": 60}))


class ExitTests(unittest.TestCase):
    def test_take_profit_and_stop(self):
        v = {"take_profit": 1.0, "stop_loss": 0.5}
        self.assertEqual(check_exit(1.0, 2.0, 2.0, v), "take_profit")
        self.assertEqual(check_exit(1.0, 1.0, 0.5, v), "stop_loss")
        self.assertIsNone(check_exit(1.0, 1.5, 1.2, v))

    def test_trailing_stop_locks_gain(self):
        v = {"take_profit": None, "stop_loss": 0.5, "trail_after": 1.0, "trail_giveback": 0.4}
        self.assertIsNone(check_exit(1.0, 3.0, 2.0, v))
        self.assertEqual(check_exit(1.0, 3.0, 1.79, v), "trail")
        self.assertEqual(check_exit(1.0, 2.0, 1.0, v), "trail")  # floored at breakeven


class MathTests(unittest.TestCase):
    def test_put_call_parity_and_delta(self):
        call = bs_price(100, 101, 1 / 252, 0.2, "call")
        put = bs_price(100, 101, 1 / 252, 0.2, "put")
        self.assertAlmostEqual(call - put, 100 - 101, places=6)
        self.assertTrue(0 < bs_delta(100, 101, 1 / 252, 0.2, "call") < 0.5)
        self.assertTrue(-0.5 < bs_delta(100, 99, 1 / 252, 0.2, "put") < 0)

    def test_expiry_is_intrinsic(self):
        self.assertEqual(bs_price(100, 95, 0, 0.2, "call"), 5)
        self.assertEqual(bs_price(100, 95, 0, 0.2, "put"), 0)

    def test_parse_occ(self):
        self.assertEqual(parse_occ("SPY261005C00580000"), ("SPY", "261005", "call", 580.0))
        self.assertEqual(parse_occ("SPY261005P00579500"), ("SPY", "261005", "put", 579.5))

    def test_round_limit(self):
        self.assertEqual(round_limit(0.523), 0.53)
        self.assertEqual(round_limit(3.12), 3.15)
        self.assertEqual(round_limit(0.001), 0.01)


class SizingTests(unittest.TestCase):
    config = {"phases": [{"name": "a", "min_equity": 0, "risk_per_trade": 0.3},
                         {"name": "b", "min_equity": 2000, "risk_per_trade": 0.1}]}

    def test_phase(self):
        self.assertEqual(current_phase(self.config, 500)["name"], "a")
        self.assertEqual(current_phase(self.config, 2500)["name"], "b")

    def test_contracts_and_selection(self):
        self.assertEqual(contracts_for(150, 0.7), 2)
        cands = [{"symbol": "A", "strike": 1, "ask": 2.0, "delta": 0.3},
                 {"symbol": "B", "strike": 2, "ask": 1.0, "delta": 0.2},
                 {"symbol": "C", "strike": 3, "ask": 0.4, "delta": 0.1}]
        self.assertEqual(select_contract(cands, 0.3, 150)["symbol"], "B")
        self.assertIsNone(select_contract(cands, 0.3, 30))


class BacktestTests(unittest.TestCase):
    def test_breakout_day_wins(self):
        closes = [100.0] * 30 + [100 + 0.02 * i for i in range(1, 361)]
        variant = {"signal": "orb", "or_minutes": 30, "target_delta": 0.3, "take_profit": 1.0,
                   "stop_loss": 0.5}
        trade = backtest.simulate_day(make_bars(closes), variant, 0.16, 0.03, time(15, 45))
        self.assertEqual(trade["kind"], "call")
        self.assertEqual(trade["reason"], "take_profit")
        self.assertGreater(trade["pnl_pct"], 0.9)


class HeroOddsTests(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(backtest.hero_odds([-1.0], 1.0, 500, 2000, 50), 0.0)
        self.assertEqual(backtest.hero_odds([4.0], 1.0, 500, 2000, 50), 1.0)
        odds = backtest.hero_odds([3.0, -1.0], 1.0, 500, 2000, 50, paths=2000)
        self.assertAlmostEqual(odds, 0.5, delta=0.05)  # one all-in coin flip


class ReviewTests(unittest.TestCase):
    def test_promotion(self):
        config = {"champion": "a", "variants": [{"id": "a"}, {"id": "b"}]}
        trades = ([{"variant": "a", "mode": "shadow", "pnl_pct": "-0.5"}] * 10
                  + [{"variant": "b", "mode": "shadow", "pnl_pct": "0.4"}] * 10)
        old, new = review.promotion(config, review.leaderboard(config, trades))
        self.assertEqual((old["id"], new["id"]), ("a", "b"))

    def test_no_promotion_with_few_trades(self):
        config = {"champion": "a", "variants": [{"id": "a"}, {"id": "b"}]}
        trades = [{"variant": "b", "mode": "shadow", "pnl_pct": "0.4"}] * 10
        self.assertIsNone(review.promotion(config, review.leaderboard(config, trades)))


if __name__ == "__main__":
    unittest.main()
