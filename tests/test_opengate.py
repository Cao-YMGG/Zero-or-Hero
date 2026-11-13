import unittest
from datetime import date, timedelta

from zoh.research import opengate as g


def trade(sym, day, hold, kind="call", move=0.01, macro=""):
    return {"sym": sym, "day": day, "kind": kind, "move10": move, "macro": macro, "spot": 100.0,
            "d35": {"exits": {"hold": hold, "take3": hold, "trail": hold, "half3_trail": hold}}}


class OpenGate(unittest.TestCase):
    def test_signal_follows_the_live_thresholds(self):
        self.assertEqual(g.signal("SPY", 0.0051), "call")
        self.assertEqual(g.signal("SPY", -0.0051), "put")
        self.assertIsNone(g.signal("SPY", 0.0049))
        self.assertEqual(g.signal("TSLA", 0.008), "call")
        self.assertIsNone(g.signal("TSLA", 0.0079))
        self.assertIsNone(g.signal("NVDA", -0.03))   # the stock ledger buys calls only

    def test_stats_without_the_best(self):
        n, win, avg, cut1, cut2 = g.stats([-1.0, -1.0, 0.5, 4.0])
        self.assertEqual((n, win), (4, 0.5))
        self.assertAlmostEqual(avg, 0.625)
        self.assertAlmostEqual(cut1, -0.5)
        self.assertAlmostEqual(cut2, -1.0)
        self.assertEqual(g.stats([]), (0, None, None, None, None))
        self.assertIsNone(g.stats([1.0, 2.0])[4])    # nothing left once the best two are gone

    def test_shuffle_test_separates_a_real_gap_from_none(self):
        days = [(date(2026, 1, 5) + timedelta(days=i)).isoformat() for i in range(40)]
        lit = {d: i % 2 == 0 for i, d in enumerate(days)}
        strong = [trade("NVDA", d, 1.0 if lit[d] else -1.0) for d in days]
        gap, p_avg, win_gap, p_win = g.shuffle_test(strong, lit, lambda t: t["d35"]["exits"]["hold"], shuffles=500)
        self.assertAlmostEqual(gap, 2.0)
        self.assertLess(p_avg, 0.01)
        self.assertLess(p_win, 0.01)
        flat = [trade("NVDA", d, 1.0 if i % 4 < 2 else -1.0) for i, d in enumerate(days)]
        gap, p_avg, _, _ = g.shuffle_test(flat, lit, lambda t: t["d35"]["exits"]["hold"], shuffles=500)
        self.assertAlmostEqual(gap, 0.0)
        self.assertGreater(p_avg, 0.3)
        self.assertIsNone(g.shuffle_test(strong, {d: True for d in days}, lambda t: 0.0, shuffles=10))

    def test_live_rule_keeps_the_ledgers_own_days(self):
        monday, friday = "2026-11-02", "2026-11-06"       # neither is in a monthly-expiry week
        opex_wed = "2026-11-18"                           # third Friday is 11-20
        rows = [trade("NVDA", monday, 0.1, move=0.009), trade("TSLA", monday, 0.2, move=0.02),
                trade("TSLA", friday, 0.3), trade("TSLA", opex_wed, 0.4),
                trade("NVDA", "2026-11-04", 0.5, macro="CPI"),
                trade("SPY", monday, 0.6, kind="put", move=-0.006), trade("SPY", friday, 0.7, kind="put", move=-0.006)]
        stock = g.live_rule(rows, "stock")
        self.assertEqual([(t["sym"], t["day"]) for t in stock], [("TSLA", monday)])   # the stronger of the two
        self.assertEqual([t["day"] for t in g.live_rule(rows, "spy_put")], [monday])  # Monday to Thursday
        self.assertEqual(g.live_rule(rows, "spy_call"), [])

    def test_evenings_are_keyed_by_the_next_session(self):
        days = [date(2026, 1, 1) + timedelta(days=i) for i in range(40)]
        fall = [100 - i for i in range(40)]               # every name below its 20-day average at the end
        bars = {s: [(d, c, c) for d, c in zip(days, fall)] for s in ("NVDA", "TSLA")}
        members = [{d: (c, c) for d, c in zip(days, fall)} for _ in range(4)]
        lights = {k: False for k in g.SINGLE}
        data = {"days": days, "spy": [100.0] * 40, "smh": fall, "bars": bars, "members": members,
                "rows": [{"i": 30, "day": days[30], "lights": lights},
                         {"i": 39, "day": days[39], "lights": dict(lights, breadth=True)}]}
        state = g.evenings(data)
        self.assertEqual(set(state), {days[31].isoformat(), "next"})
        first = state[days[31].isoformat()]
        self.assertEqual(first["evening"], days[30].isoformat())
        self.assertEqual(first["share"], 1.0)
        self.assertTrue(first["smh_below"] and first["NVDA_below"] and first["TSLA_down5"])
        self.assertFalse(first["spy_below"] or first["breadth"])
        self.assertTrue(state["next"]["breadth"])

    def test_cells_and_long_average(self):
        self.assertEqual(g.cell_of(True, True), "dip in an uptrend")
        self.assertEqual(g.cell_of(True, False), "dip in a downtrend")
        self.assertEqual(g.cell_of(False, True), "above its 20-day average")
        rising = [float(i) for i in range(1, 121)]
        self.assertTrue(g.above_long(rising, 119))
        self.assertFalse(g.above_long(rising[::-1], 119))
        self.assertFalse(g.above_long(rising, 30))        # under 80 closes: not enough to call a trend

    def test_best_quarters_and_positive_count(self):
        rows = [trade("NVDA", "2026-05-04", 5.0), trade("NVDA", "2026-05-06", -1.0),    # Q2: +4
                trade("TSLA", "2026-08-03", 2.0),                                       # Q3: +2
                trade("TSLA", "2026-02-02", -1.0), trade("TSLA", "2025-11-03", -0.5)]   # two losing quarters
        value = lambda t: t["d35"]["exits"]["hold"]
        self.assertEqual(g.quarter_of(rows[0]), "2026 Q2")
        self.assertEqual(g.best_quarters(rows, value), (["2026 Q2", "2026 Q3"], 2, 4))
        self.assertEqual(g.best_quarters(rows, value, k=1)[0], ["2026 Q2"])

    def test_half_hours_and_signals_on_the_underlying(self):
        class Api:
            def stock_bars(self, sym, start, end, timeframe="1Min", feed="iex", adjustment="raw"):
                if start.year != 2026:
                    return []
                up = {"NVDA": 101.0, "TSLA": 100.5, "SPY": 99.4}[sym]       # +1.0%, +0.5%, -0.6% by 10:00
                return [{"t": "2026-11-02T14:30:00Z", "o": 100.0, "h": 102, "l": 99, "c": up, "v": 1},
                        {"t": "2026-11-02T20:00:00Z", "o": up, "h": 103, "l": 99, "c": up * 1.02, "v": 1},
                        {"t": "2026-11-03T14:30:00Z", "o": 100.0, "h": 102, "l": 99, "c": 100.0, "v": 1}]  # no 15:00 bar
        rows = g.underlying(Api(), start=date(2026, 1, 1))
        self.assertEqual([(r["sym"], r["kind"]) for r in rows], [("NVDA", "call"), ("SPY", "put")])
        self.assertAlmostEqual(rows[0]["rest"], 0.02)       # the call wants the stock higher
        self.assertAlmostEqual(rows[1]["rest"], -0.02)      # the put is signed the other way
        self.assertEqual(g.drift(rows), "2 | +0.00% | 50% | 50% | 50%")
        self.assertEqual(g.drift([]), "0 | - | - | - | -")

    def test_gate_table_splits_lit_and_unlit(self):
        state = {"2026-11-02": {"breadth": True}, "2026-11-04": {"breadth": False}}
        rows = [trade("TSLA", "2026-11-02", 2.0), trade("TSLA", "2026-11-04", -1.0)]
        table = g.gate_table(rows, state, lambda t: t["d35"]["exits"]["hold"],
                             gates=[("light", lambda t, s: s["breadth"])])
        self.assertEqual(table[2], "| light | 1 | 100% | 200% | - | 1 | 0% | -100% | - |")


if __name__ == "__main__":
    unittest.main()
