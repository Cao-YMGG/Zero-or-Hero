import unittest

from zoh.research.surges import classify, find_surges, is_fund


class ClassifyTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(classify(["Acme to be acquired by Globex for $40 per share in cash"]),
                         "M&A")
        self.assertEqual(classify(["BioCo says FDA grants approval for lead drug"]),
                         "FDA / clinical")
        self.assertEqual(classify(["Acme Q3 earnings beat, raises guidance"]), "earnings")
        self.assertEqual(classify(["Pentagon awards Acme drone contract"]), "government / policy")
        self.assertEqual(classify(["Acme signs partnership with Nvidia"]),
                         "contract / partnership")
        self.assertEqual(classify(["Analyst upgrades Acme, raises price target"]), "analyst")
        self.assertEqual(classify(["Acme shares are trading higher"]), "other news")
        self.assertEqual(classify(["Sandisk wins customer approval for new SSD line"]),
                         "other news")  # generic "approval" is not FDA
        self.assertEqual(classify([]), "no news found")

    def test_fund_filter(self):
        self.assertTrue(is_fund({"name": "ProShares UltraPro QQQ"}))
        self.assertFalse(is_fund({"name": "Palantir Technologies Inc. Class A Common Stock"}))


class SurgeTests(unittest.TestCase):
    def test_find_surges_with_forward_returns(self):
        closes = [10.0] * 60 + [12.0] + [13.0] * 25
        bars = [{"t": f"2025-01-{1 + i % 28:02d}T05:00:00Z", "o": c, "c": c, "v": 2_000_000}
                for i, c in enumerate(closes)]
        events = find_surges({"ACME": bars})
        self.assertEqual(len(events), 1)
        ev = events[0]
        self.assertAlmostEqual(ev["gain"], 0.2)
        self.assertAlmostEqual(ev["fwd20"], 13 / 12 - 1)


if __name__ == "__main__":
    unittest.main()
