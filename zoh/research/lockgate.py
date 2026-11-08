"""Was the lock visible at 10:00? A replay of the "锁上了没有" gate (owner, 2026-11-05).

On 2026-11-05 the index lost 4.2% open to close while the morning file said "none" (p_up 0.49)
and an AMZN call. The structure was complete by 10:00: SPY below its open, VIXY up with the
index (not against it), every mega cap below its own open. The gate was written down before this
replay ran (journal/research/SUNDAY_TESTS.md item 45):

    LOCK at 10:00 ET = SPY below its open by >= 0.1%
                       AND VIXY >= 3% above its own open
                       AND >= 8 of 10 mega caps below their opens.

Days are classed from what was knowable at 10:00: lock, vix_only (SPY below, VIXY up, breadth
short), breadth_only (SPY below, breadth full, VIXY calm), below_open (neither flag) and
above_open. Outcomes: SPY / QQQ / SMH from the 10:00 price to the close, and the real 0DTE put
results from journal/research/opendrive.json (SPY/QQQ/NVDA/TSLA puts bought at 10:00, 0.7% OTM;
exits take3 / hold / trail) joined by day.

Prices: Alpaca 30-minute bars (SIP, ending 20 minutes ago), 2024-02+. The 09:30 bar gives the
open and the 10:00 price, the 10:30 bar the 11:00 price, the last regular bar the close.

    python -m zoh.research.lockgate --cache DIR      # DIR keeps bars_<SYM>.json between runs
"""
import argparse
import json
import statistics as st
from datetime import date, datetime, time as dtime, timedelta, timezone
from pathlib import Path

from .. import journal
from ..alpaca import Alpaca
from ..strategy import ET

MEGA = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "AMD", "MU"]
INDEX = ["SPY", "QQQ", "SMH", "IWM", "VIXY"]
SECTORS = ["XLK", "XLF", "XLV", "XLP", "XLE", "XLY", "XLI", "XLU"]
SYMS = INDEX + MEGA + SECTORS
START = date(2024, 2, 1)
OUT = Path(__file__).resolve().parents[2] / "journal" / "research"
MIN_MOVE = 0.001   # SPY "below its open" means by at least 0.1% (OPENDRIVE's skip band)
VIX_UP = 0.03      # VIXY at least 3% above its own open at 10:00
BREADTH = 8        # of the 10 mega caps below their opens
OPEN_T, TEN30_T, CLOSE_T = dtime(9, 30), dtime(10, 30), dtime(16, 0)


def fetch(api, sym, cache, start=START, end=None):
    p = Path(cache) / f"bars_{sym}.json"
    if p.exists():
        return json.load(open(p))
    start = datetime.combine(start, dtime(8, 0), tzinfo=timezone.utc)
    end = (datetime.combine(end, dtime(23, 0), tzinfo=timezone.utc) if end
           else datetime.now(timezone.utc) - timedelta(minutes=20))
    bars = api.stock_bars(sym, start, end, timeframe="30Min", feed="sip")
    json.dump(bars, open(p, "w"))
    return bars


def day_points(bars):
    """{day: {"open", "p10", "p11", "close"}} from raw 30-minute bars (Alpaca JSON)."""
    days = {}
    for b in bars:
        t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
        if t.time() < OPEN_T or t.time() >= CLOSE_T:
            continue
        d = days.setdefault(t.date().isoformat(), {})
        if t.time() == OPEN_T:
            d["open"], d["p10"] = b["o"], b["c"]
        elif t.time() == TEN30_T:
            d["p11"] = b["c"]
        d["close"] = b["c"]  # last regular bar wins (half days close at 13:00)
    return {k: v for k, v in days.items() if "open" in v and "close" in v}


def ret10(points, sym, day):
    d = points.get(sym, {}).get(day)
    return d["p10"] / d["open"] - 1 if d and d.get("open") else None


def features(points, day):
    spy, vix = ret10(points, "SPY", day), ret10(points, "VIXY", day)
    mega = [ret10(points, s, day) for s in MEGA]
    mega = [m for m in mega if m is not None]
    sect = [ret10(points, s, day) for s in SECTORS]
    sect = [s for s in sect if s is not None]
    if spy is None or vix is None or len(mega) < BREADTH:
        return None
    return {"spy10": spy, "vix10": vix, "breadth": sum(1 for m in mega if m < 0), "n_mega": len(mega),
            "disp": st.pstdev(sect) if len(sect) >= 4 else None}


def classify(f):
    """Day class from the 10:00 features, in the order the gate was written."""
    if f["spy10"] > -MIN_MOVE:
        return "above_open"
    vix, wide = f["vix10"] >= VIX_UP, f["breadth"] >= BREADTH
    if vix and wide:
        return "lock"
    if vix:
        return "vix_only"
    if wide:
        return "breadth_only"
    return "below_open"


def outcome(points, sym, day, frm="p10"):
    d = points.get(sym, {}).get(day)
    return d["close"] / d[frm] - 1 if d and d.get(frm) else None


def build(points, macro):
    rows = []
    for day in sorted(points["SPY"]):
        if day < START.isoformat():
            continue
        f = features(points, day)
        if not f:
            continue
        rows.append({"day": day, "cls": classify(f), **f, "macro": ",".join(macro.get(day, [])),
                     "spy_oc10": outcome(points, "SPY", day), "qqq_oc10": outcome(points, "QQQ", day),
                     "smh_oc10": outcome(points, "SMH", day), "spy_oc": outcome(points, "SPY", day, "open"),
                     "spy_11_close": (outcome(points, "SPY", day, "p11")
                                      if points["SPY"][day].get("p11") else None)})
    return rows


def opendrive_puts():
    p = OUT / "opendrive.json"
    if not p.exists():
        return {}
    out = {}
    for r in json.load(open(p)):
        if r.get("kind") == "put" and r.get("exits_10"):
            out.setdefault(r["day"], []).append(r)
    return out


def periods(end):
    return [(f"since {START.isoformat()[:7]}", START.isoformat()), ("last year", (end - timedelta(days=365)).isoformat()),
            ("last 3 months", (end - timedelta(days=91)).isoformat())]


def avg(x):
    return sum(x) / len(x) if x else 0.0


def wo_best(x, k):
    return avg(sorted(x)[:-k]) if len(x) > k else 0.0


def pct(x):
    return f"{x:+.1%}"


def table_days(rows, end):
    lines = ["| class | period | days | SPY closed below 10:00 | SPY 10:00->close avg | median | QQQ avg | SMH avg | SMH down% | macro days |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for cls in ("lock", "vix_only", "breadth_only", "below_open", "above_open"):
        for label, start in periods(end):
            sel = [r for r in rows if r["cls"] == cls and r["day"] >= start and r["spy_oc10"] is not None]
            if not sel:
                continue
            spy = [r["spy_oc10"] for r in sel]
            qqq = [r["qqq_oc10"] for r in sel if r["qqq_oc10"] is not None]
            smh = [r["smh_oc10"] for r in sel if r["smh_oc10"] is not None]
            lines.append(f"| {cls} | {label} | {len(sel)} | {sum(1 for s in spy if s < 0) / len(spy):.0%} | "
                         f"{pct(avg(spy))} | {pct(st.median(spy))} | {pct(avg(qqq))} | {pct(avg(smh))} | "
                         f"{(sum(1 for s in smh if s < 0) / len(smh)) if smh else 0:.0%} | "
                         f"{sum(1 for r in sel if r['macro'])} |")
    return lines


def table_puts(rows, puts, end):
    cls_of = {r["day"]: r["cls"] for r in rows}
    lines = ["| class | underlying | period | trades | win% (take3) | take3 avg | w/o best | w/o best 2 | hold avg | trail avg | median hold |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    groups = [("SPY", {"SPY"}), ("QQQ", {"QQQ"}), ("NVDA+TSLA", {"NVDA", "TSLA"})]
    for cls in ("lock", "vix_only", "breadth_only", "below_open"):
        for gname, syms in groups:
            for label, start in periods(end):
                sel = [r for d, rs in puts.items() if cls_of.get(d) == cls and d >= start
                       for r in rs if r["sym"] in syms]
                if len(sel) < 3:
                    continue
                t3 = [r["exits_10"]["take3"] for r in sel]
                hold = [r["exits_10"]["hold"] for r in sel]
                trail = [r["exits_10"]["trail"] for r in sel]
                lines.append(f"| {cls} | {gname} | {label} | {len(sel)} | {sum(1 for x in t3 if x > 0) / len(t3):.0%} | "
                             f"{pct(avg(t3))} | {pct(wo_best(t3, 1))} | {pct(wo_best(t3, 2))} | {pct(avg(hold))} | "
                             f"{pct(avg(trail))} | {pct(st.median(hold))} |")
    return lines


def table_single_flags(rows, end):
    """Each flag on its own, among days with SPY below its open."""
    lines = ["| flag (SPY below open and ...) | period | days | SPY closed below 10:00 | SPY 10:00->close avg | SMH avg |",
             "|---|---|---|---|---|---|"]
    flags = [("VIXY >= +3%", lambda r: r["vix10"] >= VIX_UP), ("VIXY >= +5%", lambda r: r["vix10"] >= 0.05),
             ("breadth >= 8/10", lambda r: r["breadth"] >= BREADTH), ("breadth 10/10", lambda r: r["breadth"] >= 10),
             ("VIXY < 0 (fading)", lambda r: r["vix10"] < 0), ("SPY <= -1% at 10:00", lambda r: r["spy10"] <= -0.01),
             ("lock and SPY <= -1%", lambda r: r["cls"] == "lock" and r["spy10"] <= -0.01),
             ("lock, not a macro day", lambda r: r["cls"] == "lock" and not r["macro"])]
    for name, fn in flags:
        for label, start in periods(end):
            sel = [r for r in rows if r["spy10"] <= -MIN_MOVE and r["day"] >= start and fn(r)
                   and r["spy_oc10"] is not None]
            if not sel:
                continue
            spy = [r["spy_oc10"] for r in sel]
            smh = [r["smh_oc10"] for r in sel if r["smh_oc10"] is not None]
            lines.append(f"| {name} | {label} | {len(sel)} | {sum(1 for s in spy if s < 0) / len(spy):.0%} | "
                         f"{pct(avg(spy))} | {pct(avg(smh))} |")
    return lines


def report(rows, puts, end):
    lock = [r for r in rows if r["cls"] == "lock"]
    lines = ["# The lock gate: was 2026-11-05 knowable at 10:00?", "",
             "Gate (registered before the replay, SUNDAY_TESTS 45): at 10:00 ET SPY >= 0.1% below its open, VIXY >= 3% "
             "above its own open, and >= 8 of 10 mega caps (AAPL MSFT NVDA AMZN META GOOGL TSLA AVGO AMD MU) below "
             f"their opens. 30-minute bars (Alpaca SIP) from {START.isoformat()[:7]}; the 09:30 bar's close is the 10:00 price. "
             f"Data through {end}. {len(rows)} sessions, {len(lock)} lock days.", "",
             "## Index from 10:00 to the close, by day class", "", *table_days(rows, end), "",
             "## One flag at a time (days with SPY below its open at 10:00)", "", *table_single_flags(rows, end), "",
             "## Real 0DTE puts bought at 10:00 (OPENDRIVE rows, 0.7% OTM; data through 2026-10-15)", "",
             "take3 = sell at 3x else 15:30; hold = 15:30; trail = OPENDRIVE's trail. 'w/o best' drops the best trade.", "",
             *table_puts(rows, puts, end), "", "## Lock days, most recent first", "",
             "| day | macro | SPY 10:00 | VIXY 10:00 | breadth | SPY 10:00->close | SPY 11:00->close | QQQ | SMH |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(lock, key=lambda r: r["day"], reverse=True)[:40]:
        lines.append(f"| {r['day']} | {r['macro']} | {pct(r['spy10'])} | {pct(r['vix10'])} | {r['breadth']}/{r['n_mega']} | "
                     f"{pct(r['spy_oc10'])} | {pct(r['spy_11_close']) if r['spy_11_close'] is not None else ''} | "
                     f"{pct(r['qqq_oc10']) if r['qqq_oc10'] is not None else ''} | "
                     f"{pct(r['smh_oc10']) if r['smh_oc10'] is not None else ''} |")
    recent = [r for r in rows if r["day"] >= "2026-10-28"]
    lines += ["", "## The last sessions, classed", "", "| day | class | SPY 10:00 | VIXY 10:00 | breadth | SPY 10:00->close | SMH |",
              "|---|---|---|---|---|---|---|"]
    for r in recent:
        lines.append(f"| {r['day']} | {r['cls']} | {pct(r['spy10'])} | {pct(r['vix10'])} | {r['breadth']}/{r['n_mega']} | "
                     f"{pct(r['spy_oc10'])} | {pct(r['smh_oc10']) if r['smh_oc10'] is not None else ''} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(OUT / "cache_lockgate"))
    ap.add_argument("--start", default=None, help="first day (default 2024-02-01)")
    ap.add_argument("--end", default=None, help="last day (default now); with --start writes LOCKGATE_<suffix>")
    ap.add_argument("--suffix", default="", help="output name suffix, e.g. 2020_2023")
    args = ap.parse_args()
    Path(args.cache).mkdir(parents=True, exist_ok=True)
    api = Alpaca()
    global START
    if args.start:
        START = date.fromisoformat(args.start)  # the period tables and the row filter follow the run's start
    start = START
    stop = date.fromisoformat(args.end) if args.end else None
    points = {s: day_points(fetch(api, s, args.cache, start, stop)) for s in SYMS}
    macro = journal.load_events()
    rows = build(points, macro)
    puts = opendrive_puts()
    end = date.fromisoformat(rows[-1]["day"])
    sfx = f"_{args.suffix}" if args.suffix else ""
    (OUT / f"LOCKGATE{sfx}.md").write_text(report(rows, puts, end))
    json.dump(rows, open(OUT / f"lockgate{sfx}.json", "w"))
    print(f"{len(rows)} sessions, {sum(1 for r in rows if r['cls'] == 'lock')} lock days; wrote LOCKGATE.md")


if __name__ == "__main__":
    main()
