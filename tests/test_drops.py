import unittest

from zoh.research.drops import aligned, any_hit, returns, runs


class DropsHelpersTest(unittest.TestCase):
    def test_any_hit_looks_only_at_the_sessions_after(self):
        rets = [None, -0.02, 0.0, 0.01, -0.016, 0.0]
        self.assertFalse(any_hit(rets, 1, 2, -0.015))   # the drop on the evening's own day does not count
        self.assertTrue(any_hit(rets, 1, 3, -0.015))    # index 4 is inside a 3-session window
        self.assertIsNone(any_hit(rets, 4, 3, -0.015))  # no full window left

    def test_runs_start_a_new_episode_only_after_a_quiet_spell(self):
        lit = [True, True, False, True] + [False] * 10 + [True]
        self.assertEqual(runs(lit, quiet=10), [0, 14])
        self.assertEqual(runs(lit, quiet=1), [0, 3, 14])

    def test_aligned_carries_the_last_close_and_returns_follow(self):
        days = [1, 2, 3]
        self.assertEqual(aligned([(1, 9.0, 10.0), (3, 10.0, 11.0)], days), [10.0, 10.0, 11.0])
        self.assertEqual(returns([10.0, 10.0, 11.0]), [None, 0.0, 0.10000000000000009])

    def test_lights_on_a_synthetic_chip_slide(self):
        from datetime import date, timedelta
        from zoh.research.drops import SINGLE, lights_at
        from zoh.research.themes import basket
        days = [date(2026, 1, 1) + timedelta(days=i) for i in range(30)]
        flat = [100.0] * 30
        slide = [100.0] * 20 + [100.0 - 2 * k for k in range(1, 11)]   # -20% over the last ten sessions
        members = [{d: (px, px) for d, px in zip(days, slide)} for _ in range(4)]
        spy_bars = [(d, 100.0, 100.0) for d in days]
        got = lights_at(29, days, spy_bars, flat, slide, flat, basket(days, members), members)
        self.assertTrue(got["stretched"])     # SMH 20% off its 20-day high, SPY flat over five sessions
        self.assertTrue(got["breadth"])       # every name below its own 20-day average
        self.assertFalse(got["rates"])        # TLT flat
        self.assertTrue(got["two or more"])
        self.assertEqual(set(SINGLE) - set(got), set())
        still = [{d: (100.0, 100.0) for d in days} for _ in range(4)]
        calm = lights_at(29, days, spy_bars, flat, flat, flat, basket(days, still), still)
        self.assertFalse(any(calm[k] for k in SINGLE))   # nothing lit on a flat tape


if __name__ == "__main__":
    unittest.main()
