"""Follow the open on real 0DTE option prices: was 2026-10-14 a pattern or a lucky day?

Rule (the other Claude's 0DTE sleeves, which made +200% on SPY/NVDA puts on 2026-10-14):
at 10:00 ET, if the underlying is above its open buy a same-day call, if below buy a same-day
put, strike about 0.7% out of the money; sell at 3x the entry, otherwise at 15:30.

Days are split by what was knowable at 10:00: macro release days (CPI / NFP / FOMC), the gap
direction, and whether the gap and the first 30 minutes agree. "Like 2026-10-14" = a macro day
that gapped down and was still below its open at 10:00.

Prices are 1-minute option bar closes (Alpaca, 2024-02+). Entry at close x (1 + slip), exits
at close x (1 - slip), at least $0.01 each way.

    python -m zoh.research.opendrive
"""
import json
import statistics
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import at_or_after, daily_raw, has_same_day_expiry, occ, option_minutes
from ..strategy import ET, MARKET_OPEN, hhmm, parse_bar, regular_session

SYMBOLS = ["SPY", "QQQ", "NVDA", "TSLA"]
DAILY = {"SPY", "QQQ"}  # same-day expiries every weekday
START = date(2024, 2, 1)
ENTRY = hhmm("10:00")
EXIT_AT = hhmm("15:30")
OTM = 0.007
MIN_MOVE = 0.001  # 0.1% from the open, so a flat open is skipped
TAKE = 3.0
SLIPS = (0.05, 0.10)
OUT = Path(__file__).resolve().parents[2] / "journal" / "research"

# Release days before config/macro_events.json starts (2025-10); public BLS / Fed calendars.
OLDER_EVENTS = {
    "CPI": ["2024-02-13", "2024-03-12", "2024-04-10", "2024-05-15", "2024-06-12", "2024-07-11",
            "2024-08-14", "2024-09-11", "2024-10-10", "2024-11-13", "2024-12-11", "2025-01-15",
            "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13", "2025-06-11", "2025-07-15",
            "2025-08-12", "2025-09-11"],
    "NFP": ["2024-02-02", "2024-03-08", "2024-04-05", "2024-05-03", "2024-06-07", "2024-07-05",
            "2024-08-02", "2024-09-06", "2024-10-04", "2024-11-01", "2024-12-06", "2025-01-10",
            "2025-02-07", "2025-03-07", "2025-04-04", "2025-05-02", "2025-06-06", "2025-07-03",
            "2025-08-01", "2025-09-05"],
    "FOMC": ["2024-03-20", "2024-05-01", "2024-06-12", "2024-07-31", "2024-09-18", "2024-11-07",
             "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18", "2025-07-30",
             "2025-09-17"],
}


def macro_days():
    days = {d: kinds for d, kinds in journal.load_events().items()}
    for kind, dates in OLDER_EVENTS.items():
        for d in dates:
            days.setdefault(d, []).append(kind)
    return days


def expiry_today(sym, day):
    return day.weekday() < 5 if sym in DAILY else has_same_day_expiry(sym, day)


def strikes_near(target, kind):
    """A few listed-looking strikes around the target (the right one is whichever trades)."""
    out = set()
    for step in (0.5, 1, 2.5, 5):
        base = round(target / step) * step
        out.update(round(base + i * step, 2) for i in (-1, 0, 1))
    return sorted(out, key=lambda k: abs(k - target))[:8]


def trade(path, entry, slip):
    """3x take profit or 15:30. path: [(t, close)] after entry."""
    last = entry
    for t, c in path:
        bid = max(0.0, min(c * (1 - slip), c - 0.01))
        last = bid
        if t.time() >= EXIT_AT:
            return bid, "time"
        if bid >= TAKE * entry:
            return bid, "take"
    return last, "eod"


def main():
    api = Alpaca()
    events = macro_days()
    end = datetime.now(ET).date() - timedelta(days=1)
    rows, skipped = [], {"no_bars": 0, "no_option": 0}
    for sym in SYMBOLS:
        days = daily_raw(api, sym, START - timedelta(days=7), end)
        n = 0
        for i in range(1, len(days)):
            day, o, _ = days[i]
            prev = days[i - 1][2]
            if day < START or not expiry_today(sym, day):
                continue
            start = datetime.combine(day, MARKET_OPEN, ET)
            try:
                stock = regular_session([parse_bar(b) for b in api.stock_bars(
                    sym, start, start + timedelta(minutes=32), feed="sip", adjustment="raw")])
            except AlpacaError:
                skipped["no_bars"] += 1
                continue
            bar = at_or_after(stock, hhmm("09:59"), 2)
            if not stock or not bar:
                skipped["no_bars"] += 1
                continue
            open_, spot = stock[0]["o"], bar["c"]
            move = spot / open_ - 1
            if abs(move) < MIN_MOVE:
                continue
            kind = "call" if move > 0 else "put"
            target = spot * (1 + OTM) if kind == "call" else spot * (1 - OTM)
            contracts = {occ(sym, day, k, kind): k for k in strikes_near(target, kind)}
            try:
                opts = option_minutes(api, list(contracts), day)
            except AlpacaError:
                skipped["no_option"] += 1
                continue
            time.sleep(0.15)
            best = None
            for s, bars in opts.items():
                b = at_or_after(bars, ENTRY, 5)
                if b and b["c"] > 0 and (best is None or abs(contracts[s] - target)
                                         < abs(contracts[best[0]] - target)):
                    best = (s, b)
            if not best:
                skipped["no_option"] += 1
                continue
            s, b = best
            path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
            gap = o / prev - 1
            row = {"sym": sym, "day": day.isoformat(), "kind": kind, "gap": round(gap, 4),
                   "move10": round(move, 4), "macro": ",".join(events.get(day.isoformat(), [])),
                   "contract": s, "px": b["c"],
                   "max_x": round(max([c for _, c in path] or [b["c"]]) / b["c"], 2)}
            for slip in SLIPS:
                entry = max(b["c"] * (1 + slip), b["c"] + 0.01)
                exit_, why = trade(path, entry, slip)
                row[f"pnl_{int(slip * 100)}"] = round(exit_ / entry - 1, 4)
                row[f"why_{int(slip * 100)}"] = why
            rows.append(row)
            n += 1
        print(f"{sym}: {n} trades", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "opendrive.json").write_text(json.dumps(rows, indent=1) + "\n")
    (OUT / "OPENDRIVE.md").write_text(report(rows, skipped, end))
    print(report(rows, skipped, end))


def stats(p):
    if not p:
        return None
    s = sorted(p)
    def avg(x):
        return sum(x) / len(x) if x else float("nan")
    return {"n": len(p), "avg": avg(p), "ex1": avg(s[:-1]), "ex2": avg(s[:-2]),
            "med": statistics.median(p), "win": sum(x > 0 for x in p) / len(p),
            "best": s[-1]}


def report(rows, skipped, end):
    recent = (end - timedelta(days=91)).isoformat()
    year = (end - timedelta(days=365)).isoformat()
    groups = {
        "all days": lambda r: True,
        "puts (below the open at 10:00)": lambda r: r["kind"] == "put",
        "calls (above the open at 10:00)": lambda r: r["kind"] == "call",
        "macro days": lambda r: bool(r["macro"]),
        "gap and 10:00 move agree": lambda r: r["gap"] * r["move10"] > 0,
        "gap and 10:00 move disagree": lambda r: r["gap"] * r["move10"] < 0,
        "like 2026-10-14 (macro, gap down, below open)":
            lambda r: bool(r["macro"]) and r["gap"] < 0 and r["kind"] == "put",
        "gap down + below open (any day)": lambda r: r["gap"] < 0 and r["kind"] == "put",
    }

    def pct(x):
        return f"{x:+.0%}"

    lines = ["# Follow the open on real 0DTE option prices", "",
             "Rule: at 10:00 ET buy a same-day call if the underlying is above its open (put if "
             f"below; skip if within {MIN_MOVE:.1%}), strike ~{OTM:.1%} out of the money; sell at "
             f"{TAKE:.0f}x entry, else at 15:30. SPY/QQQ every weekday; NVDA/TSLA on same-day "
             "expiry days (Fridays; Mon/Wed too since 2026-01-26). Real 1-minute option closes, "
             "10% slippage each way in the tables (5% in opendrive.json). Macro calendar: "
             "config/macro_events.json plus 2024-25 CPI/NFP/FOMC dates.", "",
             f"Skipped: {skipped}. Data through {end}.", ""]
    for sym in ["all"] + SYMBOLS:
        lines += [f"## {sym}", "",
                  "| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, f in groups.items():
            for period, cut in (("last 3 months", recent), ("last year", year), ("since 2024-02", "")):
                p = [r["pnl_10"] for r in rows if (sym == "all" or r["sym"] == sym)
                     and f(r) and r["day"] >= cut]
                s = stats(p)
                if s:
                    lines.append(f"| {name} | {period} | {s['n']} | {s['win']:.0%} | {pct(s['avg'])} | "
                                 f"{pct(s['ex1'])} | {pct(s['ex2'])} | {pct(s['med'])} | {pct(s['best'])} |")
        lines.append("")
    like = [r for r in rows if r["macro"] and r["gap"] < 0 and r["kind"] == "put"]
    lines += ["## Every 'like 2026-10-14' trade", "",
              "| day | sym | macro | gap | 10:00 move | contract | entry | max x | pnl (10%) | exit |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(like, key=lambda r: (r["day"], r["sym"])):
        lines.append(f"| {r['day']} | {r['sym']} | {r['macro']} | {r['gap']:+.1%} | {r['move10']:+.1%} | "
                     f"{r['contract']} | {r['px']} | {r['max_x']} | {r['pnl_10']:+.0%} | {r['why_10']} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
