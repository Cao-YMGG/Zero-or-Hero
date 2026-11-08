"""Overnight dip-buy, stock only (Sunday test 47, owner idea 2026-11-05).

On a day SPY closes >= 1.5% below its open, buy SPY, QQQ or the day's weakest sector ETF at the
close (the owner said 15:50; 30-minute bars give the 16:00 print) and sell at the next open, at
the next 10:00 and at the next close. Splits: depth of the drop, lock days (LOCKGATE.md class),
VIXY's own move that day, and whether the next day carries a CPI / NFP / FOMC release. No options,
so no bleed: the numbers are the stock's own moves. Uses the 30-minute bars cached by lockgate.py.

    python -m zoh.research.dipbuy --cache <dir>
"""
import argparse
import json
import statistics
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca
from .lockgate import SECTORS, day_points, fetch
from .opendrive import macro_days

OUT = journal.ROOT / "journal" / "research"
ETFS = ["SPY", "QQQ", "SMH"] + SECTORS
DROP = -0.015


def stats(xs):
    if not xs:
        return "-"
    return (f"{len(xs)} | {sum(1 for x in xs if x > 0) / len(xs):.0%} | {statistics.mean(xs):+.2%} | "
            f"{statistics.median(xs):+.2%}")


def build(points, lock, macro):
    days = sorted(points["SPY"])
    rows = []
    for i, day in enumerate(days[:-1]):
        spy = points["SPY"][day]
        oc = spy["close"] / spy["open"] - 1
        nxt = days[i + 1]
        if nxt not in points["SPY"]:
            continue
        weakest = min((s for s in ETFS if day in points.get(s, {}) and nxt in points.get(s, {})),
                      key=lambda s: points[s][day]["close"] / points[s][day]["open"] - 1, default=None)
        vix = points.get("VIXY", {}).get(day)
        row = {"day": day, "next": nxt, "spy_oc": round(oc, 4), "lock": lock.get(day, "?"),
               "vixy_oc": round(vix["close"] / vix["open"] - 1, 4) if vix else None,
               "next_macro": nxt in macro, "weakest": weakest, "legs": {}}
        for sym in ("SPY", "QQQ", weakest):
            if not sym or day not in points.get(sym, {}) or nxt not in points.get(sym, {}):
                continue
            a, b = points[sym][day], points[sym][nxt]
            row["legs"][sym if sym in ("SPY", "QQQ") else "weakest"] = {
                "sym": sym, "to_open": round(b["open"] / a["close"] - 1, 4),
                "to_10": round(b["p10"] / a["close"] - 1, 4), "to_close": round(b["close"] / a["close"] - 1, 4)}
        rows.append(row)
    return rows


def table(rows, leg, groups):
    out = "| group | n | win | avg | median (to next open) | to next 10:00: n \\| win \\| avg \\| median | to next close |\n|---|---|---|---|---|---|---|\n"
    for name, f in groups:
        sel = [r["legs"][leg] for r in rows if f(r) and leg in r["legs"]]
        out += (f"| {name} | " + stats([x["to_open"] for x in sel]) + " | " + stats([x["to_10"] for x in sel])
                + " | " + stats([x["to_close"] for x in sel]) + " |\n")
    return out


def report(rows, end):
    dips = [r for r in rows if r["spy_oc"] <= DROP]
    groups = [
        ("all days (base rate)", lambda r: True),
        (f"SPY <= {DROP:.1%} open to close", lambda r: r["spy_oc"] <= DROP),
        ("  -1.5% to -2.5%", lambda r: DROP >= r["spy_oc"] > -0.025),
        ("  <= -2.5%", lambda r: r["spy_oc"] <= -0.025),
        ("  lock day (LOCKGATE class)", lambda r: r["spy_oc"] <= DROP and r["lock"] == "lock"),
        ("  not a lock day", lambda r: r["spy_oc"] <= DROP and r["lock"] != "lock"),
        ("  VIXY >= +5% on the day", lambda r: r["spy_oc"] <= DROP and (r["vixy_oc"] or 0) >= 0.05),
        ("  VIXY < +5%", lambda r: r["spy_oc"] <= DROP and (r["vixy_oc"] or 0) < 0.05),
        ("  next day CPI / NFP / FOMC", lambda r: r["spy_oc"] <= DROP and r["next_macro"]),
        ("  next day no release", lambda r: r["spy_oc"] <= DROP and not r["next_macro"]),
        ("  last 3 months", lambda r: r["spy_oc"] <= DROP and r["day"] >= (end - timedelta(days=91)).isoformat()),
        ("  last year", lambda r: r["spy_oc"] <= DROP and r["day"] >= (end - timedelta(days=365)).isoformat()),
    ]
    out = ["# Overnight dip-buy, stock only\n",
           f"Buy at the close of a day SPY fell >= 1.5% from its open, sell at the next open / 10:00 / close. "
           f"30-minute SIP bars 2024-02 to {end}; no option costs. Columns: n | win% | average | median. "
           f"Sunday test 47; see zoh/research/dipbuy.py.\n",
           f"\n{len(dips)} dip days of {len(rows)}.\n",
           "\n## SPY\n\n", table(rows, "SPY", groups),
           "\n## QQQ\n\n", table(rows, "QQQ", groups),
           "\n## The day's weakest ETF (SPY, QQQ, SMH, sectors)\n\n", table(rows, "weakest", groups)]
    counts = {}
    for r in dips:
        counts[r["weakest"]] = counts.get(r["weakest"], 0) + 1
    out.append("\nWeakest on dip days: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])) + "\n")
    out.append("\n## Every dip day\n\n| day | SPY o->c | lock | VIXY o->c | next macro | SPY to open | to 10:00 | to close | weakest | its to-open |\n|---|---|---|---|---|---|---|---|---|---|\n")
    for r in dips:
        s, w = r["legs"].get("SPY", {}), r["legs"].get("weakest", {})
        out.append(f"| {r['day']} | {r['spy_oc']:+.2%} | {r['lock']} | {(r['vixy_oc'] or 0):+.1%} | {'yes' if r['next_macro'] else ''} | "
                   f"{s.get('to_open', 0):+.2%} | {s.get('to_10', 0):+.2%} | {s.get('to_close', 0):+.2%} | {r['weakest']} | {w.get('to_open', 0):+.2%} |\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    args = ap.parse_args()
    api = Alpaca()
    points = {s: day_points(fetch(api, s, args.cache)) for s in ETFS + ["VIXY"]}
    lock = {}
    p = OUT / "lockgate.json"
    if p.exists():
        data = json.loads(p.read_text())
        for r in (data if isinstance(data, list) else data.get("rows", [])):
            lock[r["day"]] = r.get("cls") or r.get("class")
    rows = build(points, lock, macro_days())
    end = datetime.fromisoformat(max(points["SPY"])).date()
    (OUT / "dipbuy.json").write_text(json.dumps(rows, indent=0) + "\n")
    text = report(rows, end)
    (OUT / "DIPBUY.md").write_text(text)
    print(text[:5000])


if __name__ == "__main__":
    main()
