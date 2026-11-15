import csv
import json
import tempfile
import unittest
from pathlib import Path

from zoh.research import week46 as w


class Week46(unittest.TestCase):
    def test_trio_and_cell(self):
        n, win, avg, cut1, cut2 = w.trio([-1.0, -1.0, 0.5, 4.0])
        self.assertEqual((n, win), (4, 0.5))
        self.assertAlmostEqual(avg, 0.625)
        self.assertAlmostEqual(cut1, -0.5)
        self.assertAlmostEqual(cut2, -1.0)
        self.assertEqual(w.cell([-1.0, -1.0, 0.5, 4.0]), "4 | 50% | +62% / -50% / -100%")
        self.assertEqual(w.cell([]), "0 | - | - / - / -")
        self.assertEqual(w.cell([0.2]), "1 | 100% | +20% / - / -")       # nothing left once the best is gone

    def test_hero_pairs_estimate_a_trail_from_the_peak(self):
        fields = ["date", "variant", "mode", "contract", "direction", "entry_time", "entry_price", "exit_time",
                  "exit_price", "qty", "pnl", "pnl_pct", "exit_reason", "phase", "equity_before"]

        def row(variant, contract, entry, exit_, qty, day="2026-11-13", entered="2026-11-10T09:32:00-05:00"):
            return dict(zip(fields, [day, variant, "shadow", contract, "call", entered, entry, "", exit_, qty,
                                     round((exit_ - entry) * qty * 100, 2), round(exit_ / entry - 1, 4), "time", "", ""]))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "journal").mkdir()
            rows = [row("catalyst_open_hero", "TSM261113C00415000", 1.01, 0.0, 4),
                    row("catalyst_open", "TSM261113C00417500", 0.82, 1.28, 1, day="2026-11-10"),
                    row("catalyst_intraday_hero", "AMZN261111C00277500", 0.77, 0.0, 5, day="2026-11-11")]
            with open(root / "journal" / "trades.csv", "w", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=fields)
                wr.writeheader()
                wr.writerows(rows)
            with open(root / "journal" / "exits.csv", "w", newline="") as f:
                wr = csv.writer(f)
                wr.writerow(["date", "variant", "mode", "contract", "entry_price", "exit_price", "peak", "exit_reason"])
                wr.writerow(["2026-11-13", "catalyst_open_hero", "shadow", "TSM261113C00415000", 1.01, 0, 7.13, "time"])
                wr.writerow(["2026-11-11", "catalyst_intraday_hero", "shadow", "AMZN261111C00277500", 0.77, 0, 0.77, "time"])
            tsm, amzn = w.hero_pairs(root)
        self.assertEqual((tsm["stake"], tsm["peak_x"], tsm["pnl_pct"]), (404, 7.06, -1.0))
        self.assertAlmostEqual(tsm["trail_pct"], 0.6 * 7.13 / 1.01 - 1, places=3)      # out at 60% of the peak
        self.assertEqual((tsm["twin_pct"], tsm["twin_same"]), (0.561, False))          # the small leg held another strike
        self.assertEqual((amzn["peak_x"], amzn["trail_pct"], amzn["twin_pct"]), (1.0, -1.0, None))  # never armed

    def test_class_falls_back_to_the_table_and_then_to_news(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "journal" / "bias").mkdir(parents=True)
            (root / "journal" / "bias" / "2026-11-16.json").write_text(json.dumps({"sniper": {"symbol": "V", "class": "upgrade"}}))
            (root / "journal" / "bias" / "2026-11-17.json").write_text(json.dumps({"sniper": {"symbol": "V"}}))
            self.assertEqual(w.class_of("2026-11-16", root), "upgrade")
            self.assertEqual(w.class_of("2026-11-17", root), "news")
            self.assertEqual(w.class_of("2026-11-12", root), "upgrade")     # before the field existed: the table
            self.assertEqual(w.class_of("2026-10-15", root), "none")

    def test_upgrade_stats_split_by_period_and_side(self):
        def ev(day, kind, x45):
            return {"day": day, "kind": kind, "picks": {"d0.45": {"exits_10": {"half2_arm1.5": x45, "half3_arm1.5": x45, "hold": -1.0},
                                                                    "carry_10": {"half2_arm1.5": x45 + 0.1, "half3_arm1.5": x45, "hold": -1.0}}}}
        st = w.upgrade_stats([ev("2024-05-01", "call", 0.5), ev("2026-09-01", "call", -0.5), ev("2026-09-02", "put", 1.0)])
        self.assertEqual(st["all | d0.45 | half2_arm1.5"]["day1"], [0.5, -0.5, 1.0])
        self.assertEqual(st["last 3 months | d0.45 | half2_arm1.5"]["day1"], [-0.5, 1.0])
        self.assertEqual(st["calls (upgrades), all | d0.45 | half2_arm1.5"]["carried"], [0.6, -0.4])
        self.assertEqual(st["all | d0.30 | hold"]["day1"], [])               # a strike with no contract is left out

    def test_report_runs_on_a_small_record(self):
        pick = {"day": "2026-11-12", "sym": "AMD", "kind": "call", "oc": 0.03, "entered": True, "entry_t": "09:32",
                "ext": 0.004, "fwd": 0.025, "class": "upgrade",
                "opt": {d: {"day1": {"half3_arm1.5": 0.2, "half2_arm1.5": 0.5, "hold": 0.3},
                            "carry": {"half3_arm1.5": 0.2, "half2_arm1.5": 0.5, "hold": -1.0}} for d in ("d0.10", "d0.20", "d0.30", "d0.45")}}
        data = {"through": "2026-11-13", "picks": {"snipers": [pick], "intraday": [dict(pick, own_range=0.02)]},
                "gates": [{"day": "2026-11-12", "sym": "AMD", "class": "upgrade",
                           "gates": {"live": {"t": "09:32", "ext": 0.004, "fwd": 0.025}, "five": {"t": "09:36", "ext": 0.01, "fwd": 0.02}}}],
                "open_drive": {"stock | all": {"n": 2, "x2": 1, "x3": 0,
                                               "exits": {k: [0.5, -1.0] for k in ("hold", "take3", "trail", "half3_trail")}}},
                "heroes": [{"day": "2026-11-12", "variant": "catalyst_open_hero", "contract": "AMD261113C00617500", "entry": 1.65,
                            "qty": 2, "stake": 330, "peak_x": 2.53, "pnl_pct": -1.0, "pnl": -330.0, "trail_pct": 0.52,
                            "twin_pct": None, "twin_same": False}],
                "bias": [{"date": "2026-10-22", "bias": "put", "p_up": None, "oc": -0.003, "cc": -0.01},
                         {"date": "2026-11-12", "bias": "none", "p_up": 0.53, "oc": 0.004, "cc": -0.003}],
                "opportunities": {"days": 1, "groups": {"all": {"n": 2, "paid": 1, "right": 0, "wrong": 1, "vs_spy": 0.5, "vs_spy_cut": None}}},
                "rotation_model": {"two years | heating": {"n": 10, "avg": -0.02, "beat": 0.5}},
                "rotation_map": [{"date": "2026-11-12", "heating": 1.5, "cooling": 1.6}],
                "release": [{"day": "2026-11-13", "pop": 0.0034, "kept": -0.01, "oc_with": -0.0075}]}
        text = w.report(data)
        self.assertIn("| sniper, rating change (upgrade or target) | 1 | 1 | +3.00% | 1 | 1 | +2.50% | 1 |", text)
        self.assertIn("| rating change | d0.45 | half2_arm1.5 | 1 | 100% | +50% / - / - | 1 | 100% | +50% / - / - |", text)
        self.assertIn("1 trades, 0 wins, $-330; 1 traded at 1.5x or better first.", text)
        self.assertIn("| half or more of the reaction gone | 1 | 0 | -0.75% | 1 |", text)
        self.assertNotIn("every rating headline of two years", text)        # no replay rows given


if __name__ == "__main__":
    unittest.main()
