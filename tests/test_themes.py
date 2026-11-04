import unittest
from datetime import date, timedelta

from zoh.research.themes import basket, classify, episodes, flags, state_of


def days_from(d0, n):
    return [d0 + timedelta(days=i) for i in range(n)]


class Basket(unittest.TestCase):
    def test_equal_weight_basket_chains_member_returns(self):
        days = days_from(date(2026, 1, 1), 3)
        a = {days[0]: (100, 100), days[1]: (105, 110), days[2]: (110, 110)}
        b = {days[0]: (100, 100), days[1]: (95, 90), days[2]: (90, 90)}
        idx = basket(days, [a, b])
        # day 2: opens +5%/-5% -> 100, closes +10%/-10% -> 100
        self.assertAlmostEqual(idx[1][1], 100.0)
        self.assertAlmostEqual(idx[1][2], 100.0)
        # a member missing on a day is left out, the other carries the basket
        c = {days[0]: (100, 100), days[1]: (100, 100)}
        idx2 = basket(days, [a, c])
        self.assertAlmostEqual(idx2[2][2], idx2[1][2] * 1.0)  # day 3 only a trades, flat


class Flags(unittest.TestCase):
    def test_turning_flags_fire_when_the_theme_falls_and_spy_holds(self):
        days = days_from(date(2026, 1, 1), 40)
        spy = [(d, 100.0, 100.0) for d in days]
        lead = {d: (100.0, 100.0) for d in days}          # two leaders flat
        peri = {d: (100.0, 100.0 if i < 30 else 100.0 - 2 * (i - 29)) for i, d in enumerate(days)}  # -20% over 10 days
        members = [dict(lead), dict(lead), dict(peri), dict(peri), dict(peri)]
        theme = basket(days, members)
        turn, heat = flags(theme, spy, members, days, len(days) - 1)
        self.assertTrue(all(turn.values()), turn)
        self.assertFalse(any(heat.values()), heat)
        self.assertEqual(state_of(turn, heat), "turning")

    def test_heating_flags_fire_when_the_theme_leads_broadly(self):
        days = days_from(date(2026, 1, 1), 40)
        spy = [(d, 100.0, 100.0) for d in days]
        up = {d: (100.0 + i, 100.0 + i) for i, d in enumerate(days)}
        members = [dict(up) for _ in range(5)]
        theme = basket(days, members)
        turn, heat = flags(theme, spy, members, days, len(days) - 1)
        self.assertEqual(state_of(turn, heat), "heating")
        self.assertTrue(heat["AT_HIGH"] and heat["RATIO_HIGH"] and heat["BREADTH_UP"] and heat["REL_STRONG"])


class Episodes(unittest.TestCase):
    def test_episodes_need_ten_quiet_sessions_between_them(self):
        states = ["neutral"] * 12 + ["turning"] * 3 + ["neutral"] * 4 + ["turning"] + ["neutral"] * 12 + ["turning"]
        self.assertEqual(episodes(states), [12, 32])

    def test_classify_continued_vs_recovered(self):
        d = date(2026, 1, 1)
        falls = [(d, 100, 100)] + [(d + timedelta(days=k), 100 - k, 100 - k) for k in range(1, 10)]
        self.assertEqual(classify(falls, 0, 110.0), "continued")   # 95 reached on day 5
        rises = [(d, 100, 100)] + [(d + timedelta(days=k), 100 + k, 100 + k) for k in range(1, 12)]
        self.assertEqual(classify(rises, 0, 110.0), "recovered")   # 110 reached on day 10
        flat = [(d + timedelta(days=k), 100, 100) for k in range(25)]
        self.assertEqual(classify(flat, 0, 110.0), "neither")


if __name__ == "__main__":
    unittest.main()
