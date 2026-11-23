import unittest

from zoh import news
from zoh.research.slowdrift import WIDE
from zoh.analyst import SYMBOLS


class FakeApi:
    def __init__(self, items):
        self.items, self.asked = items, []

    def _paged(self, url, params, key):
        self.asked.append(params["symbols"].split(","))
        yield [it for it in self.items if set(it["symbols"]) & set(params["symbols"].split(","))]


def item(i, symbols, headline, at="2026-11-23T12:32:00Z"):
    return {"id": i, "symbols": symbols, "headline": headline, "created_at": at}


class RatedOnlyTest(unittest.TestCase):
    def test_the_list_is_the_other_large_caps(self):
        """Every name the rating studies and the sniper cover is read by one of the two pulls."""
        self.assertEqual(set(news.RATED_ONLY) & set(news.WATCH), set())
        self.assertEqual(len(news.RATED_ONLY), len(set(news.RATED_ONLY)))
        self.assertLessEqual(set(WIDE) | set(SYMBOLS), set(news.RATED_ONLY) | set(news.WATCH))

    def test_only_upgrades_and_downgrades_of_those_names_are_kept(self):
        """2026-11-23 07:32: Cantor upgraded TXN and the file did not have it."""
        api = FakeApi([item(1, ["TXN"], "Cantor Fitzgerald Upgrades Texas Instruments to Overweight"),
                       item(2, ["TXN"], "Rothschild & Co Redburn Adjusts Price Target on Texas Instruments"),
                       item(3, ["DELL"], "Dell Technologies Launches New AI Servers"),
                       item(4, ["KO"], "HSBC Downgrades Coca-Cola to Hold", "2026-11-23T11:02:00Z")])
        rows = news.rated_only(api, news.previous_close(news.datetime(2026, 11, 23, 8, tzinfo=news.ET)),
                               news.datetime(2026, 11, 23, 8, tzinfo=news.ET))
        self.assertEqual([(r["symbols"], r["rating"]) for r in rows], [(["TXN"], "upgrade"), (["KO"], "downgrade")])
        self.assertTrue(all(len(chunk) <= 15 for chunk in api.asked))

    def test_merge_keeps_one_copy_newest_first(self):
        a = {"time": "11-23 06:33", "headline": "JPMorgan Maintains Neutral on Tesla", "rating": "rating", "symbols": ["TSLA"]}
        b = {"time": "11-23 07:32", "headline": "Cantor Fitzgerald Upgrades Texas Instruments to Overweight", "rating": "upgrade", "symbols": ["TXN"]}
        self.assertEqual(news.merge([a], [b, dict(a)]), [b, a])
        self.assertIn("| 11-23 07:32 | TXN | upgrade |", news.markdown(news.merge([a], [b]), news.datetime(2026, 11, 20, 16, tzinfo=news.ET),
                                                                  news.datetime(2026, 11, 23, 8, tzinfo=news.ET)))


if __name__ == "__main__":
    unittest.main()
