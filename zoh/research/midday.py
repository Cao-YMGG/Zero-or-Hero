"""Stock-only replays for the 11:30 check-in and the 3% line (Sunday tests 42 and 48).

30-minute SIP bars cached by lockgate.py (2024-02 onward). Prices: open, 10:00 (close of the
09:30 bar), 11:00, 11:30, 13:30, close.
- Item 42: days SMH is above its open at 10:00 and below it at 11:00 or 11:30 ("the mirror arms
  between the check-ins"). How many a month, SMH 11:30 -> close, and the weakest cached chip
  (NVDA, AMD, MU, AVGO) that is below its own open at 11:30: its 11:30 -> close, next to what the
  13:16 check would see (13:30 -> close).
- Item 48: liquidation days (SMH <= -3% from its open at 10:00). Chips by their distance from
  their own open at 10:00 (within 3%, beyond 3%): 10:00 -> close; the same at 11:00.
No options here; the put mirror's option leg stays in BOUNCE.md.

    python -m zoh.research.midday --cache <dir>
"""
import argparse
import json
import statistics
from datetime import datetime, time as dtime

from .. import journal
from ..alpaca import Alpaca
from ..strategy import ET
from .lockgate import fetch

OUT = journal.ROOT / "journal" / "research"
CHIPS = ["NVDA", "AMD", "MU", "AVGO"]
T = {"10:00": dtime(9, 30), "11:00": dtime(10, 30), "11:30": dtime(11, 0), "13:30": dtime(13, 0)}


def points(bars):
    """{day: {"open", "10:00", "11:00", "11:30", "13:30", "close"}} from raw 30-minute bars."""
    days = {}
    for b in bars:
        t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
        if t.time() < dtime(9, 30) or t.time() >= dtime(16, 0):
            continue
        d = days.setdefault(t.date().isoformat(), {})
        if t.time() == dtime(9, 30):
            d["open"] = b["o"]
        for label, bt in T.items():
            if t.time() == bt:
                d[label] = b["c"]
        d["close"] = b["c"]
    return {k: v for k, v in days.items() if "open" in v and "10:00" in v and "11:30" in v}


def stats(xs):
    if not xs:
        return "-"
    return f"{len(xs)} | {sum(1 for x in xs if x > 0) / len(xs):.0%} | {statistics.mean(xs):+.2%} | {statistics.median(xs):+.2%}"


def study42(pts):
    rows = []
    for day, s in sorted(pts["SMH"].items()):
        if s["10:00"] <= s["open"] or not (s.get("11:00", s["11:30"]) < s["open"] or s["11:30"] < s["open"]):
            continue
        chips = {c: pts[c][day] for c in CHIPS if day in pts.get(c, {})}
        below = {c: p["11:30"] / p["open"] - 1 for c, p in chips.items() if p["11:30"] < p["open"]}
        weakest = min(below, key=below.get) if below else None
        w = chips.get(weakest)
        rows.append({"day": day, "smh_1130": round(s["11:30"] / s["open"] - 1, 4),
                     "smh_1130_close": round(s["close"] / s["11:30"] - 1, 4),
                     "smh_1330_close": round(s["close"] / s["13:30"] - 1, 4) if "13:30" in s else None,
                     "weakest": weakest, "w_1130": round(below[weakest], 4) if weakest else None,
                     "w_1130_close": round(w["close"] / w["11:30"] - 1, 4) if w else None,
                     "w_1330_close": round(w["close"] / w["13:30"] - 1, 4) if w and "13:30" in w else None,
                     "w_low_after": None})
    return rows


def study48(pts):
    rows = []
    for day, s in sorted(pts["SMH"].items()):
        if s["10:00"] / s["open"] - 1 > -0.03:
            continue
        for c in CHIPS:
            p = pts.get(c, {}).get(day)
            if not p or "11:00" not in p:
                continue
            rows.append({"day": day, "sym": c, "smh10": round(s["10:00"] / s["open"] - 1, 4),
                         "d10": round(p["10:00"] / p["open"] - 1, 4), "r10": round(p["close"] / p["10:00"] - 1, 4),
                         "d11": round(p["11:00"] / p["open"] - 1, 4), "r11": round(p["close"] / p["11:00"] - 1, 4),
                         "d10_from10": 0.0, "stock_close": round(p["close"] / p["open"] - 1, 4)})
    return rows


def report(r42, r48, end):
    months = {}
    for r in r42:
        months[r["day"][:7]] = months.get(r["day"][:7], 0) + 1
    out = [f"# The 11:30 check-in and the 3% line, stock only\n",
           f"30-minute SIP bars 2024-02 to {end}. Columns: n | share up | average | median. Sunday tests 42 and 48; "
           f"see zoh/research/midday.py. Stock moves only: a 0.20-delta same-day put turns a -1% stock move into roughly "
           f"+50-100% and a +0.5% move into -60% or worse (BOUNCE.md), so the win rate below is the floor, not the option's.\n",
           f"\n## Item 42: SMH above its open at 10:00, below it at 11:00 or 11:30\n\n{len(r42)} days "
           f"({len(r42) / max(1, len(months)):.1f} a month; last 3 months: "
           f"{sum(1 for r in r42 if r['day'] >= '2026-08-08')}).\n\n"]
    out.append("| leg | n | up | avg | median |\n|---|---|---|---|---|\n")
    out.append(f"| SMH 11:30 -> close (a put wants negative) | {stats([r['smh_1130_close'] for r in r42])} |\n")
    out.append(f"| SMH 13:30 -> close (what the 13:16 check sees) | {stats([r['smh_1330_close'] for r in r42 if r['smh_1330_close'] is not None])} |\n")
    sel = [r for r in r42 if r["weakest"]]
    out.append(f"| weakest chip below its open at 11:30: 11:30 -> close | {stats([r['w_1130_close'] for r in sel])} |\n")
    out.append(f"| the same chip 13:30 -> close | {stats([r['w_1130_close'] and r['w_1330_close'] for r in sel if r['w_1330_close'] is not None])} |\n")
    for lo, hi, name in ((-1.0, -0.02, "chip <= -2% from its open at 11:30"), (-0.02, -0.01, "-2% to -1%"), (-0.01, 0.0, "-1% to 0")):
        xs = [r["w_1130_close"] for r in sel if lo <= r["w_1130"] < hi]
        out.append(f"| weakest chip, {name}: 11:30 -> close | {stats(xs)} |\n")
    xs = [r["smh_1130_close"] for r in r42 if r["day"] >= "2026-08-08"]
    out.append(f"| last 3 months, SMH 11:30 -> close | {stats(xs)} |\n")
    xs = [r["w_1130_close"] for r in sel if r["day"] >= "2026-08-08"]
    out.append(f"| last 3 months, weakest chip 11:30 -> close | {stats(xs)} |\n")
    out.append("\nDays a month: " + ", ".join(f"{k} {v}" for k, v in sorted(months.items())[-12:]) + "\n")
    out.append("\n### Last 3 months, day by day\n\n| day | SMH at 11:30 | SMH 11:30->close | weakest | at 11:30 | 11:30->close | 13:30->close |\n|---|---|---|---|---|---|---|\n")
    for r in r42:
        if r["day"] >= "2026-08-08":
            out.append(f"| {r['day']} | {r['smh_1130']:+.2%} | {r['smh_1130_close']:+.2%} | {r['weakest'] or '-'} | "
                       f"{(r['w_1130'] or 0):+.2%} | {(r['w_1130_close'] or 0):+.2%} | {(r['w_1330_close'] or 0):+.2%} |\n")
    days48 = sorted({r["day"] for r in r48})
    out.append(f"\n## Item 48: liquidation days (SMH <= -3% from its open at 10:00): {len(days48)} days\n\n")
    out.append("| chips by distance from their own open | n | share up | avg | median |\n|---|---|---|---|---|\n")
    for lo, hi, name in ((-1.0, -0.03, "beyond 3% below at 10:00 (the line excludes them)"), (-0.03, 0.0, "within 3% below at 10:00"), (0.0, 1.0, "above their open at 10:00")):
        xs = [r["r10"] for r in r48 if lo <= r["d10"] < hi]
        out.append(f"| {name}: 10:00 -> close | {stats(xs)} |\n")
    for lo, hi, name in ((-1.0, -0.03, "beyond 3% below at 11:00"), (-0.03, 0.0, "within 3% below at 11:00"), (0.0, 1.0, "above their open at 11:00")):
        xs = [r["r11"] for r in r48 if lo <= r["d11"] < hi]
        out.append(f"| {name}: 11:00 -> close | {stats(xs)} |\n")
    out.append("\n| day | SMH at 10:00 | NVDA 10:00 / ->close | AMD | MU | AVGO |\n|---|---|---|---|---|---|\n")
    for d in days48:
        cells = []
        for c in CHIPS:
            r = next((x for x in r48 if x["day"] == d and x["sym"] == c), None)
            cells.append(f"{r['d10']:+.1%} / {r['r10']:+.1%}" if r else "-")
        smh = next(x for x in r48 if x["day"] == d)["smh10"]
        out.append(f"| {d} | {smh:+.1%} | " + " | ".join(cells) + " |\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    args = ap.parse_args()
    api = Alpaca()
    pts = {s: points(fetch(api, s, args.cache)) for s in ["SMH"] + CHIPS}
    r42, r48 = study42(pts), study48(pts)
    end = max(pts["SMH"])
    (OUT / "midday.json").write_text(json.dumps({"item42": r42, "item48": r48}, indent=0) + "\n")
    text = report(r42, r48, end)
    (OUT / "MIDDAY.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
