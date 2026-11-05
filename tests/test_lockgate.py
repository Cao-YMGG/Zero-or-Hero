import unittest

from zoh.research.lockgate import classify, day_points


def bar(t, o, c):
    return {"t": t, "o": o, "h": max(o, c), "l": min(o, c), "c": c, "v": 1}


class DayPoints(unittest.TestCase):
    def test_open_ten_eleven_and_close_from_half_hour_bars(self):
        # 2026-11-05 is after the DST change: 09:30 ET = 14:30Z. Pre-market bars are ignored.
        bars = [bar("2026-11-05T13:00:00Z", 1, 1), bar("2026-11-05T14:30:00Z", 100.0, 99.0),
                bar("2026-11-05T15:00:00Z", 99.0, 98.5), bar("2026-11-05T15:30:00Z", 98.5, 98.0),
                bar("2026-11-05T20:30:00Z", 97.0, 96.0), bar("2026-11-05T21:00:00Z", 96.0, 95.0)]
        d = day_points(bars)["2026-11-05"]
        self.assertEqual((d["open"], d["p10"], d["p11"], d["close"]), (100.0, 99.0, 98.0, 96.0))

    def test_summer_time_and_days_without_an_open_bar_are_dropped(self):
        bars = [bar("2026-07-06T13:30:00Z", 50.0, 51.0), bar("2026-07-06T19:30:00Z", 51.0, 52.0),
                bar("2026-07-07T19:30:00Z", 52.0, 53.0)]
        pts = day_points(bars)
        self.assertEqual(list(pts), ["2026-07-06"])
        self.assertEqual((pts["2026-07-06"]["p10"], pts["2026-07-06"]["close"]), (51.0, 52.0))


class Classify(unittest.TestCase):
    def test_classes_follow_the_registered_gate(self):
        base = {"spy10": -0.012, "vix10": 0.08, "breadth": 10, "n_mega": 10}
        self.assertEqual(classify(base), "lock")
        self.assertEqual(classify({**base, "breadth": 6}), "vix_only")
        self.assertEqual(classify({**base, "vix10": 0.01}), "breadth_only")
        self.assertEqual(classify({**base, "vix10": -0.02, "breadth": 5}), "below_open")
        self.assertEqual(classify({**base, "spy10": 0.0005}), "above_open")
        self.assertEqual(classify({**base, "spy10": -0.0005}), "above_open")  # inside the 0.1% band


if __name__ == "__main__":
    unittest.main()
