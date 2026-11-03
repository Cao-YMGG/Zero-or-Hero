"""Failed bounce in a cooling theme on real option prices: the 2026-11-03 put mirror (Sunday item 40).

Event day t: SMH is cooling (prior close vs the close 21 sessions earlier <= -10%), gaps up >= 1%
at the open, and is back below its open at 11:00 ET (the first intraday check-in). Pick: the
weakest of NVDA / AMD / MU / AVGO / INTC / MRVL from its own open at 11:00 that is below its open
and not on a report day (reaction day, or reporting after today's close; Benzinga EPS headlines).
Buy its nearest-expiry put at 11:03 (0.10 / 0.20 / 0.30 delta). Exits: live (half at 3x, trail armed
at 1.5x, 40% giveback), half3_hold (half at 3x, the rest to 15:45), hold to 15:45, trail2x, and a
stock stop (sell the first minute the stock closes back at or above its open). The same put on SMH
is the index version. Costs 10% each way. Days where the bounce held at 11:00 are kept for the base
rate (how often a cooling-theme gap-up fails by 11:00 and by the close).

    python -m zoh.research.bounce [--years 2]
"""
import argparse
import json
import time
from datetime import datetime, timedelta, timezone

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import at_or_after
from ..runup import daily, earnings_events
from ..strategy import hhmm
from .exits import EXITS, bid, candidates, nearest_expiry, run
from .snipers import stats, stock_minutes

OUT = journal.ROOT / "journal" / "research"
CHIPS = ["NVDA", "AMD", "MU", "AVGO", "INTC", "MRVL"]
THEME = "SMH"
COOLING, GAP = -0.10, 0.01
CHECK, ENTRY, EXIT_AT = hhmm("11:00"), hhmm("11:03"), hhmm("15:45")
DELTAS = (0.10, 0.20, 0.30)
SLIP = 0.10
EXITS.update({"half3_arm1.5": (1.5, 0.4, None, 3.0), "half3_hold": (None, None, None, 3.0)})
RULES = ("half3_arm1.5", "half3_hold", "hold", "trail2x")
LIVE = "half3_arm1.5"


def events(theme_daily):
    """[(day, month_change, gap)] for days the theme is cooling and gaps up, from (day, open, close)."""
    out = []
    for i in range(22, len(theme_daily)):
        day, o, _ = theme_daily[i]
        prev, month = theme_daily[i - 1][2], theme_daily[i - 22][2]
        if prev / month - 1 <= COOLING and o / prev - 1 >= GAP:
            out.append((day, prev / month - 1, o / prev - 1))
    return out


def stop_run(path, stock, open_px, entry, slip):
    """Exit value per $1 when sold the first minute the stock closes at/above its open, else 15:45."""
    above = {b["t"]: b["c"] >= open_px for b in stock}
    for t, c in path:
        if t.time() >= EXIT_AT or above.get(t):
            return bid(c, slip) / entry
    return bid(path[-1][1], slip) / entry if path else 0.0


def price_put(api, sym, day, bars, entry_bar):
    expiry = nearest_expiry(sym, day)
    if not expiry:
        return None
    t = (entry_bar["t"] + timedelta(minutes=1)).time()
    try:
        cands, opts = candidates(api, sym, day, expiry, t, entry_bar["c"], "put")
    except AlpacaError:
        return None
    res = {"expiry": expiry.isoformat()}
    for d in DELTAS:
        if not cands:
            break
        s, k, dl, b = min(cands, key=lambda x: abs(x[2] - d))
        path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
        if not path:
            continue
        entry = max(b["c"] * (1 + SLIP), b["c"] + 0.01)
        r = {rule: round(run(path, entry, SLIP, rule) - 1, 4) for rule in RULES}
        r["stock_stop"] = round(stop_run(path, bars, bars[0]["o"], entry, SLIP) - 1, 4)
        res[f"d{d:.2f}"] = {"contract": s, "strike": k, "delta": round(dl, 3), "px": b["c"],
                            "peak": round(max(bid(c, SLIP) for _, c in path) / entry, 3), **r}
    return res if len(res) > 1 else None


def in_report_window(day, reports):
    return day in reports or any(day + timedelta(days=k) in reports for k in (1, 2, 3))


def study(api, years):
    end = datetime.now(timezone.utc) - timedelta(days=1)  # the free tier refuses recent SIP daily bars
    start = end - timedelta(days=365 * years + 40)
    theme = daily(api, [THEME], start, end)[THEME]
    reports = {}
    for s in CHIPS:
        reports[s] = {r[0] for r in earnings_events(api, s, start, end)}
        print(f"{s}: {len(reports[s])} reports", flush=True)
    rows = []
    for day, month, gap in events(theme):
        tb = stock_minutes(api, THEME, day)
        chk = at_or_after(tb, CHECK, 3) if tb else None
        if not chk:
            continue
        o = tb[0]["o"]
        row = {"day": day.isoformat(), "theme_month": round(month, 4), "gap": round(gap, 4),
               "theme_1100": round(chk["c"] / o - 1, 4), "theme_close": round(tb[-1]["c"] / o - 1, 4),
               "failed": chk["c"] < o, "chips": {}}
        bars = {}
        for s in CHIPS:
            sb = stock_minutes(api, s, day)
            cb = at_or_after(sb, CHECK, 3) if sb else None
            if not cb:
                continue
            bars[s] = sb
            row["chips"][s] = {"from_open": round(cb["c"] / sb[0]["o"] - 1, 4),
                               "close": round(sb[-1]["c"] / sb[0]["o"] - 1, 4),
                               "report": in_report_window(day, reports[s])}
        elig = [s for s, c in row["chips"].items() if c["from_open"] < 0 and not c["report"]]
        if row["failed"] and elig:
            pick = min(elig, key=lambda s: row["chips"][s]["from_open"])
            eb = at_or_after(bars[pick], ENTRY, 3)
            row["pick"] = pick
            row["put"] = price_put(api, pick, day, bars[pick], eb) if eb else None
            eb2 = at_or_after(tb, ENTRY, 3)
            row["theme_put"] = price_put(api, THEME, day, tb, eb2) if eb2 else None
        rows.append(row)
        print(f"{day} month {month:+.1%} gap {gap:+.1%} 11:00 {row['theme_1100']:+.2%} "
              f"{'failed' if row['failed'] else 'held'} pick {row.get('pick')}", flush=True)
        time.sleep(0.2)
    return rows


def window(rows, days, end):
    return [r for r in rows if datetime.fromisoformat(r["day"]).date() >= end - timedelta(days=days)]


def report(rows, years):
    end = datetime.now(timezone.utc).date()
    L = [f"# Failed bounce in a cooling theme: the put mirror on real option prices", "",
         f"{len(rows)} days in {years} years where SMH was down >= 10% over the prior month and gapped up >= 1% "
         f"(Alpaca daily and minute bars, option minute bars, costs 10% each way). 'Failed' = SMH back below its open "
         f"at 11:00. Pick = weakest of {', '.join(CHIPS)} from its own open at 11:00, below its open, outside a report "
         f"window; put bought at 11:03 on the nearest expiry. Columns: n | win% | avg | without the best | without the "
         f"best two. See zoh/research/bounce.py.", "", "## Base rate", "",
         "| window | gap-up days | failed by 11:00 | SMH open->close, failed days | SMH open->close, held days | pick found |",
         "|---|---|---|---|---|---|"]
    for name, days in (("last 3 months", 92), ("1 year", 365), ("all", 100000)):
        sel = window(rows, days, end)
        if not sel:
            continue
        f = [r for r in sel if r["failed"]]
        h = [r for r in sel if not r["failed"]]
        m = lambda xs: f"{sum(x['theme_close'] for x in xs) / len(xs):+.2%} ({sum(x['theme_close'] < 0 for x in xs)}/{len(xs)} down)" if xs else "-"
        L.append(f"| {name} | {len(sel)} | {len(f)} ({len(f) / len(sel):.0%}) | {m(f)} | {m(h)} | "
                 f"{sum(1 for r in f if r.get('put'))} |")
    for which, title in (("put", "Pick put (weakest chip)"), ("theme_put", "SMH put (index version)")):
        L += ["", f"## {title}", "", "| window | delta | exit | n | win% | avg | -best | -best2 |",
              "|---|---|---|---|---|---|---|---|"]
        for name, days in (("last 3 months", 92), ("1 year", 365), ("all", 100000)):
            sel = [r for r in window(rows, days, end) if r.get(which)]
            if not sel:
                continue
            for d in DELTAS:
                lab = f"d{d:.2f}"
                for rule in RULES + ("stock_stop",):
                    xs = [r[which][lab][rule] for r in sel if lab in r[which]]
                    L.append(f"| {name} | {lab} | {rule} | {stats(xs)} |")
    L += ["", "## Each failed day with a pick (0.20 delta)", "",
          "| day | SMH 1m | gap | SMH 11:00 | SMH close | pick | pick 11:00 -> close | peak x | live | half3_hold | hold | stock stop | SMH put live / hold |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if not r.get("put"):
            continue
        c = r["chips"][r["pick"]]
        p = r["put"].get("d0.20")
        tp = (r.get("theme_put") or {}).get("d0.20")
        cell = (f"{p['peak']:.1f} | {p[LIVE]:+.0%} | {p['half3_hold']:+.0%} | {p['hold']:+.0%} | {p['stock_stop']:+.0%}"
                if p else "- | - | - | - | -")
        tcell = f"{tp[LIVE]:+.0%} / {tp['hold']:+.0%}" if tp else "-"
        L.append(f"| {r['day']} | {r['theme_month']:+.0%} | {r['gap']:+.1%} | {r['theme_1100']:+.2%} | {r['theme_close']:+.2%} | "
                 f"{r['pick']} | {c['from_open']:+.1%} -> {c['close']:+.1%} | {cell} | {tcell} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=2)
    ap.add_argument("--from-json", action="store_true", help="rebuild the report from bounce.json")
    a = ap.parse_args()
    if a.from_json:
        rows = json.loads((OUT / "bounce.json").read_text())
    else:
        rows = study(Alpaca(), a.years)
        (OUT / "bounce.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    text = report(rows, a.years)
    (OUT / "BOUNCE.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
