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

