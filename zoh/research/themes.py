"""Theme turn flags on daily bars: how early does a theme's turn show, and what follows (2026-11-04).

Five flags per theme per day from Alpaca daily bars (closes and opens only, no option prices):
  REL_WEAK   theme 5-day return minus SPY's <= -3%
  DIVERGE    theme close <= 95% of its 20-day high while SPY is within 2% of its own
  BREADTH    at least half the members are > 10% below their own 20-day high
  RATIO_LOW  theme / SPY ratio at a 20-day low
  PERIPH     median 21-day return of the periphery minus the leaders' mean <= -8%
State: 'turning' with >= 3 flags; the heating mirror (REL_STRONG, AT_HIGH, BREADTH_UP, RATIO_HIGH,
PERIPH_UP) gives 'heating' with >= 3; otherwise 'neutral'. The theme index is the equal-weight
basket of its members (open and close chained from member returns), so every theme is measured the
same way whether or not an ETF exists. The state used for a day is the one known at the prior close.

Tests: forward 5/10/20-day theme return minus SPY by state and from the first turning day; each
turning episode's continuation (another -5%) vs recovery (back to the fire-day 20-day high) within
20 sessions; open->close of theme gap-up and gap-down days by state (the sell-the-news / failed-bounce
base rate without minute data) and of the members on those days; our own trades on theme members
by state. The option layer for chips is journal/research/BOUNCE.md (14 events, costs 10% each way).

    python -m zoh.research.themes [--years 2] [--today] [--from-json]
"""
import argparse
import csv
import json
import re
import statistics as st
from datetime import datetime, timedelta, timezone

from .. import journal
from ..alpaca import Alpaca
from ..runup import daily

OUT = journal.ROOT / "journal" / "research"
# leaders first (two), then the periphery
THEMES = {
    "chips": ["NVDA", "AVGO", "AMD", "MU", "INTC", "MRVL", "ARM", "LRCX", "TSM", "ASML", "AMAT", "KLAC"],
    "internet": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NFLX"],
    "software": ["ORCL", "CRM", "NOW", "ADBE", "PLTR", "INTU"],
    "banks": ["JPM", "GS", "BAC", "MS", "C", "WFC"],
    "health": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "PFE"],
    "energy": ["XOM", "CVX", "COP", "SLB", "EOG", "OXY"],
    "consumer": ["WMT", "COST", "HD", "MCD", "NKE", "LOW", "TJX"],
    "industrials": ["GE", "CAT", "HON", "UNP", "DE", "RTX"],
    "power": ["GEV", "VST", "CEG", "NRG", "ETN", "PWR"],
    "optical": ["LITE", "CIEN", "COHR", "ANET"],
}
LEADERS = 2
LOOK, MONTH, WEEK = 20, 21, 5
REL, OFF_HIGH, BREADTH_OFF, PERIPH_GAP = 0.03, 0.05, 0.10, 0.08
NEAR_HIGH = 0.03
MIN_FLAGS, QUIET, GAP, FWD = 3, 10, 0.007, (5, 10, 20)
TURN = ("REL_WEAK", "DIVERGE", "BREADTH", "RATIO_LOW", "PERIPH")
HEAT = ("REL_STRONG", "AT_HIGH", "BREADTH_UP", "RATIO_HIGH", "PERIPH_UP")


def basket(days, members):
    """Equal-weight theme index: [(day, open, close)] chained from the members' daily returns."""
    out, level = [], 100.0
    prev = None
    for d in days:
        rets, gaps = [], []
        for m in members:
            if prev and d in m and prev in m:
                rets.append(m[d][1] / m[prev][1] - 1)
                gaps.append(m[d][0] / m[prev][1] - 1)
        if prev is None:
            out.append((d, level, level))
        elif rets:
            out.append((d, level * (1 + st.mean(gaps)), level * (1 + st.mean(rets))))
            level = out[-1][2]
        else:
            out.append((d, level, level))
        prev = d
    return out


def flags(theme, spy, members, days, i):
    """Turn and heat flags for day index i (needs i >= MONTH)."""
    c = [x[2] for x in theme]
    s = [x[2] for x in spy]
    hi = max(c[i - LOOK + 1:i + 1])
    shi = max(s[i - LOOK + 1:i + 1])
    ratio = [c[j] / s[j] for j in range(i - LOOK + 1, i + 1)]
    rel = (c[i] / c[i - WEEK] - 1) - (s[i] / s[i - WEEK] - 1)
    off, near, n = 0, 0, 0
    mret = {}
    for k, m in enumerate(members):
        d, d0, dm = days[i], days[i - LOOK + 1], days[i - MONTH]
        closes = [m[x][1] for x in days[i - LOOK + 1:i + 1] if x in m]
        if d in m and len(closes) >= LOOK // 2:
            n += 1
            mh = max(closes)
            off += m[d][1] / mh - 1 < -BREADTH_OFF
            near += m[d][1] / mh - 1 > -NEAR_HIGH
        if d in m and dm in m:
            mret[k] = m[d][1] / m[dm][1] - 1
    lead = [mret[k] for k in range(LEADERS) if k in mret]
    peri = [mret[k] for k in range(LEADERS, len(members)) if k in mret]
    gap = (st.median(peri) - st.mean(lead)) if lead and peri else 0.0
    turn = {"REL_WEAK": rel <= -REL,
            "DIVERGE": c[i] / hi - 1 <= -OFF_HIGH and s[i] / shi - 1 > -0.02,
            "BREADTH": n > 0 and off >= n / 2,
            "RATIO_LOW": ratio[-1] <= min(ratio),
            "PERIPH": gap <= -PERIPH_GAP}
    heat = {"REL_STRONG": rel >= REL,
            "AT_HIGH": c[i] >= hi,
            "BREADTH_UP": n > 0 and near >= n / 2,
            "RATIO_HIGH": ratio[-1] >= max(ratio),
            "PERIPH_UP": gap >= PERIPH_GAP}
    return turn, heat


def state_of(turn, heat):
    if sum(turn.values()) >= MIN_FLAGS:
        return "turning"
    if sum(heat.values()) >= MIN_FLAGS:
        return "heating"
    return "neutral"


def episodes(states):
    """Indexes where 'turning' starts after >= QUIET days without it."""
    out, quiet = [], QUIET
    for i, s in enumerate(states):
        if s == "turning":
            if quiet >= QUIET:
                out.append(i)
            quiet = 0
        else:
            quiet += 1
    return out


def classify(theme, i, hi20):
    """'continued' if the basket falls another 5% below the fire-day close before reclaiming the
    fire-day 20-day high within 20 sessions, 'recovered' if the reverse, else 'neither'."""
    c0 = theme[i][2]
    for j in range(i + 1, min(i + LOOK + 1, len(theme))):
        if theme[j][2] <= c0 * 0.95:
            return "continued"
        if theme[j][2] >= hi20:
            return "recovered"
    return "neither"


def series(theme, spy, members, days):
    """Per-day rows: state (known at that close), flags, basket gap and open->close, forward excess."""
    rows = []
    for i in range(MONTH, len(days)):
        turn, heat = flags(theme, spy, members, days, i)
        c = theme[i][2]
        fwd = {}
        for k in FWD:
            if i + k < len(days):
                fwd[k] = (theme[i + k][2] / c - 1) - (spy[i + k][2] / spy[i][2] - 1)
        rows.append({"i": i, "day": days[i].isoformat(), "state": state_of(turn, heat),
                     "turn": [k for k, v in turn.items() if v], "heat": [k for k, v in heat.items() if v],
                     "gap": theme[i][1] / theme[i - 1][2] - 1, "oc": theme[i][2] / theme[i][1] - 1,
                     "fwd": fwd, "hi20": max(x[2] for x in theme[i - LOOK + 1:i + 1]),
                     "off_high": c / max(x[2] for x in theme[i - LOOK + 1:i + 1]) - 1})
    return rows


def study(api, years):
    end = datetime.now(timezone.utc) - timedelta(days=1)
    start = end - timedelta(days=365 * years + 45)
    syms = sorted({s for v in THEMES.values() for s in v} | {"SPY"})
    bars = daily(api, syms, start, end)
    spy = bars["SPY"]
    days = [d for d, _, _ in spy]
    out = {"days": [d.isoformat() for d in days], "themes": {}}
    for name, syms in THEMES.items():
        members = [{d: (o, c) for d, o, c in bars.get(s, [])} for s in syms]
        idx = basket(days, members)
        rows = series(idx, spy, members, days)
        states = [r["state"] for r in rows]
        eps = []
        for e in episodes(states):
            r = rows[e]
            eps.append({"day": r["day"], "flags": r["turn"], "result": classify(idx, r["i"], r["hi20"]),
                        "fwd20": r["fwd"].get(20), "pre": r["i"]})
        # member open->close on basket gap days
        for r in rows:
            i = r["i"]
            r["members_oc"] = [m[days[i]][1] / m[days[i]][0] - 1 for m in members if days[i] in m and m[days[i]][0]]
        out["themes"][name] = {"rows": rows, "episodes": eps,
                               "today": {"day": rows[-1]["day"], "state": rows[-1]["state"],
                                         "turn": rows[-1]["turn"], "heat": rows[-1]["heat"]}}
        print(f"{name:12s} {rows[-1]['day']} {rows[-1]['state']:8s} turn={rows[-1]['turn']} heat={rows[-1]['heat']} "
              f"episodes={len(eps)}", flush=True)
    return out


def trades_by_state(data):
    """Our own trades (journal/trades.csv, real and shadow) on theme members, by the state at entry."""
    sym_theme = {s: t for t, v in THEMES.items() for s in v}
    by_day = {t: {r["day"]: r["state"] for r in v["rows"]} for t, v in data["themes"].items()}
    days = data["days"]
    out = {}
    try:
        rows = list(csv.DictReader(open(journal.ROOT / "journal" / "trades.csv")))
    except OSError:
        return out
    for r in rows:
        m = re.match(r"([A-Z]+)\d{6}[CP]", r.get("contract", ""))
        if not m or m.group(1) not in sym_theme:
            continue
        t = sym_theme[m.group(1)]
        prev = [d for d in days if d < r["date"]]
        if not prev:
            continue
        s = by_day[t].get(prev[-1], "neutral")
        try:
            out.setdefault((r["direction"], s), []).append((float(r["pnl_pct"]), float(r.get("pnl") or 0), r.get("mode", "")))
        except (TypeError, ValueError):
            continue
    return out


def fmt(xs, pct=True):
    if not xs:
        return "- | - | - | -"
    return (f"{len(xs)} | {st.mean(xs):+.2%} | {st.median(xs):+.2%} | {sum(x > 0 for x in xs) / len(xs):.0%}")


def report(data, years):
    end = datetime.fromisoformat(data["days"][-1]).date()
    win = lambda d, n: datetime.fromisoformat(d).date() >= end - timedelta(days=n)
    L = [f"# Theme turn flags on daily bars", "",
         f"{len(THEMES)} themes, {years} years of Alpaca daily bars to {end}. Theme = equal-weight basket of its members; "
         f"five turn flags and five heat flags per day (see zoh/research/themes.py); state 'turning' / 'heating' with >= 3, "
         f"used from the next session. Stock moves only, no option prices and no costs: these are forecast tests. "
         f"Columns: n | mean | median | % positive.", ""]
    # today
    L += ["## State at the last close", "", "| theme | state | turn flags | heat flags |", "|---|---|---|---|"]
    for t, v in data["themes"].items():
        td = v["today"]
        L.append(f"| {t} | {td['state']} | {', '.join(td['turn']) or '-'} | {', '.join(td['heat']) or '-'} |")
    # forward returns by state
    for title, n in (("last 3 months", 92), ("1 year", 365), ("all", 100000)):
        L += ["", f"## Forward theme return minus SPY, by state ({title})", "",
              "| theme | state | days | 5d | 10d | 20d |", "|---|---|---|---|---|---|"]
        pooled = {}
        for t, v in data["themes"].items():
            by = {}
            for r in v["rows"]:
                if win(r["day"], n):
                    by.setdefault(r["state"], []).append(r["fwd"])
                    pooled.setdefault(r["state"], []).append(r["fwd"])
            for s in ("turning", "neutral", "heating"):
                fs = by.get(s, [])
                if not fs:
                    continue
                cells = [f"{st.mean([f[k] for f in fs if k in f]):+.2%} ({sum(f[k] > 0 for f in fs if k in f) / max(1, len([f for f in fs if k in f])):.0%})"
                         if any(k in f for f in fs) else "-" for k in FWD]
                L.append(f"| {t} | {s} | {len(fs)} | " + " | ".join(cells) + " |")
        for s in ("turning", "neutral", "heating"):
            fs = pooled.get(s, [])
            if not fs:
                continue
            cells = [f"{st.mean([f[k] for f in fs if k in f]):+.2%} ({sum(f[k] > 0 for f in fs if k in f) / max(1, len([f for f in fs if k in f])):.0%})"
                     if any(k in f for f in fs) else "-" for k in FWD]
            L.append(f"| **all** | {s} | {len(fs)} | " + " | ".join(cells) + " |")
    # episodes
    L += ["", "## Turning episodes (first day with >= 3 flags after 10 quiet sessions)", "",
          "Result within 20 sessions: 'continued' = basket fell another 5% first, 'recovered' = reclaimed the fire-day 20-day high first.", "",
          "| theme | fired | flags | result | 20d vs SPY |", "|---|---|---|---|---|"]
    tally = {}
    for t, v in data["themes"].items():
        for e in v["episodes"]:
            tally[e["result"]] = tally.get(e["result"], 0) + 1
            f20 = f"{e['fwd20']:+.1%}" if e["fwd20"] is not None else "open"
            L.append(f"| {t} | {e['day']} | {', '.join(e['flags'])} | {e['result']} | {f20} |")
    L.append("")
    L.append("Tally: " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())) + ".")
    # gap days by state
    for title, n in (("last 3 months", 92), ("1 year", 365), ("all", 100000)):
        L += ["", f"## Basket gap days, open -> close by prior-close state ({title})", "",
              f"Gap up = basket opens >= +{GAP:.1%} vs the prior close (the bounce / good-news day); gap down <= -{GAP:.1%}. "
              f"Members = each member's own open->close on those days.", "",
              "| gap | state | basket n | mean | median | % up | members n | mean | median | % up |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for gname, test in (("up", lambda g: g >= GAP), ("down", lambda g: g <= -GAP)):
            for s in ("turning", "neutral", "heating"):
                b, m = [], []
                for t, v in data["themes"].items():
                    prev = None
                    for r in v["rows"]:
                        if prev and prev["state"] == s and test(r["gap"]) and win(r["day"], n):
                            b.append(r["oc"])
                            m.extend(r["members_oc"])
                        prev = r
                L.append(f"| {gname} | {s} | {fmt(b)} | {fmt(m)} |")
    # chips detail
    L += ["", "## Chips: the flags this autumn", "", "| day | state | turn flags | basket vs 20d high |", "|---|---|---|---|"]
    for r in data["themes"]["chips"]["rows"]:
        if win(r["day"], 60) and (r["turn"] or r["state"] != "neutral"):
            L.append(f"| {r['day']} | {r['state']} | {', '.join(r['turn']) or '-'} | {r['off_high']:+.1%} |")
    # our trades
    tb = trades_by_state(data)
    if tb:
        L += ["", "## Our trades on theme members (journal/trades.csv), by the theme's state at entry", "",
              "pnl % per trade on the contract; $ = summed real-paper P&L of the real fills among them.", "",
              "| direction | state | n (real) | mean pnl % | median | % positive | real $ |", "|---|---|---|---|---|---|---|"]
        for (d, s), xs in sorted(tb.items()):
            p = [x[0] for x in xs]
            real = [x for x in xs if x[2] == "real"]
            L.append(f"| {d} | {s} | {len(xs)} ({len(real)}) | {st.mean(p):+.0%} | {st.median(p):+.0%} | "
                     f"{sum(x > 0 for x in p) / len(p):.0%} | {sum(x[1] for x in real):+.0f} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=2)
    ap.add_argument("--from-json", action="store_true")
    ap.add_argument("--today", action="store_true", help="print the state table only")
    a = ap.parse_args()
    if a.from_json:
        data = json.loads((OUT / "themes.json").read_text())
    else:
        data = study(Alpaca(), a.years if not a.today else 1)
    if a.today:
        for t, v in data["themes"].items():
            td = v["today"]
            print(f"{t:12s} {td['state']:8s} turn={','.join(td['turn']) or '-'} heat={','.join(td['heat']) or '-'}")
        return
    slim = {"days": data["days"], "themes": {t: {"rows": [{k: r[k] for k in ("day", "state", "turn", "heat", "gap", "oc", "fwd", "members_oc", "off_high")} for r in v["rows"]],
                                                "episodes": v["episodes"], "today": v["today"]} for t, v in data["themes"].items()}}
    (OUT / "themes.json").write_text(json.dumps(slim, separators=(",", ":")) + "\n")
    text = report(data, a.years)
    (OUT / "THEMES.md").write_text(text)
    print(text[:7000])


if __name__ == "__main__":
    main()
