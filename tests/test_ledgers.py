import tempfile
import unittest
from datetime import date, datetime
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

    def _buy(self, fresh_ask):
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

        return FakeBot()._buy_entry("AMAT261030C00445000", 1, 1.32), orders

    def test_retries_at_the_fresh_ask(self):
        result, orders = self._buy(1.38)
        self.assertEqual(orders, [("in", 1.32), ("in2", 1.38)])
        self.assertEqual(result, (1, 1.38))

    def test_no_retry_when_the_ask_ran_away(self):
        result, orders = self._buy(1.60)
        self.assertEqual(orders, [("in", 1.32)])
        self.assertEqual(result, (0, None))


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


class NotifyTest(unittest.TestCase):
    def test_no_webhook_is_a_quiet_no_op(self):
        import os
        from zoh import notify
        saved = os.environ.pop("DISCORD_WEBHOOK_URL", None)
        try:
            self.assertFalse(notify.post("hello"))
        finally:
            if saved is not None:
                os.environ["DISCORD_WEBHOOK_URL"] = saved

    def test_long_text_is_split_under_the_limit(self):
        from zoh import notify
        parts = notify.chunks("x" * 50 + "\n" + "y" * 4000)
        self.assertTrue(all(len(p) <= 2000 for p in parts))
        self.assertEqual("".join(parts).replace("\n", ""), "x" * 50 + "y" * 4000)
