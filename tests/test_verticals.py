import unittest
from datetime import date, timedelta

from zoh.research.verticals import expiry_near, legs, run, third_friday


class Expiry(unittest.TestCase):
    def test_third_friday_and_the_expiry_nearest_sixty_days(self):
        self.assertEqual(third_friday(2026, 11), date(2026, 11, 20))
        self.assertEqual(third_friday(2026, 12), date(2026, 12, 18))
        # from 2026-11-04: Dec 18 is 44 days (too near), Jan 15 is 72 days -> January
        self.assertEqual(expiry_near(date(2026, 11, 4)), date(2027, 1, 15))
        # from 2026-10-20: Dec 18 is 59 days -> December
        self.assertEqual(expiry_near(date(2026, 10, 20)), date(2026, 12, 18))


class Legs(unittest.TestCase):
    def test_long_at_the_money_short_near_quarter_delta(self):
        strikes = [195, 200, 205, 210, 215, 220, 225, 230, 240]
        # sigma 0.40, T 0.17y: 0.67 * 0.40 * sqrt(0.17) = 11% above 204 -> 226 -> nearest listed 225
        self.assertEqual(legs(204.0, 0.40, 0.17, strikes), (205, 225))
        # low vol: 0.67 * 0.15 * sqrt(0.17) = 4% -> 212 -> 210
        self.assertEqual(legs(204.0, 0.15, 0.17, strikes), (205, 210))
        self.assertIsNone(legs(250.0, 0.4, 0.17, strikes))


class Run(unittest.TestCase):
    def setUp(self):
        self.d0 = date(2026, 1, 5)
        self.days = [self.d0 + timedelta(days=k) for k in range(40)]

    def test_target_exit_at_half_the_maximum_profit(self):
        long = {d: 5.0 + 0.5 * k for k, d in enumerate(self.days)}    # rises 0.5 a day
        short = {d: 2.0 + 0.1 * k for k, d in enumerate(self.days)}
        r = run(long, short, 10.0, self.d0, self.d0 + timedelta(days=60))
        # debit 5*1.05 - 2*0.95 = 3.35 (34% of width); target = 3.35 + 0.5 * 6.65 = 6.675;
        # value day k = 2.65 + 0.37k >= 6.675 from k = 11
        self.assertEqual(r["reason"], "target")
        self.assertEqual(r["exit"], (self.d0 + timedelta(days=11)).isoformat())
        self.assertGreater(r["ret"], 0.9)

    def test_spreads_priced_above_sixty_percent_of_width_are_skipped(self):
        long = {d: 7.0 for d in self.days}
        short = {d: 0.5 for d in self.days}
        self.assertIsNone(run(long, short, 10.0, self.d0, self.d0 + timedelta(days=60)))

    def test_time_stop_after_thirty_sessions(self):
        long = {d: 5.0 for d in self.days}
        short = {d: 2.0 for d in self.days}
        r = run(long, short, 10.0, self.d0, self.d0 + timedelta(days=90))
        self.assertEqual(r["reason"], "time")
        self.assertEqual(r["held"], 30)
        self.assertLess(r["ret"], 0)  # flat market: the spread pays the 5% brackets twice


if __name__ == "__main__":
    unittest.main()
