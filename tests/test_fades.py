import unittest
from datetime import date, datetime

from zoh.research.fades import classify, schedule
from zoh.strategy import ET


class Classifier(unittest.TestCase):
    def test_the_company_must_be_the_subject(self):
        h = "Marvell to Buy Lumentum in $115 Billion All-Stock Deal"
        self.assertEqual(classify("MRVL", h), "acquirer")
        self.assertIsNone(classify("LITE", h))  # the target is not an acquirer

    def test_offerings(self):
        self.assertEqual(classify("ORCL", "Oracle Announces Proposed Offering of $10 Billion of Common Stock"), "equity")
        self.assertEqual(classify("ORCL", "Oracle Prices $18 Billion Senior Notes Offering"), "debt")
        self.assertEqual(classify("META", "'Meta Readies Cross-Border Investment Bond Offering' - Bloomberg"), "debt")
        self.assertEqual(classify("HOOD", "Robinhood Announces Proposed Private Offering of $1 Billion Convertible Senior Notes"), "equity")

    def test_noise_is_not_an_event(self):
        self.assertIsNone(classify("ORCL", "Stephens & Co. Upgrades Oracle to Overweight, Raises Price Target to $213"))
        self.assertIsNone(classify("ORCL", "Oracle Shares Dip Monday: What's Happening?"))
        self.assertIsNone(classify("AAPL", "Apple Announces $110 Billion Buyback, Raises Dividend"))
        self.assertIsNone(classify("AMZN", "Amazon to Buy 500 Rivian Vans"))  # no size, no stock

    def test_schedule_rolls_late_headlines_to_the_next_day(self):
        days = {date(2026, 10, 30), date(2026, 11, 2), date(2026, 11, 3)}
        self.assertEqual(schedule(datetime(2026, 10, 30, 17, 5, tzinfo=ET), days), (date(2026, 11, 2), "pre"))
        self.assertEqual(schedule(datetime(2026, 11, 2, 8, 20, tzinfo=ET), days), (date(2026, 11, 2), "pre"))
        day, t = schedule(datetime(2026, 11, 2, 12, 39, tzinfo=ET), days)
        self.assertEqual((day, t.strftime("%H:%M")), (date(2026, 11, 2), "12:41"))
        self.assertEqual(schedule(datetime(2026, 11, 2, 15, 10, tzinfo=ET), days), (date(2026, 11, 3), "pre"))


if __name__ == "__main__":
    unittest.main()


class Subject(unittest.TestCase):
    def test_a_buyer_named_after_the_verb_is_not_the_issuer(self):
        h = "UPDATE: Meta Announces That Nvidia, Advanced Micro Devices And Broadcom Have Each Indicated An Interest In Purchasing Depositary Shares"
        self.assertEqual(classify("META", h), "equity")
        self.assertIsNone(classify("NVDA", h))
        self.assertIsNone(classify("AMD", h))
