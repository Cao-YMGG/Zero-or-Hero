import json
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from zoh import bot as botmod
from zoh import journal, ledgers
from zoh.strategy import ET

CFG = {"base": 500, "dead": 50, "risk": 0.2, "one_contract_cap": 0.25, "pause_after": 5,
       "variants": ["meta_follow2", "spy_open_drive"]}


def trade(vid, mode, pnl, n, contract="META261016P00715000"):
    return {"variant": vid, "mode": mode, "contract": contract, "entry_time": f"2026-10-{n:02d}T10:00",
            "exit_time": f"2026-10-{n:02d}T12:00", "pnl": str(pnl)}


class LedgerRollTest(unittest.TestCase):
    def test_new_ledgers_and_generation_restart(self):
        book = ledgers.roll({}, CFG, "2026-10-19")
        self.assertEqual(ledgers.equity(book, "meta_follow2", CFG), 500)
        ledgers.book(book, "meta_follow2", -460.0)
        self.assertEqual(ledgers.equity(book, "meta_follow2", CFG), 40)
        ledgers.roll(book, CFG, "2026-10-20")
        led = book["meta_follow2"]
        self.assertEqual((led["generation"], led["realized"], led["started"]), (2, 0.0, "2026-10-20"))
        self.assertEqual(led["history"][0]["final_equity"], 40.0)
        self.assertEqual(book["spy_open_drive"]["generation"], 1)


class LosingStreakTest(unittest.TestCase):
    def test_streak_counts_trailing_losses_and_resets_on_a_win(self):
        rows = [trade("meta_follow2", "shadow", 50, 1)] + [trade("meta_follow2", "shadow", -10, n) for n in range(2, 7)]
        self.assertEqual(ledgers.losing_streak(rows, "meta_follow2"), 5)
        self.assertTrue(ledgers.paused(rows, "meta_follow2", CFG))
        rows.append(trade("meta_follow2", "shadow", 30, 8))
        self.assertFalse(ledgers.paused(rows, "meta_follow2", CFG))

    def test_real_row_replaces_its_shadow_twin(self):
        rows = [trade("meta_follow2", "shadow", 20, 1), trade("meta_follow2", "real", -5, 1)]
        self.assertEqual(ledgers.losing_streak(rows, "meta_follow2"), 1)
        self.assertEqual(ledgers.losing_streak(rows, "other"), 0)

    def test_real_fill_seconds_after_the_shadow_is_one_entry(self):
        shadow = trade("meta_follow2", "shadow", -20, 1)
        real = dict(trade("meta_follow2", "real", -15, 1), entry_time="2026-10-01T10:00:05")
        self.assertEqual(ledgers.losing_streak([shadow, real], "meta_follow2"), 1)


class LedgerOrderTest(unittest.TestCase):
    """A ledger variant sizes its real order on its own ledger and ignores the main theme rule."""

    def _bot(self, own):
        orders = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.api, self.dry_run, self.underlying = None, False, "SPY"
                self.today = date(2026, 10, 19)
                self.config = {"backtest": {"start_equity": 500}, "ledgers": CFG}
                self.state = {"equity_start": 677.0, "risk_per_trade": 0.2, "champion": "rebound_scanner",
                              "real_underlyings": ["SPY"], "ledgers": {"spy_open_drive": own}}

            def _order(self, symbol, qty, side, kind, tag, limit=None):
                orders.append((symbol, qty))
                return qty, limit

        return FakeBot(), orders

    def _enter(self, own):
        b, orders = self._bot(own)
        old = botmod.chain_candidates
        botmod.chain_candidates = lambda *a, **k: [{"symbol": "SPY261019C00770000", "strike": 770, "ask": 0.30,
                                                    "bid": 0.28, "delta": 0.2, "quote_time": None}]
        try:
            b.try_enter({"id": "spy_open_drive", "target_delta": 0.2}, {}, "call", 765.0,
                        datetime(2026, 10, 19, 10, 0, tzinfo=ET))
        finally:
            botmod.chain_candidates = old
        return b, orders

    def test_sized_on_its_ledger_despite_index_theme_taken(self):
        b, orders = self._enter({"equity": 300.0, "paused": False, "generation": 1})
        self.assertEqual(orders, [("SPY261019C00770000", 2)])  # 20% of $300 at $0.30 x 100
        self.assertEqual(b.state["real_underlyings"], ["SPY"])  # main theme list untouched

    def test_paused_ledger_trades_shadow_only(self):
        b, orders = self._enter({"equity": 300.0, "paused": True, "generation": 1})
        self.assertEqual(orders, [])

    def test_gated_ledger_trades_shadow_only(self):
        b, orders = self._enter({"equity": 300.0, "paused": False, "generation": 1, "gated": True})
        self.assertEqual(orders, [])
        b, orders = self._enter({"equity": 300.0, "paused": False, "generation": 1, "gated": False})
        self.assertEqual(orders, [("SPY261019C00770000", 2)])


class RealGateTest(unittest.TestCase):
    """`real_when` on a ledger variant: real orders only when the condition held at the last close."""

    RULE = {"id": "stock_open_drive", "real_when": {"symbol": "SMH", "below_average": 20}}

    class Api:
        def __init__(self, closes, fail=()):
            self.closes, self.fail, self.feeds = closes, fail, []

        def daily_bars_multi(self, symbols, start, end, feed="sip"):
            self.feeds.append(feed)
            if feed in self.fail:
                raise botmod.AlpacaError(403, "no")
            # one bar a day, the newest on 2026-11-23 (today's own bar, which must not count)
            first = date(2026, 11, 23) - timedelta(days=len(self.closes) - 1)
            return {symbols[0]: [{"t": f"{first + timedelta(days=i)}T05:00:00Z", "c": c}
                                 for i, c in enumerate(self.closes)]}

    def test_no_rule_is_always_on(self):
        self.assertEqual(ledgers.real_gate(None, {"id": "spy_open_drive"}, "2026-11-23"), (True, ""))
        self.assertEqual(ledgers.real_gate(None, None, "2026-11-23"), (True, ""))

    def test_below_the_average_is_on_and_above_is_off(self):
        falling = [530 - i for i in range(24)] + [999]          # the last bar is today's and must not count
        ok, note = ledgers.real_gate(self.Api(falling), self.RULE, "2026-11-23")
        self.assertTrue(ok)
        self.assertIn("below its 20-day average", note)
        rising = [500 + i for i in range(24)] + [1]
        ok, note = ledgers.real_gate(self.Api(rising), self.RULE, date(2026, 11, 23))
        self.assertFalse(ok)
        self.assertIn("SMH closed 523.00, above its 20-day average 513.50", note)

    def test_unknown_state_is_shadow_only(self):
        self.assertFalse(ledgers.real_gate(None, self.RULE, "2026-11-23")[0])                       # no api
        self.assertFalse(ledgers.real_gate(self.Api([500.0] * 10), self.RULE, "2026-11-23")[0])     # too few bars
        api = self.Api([530 - i for i in range(25)], fail=("sip", "iex"))
        ok, note = ledgers.real_gate(api, self.RULE, "2026-11-23")
        self.assertFalse(ok)
        self.assertIn("daily bars failed", note)

        class Down:
            def daily_bars_multi(self, *a, **k):
                raise OSError("network unreachable")
        ok, note = ledgers.real_gate(Down(), self.RULE, "2026-11-23")      # never raises into the bot's start
        self.assertFalse(ok)
        self.assertIn("network unreachable", note)

    def test_falls_back_to_iex_when_sip_refuses(self):
        api = self.Api([530 - i for i in range(25)], fail=("sip",))
        self.assertTrue(ledgers.real_gate(api, self.RULE, "2026-11-23")[0])
        self.assertEqual(api.feeds, ["sip", "iex"])

    def test_start_ledgers_marks_the_gated_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            saved = (journal.JOURNAL_DIR, journal.TRADES_PATH, ledgers.PATH)
            journal.JOURNAL_DIR, journal.TRADES_PATH, ledgers.PATH = tmp, tmp / "t.csv", tmp / "ledgers.json"
            try:
                config = {"ledgers": dict(CFG, variants=["stock_open_drive", "spy_open_drive"]),
                          "variants": [self.RULE, {"id": "spy_open_drive"}]}
                out = botmod.start_ledgers(config, "2026-11-23", self.Api([500 + i for i in range(25)]))
            finally:
                journal.JOURNAL_DIR, journal.TRADES_PATH, ledgers.PATH = saved
        self.assertTrue(out["stock_open_drive"]["gated"])
        self.assertFalse(out["spy_open_drive"]["gated"])
        self.assertEqual(out["stock_open_drive"]["equity"], 500)


class SpreadGateTest(unittest.TestCase):
    """A quote wider than MAX_SPREAD gets no real order; the shadow books the mid (GE 330C 0.09/0.54, 11-06)."""

    def _enter(self, bid, ask):
        orders = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.api, self.dry_run, self.underlying = None, False, "SPY"
                self.today = date(2026, 11, 6)
                self.config = {"backtest": {"start_equity": 500}, "ledgers": CFG}
                self.state = {"equity_start": 457.0, "risk_per_trade": 0.2, "champion": "rebound_scanner",
                              "real_underlyings": [], "ledgers": {"spy_open_drive": {"equity": 500.0, "paused": False, "generation": 1}}}

            def _order(self, symbol, qty, side, kind, tag, limit=None):
                orders.append((symbol, qty, limit))
                return qty, limit

        b = FakeBot()
        vstate = {}
        old = botmod.chain_candidates
        botmod.chain_candidates = lambda *a, **k: [{"symbol": "SPY261106C00740000", "strike": 740, "ask": ask,
                                                    "bid": bid, "delta": 0.13, "quote_time": None}]
        try:
            b.try_enter({"id": "spy_open_drive", "target_delta": 0.15}, vstate, "call", 736.0,
                        datetime(2026, 11, 6, 10, 21, tzinfo=ET))
        finally:
            botmod.chain_candidates = old
        return orders, vstate

    def test_wide_quote_is_shadow_only_at_the_mid(self):
        orders, vstate = self._enter(bid=0.09, ask=0.54)
        self.assertEqual(orders, [])
        self.assertEqual(vstate["shadow"]["entry_price"], 0.32)  # mid 0.315 rounded up to the tick
        # since 2026-11-09 the shadow of a ledger variant is sized off its ledger: CFG risk 20% of $500 at $0.32
        self.assertEqual(vstate["shadow"]["qty"], 3)

    def test_normal_quote_still_trades_real_at_the_ask(self):
        orders, vstate = self._enter(bid=0.50, ask=0.54)
        self.assertEqual(orders, [("SPY261106C00740000", 1, 0.54)])
        self.assertEqual(vstate["shadow"]["entry_price"], 0.54)

    def test_spread_of(self):
        self.assertAlmostEqual(botmod.spread_of({"ask": 0.54, "bid": 0.09}), 0.8333, places=3)
        self.assertEqual(botmod.spread_of({"ask": 0.54, "bid": None}), 0.0)
        self.assertEqual(botmod.spread_of({"ask": 0, "bid": 0}), 0.0)


class LedgerBookingTest(unittest.TestCase):
    def test_real_exit_books_ledger_and_shifts_main_anchor(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            saved = (journal.JOURNAL_DIR, journal.TRADES_PATH, journal.EXITS_PATH, journal.LEDGER_PATH, ledgers.PATH)
            journal.JOURNAL_DIR, journal.TRADES_PATH, journal.EXITS_PATH = tmp, tmp / "t.csv", tmp / "e.csv"
            journal.LEDGER_PATH, ledgers.PATH = tmp / "ledger.json", tmp / "ledgers.json"
            try:
                journal.save_ledger({"base": 500, "generation": 1, "anchor": 50000.0})

                class FakeBot(botmod.Bot):
                    def __init__(self):
                        self.config = {"ledgers": CFG}
                        self.state = {"date": "2026-10-19", "phase": "zero-or-hero", "equity_start": 677.0}

                pos = {"contract": "SPY261019C00770000", "entry_price": 0.30, "entry_time": "2026-10-19T10:00"}
                FakeBot()._record({"id": "spy_open_drive"}, "real", pos, 0.90, datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                                  "trail", 2, 1.0)
                FakeBot()._record({"id": "catalyst_open"}, "real", pos, 0.10, datetime(2026, 10, 19, 12, 0, tzinfo=ET),
                                  "time", 1, 0.3)
                book, main = ledgers.load(), journal.load_ledger()
            finally:
                (journal.JOURNAL_DIR, journal.TRADES_PATH, journal.EXITS_PATH, journal.LEDGER_PATH,
                 ledgers.PATH) = saved
        self.assertEqual(book["spy_open_drive"]["realized"], 120.0)
        self.assertEqual(book["spy_open_drive"]["real_trades"], 1)
        self.assertNotIn("catalyst_open", book)
        self.assertEqual(main["anchor"], 50120.0)  # main ledger ignores the $120


if __name__ == "__main__":
    unittest.main()


class AlreadySoldTest(unittest.TestCase):
    """2026-10-19: a second run booked positions the first run had sold as expired at 0."""

    def _bot(self, positions, orders):
        class Api:
            def positions(self):
                return positions

            def orders(self, after):
                return orders

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.api, self.today = Api(), date(2026, 10, 19)

        return FakeBot()

    def test_books_the_earlier_fill(self):
        fills = [{"symbol": "TSLA261019C00365000", "side": "sell", "filled_qty": "1", "filled_avg_price": "3.7"},
                 {"symbol": "MSFT261019C00537500", "side": "sell", "filled_qty": "3", "filled_avg_price": "0.01"}]
        b = self._bot([], fills)
        self.assertEqual(b._already_sold({"contract": "TSLA261019C00365000"}), 3.7)
        self.assertIsNone(b._already_sold({"contract": "AMZN261019C00262500"}))

    def test_still_held_is_not_sold(self):
        b = self._bot([{"symbol": "TSLA261019C00365000"}], [])
        self.assertIsNone(b._already_sold({"contract": "TSLA261019C00365000"}))


class ReportedRecentlyTest(unittest.TestCase):
    """leader_follow skips names that just reported (NFLX 2026-10-21/22)."""

    def test_window(self):
        from zoh.strategy import reported_recently
        cal = {"2026-10-20": ["NFLX"], "2026-10-21": ["TSLA", "META"], "2026-10-28": ["MSFT"]}
        self.assertTrue(reported_recently("NFLX", date(2026, 10, 22), cal, 3))
        self.assertTrue(reported_recently("NFLX", date(2026, 10, 23), cal, 3))
        self.assertFalse(reported_recently("NFLX", date(2026, 10, 26), cal, 3))  # 4 weekdays later
        self.assertTrue(reported_recently("META", date(2026, 10, 21), cal, 3))   # report day itself
        self.assertFalse(reported_recently("MSFT", date(2026, 10, 22), cal, 3))  # reports later
        self.assertFalse(reported_recently("AAPL", date(2026, 10, 22), cal, 3))


class ReportsSoonTest(unittest.TestCase):
    """Carried news picks are sold before the underlying's report (INTC 2026-10-26)."""

    def test_today_or_next_weekday(self):
        from zoh.strategy import reports_soon
        cal = {"2026-10-29": ["INTC", "AMZN"], "2026-11-02": ["AAPL"]}
        self.assertFalse(reports_soon("INTC", date(2026, 10, 27), cal))
        self.assertTrue(reports_soon("INTC", date(2026, 10, 28), cal))   # day before
        self.assertTrue(reports_soon("INTC", date(2026, 10, 29), cal))   # report day
        self.assertTrue(reports_soon("AAPL", date(2026, 10, 30), cal))   # Friday before a Monday report
        self.assertFalse(reports_soon("AAPL", date(2026, 10, 29), cal))
        self.assertFalse(reports_soon("MSFT", date(2026, 10, 28), cal))


class StockChainWidthTest(unittest.TestCase):
    """Single-stock entries search a strike band wide enough to reach affordable OTM strikes."""

    def test_try_enter_uses_the_wide_band(self):
        seen = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.underlying = date(2026, 10, 27), True, "SPY"
                self.config = {"backtest": {"start_equity": 500}}
                self.state = {"equity_start": 685.0, "risk_per_trade": 0.2}

            def nearest_chain(self, underlying, direction, spot, now, width):
                seen.append(width)
                return []

        b = FakeBot()
        b.try_enter({"id": "catalyst_intraday", "target_delta": 0.2}, {}, "call", 131.3,
                    datetime(2026, 10, 27, 13, 21, tzinfo=ET), underlying="ORCL")
        self.assertEqual(seen, [botmod.STOCK_WIDTH])
        self.assertGreaterEqual(botmod.STOCK_WIDTH, 0.15)



class EntryRetryTest(unittest.TestCase):
    """An entry unfilled at the ask is retried once at a fresh ask within ENTRY_RETRY_SLACK."""

    def _buy(self, fresh_ask, symbol="AMAT261030C00445000", ask=1.32):
        orders = []

        class Api:
            def option_snapshots(self, symbols):
                return {symbols[0]: {"latestQuote": {"ap": fresh_ask, "bp": 1.0}}}

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.api = Api()

            def _order(self, symbol, qty, side, kind, tag, limit=None):
                orders.append((tag, limit))
                return (0, None) if tag == "in" else (qty, limit)

        return FakeBot()._buy_entry(symbol, 1, ask), orders

    def test_retries_at_the_fresh_ask(self):
        result, orders = self._buy(1.38)
        self.assertEqual(orders, [("in", 1.32), ("in2", 1.38)])
        self.assertEqual(result, (1, 1.38))

    def test_no_retry_when_the_ask_ran_away(self):
        result, orders = self._buy(1.60)
        self.assertEqual(orders, [("in", 1.32)])
        self.assertEqual(result, (0, None))

    def test_index_contract_retries_within_half(self):
        """2026-11-09: SPY 753C 0.37 -> fresh ask 0.51 (+38%) must be retried; a stock stays at 10%."""
        result, orders = self._buy(0.51, "SPY261109C00753000", 0.37)
        self.assertEqual(orders, [("in", 0.37), ("in2", 0.51)])
        self.assertEqual(result, (1, 0.51))
        result, orders = self._buy(0.60, "SPY261109C00753000", 0.37)
        self.assertEqual(orders, [("in", 0.37)])
        result, orders = self._buy(0.51, "TSLA261109C00385000", 0.37)
        self.assertEqual(orders, [("in", 0.37)])
        self.assertEqual(botmod.retry_slack("QQQ261109P00670000"), botmod.INDEX_RETRY_SLACK)
        self.assertEqual(botmod.retry_slack("NVDA261109C00185000"), botmod.ENTRY_RETRY_SLACK)


class ExpiryDeltaTest(unittest.TestCase):
    """Fallback deltas use the time to the contract's expiry, not to today's close."""

    def test_friday_option_on_thursday_has_a_day_and_a_half(self):
        from zoh.strategy import years_to_close, years_to_expiry
        now = datetime(2026, 10, 29, 9, 46, tzinfo=ET)
        today = years_to_close(now)
        self.assertAlmostEqual(years_to_expiry(now, date(2026, 10, 29)), today)
        self.assertAlmostEqual(years_to_expiry(now, date(2026, 10, 30)), today + 390 / (252 * 390))
        self.assertAlmostEqual(years_to_expiry(now, date(2026, 11, 2)), today + 2 * 390 / (252 * 390))

    def test_implied_vol_round_trip(self):
        from zoh.strategy import bs_price, implied_vol
        p = bs_price(161.0, 185.0, 1.5 / 252, 1.2, "call")
        self.assertAlmostEqual(implied_vol(p, 161.0, 185.0, 1.5 / 252, "call"), 1.2, places=3)
        self.assertIsNone(implied_vol(0, 161.0, 185.0, 1.5 / 252, "call"))

    def test_chain_without_greeks_gets_a_real_delta(self):
        class Api:
            def option_chain(self, *a, **k):
                return {"COIN261030C00185000": {"latestQuote": {"ap": 0.70, "bp": 0.60}},
                        "COIN261030C00170000": {"latestQuote": {"ap": 2.10, "bp": 1.95}}}
        c = botmod.chain_candidates(Api(), "COIN", date(2026, 10, 30), "call", 161.23,
                                    datetime(2026, 10, 29, 9, 46, tzinfo=ET), width=0.15)
        deltas = {x["strike"]: x["delta"] for x in c}
        self.assertGreater(deltas[185.0], 0.05)  # was 0.00 with years-to-today's-close and IV 0.16
        self.assertGreater(deltas[170.0], deltas[185.0])


class NoEntryIntoPrintTest(unittest.TestCase):
    """No new position on a name that reports today or the next trading day."""

    def test_try_enter_skips_a_reporting_name(self):
        seen = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.underlying = date(2026, 10, 29), True, "SPY"
                self.config = {"backtest": {"start_equity": 500}}
                self.state = {"equity_start": 727.0, "risk_per_trade": 0.2}
                self.earnings = {"2026-10-29": ["COIN"], "2026-11-02": ["AAPL"]}

            def nearest_chain(self, underlying, direction, spot, now, width):
                seen.append(underlying)
                return []

        b = FakeBot()
        b.try_enter({"id": "leader_follow", "target_delta": 0.2}, {}, "call", 161.2,
                    datetime(2026, 10, 29, 9, 46, tzinfo=ET), underlying="COIN")
        b.try_enter({"id": "leader_follow", "target_delta": 0.2}, {}, "call", 349.0,
                    datetime(2026, 10, 29, 9, 46, tzinfo=ET), underlying="AAPL")
        b.try_enter({"id": "leader_follow", "target_delta": 0.2}, {}, "call", 630.0,
                    datetime(2026, 10, 29, 9, 46, tzinfo=ET), underlying="META")
        self.assertEqual(seen, ["AAPL", "META"])  # AAPL reports Monday, not the next weekday

    def test_news_picks_skip_the_day_after_a_report(self):
        seen = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.underlying = date(2026, 10, 30), True, "SPY"
                self.config = {"backtest": {"start_equity": 500}}
                self.state = {"equity_start": 1167.0, "risk_per_trade": 0.2}
                self.earnings = {"2026-10-29": ["AMZN"], "2026-10-27": ["V"]}

            def nearest_chain(self, underlying, direction, spot, now, width):
                seen.append(underlying)
                return []

        b = FakeBot()
        now = datetime(2026, 10, 30, 13, 21, tzinfo=ET)
        news = {"id": "catalyst_intraday", "signal": "catalyst", "target_delta": 0.2}
        b.try_enter(news, {}, "put", 238.5, now, underlying="AMZN")
        b.try_enter(news, {}, "call", 413.0, now, underlying="V")
        b.try_enter({"id": "rebound_scanner", "signal": "gap", "target_delta": 0.08}, {}, "call", 232.5,
                    now, underlying="AMZN")
        self.assertEqual(seen, ["V", "AMZN"])  # the scanner is not a news pick


class OpportunityScoreTest(unittest.TestCase):
    def test_score_signs_by_direction(self):
        from zoh.research.opportunities import score
        bars = [{"t": "2026-10-29T13:30:00Z", "o": 100, "h": 101, "l": 99, "c": 100.5},
                {"t": "2026-10-29T14:00:00Z", "o": 101, "h": 103, "l": 100, "c": 102},
                {"t": "2026-10-29T19:59:00Z", "o": 102, "h": 102, "l": 98, "c": 99}]
        call = score(bars, "10:00", "call")
        self.assertEqual(call["entry"], 101)
        self.assertAlmostEqual(call["entry_close_pct"], -1.98, places=2)
        self.assertAlmostEqual(call["best_after_entry_pct"], 1.98, places=2)
        put = score(bars, "10:00", "put")
        self.assertAlmostEqual(put["entry_close_pct"], 1.98, places=2)
        self.assertAlmostEqual(put["open_close_pct"], 1.0, places=2)

    def test_collect_reads_all_three_sources(self):
        import json as _json
        from zoh.research.opportunities import collect
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bias" / "intraday").mkdir(parents=True)
            (root / "opportunities").mkdir()
            (root / "bias" / "2026-10-29.json").write_text(_json.dumps({
                "sniper": {"symbol": "V", "direction": "call", "catalyst_type": "company_news"},
                "opportunities": [{"type": "rotation_laggard", "symbol": "META", "direction": "call"}]}))
            (root / "bias" / "intraday" / "2026-10-29.json").write_text(_json.dumps({
                "picks": [{"time": "13:16", "symbol": "ORCL", "direction": "put"}]}))
            (root / "opportunities" / "2026-10-29.json").write_text(_json.dumps({
                "opportunities": [{"type": "financing_fade", "symbol": "MSFT", "direction": "put"}]}))
            got = [(o["symbol"], o["source"]) for o in collect("2026-10-29", root)]
        self.assertEqual(got, [("V", "sniper"), ("META", "premarket"), ("ORCL", "intraday"), ("MSFT", "review")])

    def test_pick_action_follows_the_variant_real_risk(self):
        import json as _json
        from zoh import journal
        from zoh.research.opportunities import collect, pick_action
        live = {"variants": [{"id": "catalyst_open", "real_risk": 0.2}, {"id": "catalyst_intraday", "real_risk": 0.2}]}
        shadow = {"variants": [{"id": "catalyst_open", "real_risk": 0}, {"id": "catalyst_intraday", "real_risk": 0}]}
        self.assertEqual(pick_action("sniper", live), "real")
        self.assertEqual(pick_action("intraday", shadow), "shadow")
        self.assertEqual(pick_action("sniper", {"variants": []}), "shadow")
        # the checked-in config has both shadow-only since 2026-11-09
        self.assertEqual(pick_action("sniper", journal.load_config()), "shadow")
        self.assertEqual(pick_action("intraday", journal.load_config()), "shadow")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bias" / "intraday").mkdir(parents=True)
            (root / "bias" / "2026-11-10.json").write_text(_json.dumps({"sniper": {"symbol": "TSM", "direction": "call"}}))
            (root / "bias" / "intraday" / "2026-11-10.json").write_text(_json.dumps(
                {"picks": [{"time": "10:18", "symbol": "AMZN", "direction": "call"}]}))
            self.assertEqual([o["action"] for o in collect("2026-11-10", root, live)], ["real", "real"])
            self.assertEqual([o["action"] for o in collect("2026-11-10", root, shadow)], ["shadow", "shadow"])


class NotifyTest(unittest.TestCase):
    def test_no_webhook_is_a_quiet_no_op(self):
        import os
        from zoh import notify
        names = list(notify.CHANNELS.values()) + [notify.FALLBACK]
        saved = {n: os.environ.pop(n) for n in names if n in os.environ}
        try:
            self.assertFalse(notify.post("hello", "premarket"))
            os.environ["DISCORD_WEBHOOK_URL"] = "https://example.invalid/fallback"
            self.assertEqual(notify.webhook("premarket"), "https://example.invalid/fallback")
            os.environ["DISCORD_WEBHOOK_PREMARKET"] = "https://example.invalid/premarket"
            self.assertEqual(notify.webhook("premarket"), "https://example.invalid/premarket")
            self.assertEqual(notify.webhook("trades"), "https://example.invalid/fallback")
        finally:
            for n in names:
                os.environ.pop(n, None)
            os.environ.update(saved)

    def test_channels_without_a_webhook_fall_back_to_the_owners_channel(self):
        import os
        from zoh import notify
        names = list(notify.CHANNELS.values()) + [notify.FALLBACK]
        saved = {n: os.environ.pop(n) for n in names if n in os.environ}
        try:
            os.environ["DISCORD_WEBHOOK_PREMARKET"] = "https://example.invalid/premarket"
            self.assertEqual(notify.webhook("review"), "https://example.invalid/premarket")
            self.assertEqual(notify.webhook("intraday"), "https://example.invalid/premarket")
            self.assertFalse(notify.has_own("review"))
        finally:
            for n in names:
                os.environ.pop(n, None)
            os.environ.update(saved)
        msg = notify.check_message({"date": "2026-11-02", "text": "大盘：不做，对。"})
        self.assertEqual(msg, "**🔎 盘后核对 2026-11-02**\n大盘：不做，对。")
        self.assertEqual(notify.check_message({"date": "2026-11-02"}), "")

    def test_messages_are_plain_chinese(self):
        from zoh import notify
        bias = {"date": "2026-11-02", "bias": "none", "p_up": 0.53, "summary": "English summary",
                "zh": {"summary": "反弹日，不做。", "heating": "医疗", "cooling": "芯片"},
                "sniper": {"symbol": "GEV", "direction": "call", "catalyst": "HSBC upgrade"},
                "opportunities": [{"type": "financing_fade", "symbol": "ORCL", "direction": "put",
                                   "why": "offering", "why_zh": "增发 $200 亿", "action": "none"}]}
        text = notify.bias_message(bias)
        self.assertIn("大盘 SPY：**不做**（收盘高于开盘的概率 53%）", text)
        self.assertIn("理由：反弹日，不做。", text)
        self.assertIn("狙击：**GEV 看涨**", text)
        self.assertIn("1. ORCL 看跌｜借钱搞 AI 被抛：增发 $200 亿（只记录）", text)
        self.assertNotIn("English summary", text)
        self.assertEqual(notify._contract("ORCL261030P00134000"), "ORCL 10-30 134 看跌")
        self.assertEqual(notify._usd(-215.0), "-$215")

    def test_long_text_is_split_under_the_limit(self):
        from zoh import notify
        parts = notify.chunks("x" * 50 + "\n" + "y" * 4000)
        self.assertTrue(all(len(p) <= 2000 for p in parts))
        self.assertEqual("".join(parts).replace("\n", ""), "x" * 50 + "y" * 4000)


class ShadowRiskTest(unittest.TestCase):
    """A shadow-only variant can size off its own fraction of the stake ("shadow_risk"): the hero
    shadows (2026-11-03) put the whole ledger on one pick; the default is the phase risk."""

    def _enter(self, variant):
        class FakeBot(botmod.Bot):
            def __init__(self):
                self.today, self.dry_run, self.underlying = date(2026, 11, 3), True, "SPY"
                self.config = {"backtest": {"start_equity": 500}}
                self.state = {"equity_start": 500.0, "risk_per_trade": 0.2, "champion": "rebound_scanner"}

            def nearest_chain(self, underlying, direction, spot, now, width):
                return [{"symbol": "MU261103P00860000", "strike": 860.0, "ask": 0.5, "bid": 0.45,
                         "delta": -0.2}]

        vstate = {}
        FakeBot().try_enter(variant, vstate, "put", 870.0, datetime(2026, 11, 3, 11, 3, tzinfo=ET),
                            underlying="MU")
        return vstate["shadow"]["qty"]

    def test_hero_shadow_takes_the_whole_stake(self):
        self.assertEqual(self._enter({"id": "catalyst_intraday_hero", "target_delta": 0.2, "shadow_risk": 1.0}), 10)
        self.assertEqual(self._enter({"id": "catalyst_intraday", "target_delta": 0.2}), 2)

    def test_hero_shadows_hold_to_the_close(self):
        config = json.loads((journal.ROOT / "config" / "strategy.json").read_text())
        heroes = [v for v in config["variants"] if v["id"].endswith("_hero")]
        self.assertEqual(len(heroes), 2)
        for v in heroes:
            self.assertEqual(v["shadow_risk"], 1.0)
            self.assertNotIn("real_risk", v)
            for k in ("take_profit", "stop_loss", "trail_after"):
                self.assertIsNone(v.get(k), k)
            self.assertNotIn("half_at", v)
        self.assertLessEqual(len(config["variants"]), 12)


class LedgerSizingTest(unittest.TestCase):
    """Owner, 2026-11-09: a ledger variant buys one contract near the money for up to half its ledger,
    and the sniper / intraday pick variants are shadow-only until their live rule turns positive."""

    def test_ledger_budget_and_contract_cap(self):
        self.assertEqual(botmod.ledger_budget({"equity": 410.0}, {"risk": 0.5}), 205.0)
        self.assertEqual(botmod.ledger_budget({"equity": 410.0}, {}), 82.0)
        self.assertEqual(botmod.cap_contracts(3, {"max_contracts": 1}), 1)
        self.assertEqual(botmod.cap_contracts(3, {}), 3)
        self.assertEqual(botmod.cap_contracts(0, {"max_contracts": 1}), 0)

    def test_config_after_2026_11_09(self):
        config = json.loads((journal.ROOT / "config" / "strategy.json").read_text())
        cfg = config["ledgers"]
        self.assertEqual(cfg["risk"], 0.5)
        self.assertEqual(cfg["max_contracts"], 1)
        self.assertLessEqual(cfg["one_contract_cap"], 0.5)
        by_id = {v["id"]: v for v in config["variants"]}
        for vid in cfg["variants"]:
            self.assertTrue(0.30 <= by_id[vid]["target_delta"] <= 0.45, vid)
        for vid in ("catalyst_open", "catalyst_intraday"):
            self.assertEqual(by_id[vid].get("real_risk", 0), 0, vid)
        # the hero shadows still put the whole ledger on the pick
        for vid in ("catalyst_open_hero", "catalyst_intraday_hero"):
            self.assertEqual(by_id[vid]["shadow_risk"], 1.0)

    def _enter_ledger(self, candidates, cfg):
        orders = []

        class FakeBot(botmod.Bot):
            def __init__(self):
                self.api, self.dry_run, self.underlying = None, False, "SPY"
                self.today = date(2026, 11, 9)
                self.config = {"backtest": {"start_equity": 500}, "ledgers": cfg}
                self.state = {"equity_start": 457.0, "risk_per_trade": 0.2, "champion": "nvda_gapdown_put",
                              "real_underlyings": [],
                              "ledgers": {"spy_open_drive": {"equity": 410.0, "paused": False, "generation": 1}}}

            def _order(self, symbol, qty, side, kind, tag, limit=None):
                orders.append((symbol, qty, limit))
                return qty, limit

        vstate = {}
        old = botmod.chain_candidates
        botmod.chain_candidates = lambda *a, **k: candidates
        try:
            FakeBot().try_enter({"id": "spy_open_drive", "target_delta": 0.35}, vstate, "call", 747.5,
                                datetime(2026, 11, 9, 10, 1, tzinfo=ET))
        finally:
            botmod.chain_candidates = old
        return orders, vstate

    def test_ledger_variant_buys_one_near_the_money_contract_off_its_ledger(self):
        """2026-11-09 10:01: SPY 747.5. The old 20% / 0.15-delta rule bought the 753C at 0.37; half the
        $410 ledger ($205) now buys the 0.35-delta 750C at 1.80, one contract, shadow and real alike."""
        cands = [{"symbol": "SPY261109C00753000", "strike": 753, "ask": 0.37, "bid": 0.36, "delta": 0.14, "quote_time": None},
                 {"symbol": "SPY261109C00750000", "strike": 750, "ask": 1.80, "bid": 1.78, "delta": 0.36, "quote_time": None},
                 {"symbol": "SPY261109C00748000", "strike": 748, "ask": 2.90, "bid": 2.85, "delta": 0.48, "quote_time": None}]
        cfg = {"base": 500, "dead": 50, "risk": 0.5, "one_contract_cap": 0.5, "pause_after": 5, "max_contracts": 1}
        orders, vstate = self._enter_ledger(cands, cfg)
        self.assertEqual(vstate["shadow"]["contract"], "SPY261109C00750000")
        self.assertEqual(vstate["shadow"]["qty"], 1)
        self.assertEqual(orders, [("SPY261109C00750000", 1, 1.80)])
        self.assertEqual(vstate["real"]["qty"], 1)
        # a cheap contract would afford several; max_contracts keeps it to one
        cheap = [{"symbol": "SPY261109C00751000", "strike": 751, "ask": 0.80, "bid": 0.78, "delta": 0.33, "quote_time": None}]
        orders, vstate = self._enter_ledger(cheap, cfg)
        self.assertEqual(vstate["shadow"]["qty"], 1)
        self.assertEqual(orders, [("SPY261109C00751000", 1, 0.80)])
        # nothing within half the ledger at the delta floor: no entry at all
        pricey = [{"symbol": "SPY261109C00748000", "strike": 748, "ask": 2.90, "bid": 2.85, "delta": 0.48, "quote_time": None}]
        orders, vstate = self._enter_ledger(pricey, cfg)
        self.assertNotIn("shadow", vstate)
        self.assertEqual(orders, [])
