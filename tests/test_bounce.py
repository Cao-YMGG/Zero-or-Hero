import unittest
from datetime import date, datetime, timedelta

from zoh.research.bounce import events, in_report_window, stop_run
from zoh.strategy import ET


class Events(unittest.TestCase):
    def test_cooling_theme_gap_up_days(self):
        # 22 flat sessions at 100, then a -12% month: the gap-up day qualifies, the flat day does not.
        d0 = date(2026, 1, 1)
        rows = [(d0 + timedelta(days=i), 100.0, 100.0) for i in range(22)]
        rows += [(d0 + timedelta(days=22), 88.0, 88.0)]          # prior close 88 = -12% vs 100
        rows += [(d0 + timedelta(days=23), 89.5, 90.0)]          # gap +1.7%: event
        rows += [(d0 + timedelta(days=24), 90.2, 91.0)]          # gap +0.2%: no event (close 90 vs 100 = -10%)
        ev = events(rows)
        self.assertEqual([e[0] for e in ev], [d0 + timedelta(days=23)])
        self.assertAlmostEqual(ev[0][2], 89.5 / 88.0 - 1, places=6)

    def test_stock_stop_sells_when_the_stock_reclaims_its_open(self):
        day = date(2026, 11, 3)
        t = lambda hm: datetime.combine(day, datetime.strptime(hm, "%H:%M").time(), ET)
        stock = [{"t": t("11:04"), "c": 99.0}, {"t": t("11:05"), "c": 100.2}, {"t": t("11:06"), "c": 98.0}]
        path = [(t("11:04"), 1.20), (t("11:05"), 1.00), (t("11:06"), 2.00)]
        # open 100: the stock reclaims it at 11:05, so the put is sold at the 11:05 bid (1.00 less 10%)
        self.assertAlmostEqual(stop_run(path, stock, 100.0, 1.0, 0.10), 0.90, places=6)
        # a stock that never reclaims its open rides to the last bar
        self.assertAlmostEqual(stop_run(path, stock, 101.0, 1.0, 0.10), 1.80, places=6)

    def test_report_window_covers_the_reaction_day_and_the_days_before_it(self):
        reports = {date(2026, 11, 4)}  # AMD reports after the close on 11-03, reacts 11-04
        self.assertTrue(in_report_window(date(2026, 11, 3), reports))
        self.assertTrue(in_report_window(date(2026, 11, 4), reports))
        self.assertFalse(in_report_window(date(2026, 11, 5), reports))
        self.assertFalse(in_report_window(date(2026, 10, 30), reports))


if __name__ == "__main__":
    unittest.main()
