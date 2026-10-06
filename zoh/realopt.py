"""The champion rule re-tested on real historical option prices (Alpaca option bars, 2024-02+).

Rule (rebound_scanner): a stock in the universe opens >= 2% below the previous close on a day
with a same-day expiry and no macro release; at 09:45 buy the same-day call whose delta (from
the implied vol of its own 09:45 price) is closest to 0.08; exit with a trail (once the option
doubles, sell when it gives back 40% of the peak, never below cost) or at 15:45.

Prices are 1-minute option bar closes. Costs: buy at close x (1 + SLIP), sell at close x
(1 - SLIP), at least $0.01 each way. The same trades are also priced with the backtest's
Black-Scholes model so the model's bias is visible.

    python -m zoh.realopt
"""
import json
import math
import statistics
import time
from datetime import date, datetime, timedelta

from . import journal
from .alpaca import DATA_URL, Alpaca, AlpacaError
from .backtest import hero_odds
from .strategy import ET, MARKET_OPEN, bs_delta, bs_price, hhmm, parse_bar, regular_session

UNIVERSE = ["META", "NVDA", "TSLA", "AMZN", "AMD", "RKLB", "CRDO", "HOOD", "INTC", "GOOGL",
            "AAPL", "COIN", "SMCI", "PLTR", "AVGO", "MU"]
MWF = {"AAPL", "AMZN", "MSFT", "META", "NVDA", "TSLA", "GOOGL", "AVGO", "AMD", "MU"}
MWF_SINCE = date(2026, 1, 26)
START = date(2024, 2, 1)
GAP = -0.02
TARGET_DELTA = 0.08
SLIPS = (0.10, 0.05)
EXIT_AT = hhmm("15:45")
Y = 252 * 390


def has_same_day_expiry(sym, day):
    if day.weekday() == 4:
        return True
    return sym in MWF and day >= MWF_SINCE and day.weekday() in (0, 2)


def daily_raw(api, sym, start, end):
    params = {"symbols": sym, "timeframe": "1Day", "start": start.isoformat(), "end": end.isoformat(),
              "feed": "sip", "limit": 10000, "adjustment": "raw"}
    out = []
    for page in api._paged(f"{DATA_URL}/v2/stocks/bars", params, "bars"):
        out.extend((page or {}).get(sym, []))
    return [(datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date(), b["o"], b["c"])
            for b in out]


def occ(sym, day, strike):
    return f"{sym}{day:%y%m%d}C{int(round(strike * 1000)):08d}"


def strike_grid(spot):
    cands = set()
    for step in (0.5, 1, 2.5, 5, 10):
        k = math.ceil(spot / step) * step
        while k <= spot * 1.12:
            cands.add(round(k, 2))
            k += step
    return sorted(cands)


def option_minutes(api, symbols, day):
    params = {"symbols": ",".join(symbols), "timeframe": "1Min",
              "start": f"{day}T13:00:00Z", "end": f"{day}T21:00:00Z", "limit": 10000}
    out = {}
    while True:
        page = api._request("GET", f"{DATA_URL}/v1beta1/options/bars", params) or {}
        for s, bars in (page.get("bars") or {}).items():
            out.setdefault(s, []).extend(bars)
        token = page.get("next_page_token")
        if not token:
            return {s: regular_session([parse_bar(b) for b in bars]) for s, bars in out.items()}
        params["page_token"] = token


def implied_vol(price, spot, strike, years):
    lo, hi = 0.01, 5.0
    if price <= max(spot - strike, 0) or years <= 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if bs_price(spot, strike, years, mid, "call") < price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def at_or_after(bars, t, within=5):
    for b in bars:
        mins = (b["t"].hour * 60 + b["t"].minute) - (t.hour * 60 + t.minute)
        if 0 <= mins <= within:
            return b
        if mins > within:
            return None
    return None


def run_exit(path, entry, slip):
    """Trail after doubling (40% giveback, floor at cost) or 15:45. path: [(t, close)]."""
    peak = entry
    last = entry
    for t, c in path:
        bid = max(0.0, min(c * (1 - slip), c - 0.01))
        last = bid
        if t.time() >= EXIT_AT:
            return bid, "time", peak
        peak = max(peak, bid)
        if peak >= 2 * entry and bid <= max(entry, peak * 0.6):
            return bid, "trail", peak
    return last, "eod", peak


def main():
    api = Alpaca()
    events = journal.load_events()
    end = datetime.now(ET).date() - timedelta(days=1)
    trades = []
    skipped = {"no_contract": 0, "no_quote": 0}
    for sym in UNIVERSE:
        days = daily_raw(api, sym, START - timedelta(days=7), end)
        n = 0
        for i in range(1, len(days)):
            day, o, _ = days[i]
            prev = days[i - 1][2]
            if day < START or not has_same_day_expiry(sym, day) or events.get(day.isoformat()):
                continue
            if o / prev - 1 > GAP:
                continue
            start = datetime.combine(day, MARKET_OPEN, ET)
            try:
                stock = regular_session([parse_bar(b) for b in api.stock_bars(
                    sym, start, start + timedelta(minutes=20), feed="sip", adjustment="raw")])
            except AlpacaError:
                continue
            bar = at_or_after(stock, hhmm("09:44"), 3)
            if not bar:
                continue
            spot = bar["c"]
            years = 375 / Y
            syms = {occ(sym, day, k): k for k in strike_grid(spot)}
            try:
                opts = {}
                keys = list(syms)
                for j in range(0, len(keys), 100):
                    opts.update(option_minutes(api, keys[j:j + 100], day))
            except AlpacaError:
                skipped["no_contract"] += 1
                continue
            time.sleep(0.2)
            best = None
            for s, bars in opts.items():
                b = at_or_after(bars, hhmm("09:45"), 5)
                if not b or b["c"] <= 0:
                    continue
                k = syms[s]
                iv = implied_vol(b["c"], spot, k, years)
                if not iv:
                    continue
                d = bs_delta(spot, k, years, iv, "call")
                if best is None or abs(d - TARGET_DELTA) < abs(best[1] - TARGET_DELTA):
                    best = (s, d, b, iv, k)
            if not best:
                skipped["no_quote" if opts else "no_contract"] += 1
                continue
            s, d, b, iv, k = best
            path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
            row = {"sym": sym, "day": day.isoformat(), "gap": o / prev - 1, "spot": spot,
                   "contract": s, "delta": round(d, 3), "iv": round(iv, 3), "mid0945": b["c"]}
            for slip in SLIPS:
                entry = max(b["c"] * (1 + slip), b["c"] + 0.01)
                exit_, why, peak = run_exit(path, entry, slip)
                row[f"pnl_{int(slip*100)}"] = exit_ / entry - 1
                row[f"why_{int(slip*100)}"] = why
                row[f"peak_{int(slip*100)}"] = peak / entry
            row["max_multiple_mid"] = max([c for _, c in path] or [b["c"]]) / b["c"]
            trades.append(row)
            n += 1
        print(f"{sym}: {n} trades", flush=True)

    def summary(rows, key):
        p = [r[key] for r in rows]
        if not p:
            return None
        return {"n": len(p), "avg": sum(p) / len(p), "median": statistics.median(p),
                "win": sum(x > 0 for x in p) / len(p), "best": max(p),
                "x2": sum(x >= 1 for x in p), "x5": sum(x >= 4 for x in p),
                "odds_2k_50pct": hero_odds(p, 0.5, 500, 2000, 50)}

    recent_cut = (end - timedelta(days=91)).isoformat()
    groups = {"all": trades, "last 3 months": [t for t in trades if t["day"] >= recent_cut],
              "since 2026-01-26 (MWF expiries)": [t for t in trades if t["day"] >= "2026-01-26"]}

    def pct(x):
        return f"{x:+.0%}"

    lines = ["# Champion rule on real option prices (Alpaca option bars)", "",
             f"Rule: universe of {len(UNIVERSE)}, open <= {GAP:.0%} vs previous close, same-day expiry "
             "(Fridays; Mon/Wed too for mega caps since 2026-01-26), no macro release (calendar only "
             "covers 2025-10 onwards), buy at 09:45 the call whose delta from its own implied vol is "
             "closest to 0.08, exit on a trail after doubling (40% giveback, not below cost) or 15:45. "
             "Prices are 1-minute option closes; entry at close +slip, exits at close -slip.", "",
             f"Skipped events: {skipped}", "",
             "| period | slippage | trades | win% | avg / trade | median | best | >= 2x | >= 5x | odds $500->$2k (50% stake) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for name, rows in groups.items():
        for slip in SLIPS:
            s = summary(rows, f"pnl_{int(slip*100)}")
            if s:
                lines.append(f"| {name} | {slip:.0%} | {s['n']} | {s['win']:.0%} | {pct(s['avg'])} | "
                             f"{pct(s['median'])} | {pct(s['best'])} | {s['x2']} | {s['x5']} | "
                             f"{s['odds_2k_50pct']:.0%} |")
    ivs = [t["iv"] for t in trades]
    if ivs:
        lines += ["", f"Implied vol at 09:45 of the chosen contracts: median {statistics.median(ivs):.0%}, "
                  f"range {min(ivs):.0%}-{max(ivs):.0%}. Median 09:45 price ${statistics.median([t['mid0945'] for t in trades]):.2f}; "
                  f"median best multiple reached (mid, before costs) {statistics.median([t['max_multiple_mid'] for t in trades]):.1f}x."]
    lines += ["", "## By stock (10% slippage)", "", "| stock | trades | avg | win% |", "|---|---|---|---|"]
    by = {}
    for t in trades:
        by.setdefault(t["sym"], []).append(t["pnl_10"])
    for sym, p in sorted(by.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
        lines.append(f"| {sym} | {len(p)} | {pct(sum(p) / len(p))} | {sum(x > 0 for x in p) / len(p):.0%} |")
    lines += ["", "## Every trade", "", "| day | stock | gap | contract | delta | 09:45 | exit (10%) | why | peak |",
              "|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(trades, key=lambda t: t["day"]):
        lines.append(f"| {t['day']} | {t['sym']} | {t['gap']:+.1%} | {t['contract']} | {t['delta']} | "
                     f"{t['mid0945']} | {pct(t['pnl_10'])} | {t['why_10']} | {t['peak_10']:.1f}x |")
    out = journal.ROOT / "journal" / "research"
    (out / "REALOPT.md").write_text("\n".join(lines) + "\n")
    (out / "realopt.json").write_text(json.dumps(trades, indent=1))
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()
