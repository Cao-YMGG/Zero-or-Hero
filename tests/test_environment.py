import math
import unittest

from zoh.research import environment as env


def wave(n, start=100.0, drift=0.001, amp=0.01):
    """A deterministic price path: steady drift with an alternating wiggle."""
    out = [start]
    for i in range(n - 1):
        out.append(out[-1] * (1 + drift + (amp if i % 2 else -amp)))
    return out


class Readings(unittest.TestCase):
    def test_trend_numbers_follow_their_definitions(self):
        closes = [100.0] * 260 + [90.0]
        t = env.trend(closes)
        self.assertAlmostEqual(t["vs_200d"], 90.0 / ((100 * 199 + 90) / 200) - 1, places=4)
        self.assertAlmostEqual(t["ret_1m"], -0.1, places=4)
        self.assertAlmostEqual(t["from_1y_high"], -0.1, places=4)

    def test_volatility_counts_big_days_and_annualizes(self):
        closes = wave(300, amp=0.02, drift=0.0)
        v = env.volatility(closes)
        self.assertEqual(v["big_days_20"], 20)                 # every day moves 2%
        self.assertAlmostEqual(v["vol_20d"], 0.02 * math.sqrt(252), places=2)

    def test_breadth_shares(self):
        up = [100.0 + i for i in range(250)]
        down = [350.0 - i for i in range(250)]
        b = env.breadth({"A": up, "B": down, "C": up})
        self.assertEqual((b["above_20d"], b["above_200d"], b["names"]), (round(2 / 3, 3), round(2 / 3, 3), 3))

    def test_average_correlation(self):
        a = [0.01 if i % 2 else -0.01 for i in range(100)]
        b = [x * 2 for x in a]
        c = [-x for x in a]
        self.assertAlmostEqual(env.avg_corr([a, b], 20), 1.0, places=6)
        self.assertAlmostEqual(env.avg_corr([a, c], 20), -1.0, places=6)
        self.assertAlmostEqual(env.avg_corr([a, b, c], 20), (1 - 1 - 1) / 3, places=3)   # rounded to 3 places

    def test_gaps_closed_against(self):
        closes = [100.0] * 5 + [101.0, 102.0, 100.0]
        opens = [100.0] * 5 + [99.0, 102.5, 101.0]   # gap -1% closed up, gap +1.5% closed down, gap -2% closed down
        g = env.gaps(opens, closes, n=3)
        self.assertEqual((g["gaps"], g["closed_against"]), (3, 2))

    def test_base_rates_use_the_condition_and_count_episodes(self):
        closes = wave(400)
        dates = [f"d{i:04d}" for i in range(400)]
        always = env.base_rates(dates, closes, lambda s: True)
        self.assertEqual(always["days"], 400 - 260)
        self.assertEqual(always["episodes"], 1)
        self.assertEqual(always["h6"]["n"], 400 - 260 - 6)
        self.assertEqual(always["h6"]["up"], 1.0)                # the drift wins over six sessions
        never = env.base_rates(dates, closes, lambda s: False)
        self.assertEqual((never["days"], never["h6"]), (0, None))

    def test_near_is_a_neighbourhood_of_today(self):
        now = {"vs_200d": -0.02, "ret_1m": -0.07, "vol_20d": 0.30, "from_1y_high": -0.08}
        test = env.near(now)
        self.assertTrue(test(now))
        self.assertTrue(test({"vs_200d": 0.0, "ret_1m": -0.05, "vol_20d": 0.38, "from_1y_high": -0.05}))
        self.assertFalse(test({"vs_200d": 0.02, "ret_1m": -0.07, "vol_20d": 0.30, "from_1y_high": -0.08}))
        self.assertFalse(test({"vs_200d": -0.02, "ret_1m": -0.07, "vol_20d": 0.45, "from_1y_high": -0.08}))


class Words(unittest.TestCase):
    def reading(self, **over):
        r = {"trend": {"vs_200d": -0.02, "ret_1m": -0.07},
             "volatility": {"vol_20d": 0.31, "vol_1y": 0.15},
             "breadth": {"above_50d": 0.37},
             "correlation": {"ai_20d": 0.85},
             "leadership": {"defensive_1m": 0.03, "tech_1m": -0.19, "defensive_1w": 0.01, "tech_1w": -0.05},
             "cross_asset": {"spy_tlt_20d": -0.13},
             "gaps": {"gaps": 6, "closed_against": 5}}
        for k, v in over.items():
            r[k] = {**r[k], **v}
        return r

    def test_label_names_each_state(self):
        words = env.label_zh(self.reading())
        for part in ("回调中", "颠簸很大", "AI 股一起涨一起跌", "钱躲进防守股", "股债反着走", "开盘方向常被盘中反过来"):
            self.assertIn(part, words)
        calm = env.label_zh(self.reading(trend={"vs_200d": 0.05, "ret_1m": 0.03},
                                         volatility={"vol_20d": 0.10, "vol_1y": 0.15},
                                         correlation={"ai_20d": 0.4}, cross_asset={"spy_tlt_20d": 0.2},
                                         gaps={"gaps": 1, "closed_against": 1}))
        self.assertIn("上升中", calm)
        self.assertIn("很平静", calm)
        self.assertNotIn("AI 股", calm)

    def test_changes_report_only_lines_crossed(self):
        prev = self.reading()
        same = env.changes(prev, self.reading())
        self.assertEqual(same, [])
        cur = self.reading(trend={"vs_200d": 0.01}, correlation={"ai_20d": 0.6},
                           leadership={"defensive_1w": -0.02, "tech_1w": 0.03})
        got = env.changes(prev, cur)
        self.assertIn("变成：标普在 200 日均线上方", got)
        self.assertIn("不再：AI 股一起涨一起跌（同步程度 0.7 以上）", got)
        self.assertIn("不再：这一周防守股跑赢科技股", got)
        self.assertEqual(env.changes(None, cur), [])


if __name__ == "__main__":
    unittest.main()
