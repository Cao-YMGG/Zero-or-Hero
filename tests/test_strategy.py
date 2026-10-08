import unittest
from datetime import datetime, time, timedelta

from zoh import backtest, review
from zoh import journal
from zoh.strategy import same_day_expiry, with_gap
from zoh.strategy import (ET, bs_delta, bs_price, check_exit, contracts_for, current_phase,
                          day_context, evaluate_signal, parse_occ, round_limit, select_contract,
                          signal_momentum, signal_orb)


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


class ContextTests(unittest.TestCase):
    day = datetime(2026, 10, 14).date()

    def test_context_gap_and_events(self):
        ctx = day_context(self.day, {"2026-10-14": ["CPI"]}, prev_close=100, open_price=100.5)
        self.assertEqual(ctx["events"], ["CPI"])
        self.assertAlmostEqual(ctx["gap_pct"], 0.5)

    def test_day_filters(self):
        bars = make_bars([100 + i * 0.05 for i in range(15)])
        variant = {"signal": "momentum", "after_minutes": 10, "threshold_pct": 0.15}
        macro = day_context(self.day, {"2026-10-14": ["CPI"]})
        calm = day_context(self.day, {})
        self.assertEqual(evaluate_signal(bars, {**variant, "days": "event"}, macro), "call")
        self.assertIsNone(evaluate_signal(bars, {**variant, "days": "event"}, calm))
        self.assertIsNone(evaluate_signal(bars, {**variant, "days": "non_event"}, macro))

    def test_gap_signal(self):
        bars = make_bars([100.6, 100.6])
        variant = {"signal": "gap", "after_minutes": 1, "min_gap_pct": 0.3}
        up = day_context(self.day, {}, prev_close=100, open_price=100.6)
        flat = day_context(self.day, {}, prev_close=100, open_price=100.1)
        self.assertEqual(evaluate_signal(bars, variant, up), "call")
        self.assertEqual(evaluate_signal(bars, {**variant, "fade": True}, up), "put")
        self.assertIsNone(evaluate_signal(bars, variant, flat))

    def test_gap_sides(self):
        bars = make_bars([100.0, 100.0])
        variant = {"signal": "gap", "after_minutes": 1, "min_gap_pct": 2.0, "sides": ["up"]}
        up = day_context(self.day, {}, prev_close=100, open_price=102.5)
        down = day_context(self.day, {}, prev_close=100, open_price=97.5)
        self.assertEqual(evaluate_signal(bars, variant, up), "call")
        self.assertIsNone(evaluate_signal(bars, variant, down))
        rebound = {**variant, "sides": ["down"], "fade": True}
        self.assertEqual(evaluate_signal(bars, rebound, down), "call")

    def test_bias_signal_and_confirm(self):
        rising = make_bars([100 + i * 0.02 for i in range(12)])
        put_bias = day_context(self.day, {}, bias={"bias": "put"})
        none_bias = day_context(self.day, {}, bias={"bias": "none"})
        plain = {"signal": "bias", "after_minutes": 5}
        confirm = {"signal": "bias", "after_minutes": 10, "confirm": True, "threshold_pct": 0.1}
        self.assertEqual(evaluate_signal(rising, plain, put_bias), "put")
        self.assertIsNone(evaluate_signal(rising, confirm, put_bias))  # tape disagrees
        self.assertEqual(evaluate_signal(rising, confirm,
                                         day_context(self.day, {}, bias={"bias": "call"})), "call")
        self.assertIsNone(evaluate_signal(rising, plain, none_bias))
        self.assertIsNone(evaluate_signal(rising, plain, day_context(self.day, {})))

    def test_cross_asset_signal(self):
        spy = make_bars([100.0] * 16)
        tlt_up = make_bars([90 + i * 0.02 for i in range(16)])  # +0.33% by 09:45
        ctx = day_context(self.day, {}, cross={"TLT": tlt_up, "USO": tlt_up})
        rates = {"signal": "cross", "asset": "TLT", "sign": 1, "after_minutes": 15,
                 "threshold_pct": 0.15}
        oil = {**rates, "asset": "USO", "sign": -1}
        self.assertEqual(evaluate_signal(spy, rates, ctx), "call")
        self.assertEqual(evaluate_signal(spy, oil, ctx), "put")
        self.assertIsNone(evaluate_signal(spy[:10], rates, ctx))  # too early
        self.assertIsNone(evaluate_signal(spy, rates, day_context(self.day, {})))  # no data

    def test_catalyst_signal(self):
        rising = make_bars([700 + i * 0.6 for i in range(20)])  # +1.6% by 09:49
        pick = {"sniper": {"symbol": "META", "direction": "call", "catalyst": "Muse #1"}}
        ctx = day_context(self.day, {}, bias=pick)
        variant = {"signal": "catalyst", "after_minutes": 15, "move_pct": 1.0}
        self.assertEqual(evaluate_signal(rising, variant, ctx), "call")
        self.assertIsNone(evaluate_signal(rising[:10], variant, ctx))  # before 09:45
        put_ctx = day_context(self.day, {}, bias={"sniper": {"symbol": "META",
                                                             "direction": "put"}})
        self.assertIsNone(evaluate_signal(rising, variant, put_ctx))  # price disagrees
        self.assertIsNone(evaluate_signal(rising, variant, day_context(self.day, {})))

    def test_weekday_filter(self):
        bars = make_bars([100 + i * 0.05 for i in range(15)])
        variant = {"signal": "momentum", "after_minutes": 10, "threshold_pct": 0.15,
                   "weekdays": [0, 2, 4]}
        wed = day_context(datetime(2026, 10, 14).date(), {})
        thu = day_context(datetime(2026, 10, 15).date(), {})
        self.assertEqual(evaluate_signal(bars, variant, wed), "call")
        self.assertIsNone(evaluate_signal(bars, variant, thu))

    def test_same_day_expiry(self):
        self.assertTrue(same_day_expiry("SPY", 1))
        self.assertTrue(same_day_expiry("META", 2))
        self.assertFalse(same_day_expiry("META", 3))
        self.assertTrue(same_day_expiry("RKLB", 4))
        self.assertFalse(same_day_expiry("RKLB", 0))

    def test_with_gap_rebases_context(self):
        spy = day_context(self.day, {}, prev_close=100, open_price=100.1)
        amd = with_gap(spy, prev_close=600, open_price=582)
        self.assertAlmostEqual(amd["gap_pct"], -3.0)
        rebound = {"signal": "gap", "sides": ["down"], "fade": True, "after_minutes": 1,
                   "min_gap_pct": 2.0}
        bars = make_bars([582.0, 583.0])
        self.assertIsNone(evaluate_signal(bars, rebound, spy))  # SPY flat: no signal
        self.assertEqual(evaluate_signal(bars, rebound, amd), "call")

    def test_macro_calendar_loads(self):
        events = journal.load_events()
        self.assertIn("CPI", events["2026-10-14"])
        self.assertIn("FOMC", events["2026-10-28"])


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


class IntradayPickTest(unittest.TestCase):
    def test_intraday_variant_enters_regardless_of_move_from_open(self):
        import json
        from datetime import datetime
        from zoh import journal
        from zoh.strategy import ET, evaluate_signal
        config = json.loads(journal.CONFIG_PATH.read_text())
        variant = next(v for v in config["variants"] if v.get("source") == "intraday")
        bars = [{"t": datetime(2026, 10, 6, 9, 30 + i, tzinfo=ET), "o": 100 + 3 * i, "h": 0,
                 "l": 0, "c": 100 + 3 * i} for i in range(3)]  # stock already up 6%
        ctx = {"events": [], "gap_pct": None, "weekday": 1,
               "bias": {"sniper": {"symbol": "AMD", "direction": "put"}}}
        self.assertEqual(evaluate_signal(bars, variant, ctx), "put")
        self.assertTrue(str(journal.intraday_path(datetime(2026, 10, 6).date())).endswith(
            "bias/intraday/2026-10-06.json"))


class FlushSignalTest(unittest.TestCase):
    def test_flush_down_then_reclaim_is_a_call(self):
        from datetime import datetime, timedelta
        from zoh.strategy import ET, signal_flush
        t0 = datetime(2026, 10, 6, 9, 30, tzinfo=ET)
        prices = [649, 640, 630, 628] + [629] * 11 + [636, 640]  # AMD 2026-10-06 shape
        bars = [{"t": t0 + timedelta(minutes=i), "o": p, "h": p, "l": p, "c": p}
                for i, p in enumerate(prices)]
        variant = {"flush_minutes": 15, "flush_pct": 2.0, "reclaim": 0.5}
        self.assertIsNone(signal_flush(bars[:16], variant))  # 636 < 628 + 10.5
        self.assertEqual(signal_flush(bars, variant), "call")
        self.assertEqual(signal_flush(bars, {**variant, "fade": True}), "put")


class RealContractsTest(unittest.TestCase):
    def test_one_contract_fallback_for_pricey_options(self):
        from zoh.bot import real_contracts
        self.assertEqual(real_contracts(500, 0.2, 1.17), 1)  # $117 > $100 stake, <= $250
        self.assertEqual(real_contracts(500, 0.2, 0.40), 2)
        self.assertEqual(real_contracts(500, 0.2, 2.60), 0)  # $260 > half the account
        self.assertEqual(real_contracts(500, 0, 0.40), 0)


class RealOrderGateTests(unittest.TestCase):
    def test_one_real_position_per_stock_and_reset(self):
        from zoh.bot import may_trade_real
        state = {}
        self.assertTrue(may_trade_real(state, "MRVL"))
        state["real_underlyings"] = ["MRVL"]
        self.assertFalse(may_trade_real(state, "MRVL"))
        self.assertTrue(may_trade_real(state, "AMD"))
        state["reset_needed"] = True
        self.assertFalse(may_trade_real(state, "AMD"))

    def test_virtual_ledger_restarts_generation(self):
        from zoh.bot import virtual_equity
        eq, led = virtual_equity(None, 5000.0, 500, 50, "2026-10-08")
        self.assertEqual((eq, led["generation"]), (500, 1))
        eq, led = virtual_equity(led, 5200.0, 500, 50, "2026-10-09")
        self.assertEqual(eq, 700)
        eq, led = virtual_equity(led, 4540.0, 500, 50, "2026-10-12")
        self.assertEqual((eq, led["generation"], led["anchor"]), (500, 2, 4540.0))
        self.assertEqual(led["history"][0]["final_equity"], 40.0)

    def test_held_positions_carry_to_next_day(self):
        from datetime import date
        prev = {"date": "2026-10-07", "done": True, "variants": {
            "catalyst_open": {"entered": True, "hold": True,
                              "shadow": {"contract": "MRVL261009C00302500", "entry_price": 0.98},
                              "real": {"contract": "MRVL261009C00302500", "qty": 1,
                                       "underlying": "MRVL"}},
            "claude_bias": {"entered": True, "closed": True}}}
        state = journal.carry_over(prev, date(2026, 10, 8))
        self.assertEqual(list(state["variants"]), ["catalyst_open@2026-10-07"])
        kept = state["variants"]["catalyst_open@2026-10-07"]
        self.assertTrue(kept["carried"])
        self.assertEqual(kept["of"], "catalyst_open")
        again = journal.carry_over({"date": "2026-10-08", "variants": {
            "catalyst_open@2026-10-07": {**kept, "hold": True}}}, date(2026, 10, 9))
        self.assertEqual(list(again["variants"]), ["catalyst_open@2026-10-07"])
        self.assertEqual(state["real_underlyings"], ["MRVL"])

    def test_carry_over_finds_underlying_from_contract(self):
        from datetime import date
        prev = {"variants": {"catalyst_sniper": {"hold": True, "shadow": {"contract": "MRVL261009C00297500"},
                                                 "real": {"contract": "MRVL261009C00297500", "qty": 1}}}}
        self.assertEqual(journal.carry_over(prev, date(2026, 10, 8))["real_underlyings"], ["MRVL"])
