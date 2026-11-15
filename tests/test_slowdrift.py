import unittest
from datetime import date

from zoh.research import slowdrift as s


class SlowDrift(unittest.TestCase):
    def test_fridays_put_the_one_nearest_three_weeks_first(self):
        got = s.fridays(date(2026, 11, 11))                      # a Wednesday
        self.assertEqual(got[0], date(2026, 12, 4))              # 23 days out
        self.assertTrue(all(d.weekday() == 4 and 12 <= (d - date(2026, 11, 11)).days <= 40 for d in got))
        self.assertEqual(len(got), 4)

    def test_strikes_step_with_the_price(self):
        self.assertIn(34.5, s.strikes(35.0))
        self.assertNotIn(349.5, s.strikes(350.0))
        self.assertIn(350.0, s.strikes(350.0))
        self.assertTrue(min(s.strikes(350.0)) >= 350 * 0.85 - 10 and max(s.strikes(350.0)) <= 350 * 1.15)

    def test_pick_and_values(self):
        self.assertEqual(s.pick({340: 0.71, 350: 0.52, 360: 0.33}, 0.45), 350)
        self.assertEqual(s.pick({340: -0.71, 350: -0.52}, 0.60), 350)        # puts carry negative deltas
        self.assertIsNone(s.pick({}, 0.45))
        day = date(2026, 11, 18)
        self.assertEqual(s.value_at({day: 7.2}, day, 356.0, 350, "call"), (7.2, True))
        self.assertEqual(s.value_at({}, day, 356.0, 350, "call"), (6.0, False))   # no trade: intrinsic, a floor
        self.assertEqual(s.value_at(None, day, 356.0, 350, "put"), (0.0, False))

    def test_returns_with_costs(self):
        self.assertAlmostEqual(s.legs_return(5.0, 7.0, 0.05), 7.0 * 0.95 / (5.0 * 1.05) - 1)
        self.assertIsNone(s.legs_return(0.0, 7.0, 0.05))
        debit = 6.0 * 1.05 - 2.0 * 0.95
        self.assertAlmostEqual(s.vertical_return(6.0, 2.0, 9.0, 3.5, 0.05), (9.0 * 0.95 - 3.5 * 1.05) / debit - 1)
        self.assertIsNone(s.vertical_return(0.4, 0.4, 2.0, 1.0, 0.05))       # no debit to speak of

    def test_table_cells_from_rows(self):
        def row(day, kind, px, out5, traded=True):
            leg = {"strike": 350, "delta": 0.45, "px": px, "out": {"5": [out5, traded]}}
            return {"day": day, "kind": kind, "early": {}, "late": {"d0.45": leg, "d0.60": dict(leg, strike=340), "d0.30": dict(leg, strike=360, px=px / 2, out={"5": [out5 / 2, True]})}}
        rows = [row("2025-03-03", "call", 5.0, 7.0), row("2026-09-01", "call", 4.0, 2.0, traded=False), row("2026-09-02", "put", 3.0, 6.0)]
        xs, floor = s.returns(rows, "late", "d0.45", 5, 0.05)
        self.assertEqual((len(xs), floor), (2, 1))
        self.assertAlmostEqual(xs[0], 7.0 * 0.95 / (5.0 * 1.05) - 1)
        self.assertEqual(len(s.returns(rows, "late", "d0.45", 5, 0.05, since="2026-08-13")[0]), 1)
        self.assertEqual(len(s.returns(rows, "late", "d0.45", 5, 0.05, kind="put")[0]), 1)
        self.assertEqual(s.returns(rows, "early", "d0.45", 5, 0.05), ([], 0))           # no early entry recorded
        self.assertEqual(len(s.returns(rows, "late", None, 5, 0.05, vertical=True)[0]), 2)
        self.assertEqual(s.cell([0.5, -0.25, -0.25]), "3 | 33% | +0% / -25% / -25%")


if __name__ == "__main__":
    unittest.main()
