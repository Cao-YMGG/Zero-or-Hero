import unittest

from zoh.research import forecasts as fc


def doc(*claims):
    return {"claims": list(claims)}


DAY = {"id": "oc_up", "horizon": "day", "p": 0.45, "kind": "close_above_open", "date": "2026-11-27"}
ABOVE = {"id": "above", "horizon": "day", "p": 0.65, "kind": "close_above", "date": "2026-11-27", "level": 716.70}
QUIET = {"id": "quiet", "horizon": "day", "p": 0.65, "kind": "abs_open_close_under", "date": "2026-11-27", "pct": 0.8}
RANGE = {"id": "range80", "horizon": "week", "p": 0.8, "kind": "close_between", "date": "2026-12-04",
         "low": 688.0, "high": 752.0}
BELOW = {"id": "below", "horizon": "week", "p": 0.33, "kind": "any_close_below", "start": "2026-11-27",
         "end": "2026-12-04", "level": 695.45}


class Validation(unittest.TestCase):
    def test_a_good_file_has_no_problems(self):
        self.assertEqual(fc.validate(doc(DAY, ABOVE, QUIET, RANGE, BELOW)), [])

    def test_problems_are_named(self):
        self.assertEqual(fc.validate({}), ["no claims"])
        bad = [dict(DAY, p=1.2), dict(ABOVE, id="oc_up"), {"id": "x", "horizon": "year", "p": 0.5, "kind": "close_above",
                                                            "date": "27-11-2026"},
               dict(RANGE, id="r2", low=760.0), dict(BELOW, id="b2", start="2026-12-05"), dict(QUIET, id="q2", revises="nope")]
        got = fc.validate(doc(*bad))
        for words in ("p must be", "id used twice", "horizon must be", "needs level", "date must be YYYY-MM-DD",
                      "low must be under high", "start must not be after end", "revises an id"):
            self.assertTrue(any(words in g for g in got), words)


class Outcomes(unittest.TestCase):
    bars = {"2026-11-27": (720.0, 718.0), "2026-11-30": (717.0, 694.0), "2026-12-04": (700.0, 705.0)}

    def test_day_claims(self):
        self.assertEqual(fc.outcome(DAY, self.bars, "2026-11-27")[0], 0)        # closed under its open
        self.assertEqual(fc.outcome(ABOVE, self.bars, "2026-11-27")[0], 1)      # 718 > 716.70
        self.assertEqual(fc.outcome(QUIET, self.bars, "2026-11-27")[0], 1)      # -0.28%

    def test_not_yet_and_no_session(self):
        self.assertEqual(fc.outcome(RANGE, {}, "2026-12-03")[0], None)
        got, why = fc.outcome(dict(DAY, date="2026-11-26"), self.bars, "2026-11-27")
        self.assertEqual((got, why), (None, "no session on that date"))

    def test_window_claims_resolve_early_or_at_the_end(self):
        self.assertEqual(fc.outcome(BELOW, {"2026-11-27": (720.0, 718.0)}, "2026-11-27")[0], None)
        self.assertEqual(fc.outcome(BELOW, self.bars, "2026-11-30")[0], 1)     # 694 < 695.45 on 11-30, early
        calm = {"2026-11-27": (720.0, 718.0), "2026-12-04": (700.0, 705.0)}
        self.assertEqual(fc.outcome(BELOW, calm, "2026-12-04")[0], 0)
        self.assertEqual(fc.outcome(RANGE, self.bars, "2026-12-04")[0], 1)


class Scoring(unittest.TestCase):
    def test_score_once_and_brier(self):
        docs = {"2026-11-27.json": doc(DAY, ABOVE, RANGE)}
        bars = {"SPY": {"2026-11-27": (720.0, 718.0)}}
        rows = fc.score(docs, bars, set(), "2026-11-27", "2026-11-27")
        self.assertEqual([r["claim"] for r in rows], ["oc_up", "above"])       # the week range waits
        self.assertEqual([r["brier"] for r in rows], [round(0.45 ** 2, 4), round(0.35 ** 2, 4)])
        done = {(r["file"], r["claim"]) for r in rows}
        self.assertEqual(fc.score(docs, bars, done, "2026-11-27", "2026-11-27"), [])

    def test_a_file_with_problems_is_not_scored(self):
        docs = {"bad.json": doc(dict(DAY, p=2))}
        self.assertEqual(fc.score(docs, {"SPY": {"2026-11-27": (1.0, 2.0)}}, set(), "2026-11-27", "2026-11-27"), [])

    def test_summary(self):
        rows = [{"horizon": "day", "kind": "close_above_open", "brier": 0.2, "outcome": 1, "p": 0.55},
                {"horizon": "day", "kind": "close_above", "brier": 0.1, "outcome": 1, "p": 0.68},
                {"horizon": "week", "kind": "close_between", "brier": 0.04, "outcome": 1, "p": 0.8}]
        lines = fc.summary(rows)
        self.assertIn("Brier 0.150 on 2", lines[0])
        self.assertIn("better", lines[0])
        self.assertIn("ranges held 1 of 1", lines[1])
        self.assertEqual(fc.summary([]), ["nothing scored yet"])


if __name__ == "__main__":
    unittest.main()
