import unittest
from datetime import date

from zoh.research.hero import expiry_of, legs_from_study, simulate


def leg(day, entry, mult):
    return {"day": day, "sym": "X", "entry": entry, "m": mult}


class Rounds(unittest.TestCase):
    def test_hero_and_zero_rounds_restart_at_500(self):
        legs = [leg("d1", 1.0, 12.0), leg("d2", 1.0, 0.0), leg("d3", 2.0, 1.5)]
        s = simulate(legs, 1.0, "m")
        # d1: 5 contracts, $500 -> $6,000 (hero, round closed); d2: 5 contracts -> $0 (zero);
        # d3: 2 contracts of $200 -> $400 -> ledger $700, round still open.
        self.assertEqual((s["heroes"], s["zeros"], s["rounds_closed"]), (1, 1, 2))
        self.assertEqual(s["open_ledger"], 700.0)
        self.assertEqual(s["net"], 5500 - 500 + 200)
        self.assertEqual([t["qty"] for t in s["trail"]], [5, 5, 2])

    def test_twenty_percent_sizing_skips_when_no_whole_contract_fits(self):
        s = simulate([leg("d1", 1.5, 3.0), leg("d2", 0.5, 2.0)], 0.2, "m")
        # 20% of $500 is $100: no $150 contract fits; then 2 x $50 -> $100 profit.
        self.assertEqual((s["taken"], s["skipped"]), (1, 1))
        self.assertEqual(s["open_ledger"], 600.0)
        self.assertEqual(s["rounds_closed"], 0)

    def test_expiry_from_the_contract_symbol(self):
        self.assertEqual(expiry_of("ORCL261106C00134000"), date(2026, 11, 6))
        self.assertEqual(expiry_of("MU261023C00910000"), date(2026, 10, 23))

    def test_legs_take_the_hero_delta_per_source(self):
        pick = {"contract": "AMD261006C00500000", "strike": 500, "delta": 0.1, "px": 1.0, "peak": 2.5,
                "day1": {"half3_arm1.5": 0.5, "hold": 1.0}, "carry": None}
        rows = [{"day": "2026-10-06", "sym": "AMD", "kind": "call", "source": "sniper", "open": 100, "close": 102,
                 "entries": {"live": {"t": "09:33", "spot": 100, "picks": {"d0.10": pick, "d0.20": dict(pick, px=2.0)}}}},
                {"day": "2026-10-06", "sym": "AVGO", "kind": "call", "source": "intraday", "open": 100, "close": 99,
                 "entries": {}}]
        legs = legs_from_study(rows)
        self.assertEqual(len(legs), 1)
        self.assertEqual(legs[0]["entry"], 1.1)  # 10% slippage on the 0.10-delta bar close
        self.assertEqual((legs[0]["live"], legs[0]["hold"], legs[0]["hold_carry"]), (1.5, 2.0, 2.0))


if __name__ == "__main__":
    unittest.main()
