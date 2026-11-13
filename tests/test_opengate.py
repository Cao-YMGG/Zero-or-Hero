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

    def test_gate_table_splits_lit_and_unlit(self):
        state = {"2026-11-02": {"breadth": True}, "2026-11-04": {"breadth": False}}
        rows = [trade("TSLA", "2026-11-02", 2.0), trade("TSLA", "2026-11-04", -1.0)]
        table = g.gate_table(rows, state, lambda t: t["d35"]["exits"]["hold"],
                             gates=[("light", lambda t, s: s["breadth"])])
        self.assertEqual(table[2], "| light | 1 | 100% | 200% | - | 1 | 0% | -100% | - |")


if __name__ == "__main__":
    unittest.main()
