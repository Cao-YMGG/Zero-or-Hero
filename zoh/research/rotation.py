"""Opportunity tests on daily bars (2026-10-29): sell the news by theme state, rotation laggard.

python -m zoh.research.rotation fetch daily.json   # two years of daily bars (Alpaca SIP)
python -m zoh.research.rotation analyze daily.json # prints the tables in journal/research/OPPORTUNITY_TESTS.md
"""
import json
import statistics as st
import sys
from datetime import datetime, timezone

from ..alpaca import Alpaca


def fetch(path):
    from zoh.alpaca import Alpaca
    GROUPS = {
     "internet": ["META", "GOOGL", "MSFT", "AMZN", "AAPL", "NFLX"],
     "chips": ["NVDA", "AMD", "AVGO", "MU", "INTC", "AMAT", "LRCX", "QCOM", "ARM", "TSM"],
     "software": ["ORCL", "CRM", "NOW", "PLTR", "ADBE", "INTU"],
     "fin": ["V", "MA", "JPM", "GS", "BAC", "AXP"],
     "health": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "PFE"],
     "staples": ["WMT", "COST", "PG", "KO", "PEP"],
     "energy": ["XOM", "CVX", "COP"],
     "industrial": ["CAT", "GE", "GEV", "HON", "BA"],
     "consumer": ["TSLA", "HD", "MCD", "NKE", "SBUX"],
    }
    ETF = {"internet": "XLC", "chips": "SMH", "software": "IGV", "fin": "XLF", "health": "XLV",
           "staples": "XLP", "energy": "XLE", "industrial": "XLI", "consumer": "XLY"}
    syms = sorted({s for g in GROUPS.values() for s in g} | set(ETF.values()) | {"SPY", "QQQ", "IWM"})
    api = Alpaca()
    bars = api.daily_bars_multi(syms, datetime(2024, 9, 1, tzinfo=timezone.utc), datetime(2026, 10, 29, tzinfo=timezone.utc))
    json.dump({"groups": GROUPS, "etf": ETF, "bars": bars}, open(path, "w"))
    print({s: len(b) for s, b in bars.items()})


def analyze(path):
    D = json.load(open(path))
    G, ETF, B = D["groups"], D["etf"], D["bars"]
    RECENT = "2026-07-29"
    bars = {s: {b["t"][:10]: b for b in v} for s, v in B.items()}
    days = sorted(bars["SPY"])
    idx = {d: i for i, d in enumerate(days)}
    group_of = {s: g for g, ms in G.items() for s in ms}
    def px(s, i, k):
        b = bars[s].get(days[i]) if 0 <= i < len(days) else None
        return b[k] if b else None
    def ret(s, i, n):  # close i / close i-n - 1
        a, b = px(s, i, "c"), px(s, i - n, "c")
        return a / b - 1 if a and b else None
    def gap(s, i):
        o, c = px(s, i, "o"), px(s, i - 1, "c")
        return o / c - 1 if o and c else None
    def oc(s, i):
        o, c = px(s, i, "o"), px(s, i, "c")
        return c / o - 1 if o and c else None
    def nxt(s, i):
        return ret(s, i + 1, 1) if i + 1 < len(days) else None
    def stats(xs):
        xs = [x for x in xs if x is not None]
        if not xs: return "n=0"
        s = sorted(xs)
        wo1 = st.mean(s[:-1]) if len(s) > 1 else float("nan")
        wo2 = st.mean(s[:-2]) if len(s) > 2 else float("nan")
        return (f"n={len(xs):3d} avg {st.mean(xs):+.2%} med {st.median(xs):+.2%} up {sum(x>0 for x in xs)/len(xs):.0%}"
                f" | w/o best {wo1:+.2%} w/o 2 {wo2:+.2%}")
    def report(name, rows):
        """rows: list of (date, value)"""
        print(f"  {name}")
        print(f"    all   : {stats([v for d, v in rows])}")
        print(f"    3 mo  : {stats([v for d, v in rows if d >= RECENT])}")
    
    stocks = [s for s in group_of]
    print("=== H2: good-news gap up, follow from the open, by theme state (sector ETF 21d minus SPY 21d) ===")
    for gmin, label in ((0.02, "gap >= 2%"), (0.03, "gap >= 3%")):
        rows = {"heating (>+2%)": [], "neutral": [], "cooling (<-2%)": []}
        nrows = {"heating (>+2%)": [], "neutral": [], "cooling (<-2%)": []}
        for s in stocks:
            e = ETF[group_of[s]]
            for i in range(23, len(days)):
                g = gap(s, i)
                if g is None or g < gmin: continue
                t1, t2 = ret(e, i - 1, 21), ret("SPY", i - 1, 21)
                if t1 is None or t2 is None: continue
                th = t1 - t2
                k = "heating (>+2%)" if th > 0.02 else "cooling (<-2%)" if th < -0.02 else "neutral"
                rows[k].append((days[i], oc(s, i)))
                nrows[k].append((days[i], nxt(s, i)))
        print(f"-- {label}: open->close (long)")
        for k in rows: report(k, rows[k])
        print(f"-- {label}: next day close->close")
        for k in nrows: report(k, nrows[k])
    
    print()
    print("=== H2b: gap up >= 2% split by 10-day run-up before it ===")
    rows = {"ran up > 5%": [], "flat": [], "fell > 5%": []}
    for s in stocks:
        for i in range(23, len(days)):
            g = gap(s, i)
            if g is None or g < 0.02: continue
            r = ret(s, i - 1, 10)
            if r is None: continue
            k = "ran up > 5%" if r > 0.05 else "fell > 5%" if r < -0.05 else "flat"
            rows[k].append((days[i], oc(s, i)))
    for k in rows: report(k, rows[k])
    
    print()
    print("=== H1: rotation laggard. Shock = a stock in internet/software/chips gaps down <= -5% while SPY gap > -1% ===")
    lag, others, lag_all = [], [], []
    events = []
    for i in range(23, len(days)):
        sg = gap("SPY", i)
        if sg is None or sg <= -0.01: continue
        for g in ("internet", "software", "chips"):
            shocked = [s for s in G[g] if (gap(s, i) or 0) <= -0.05]
            if not shocked: continue
            cands = [s for s in G[g] if s not in shocked and ret(s, i - 1, 21) is not None]
            if not cands: continue
            lg = min(cands, key=lambda s: ret(s, i - 1, 21))
            if (gap(lg, i) or -1) >= 0:
                lag.append((days[i], oc(lg, i)))
                events.append((days[i], g, ",".join(shocked), lg, round(ret(lg, i - 1, 21) * 100, 1), round(oc(lg, i) * 100, 2), round((nxt(lg, i) or 0) * 100, 2)))
            for s in cands:
                if (gap(s, i) or -1) >= 0 and s != lg:
                    others.append((days[i], oc(s, i)))
    report("laggard of the shocked group (worst 21d, green at the open): open->close", lag)
    report("other green members of that group same day: open->close", others)
    # baseline: group laggard (green at open) on every day
    for i in range(23, len(days)):
        for g in ("internet", "software", "chips"):
            cands = [s for s in G[g] if ret(s, i - 1, 21) is not None]
            lg = min(cands, key=lambda s: ret(s, i - 1, 21))
            if (gap(lg, i) or -1) >= 0:
                lag_all.append((days[i], oc(lg, i)))
    report("baseline: group laggard green at open, every day", lag_all)
    print("  events (date, group, shocked, laggard, its 21d %, open->close %, next day %):")
    for e in events[-25:]: print("   ", e)
    
    print()
    print("=== H1b: chip selloff day (chip basket gap <= -1.5%, SPY gap > -0.7%) -> internet laggard green at open ===")
    lag2 = []
    for i in range(23, len(days)):
        sg = gap("SPY", i)
        cg = [gap(s, i) for s in G["chips"] if gap(s, i) is not None]
        if sg is None or sg <= -0.007 or not cg or st.mean(cg) > -0.015: continue
        cands = [s for s in G["internet"] if ret(s, i - 1, 21) is not None]
        lg = min(cands, key=lambda s: ret(s, i - 1, 21))
        if (gap(lg, i) or -1) >= 0:
            lag2.append((days[i], oc(lg, i)))
            print("   ", days[i], lg, f"21d {ret(lg, i-1, 21):+.1%}", f"o->c {oc(lg, i):+.2%}", f"next {(nxt(lg, i) or 0):+.2%}")
    report("internet laggard on chip-selloff days: open->close", lag2)


if __name__ == "__main__":
    {"fetch": fetch, "analyze": analyze}[sys.argv[1]](sys.argv[2])
