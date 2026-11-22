import unittest

from zoh.research import sellside
from zoh.strategy import bs_price

CENT = sellside.COSTS["a cent a leg"]
NONE = sellside.COSTS["none"]


class SpreadResult(unittest.TestCase):
    def test_a_spread_that_dies_keeps_the_credit_less_the_costs(self):
        short = {m: 0.05 for m in range(601, 946)}
        long_ = {m: 0.01 for m in range(601, 946)}
        r = sellside.spread_result(short, long_, 0.80, 0.10, 600, CENT)
        self.assertAlmostEqual(r["credit"], 0.79 - 0.11)
        self.assertEqual(r["why"], "time")
        self.assertAlmostEqual(r["back"], 0.06 - 0.0)      # buy the short a cent up, the long sells for nothing
        self.assertAlmostEqual(r["pnl"], (0.68 - 0.06) * 100, places=1)

    def test_it_is_bought_back_when_that_costs_twice_the_credit(self):
        short = {601: 0.90, 602: 1.60, 603: 0.20}
        long_ = {601: 0.10, 602: 0.12, 603: 0.05}
        r = sellside.spread_result(short, long_, 0.80, 0.10, 600, NONE)
        self.assertEqual((r["why"], r["minute"]), ("stop", 602))
        self.assertAlmostEqual(r["pnl"], (0.70 - 1.48) * 100, places=1)

    def test_without_a_stop_the_loss_ends_at_the_width(self):
        short = {m: 9.0 for m in range(601, 946)}
        long_ = {m: 3.0 for m in range(601, 946)}
        r = sellside.spread_result(short, long_, 0.80, 0.10, 600, NONE, stop=None)
        self.assertEqual(r["back"], sellside.WIDTH)
        self.assertAlmostEqual(r["pnl"], (0.70 - 5) * 100, places=1)
        self.assertAlmostEqual(r["risk"], 430.0)

    def test_no_trade_when_the_costs_eat_the_credit(self):
        self.assertIsNone(sellside.spread_result({}, {}, 0.10, 0.08, 600, sellside.COSTS["10%"]))


class NearestDelta(unittest.TestCase):
    def test_picks_the_strike_whose_own_price_says_030_delta(self):
        spot, years, iv = 700.0, 360 / sellside.Y, 0.16
        quotes = [(k, bs_price(spot, k, years, iv, "call"), spot, 600) for k in range(701, 711)]
        strike, delta = sellside.nearest_delta(quotes, "call")
        self.assertLess(abs(delta - 0.30), 0.06)
        others = [sellside.nearest_delta([q], "call")[1] for q in quotes]
        self.assertEqual(min(others, key=lambda d: abs(d - 0.30)), delta)


class Summary(unittest.TestCase):
    def test_versions_split_by_the_ten_oclock_move(self):
        rows = [{"kind": "call", "move10": 0.002, "pnl": 1}, {"kind": "put", "move10": 0.002, "pnl": 2},
                {"kind": "call", "move10": -0.008, "pnl": 3}]
        v = sellside.versions(rows)
        self.assertEqual([r["pnl"] for r in v["(b) only the side against the 10:00 move"]], [1])
        self.assertEqual([r["pnl"] for r in v["the side with the 10:00 move"]], [2, 3])
        self.assertEqual(len(v["(c) days within 0.5% of the open at 10:00"]), 2)


if __name__ == "__main__":
    unittest.main()
