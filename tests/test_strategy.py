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

    def test_selection_skips_a_zero_bid(self):
        # GEV 935C on 10-30: bid 0, ask 2.19, the 0.10-delta target; skip it for a two-sided quote.
        cands = [{"symbol": "GEV935", "strike": 935, "ask": 2.19, "bid": 0, "delta": 0.10},
                 {"symbol": "GEV925", "strike": 925, "ask": 2.25, "bid": 1.9, "delta": 0.13}]
        self.assertEqual(select_contract(cands, 0.1, 233)["symbol"], "GEV925")
        self.assertIsNone(select_contract(cands[:1], 0.1, 233))


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
        self.assertFalse(may_trade_real(state, "AMD"))   # same theme (semis)
        self.assertTrue(may_trade_real(state, "AAPL"))
        self.assertTrue(may_trade_real(state, "PLTR"))   # unlisted name is its own theme
        state["reset_needed"] = True
        self.assertFalse(may_trade_real(state, "AAPL"))

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


class ReclaimSignalTests(unittest.TestCase):
    def test_megacap_reclaim_fires_after_dip_and_reclaim(self):
        from zoh.strategy import signal_flush
        base = datetime(2026, 10, 7, 9, 30, tzinfo=ET)
        prices = [254.0, 253.5, 253.0, 252.6] + [252.8] * 11 + [253.5, 254.2]
        bars = [{"t": base + timedelta(minutes=i), "o": p, "h": p + 0.1, "l": p - 0.1, "c": p}
                for i, p in enumerate(prices)]
        bars[0]["o"] = 254.0
        variant = {"flush_minutes": 15, "flush_pct": 0.5, "reclaim": 1.0, "sides": ["down"]}
        self.assertIsNone(signal_flush(bars[:16], variant))
        self.assertEqual(signal_flush(bars, variant), "call")


class PennySellTest(unittest.TestCase):
    """Expiring option with no bid: market sell rejected, then a $0.01 limit."""

    def _bot(self, penny_fills):
        from datetime import date
        from zoh import bot as botmod
        calls = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today = date(2026, 10, 12)

            def _order(self, symbol, qty, side, kind, tag, limit=None):
                calls.append((kind, limit))
                if kind == "limit" and penny_fills:
                    return qty, limit
                return 0, None

        return FakeBot(), calls

    def test_penny_limit_after_rejected_market_sell(self):
        b, calls = self._bot(penny_fills=True)
        self.assertEqual(b._sell_out("MU261012C01025000", 1, "out"), (1, 0.01, "penny"))
        self.assertEqual(calls, [("market", None), ("limit", 0.01)])

    def test_penny_unfilled_returns_zero(self):
        b, calls = self._bot(penny_fills=False)
        self.assertEqual(b._sell_out("MU261012C01025000", 1, "out")[0], 0)
        self.assertEqual(len(calls), 2)

    def test_no_penny_for_later_expiry(self):
        b, calls = self._bot(penny_fills=True)
        self.assertEqual(b._sell_out("CRM261016C00252500", 1, "out"), (0, None, "market"))
        self.assertEqual(calls, [("market", None)])


class LedgerStartTest(unittest.TestCase):
    def test_waits_for_a_reset_account(self):
        from zoh.bot import ledger_can_start
        cfg = {"base": 500, "min_account": 5000}
        self.assertFalse(ledger_can_start(None, 50.48, cfg))
        self.assertTrue(ledger_can_start(None, 30000, cfg))
        self.assertTrue(ledger_can_start({"anchor": 30000}, 29000, cfg))


class LeaderFollowTest(unittest.TestCase):
    """The stock running on its own while the index is flat (META 2026-10-12/13)."""

    def _bars(self, open_, last, minutes=31):
        from zoh.strategy import ET
        start = datetime(2026, 10, 13, 9, 30, tzinfo=ET)
        n = minutes
        return [{"t": start + timedelta(minutes=i), "o": open_ + (last - open_) * i / n,
                 "h": max(open_, last), "l": min(open_, last),
                 "c": open_ + (last - open_) * (i + 1) / n, "v": 1} for i in range(n)]

    def test_relative_momentum_needs_outperformance(self):
        from zoh.strategy import signal_momentum
        v = {"signal": "momentum", "relative": True, "after_minutes": 30, "threshold_pct": 2.0}
        bars = self._bars(735.76, 755.0)  # +2.6% from the open
        self.assertEqual(signal_momentum(bars, v, {"index_ret": 0.0}), "call")
        self.assertIsNone(signal_momentum(bars, v, {"index_ret": 0.01}))  # index +1%: only +1.6% beyond

    def test_strongest_mover_first(self):
        from zoh.strategy import rank_by_move
        a = ("AAPL", self._bars(340, 343), {})
        m = ("META", self._bars(735, 760), {})
        d = ("MU", self._bars(990, 950), {})
        self.assertEqual([c[0] for c in rank_by_move([a, m, d])], ["MU", "META", "AAPL"])
        self.assertEqual([c[0] for c in rank_by_move([a, m, d], ["up"])], ["META", "AAPL", "MU"])

    def test_up_only(self):
        from zoh.strategy import signal_momentum
        v = {"signal": "momentum", "relative": True, "after_minutes": 30, "threshold_pct": 2.0,
             "sides": ["up"]}
        self.assertIsNone(signal_momentum(self._bars(990, 950), v, {"index_ret": 0.0}))


class LedgerEquityTest(unittest.TestCase):
    def test_day_end_records_the_ledger_not_the_account(self):
        from zoh.bot import ledger_equity
        ledger = {"base": 500, "anchor": 50000.0, "generation": 1}
        self.assertAlmostEqual(ledger_equity(ledger, 50520.0), 1020.0)
        self.assertAlmostEqual(ledger_equity(None, 46.52), 46.52)

    def test_live_equity_marks_todays_real_legs(self):
        from zoh.site import live_equity
        state = {"date": "2026-10-13", "done": False, "equity_start": 500.0, "variants": {
            "catalyst_open": {"real": {"entry_price": 0.93, "qty": 1, "entry_time": "2026-10-13T09:32:07"},
                              "shadow": {"last": 6.12}},
            "catalyst_open@2026-10-12": {"real": {"entry_price": 0.7, "qty": 1,
                                                  "entry_time": "2026-10-12T09:32:22"},
                                         "shadow": {"last": 1.47}}}}
        self.assertAlmostEqual(live_equity(state, []), 500 + 519.0)
        self.assertIsNone(live_equity({**state, "done": True}, []))


class GapUpFadeTest(unittest.TestCase):
    """A big-cap gap up on known good news that slips below its open (UNH 2026-10-13)."""

    def _bars(self, open_, last, minutes=16):
        from zoh.strategy import ET
        start = datetime(2026, 10, 13, 9, 30, tzinfo=ET)
        return [{"t": start + timedelta(minutes=i), "o": open_ + (last - open_) * i / minutes,
                 "h": max(open_, last), "l": min(open_, last),
                 "c": open_ + (last - open_) * (i + 1) / minutes, "v": 1} for i in range(minutes)]

    V = {"signal": "gap", "sides": ["up"], "fade": True, "after_minutes": 15,
         "min_gap_pct": 2.0, "confirm_pct": 0.2}

    def test_fades_gap_up_once_below_open(self):
        from zoh.strategy import signal_gap
        self.assertEqual(signal_gap(self._bars(400, 397), self.V, {"gap_pct": 3.8}), "put")

    def test_holding_gap_is_left_alone(self):
        from zoh.strategy import signal_gap
        self.assertIsNone(signal_gap(self._bars(400, 401), self.V, {"gap_pct": 3.8}))
        self.assertIsNone(signal_gap(self._bars(400, 399.5), self.V, {"gap_pct": 3.8}))  # -0.125%

    def test_gap_down_and_small_gap_ignored(self):
        from zoh.strategy import signal_gap
        self.assertIsNone(signal_gap(self._bars(400, 390), self.V, {"gap_pct": -3.0}))
        self.assertIsNone(signal_gap(self._bars(400, 390), self.V, {"gap_pct": 1.5}))

    def test_without_confirm_unchanged(self):
        from zoh.strategy import signal_gap
        v = {k: x for k, x in self.V.items() if k != "confirm_pct"}
        self.assertEqual(signal_gap(self._bars(400, 405), v, {"gap_pct": 3.8}), "put")


class NvdaGapDownPutTest(unittest.TestCase):
    """NVDA gaps down and is still below its open at 10:00 -> put (journal/research/OPENDRIVE.md)."""

    def test_config_variant_fires_only_when_below_open_at_ten(self):
        from zoh import journal
        from zoh.strategy import ET, signal_gap
        v = next(x for x in journal.load_config()["variants"] if x["id"] == "nvda_gapdown_put")
        start = datetime(2026, 10, 14, 9, 30, tzinfo=ET)

        def bars(open_, last, n=31):
            return [{"t": start + timedelta(minutes=i), "o": open_, "h": max(open_, last),
                     "l": min(open_, last), "c": open_ + (last - open_) * (i + 1) / n, "v": 1}
                    for i in range(n)]
        self.assertEqual(signal_gap(bars(225.6, 224.4), v, {"gap_pct": -1.3}), "put")
        self.assertIsNone(signal_gap(bars(225.6, 226.0), v, {"gap_pct": -1.3}))  # back above open
        self.assertIsNone(signal_gap(bars(225.6, 224.4), v, {"gap_pct": 0.8}))   # gapped up
        self.assertIsNone(signal_gap(bars(225.6, 224.4, n=20), v, {"gap_pct": -1.3}))  # before 10:00


class ExitLogTest(unittest.TestCase):
    """Every close writes the peak it saw, so exits can be graded (journal/GRADING.md)."""

    def test_append_exit_writes_header_once(self):
        import csv
        import tempfile
        from pathlib import Path
        from zoh import journal
        with tempfile.TemporaryDirectory() as tmp:
            old = journal.JOURNAL_DIR, journal.EXITS_PATH
            journal.JOURNAL_DIR, journal.EXITS_PATH = Path(tmp), Path(tmp) / "exits.csv"
            try:
                journal.append_exit({"date": "2026-10-14", "variant": "meta_follow2", "mode": "shadow",
                                     "contract": "META261014P00737500", "entry_price": 1.22,
                                     "exit_price": 2.61, "peak": 4.64, "exit_reason": "trail"})
                journal.append_exit({"date": "2026-10-14", "variant": "leader_follow", "mode": "shadow",
                                     "contract": "INTC261014C00102000", "entry_price": 0.6,
                                     "exit_price": 0, "peak": "", "exit_reason": "time"})
                rows = list(csv.DictReader(journal.EXITS_PATH.open()))
            finally:
                journal.JOURNAL_DIR, journal.EXITS_PATH = old
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["peak"], "4.64")


class AutoGradeTest(unittest.TestCase):
    """zoh.grade: the price-based parts of the trade score (journal/GRADING.md)."""

    def test_thesis(self):
        from zoh.grade import thesis_score
        self.assertEqual(thesis_score("put", 771, 773.3, 769.6, 766.7), 3)    # SPY 10-14
        self.assertEqual(thesis_score("call", 650, 637.0, 645.9, 648.5), 2)   # AMD 10-07
        self.assertEqual(thesis_score("call", 1025, 990.0, 989.0, 1002.0), 1)  # MU 10-12
        self.assertEqual(thesis_score("call", 102, 100.6, 98.1, 101.3), 0)    # INTC 10-14

    def test_entry_exit(self):
        from zoh.grade import entry_score, exit_score
        self.assertEqual(entry_score(1.22, 4.64), 2)
        self.assertEqual(exit_score(1.22, 2.61, 4.64), 1)   # kept 56%
        self.assertEqual(exit_score(0.93, 4.15, 7.39), 1)
        self.assertEqual(exit_score(0.75, 1.30, 1.48), 2)
        self.assertEqual(exit_score(0.6, 0.0, 0.6), 1)      # never moved: nothing to manage
        self.assertEqual(exit_score(0.12, 0.0, 0.19), 0)    # 1.6x given back
        self.assertIsNone(entry_score(1.0, None))

    def test_discipline_and_luck(self):
        from zoh.grade import discipline_auto, luck_flag
        self.assertEqual(discipline_auto("call", "leader_follow", {}, "put", True)[0], 1)
        self.assertEqual(discipline_auto("call", "leader_follow", {"days": "non_event"}, "put", True)[0], 2)
        self.assertEqual(discipline_auto("put", "claude_bias", {}, "put", True)[0], 3)
        self.assertEqual(luck_flag(1.1, 4), "lucky")
        self.assertEqual(luck_flag(-0.9, 6), "unlucky")
        self.assertEqual(luck_flag(-0.9, None), "")


class NewsFeedTest(unittest.TestCase):
    def test_rating_kind(self):
        from zoh.news import rating_kind
        self.assertEqual(rating_kind("Wells Fargo Downgrades Netflix to Underweight, Lowers Price Target to $57"), "downgrade")
        self.assertEqual(rating_kind("Melius Upgrades Microsoft to Buy"), "upgrade")
        self.assertEqual(rating_kind("JP Morgan Maintains Overweight on Apple, Raises Price Target to $360"), "target up")
        self.assertEqual(rating_kind("Apple's first foldable iPhone sells out within minutes"), "")

    def test_clean_drops_roundups_and_duplicates(self):
        from zoh.news import clean
        items = [
            {"id": 1, "headline": "Melius Upgrades Microsoft to Buy", "symbols": ["MSFT"],
             "created_at": "2026-10-05T11:02:00Z", "source": "benzinga"},
            {"id": 1, "headline": "Melius Upgrades Microsoft to Buy", "symbols": ["MSFT"],
             "created_at": "2026-10-05T11:02:00Z", "source": "benzinga"},
            {"id": 2, "headline": "12 Tech Stocks Moving In Monday's Pre-Market Session",
             "symbols": ["MSFT"], "created_at": "2026-10-05T11:30:00Z"},
            {"id": 3, "headline": "Big list", "symbols": ["A", "B", "C", "D", "E"],
             "created_at": "2026-10-05T11:40:00Z"},
        ]
        rows = clean(items, {"MSFT"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["rating"], "upgrade")
        self.assertEqual(rows[0]["time"], "10-05 07:02")


class OpendriveExitsTest(unittest.TestCase):
    def test_split_exit_keeps_the_tail(self):
        from datetime import datetime
        from zoh.research.opendrive import exits
        from zoh.strategy import ET
        day = datetime(2026, 10, 16, tzinfo=ET)
        path = [(day.replace(hour=10, minute=m), c) for m, c in ((5, 0.20), (30, 0.70), (59, 2.0))]
        path += [(day.replace(hour=13, minute=0), 4.0), (day.replace(hour=15, minute=30), 3.0)]
        e = exits(path, 0.20, 0.0)
        self.assertAlmostEqual(e["take3"], 2.45, places=2)        # out at the first bid >= 3x (0.69)
        self.assertAlmostEqual(e["hold"], 13.95, places=2)        # 2.99 at 15:30
        self.assertGreater(e["half3_hold"], e["take3"])
        self.assertGreater(e["half3_trail"], e["take3"])
        self.assertEqual(exits([(day.replace(hour=15, minute=30), 0.05)], 0.20, 0.0)["half3_hold"],
                         exits([(day.replace(hour=15, minute=30), 0.05)], 0.20, 0.0)["hold"])


class GradeFeedFallbackTest(unittest.TestCase):
    def test_recent_sip_403_falls_back_to_iex(self):
        from datetime import datetime
        from zoh.alpaca import AlpacaError
        from zoh.grade import underlying_path
        from zoh.strategy import ET

        class Api:
            feeds = []

            def stock_bars(self, symbol, start, end, feed="iex"):
                self.feeds.append(feed)
                if feed == "sip":
                    raise AlpacaError(403, "subscription does not permit querying recent SIP data")
                return [{"t": "2026-10-16T19:40:00Z", "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10}]

        api = Api()
        t0 = datetime(2026, 10, 16, 15, 30, tzinfo=ET)
        t1 = datetime(2026, 10, 16, 15, 45, tzinfo=ET)
        bars = underlying_path(api, "AAPL", t0, t1)
        self.assertEqual(api.feeds, ["sip", "iex"])
        self.assertEqual(len(bars), 1)


class OpenDriveVariantTest(unittest.TestCase):
    """spy_open_drive / stock_open_drive: calls only, at 10:00, not in the monthly expiry week
    or on Fridays (journal/research/REGIME.md)."""

    def test_opex_week(self):
        from datetime import date
        from zoh.strategy import opex_week
        self.assertTrue(opex_week(date(2026, 10, 12)))   # week of Fri 2026-10-16
        self.assertTrue(opex_week(date(2026, 10, 16)))
        self.assertFalse(opex_week(date(2026, 10, 19)))
        self.assertFalse(opex_week(date(2026, 10, 9)))
        self.assertTrue(opex_week(date(2026, 11, 20)))   # Nov 2026: third Friday is the 20th

    def _variant(self, vid):
        return journal.variant_by_id(journal.load_config(), vid)

    def test_spy_open_drive_fires_on_a_strong_open_only(self):
        from datetime import date
        v = self._variant("spy_open_drive")
        ctx = day_context(date(2026, 10, 20), {})
        up = make_bars([700.0] * 30 + [703.6], datetime(2026, 10, 20))   # +0.51% at 10:00
        self.assertEqual(evaluate_signal(up, v, ctx), "call")
        down = make_bars([700.0] * 30 + [696.0], datetime(2026, 10, 20))
        self.assertIsNone(evaluate_signal(down, v, ctx))                   # never puts
        self.assertIsNone(evaluate_signal(up, v, day_context(date(2026, 10, 14), {})))  # expiry week
        self.assertIsNone(evaluate_signal(up, v, day_context(date(2026, 10, 23), {})))  # Friday
        self.assertIsNone(evaluate_signal(up, v, day_context(date(2026, 10, 20), {"2026-10-20": ["CPI"]})))

    def test_stock_open_drive_needs_point_eight(self):
        from datetime import date
        v = self._variant("stock_open_drive")
        ctx = day_context(date(2026, 10, 21), {})
        self.assertIsNone(evaluate_signal(make_bars([200.0] * 30 + [201.4], datetime(2026, 10, 21)), v, ctx))
        self.assertEqual(evaluate_signal(make_bars([200.0] * 30 + [201.7], datetime(2026, 10, 21)), v, ctx), "call")


class CarryAndHalfOutTest(unittest.TestCase):
    """Only news picks carry overnight; snipers sell half at 3x (journal/research/EXITS.md)."""

    def test_carries(self):
        from zoh.bot import carries
        self.assertTrue(carries({"signal": "catalyst"}))
        self.assertFalse(carries({"signal": "gap"}))
        self.assertTrue(carries({"signal": "gap", "carry": True}))

    def test_half_out_then_blended_close(self):
        from datetime import date
        from zoh import bot as botmod
        from zoh.bot import half_out
        rows, orders = [], []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.config = date(2026, 10, 19), False, {}

            def _sell_out(self, contract, qty, tag):
                orders.append((contract, qty, tag))
                return qty, 3.1, "market"

            def _record(self, variant, mode, pos, exit_price, now, reason, qty, peak=None):
                rows.append((mode, exit_price, reason, qty))

        v = {"id": "catalyst_open", "half_at": 3.0}
        vs = {"shadow": {"contract": "META261019C00780000", "entry_price": 1.0, "peak": 3.0, "qty": 2},
              "real": {"contract": "META261019C00780000", "qty": 3, "entry_price": 1.0}}
        self.assertFalse(half_out(vs["shadow"], 2.9, v))
        self.assertTrue(half_out(vs["shadow"], 3.0, v))
        b = FakeBot()
        b.sell_half(v, vs, 3.0, datetime(2026, 10, 19, 10, 0, tzinfo=ET))
        self.assertFalse(half_out(vs["shadow"], 3.5, v))          # only once
        self.assertEqual(orders, [("META261019C00780000", 1, "half")])
        self.assertEqual(vs["real"]["qty"], 2)
        self.assertEqual(rows, [("real", 3.1, "half", 1)])
        vs.pop("real")
        b.close(v, vs, 2.0, "trail", datetime(2026, 10, 19, 11, 0, tzinfo=ET))
        self.assertEqual(rows[-1], ("shadow", 2.5, "trail", 2))   # 0.5 x 3.0 + 0.5 x 2.0

    def test_trail_after_half(self):
        v = {"half_at": 3.0, "trail_after_half": 0.4}
        self.assertIsNone(check_exit(1.0, 4.0, 2.5, v))               # nothing banked: hold
        self.assertIsNone(check_exit(1.0, 4.0, 2.5, v, banked=True))  # floor 2.4
        self.assertEqual(check_exit(1.0, 4.0, 2.4, v, banked=True), "trail")
        self.assertEqual(check_exit(1.0, 1.5, 1.0, v, banked=True), "trail")  # floored at entry
        self.assertIsNone(check_exit(1.0, 4.0, 1.0, {"half_at": 3.0}, banked=True))

    def test_single_take_sells_the_one_contract(self):
        from datetime import date
        from zoh import bot as botmod
        rows, orders = [], []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.config = date(2026, 10, 26), False, {}

            def _sell_out(self, contract, qty, tag):
                orders.append((contract, qty, tag))
                return qty, 3.2, "market"

            def _record(self, variant, mode, pos, exit_price, now, reason, qty, peak=None):
                rows.append((mode, exit_price, reason, qty))

        v = {"id": "spy_open_drive", "half_at": 3.0, "single_take": True}
        vs = {"shadow": {"contract": "SPY261026C00690000", "entry_price": 1.0, "peak": 3.0, "qty": 1},
              "real": {"contract": "SPY261026C00690000", "qty": 1, "entry_price": 1.0}}
        FakeBot().sell_half(v, vs, 3.0, datetime(2026, 10, 26, 10, 0, tzinfo=ET))
        self.assertEqual(orders, [("SPY261026C00690000", 1, "take")])
        self.assertEqual(rows, [("real", 3.2, "take", 1)])
        self.assertNotIn("real", vs)
        self.assertIn("banked", vs["shadow"])
        # without single_take one contract keeps riding
        vs = {"shadow": {"contract": "X", "entry_price": 1.0, "peak": 3.0, "qty": 1},
              "real": {"contract": "X", "qty": 1, "entry_price": 1.0}}
        FakeBot().sell_half({"id": "x", "half_at": 3.0}, vs, 3.0, datetime(2026, 10, 26, 10, 0, tzinfo=ET))
        self.assertEqual(vs["real"]["qty"], 1)
