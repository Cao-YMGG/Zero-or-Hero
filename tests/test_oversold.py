import unittest

from zoh.research import oversold as ov


def series(closes, start=1):
    return [(f"d{start + i:04d}", c) for i, c in enumerate(closes)]


class OversoldRule(unittest.TestCase):
    def rising_then(self, tail):
        return [100 + 0.1 * i for i in range(260)] + tail

    def test_rsi2_is_low_after_falls_and_high_after_rises(self):
        self.assertLess(ov.rsi2(self.rising_then([125.0, 123.0, 121.0])), 10)
        self.assertGreater(ov.rsi2([100 + i for i in range(40)]), 90)

    def test_a_signal_needs_the_close_above_its_200_day_average(self):
        up = self.rising_then([125.0, 123.5, 122.0])            # two falls, still above the long average
        self.assertTrue(ov.is_signal(up))
        down = [200 - 0.2 * i for i in range(260)] + [147.0, 146.0]
        self.assertLess(ov.rsi2(down), 10)
        self.assertFalse(ov.is_signal(down))

    def test_step_opens_on_a_signal_and_closes_above_the_five_day_average(self):
        closes = self.rising_then([125.0, 123.5, 122.0])
        bars = {"SPY": series(closes)}
        today = bars["SPY"][-1][0]
        rows = ov.step([], bars, today)
        self.assertEqual([(r["symbol"], r["entry_date"], r["exit_date"]) for r in rows], [("SPY", today, "")])
        self.assertEqual(ov.step(rows, bars, today), rows)       # a second run the same day changes nothing
        bars = {"SPY": series(closes + [121.5])}                 # lower again: under the 5-day average, hold
        rows = ov.step(rows, bars, bars["SPY"][-1][0])
        self.assertEqual(rows[0]["exit_date"], "")
        bars = {"SPY": series(closes + [121.5, 126.0])}          # a close above the 5-day average: out
        day = bars["SPY"][-1][0]
        rows = ov.step(rows, bars, day)
        self.assertEqual((rows[0]["exit_date"], rows[0]["days"]), (day, "2"))
        self.assertAlmostEqual(float(rows[0]["pct"]), (126.0 / 122.0 - 1) * 100 - ov.COST_PCT, places=2)
        self.assertEqual(ov.step(rows, bars, day), rows)

    def test_step_gives_up_after_ten_closes(self):
        closes = self.rising_then([125.0, 123.5, 122.0])
        rows = ov.step([], {"SPY": series(closes)}, series(closes)[-1][0])
        falling = closes + [122.0 - 0.5 * k for k in range(1, 11)]
        for n in range(len(closes) + 1, len(falling) + 1):
            bars = {"SPY": series(falling[:n])}
            rows = ov.step(rows, bars, bars["SPY"][-1][0])
        self.assertEqual(rows[0]["days"], "10")
        self.assertLess(float(rows[0]["pct"]), 0)


if __name__ == "__main__":
    unittest.main()
