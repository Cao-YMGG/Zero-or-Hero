import unittest
from datetime import datetime

from zoh.research.gapdown import BUDGET, MIN_DELTA, pick_contracts, pnl, take
from zoh.research.strikebudget import choose
from zoh.strategy import ET


def path(*closes):
    """[(t, close)] one minute apart from 10:01, the last bar at 15:45."""
    out = []
    for i, c in enumerate(closes[:-1]):
        out.append((datetime(2026, 11, 4, 10, 1 + i, tzinfo=ET), c))
    out.append((datetime(2026, 11, 4, 15, 45, tzinfo=ET), closes[-1]))
    return out


class TakeTests(unittest.TestCase):
    def test_take3_sells_at_the_first_bid_over_three_times(self):
        entry = 1.10  # bought at 1.00 plus 10%
        p = path(1.5, 2.0, 3.8, 5.0, 0.2)
        # 3.8 * 0.9 = 3.42 >= 3.3: sold there, not at the 5.0 peak and not at the 0.2 close
        self.assertAlmostEqual(take(p, entry, 0.10, 3.0), 3.42 / 1.10)
        self.assertAlmostEqual(pnl(p, entry, "take3"), 3.42 / 1.10 - 1)

    def test_take3_falls_back_to_the_close(self):
        entry = 1.10
        p = path(1.5, 2.0, 2.5, 0.2)
        self.assertAlmostEqual(take(p, entry, 0.10, 3.0), 0.18 / 1.10)
        self.assertAlmostEqual(pnl(p, entry, "hold"), 0.18 / 1.10 - 1)


class PickTests(unittest.TestCase):
    def setUp(self):
        # (contract, strike, delta, bar): a $500 ledger can spend $150 on one contract
        self.cands = [("NVDA_P190", 190.0, 0.42, {"c": 2.80}), ("NVDA_P185", 185.0, 0.24, {"c": 1.20}),
                      ("NVDA_P180", 180.0, 0.11, {"c": 0.45}), ("NVDA_P170", 170.0, 0.04, {"c": 0.08})]

    def test_ledger_pick_is_the_affordable_contract_nearest_0_40(self):
        picks = pick_contracts(self.cands)
        self.assertEqual(picks["ledger"][0], "NVDA_P185")  # 2.80 * 1.1 * 100 = $308 is over the budget
        self.assertEqual(picks["d0.40"][0], "NVDA_P190")
        self.assertEqual(picks["d0.25"][0], "NVDA_P185")

    def test_ledger_pick_respects_the_delta_floor(self):
        cheap_only = [c for c in self.cands if c[3]["c"] * 110 <= BUDGET and c[2] < MIN_DELTA]
        self.assertNotIn("ledger", pick_contracts(cheap_only))


class ChooseTests(unittest.TestCase):
    def test_floor_skips_what_the_old_rule_bought(self):
        # the 2026-11-06 LLY case: the stake only buys a 0.03-delta call (costs include the 10% slip)
        cands = [("LLY_C1430", 1430.0, 0.03, {"c": 0.91}), ("LLY_C1390", 1390.0, 0.10, {"c": 2.36})]
        out = choose(cands, 0.10, 1350.0, "call", 110.0)
        self.assertEqual(out["old"][0], "LLY_C1430")
        self.assertIsNone(out["floor"])
        self.assertIsNone(out["pct"])  # 1430 is 5.9% out of the money, 1390 is unaffordable
        self.assertEqual(out["nobudget"][0], "LLY_C1390")


if __name__ == "__main__":
    unittest.main()
