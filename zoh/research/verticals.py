"""Two-month call debit verticals by theme state (the owner's live structure) on Alpaca option daily bars.

Entry rules, on each theme's instruments (its ETF where one exists plus its two leaders):
  dip    the 20th session after a turning episode fires (zoh/research/themes.py): the bottom-fish, late
  fire   the turning fire day itself: the bottom-fish, early
  heat   the first day of a heating state after >= 10 sessions without one: the trend entry
  base   every 25th session of every instrument: the control
Structure: call debit vertical on the monthly expiry nearest 60 calendar days out (45-75 days); long strike =
the first strike at or above the close, short strike = the listed strike nearest close * (1 + 0.67 * sigma *
sqrt(T)) (about 0.25 delta; sigma = 20-day realized volatility). Priced at the legs' daily closes with 5% of
each leg's price each way; spreads costing more than 60% of their width are skipped. Exit: the first close where
the spread has earned half of its maximum profit (value >= debit + 0.5 * (width - debit)), else after 30 sessions,
else the last close at least 7 calendar days before expiry. Returns are on the debit paid.

    python -m zoh.research.verticals [--years 2] [--from-json]
"""
import argparse
import json
import math
import pickle
import statistics as st
import time
from datetime import date, datetime, timedelta, timezone

from .. import journal
from ..alpaca import DATA_URL, Alpaca, AlpacaError
from ..realopt import occ, strike_grid
from ..runup import daily
from ..strategy import ET
from . import themes
from .snipers import stats

OUT = journal.ROOT / "journal" / "research"
INSTR = {"chips": ["SMH", "NVDA", "AVGO"], "internet": ["QQQ", "AAPL", "MSFT"], "software": ["IGV", "ORCL", "CRM"],
         "banks": ["XLF", "JPM", "GS"], "health": ["XLV", "LLY", "UNH"], "energy": ["XLE", "XOM", "CVX"],
         "consumer": ["XLY", "WMT", "COST"], "industrials": ["XLI", "GE", "CAT"], "power": ["GEV", "VST"],
         "optical": ["LITE", "CIEN"]}
ETFS = {"SMH", "QQQ", "IGV", "XLF", "XLV", "XLE", "XLY", "XLI"}
TARGET, LO, HI = 60, 45, 75
DIP_AFTER, HEAT_QUIET, BASE_EVERY = 20, 10, 25
HOLD, TAKE, COST, BEFORE_EXPIRY, MAX_DEBIT = 30, 0.5, 0.05, 7, 0.6
RULES = ("dip", "fire", "heat", "base")


def third_friday(y, m):
    d = date(y, m, 15)
    while d.weekday() != 4:
        d += timedelta(days=1)
    return d


def expiry_near(day, target=TARGET, lo=LO, hi=HI):
    cands = []
    for k in range(4):
        y, m = day.year + (day.month - 1 + k) // 12, (day.month - 1 + k) % 12 + 1
        e = third_friday(y, m)
        if lo <= (e - day).days <= hi:
            cands.append(e)
    return min(cands, key=lambda e: abs((e - day).days - target)) if cands else None


def legs(spot, sigma, years, strikes):
    """(long, short) strikes: first at/above spot, then the nearest to the ~0.25-delta level."""
    longs = [k for k in strikes if k >= spot]
    if not longs:
        return None
    kl = min(longs)
    target = spot * (1 + 0.67 * sigma * math.sqrt(max(years, 1e-6)))
    shorts = [k for k in strikes if k > kl]
    if not shorts:
        return None
    return kl, min(shorts, key=lambda k: abs(k - target))


def run(long_path, short_path, width, entry_day, expiry, hold=HOLD, take=TAKE, cost=COST):
    """Spread bought at entry_day's closes; returns (return on debit, debit, exit day, reason, peak) or None."""
    if entry_day not in long_path or entry_day not in short_path:
        return None
    debit = long_path[entry_day] * (1 + cost) - short_path[entry_day] * (1 - cost)
    if debit <= 0.05 or debit > MAX_DEBIT * width:
        return None
    target = debit + take * (width - debit)
    last_ok = expiry - timedelta(days=BEFORE_EXPIRY)
    peak, exit_v, exit_d, reason = 0.0, None, None, None
    later = sorted(d for d in long_path if d in short_path and d > entry_day)
    for n, d in enumerate(later, 1):
        v = long_path[d] * (1 - cost) - short_path[d] * (1 + cost)
        peak = max(peak, v)
        if v >= target:
            exit_v, exit_d, reason = v, d, "target"
            break
        if n >= hold:
            exit_v, exit_d, reason = v, d, "time"
            break
        if d >= last_ok:
            exit_v, exit_d, reason = v, d, "expiry"
            break
    if exit_d is None:
        if not later:
            return None
        d = later[-1]
        exit_v, exit_d, reason = long_path[d] * (1 - cost) - short_path[d] * (1 + cost), d, "open"
    return {"ret": exit_v / debit - 1, "debit": round(debit, 3), "debit_pct": round(debit / width, 3), "exit": exit_d.isoformat(),
            "reason": reason, "peak": round(peak / debit, 3), "width_pct": round(exit_v / width, 3),
            "held": len([d for d in later if d <= exit_d])}


def option_daily(api, symbols, start, end):
    """{contract: {date: close}} from Alpaca option daily bars."""
    out = {}
    for j in range(0, len(symbols), 100):
        params = {"symbols": ",".join(symbols[j:j + 100]), "timeframe": "1Day",
                  "start": start.isoformat(), "end": end.isoformat(), "limit": 10000}
        while True:
            page = api._request("GET", f"{DATA_URL}/v1beta1/options/bars", params) or {}
            for s, bars in (page.get("bars") or {}).items():
                for b in bars:
                    d = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date()
                    out.setdefault(s, {})[d] = b["c"]
            token = page.get("next_page_token")
            if not token:
                break
            params["page_token"] = token
    return out


def realized_vol(closes, i, n=20):
    xs = [math.log(closes[k] / closes[k - 1]) for k in range(max(1, i - n + 1), i + 1) if closes[k - 1] > 0]
    return (st.pstdev(xs) * math.sqrt(252)) if len(xs) >= 5 else 0.4


def heat_starts(states):
    out, quiet = [], HEAT_QUIET
    for i, s in enumerate(states):
        if s == "heating":
            if quiet >= HEAT_QUIET:
                out.append(i)
            quiet = 0
        else:
            quiet += 1
    return out


def entries(data):
    """[(rule, theme, day_index)] from the theme study."""
    out = []
    for t, v in data["themes"].items():
        rows = v["rows"]
        offset = rows[0]["i"]  # rows start at index MONTH of days
        states = [r["state"] for r in rows]
        for e in v["episodes"]:
            out.append(("fire", t, e["pre"]))
            out.append(("dip", t, e["pre"] + DIP_AFTER))
        for j in heat_starts(states):
            out.append(("heat", t, j + offset))
        for i in range(offset + 10, len(data["days"]), BASE_EVERY):
            out.append(("base", t, i))
    return out


def price_entry(api, sym, day, closes, i, cache):
    spot = closes[i]
    expiry = expiry_near(day)
    if not expiry or spot <= 0:
        return None
    years = (expiry - day).days / 365
    sigma = realized_vol(closes, i)
    grid = strike_grid(spot, "call", reach=0.35)
    key = (sym, expiry.isoformat(), day.isoformat())
    if key not in cache:
        syms = [occ(sym, expiry, k) for k in grid]
        try:
            cache[key] = option_daily(api, syms, day, expiry)
        except AlpacaError:
            cache[key] = {}
    bars = cache[key]
    by_strike = {k: bars.get(occ(sym, expiry, k)) for k in grid}
    avail = [k for k, p in by_strike.items() if p and day in p and p[day] > 0]
    lg = legs(spot, sigma, years, avail)
    if not lg:
        return None
    kl, ks = lg
    r = run(by_strike[kl], by_strike[ks], ks - kl, day, expiry)
    if not r:
        return None
    r.update({"sym": sym, "day": day.isoformat(), "expiry": expiry.isoformat(), "spot": round(spot, 2),
              "long": kl, "short": ks, "sigma": round(sigma, 3)})
    return r


def study(api, years, cache_path=None):
    data = themes.study(api, years)
    days = [date.fromisoformat(d) for d in data["days"]]
    syms = sorted({s for v in INSTR.values() for s in v})
    end = datetime.now(timezone.utc) - timedelta(days=1)
    bars = daily(api, syms, end - timedelta(days=365 * years + 45), end)
    closes = {}
    for s in syms:
        by = {d: c for d, _, c in bars.get(s, [])}
        closes[s] = [by.get(d, 0.0) for d in days]
        for k in range(1, len(days)):  # carry a missing close forward
            if closes[s][k] == 0.0:
                closes[s][k] = closes[s][k - 1]
    cache = {}
    if cache_path and cache_path.exists():
        cache = pickle.loads(cache_path.read_bytes())
    rows, seen = [], set()
    todo = entries(data)
    print(f"{len(todo)} entries", flush=True)
    for n, (rule, t, i) in enumerate(todo):
        if i >= len(days) - 1:
            continue
        for sym in INSTR[t]:
            if (rule, sym, i) in seen or closes[sym][i] <= 0:
                continue
            seen.add((rule, sym, i))
            r = price_entry(api, sym, days[i], closes[sym], i, cache)
            if r:
                r.update({"rule": rule, "theme": t})
                rows.append(r)
        if n % 50 == 0:
            print(f"{n}/{len(todo)} {rule} {t} {days[i]} rows={len(rows)}", flush=True)
            if cache_path:
                cache_path.write_bytes(pickle.dumps(cache))
            time.sleep(0.2)
    if cache_path:
        cache_path.write_bytes(pickle.dumps(cache))
    return rows


def window(rows, days, end):
    return [r for r in rows if date.fromisoformat(r["day"]) >= end - timedelta(days=days)]


def table(L, rows, title):
    L += ["", f"## {title}", "", "| rule | n | win% | avg | -best | -best2 | median | debit % of width | target / time / expiry | days held |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for rule in RULES:
        xs = [r for r in rows if r["rule"] == rule and r["reason"] != "open"]
        if not xs:
            continue
        rets = [r["ret"] for r in xs]
        reasons = {k: sum(r["reason"] == k for r in xs) for k in ("target", "time", "expiry")}
        L.append(f"| {rule} | {stats(rets)} | {st.median(rets):+.0%} | {st.mean(r['debit_pct'] for r in xs):.0%} | "
                 f"{reasons['target']} / {reasons['time']} / {reasons['expiry']} | {st.mean(r['held'] for r in xs):.0f} |")


def report(rows, years):
    end = max(date.fromisoformat(r["day"]) for r in rows) if rows else date.today()
    closed = [r for r in rows if r["reason"] != "open"]
    L = [f"# Two-month call debit verticals by theme state", "",
         f"{len(rows)} spreads ({len(closed)} closed) on {sum(len(v) for v in INSTR.values())} instruments, {years} years of Alpaca "
         f"option daily bars, costs 5% of each leg's price each way. Rules, structure and exits in zoh/research/verticals.py. "
         f"Columns: n | win% | avg return on debit | without the best | without the best two | median | average debit as % of "
         f"width | exit reasons | sessions held.", ""]
    table(L, closed, "All instruments, all entries")
    table(L, window(closed, 365, end), "All instruments, entries in the last year")
    table(L, window(closed, 183, end), "All instruments, entries in the last 6 months")
    table(L, [r for r in closed if r["sym"] in ETFS], "ETFs only")
    table(L, [r for r in closed if r["sym"] not in ETFS], "Single names only")
    table(L, [r for r in closed if r["theme"] == "chips"], "Chips (SMH, NVDA, AVGO)")
    table(L, [r for r in closed if r["theme"] in ("banks", "health", "energy", "consumer", "industrials")], "Non-tech themes")
    L += ["", "## Every dip and fire entry on chips", "", "| rule | day | sym | spot | long/short | debit | exit | reason | return | peak x |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["theme"] == "chips" and r["rule"] in ("dip", "fire"):
            L.append(f"| {r['rule']} | {r['day']} | {r['sym']} | {r['spot']} | {r['long']}/{r['short']} | {r['debit']} | {r['exit']} | "
                     f"{r['reason']} | {r['ret']:+.0%} | {r['peak']:.2f} |")
    L += ["", "## Heat entries, last year", "", "| day | theme | sym | long/short | debit | exit | reason | return |", "|---|---|---|---|---|---|---|---|"]
    for r in window(rows, 365, end):
        if r["rule"] == "heat":
            L.append(f"| {r['day']} | {r['theme']} | {r['sym']} | {r['long']}/{r['short']} | {r['debit']} | {r['exit']} | {r['reason']} | {r['ret']:+.0%} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=2)
    ap.add_argument("--from-json", action="store_true")
    ap.add_argument("--cache", help="pickle file for the fetched option paths (outside the repo)")
    a = ap.parse_args()
    if a.from_json:
        rows = json.loads((OUT / "verticals.json").read_text())
    else:
        from pathlib import Path
        rows = study(Alpaca(), a.years, Path(a.cache) if a.cache else None)
        (OUT / "verticals.json").write_text(json.dumps(rows, indent=0) + "\n")
    text = report(rows, a.years)
    (OUT / "VERTICALS.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
