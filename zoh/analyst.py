"""Analyst rating changes as same-day catalysts: does a pre-market upgrade/downgrade on a large
cap carry into the session, and would the sniper rule have made money on it?

Rating changes come from Alpaca (Benzinga) headlines like
"Melius Research Upgrades Microsoft to Buy, Announces $665 Price Target". Only changes
published before 09:30 ET count (known pre-market, like the sniper). For each event:
- stock: gap, open->close in the rating's direction, versus every other day of that stock;
- options (same-day expiry days only, Black-Scholes at the stock's realized intraday vol):
  the sniper rule (after 15 min, >= 1% from the open in the rating's direction, before 12:00)
  with three contract/exit choices.

    python -m zoh.analyst
"""
import math
import re
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .backtest import simulate_day
from .runup import daily
from .strategy import ET, MARKET_OPEN, TRADING_MINUTES_PER_YEAR, hhmm, parse_bar, \
    regular_session, same_day_expiry

SYMBOLS = ["NVDA", "AMD", "AVGO", "MU", "META", "MSFT", "GOOGL", "AMZN", "AAPL", "TSLA",
           "INTC", "ARM", "QCOM", "NFLX", "ORCL", "PLTR", "CRM", "ADBE", "ANET", "COIN",
           "WDC", "STX", "LITE", "SMCI", "UBER"]
YEARS = 2
RATING = re.compile(r"\b(upgrades?|downgrades?)\b", re.I)
EXIT_AT = hhmm("15:45")
BASE = {"signal": "catalyst", "after_minutes": 15, "move_pct": 1.0, "entry_cutoff": "12:00",
        "stop_loss": None}
RULES = {  # label -> legs (each leg is half or all of the stake)
    "d0.2 trail (sniper today)": [{**BASE, "target_delta": 0.2, "take_profit": None,
                                   "trail_after": 1.0, "trail_giveback": 0.4}],
    "d0.3 half at 2x + trail": [{**BASE, "target_delta": 0.3, "take_profit": 1.0},
                                {**BASE, "target_delta": 0.3, "take_profit": None,
                                 "trail_after": 1.0, "trail_giveback": 0.4}],
    "d0.08 trail (lottery)": [{**BASE, "target_delta": 0.08, "take_profit": None,
                               "trail_after": 1.0, "trail_giveback": 0.4}],
}


def rating_events(api, symbol, start, end):
    """[(day, direction, headline)] for pre-market rating changes, one per stock-day."""
    by_day = defaultdict(set)
    heads = {}
    params = {"symbols": symbol, "start": start.isoformat(), "end": end.isoformat(),
              "limit": 50, "sort": "asc", "include_content": "false"}
    url = "https://data.alpaca.markets/v1beta1/news"
    while True:
        page = api._request("GET", url, params)
        for item in page.get("news") or []:
            m = RATING.search(item["headline"])
            if not m or len(item.get("symbols") or []) > 2:
                continue
            t = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")).astimezone(ET)
            if t.weekday() >= 5 or t.time() >= MARKET_OPEN:
                continue  # intraday and after-hours news is a different trade
            direction = "call" if m.group(1).lower().startswith("up") else "put"
            by_day[t.date()].add(direction)
            heads.setdefault((t.date(), direction), item["headline"])
        token = page.get("next_page_token")
        if not token:
            break
        params["page_token"] = token
        time.sleep(0.32)
    return [(d, next(iter(dirs)), heads[(d, next(iter(dirs)))])
            for d, dirs in sorted(by_day.items()) if len(dirs) == 1]  # mixed calls: skip


def minute_bars(api, symbol, day):
    start = datetime.combine(day, MARKET_OPEN, ET)
    try:
        raw = api.stock_bars(symbol, start, start + timedelta(hours=6.5), feed="sip",
                             adjustment="all")
    except AlpacaError:
        raw = api.stock_bars(symbol, start, start + timedelta(hours=6.5), adjustment="all")
    return regular_session([parse_bar(b) for b in raw])


def day_vol(bars):
    rets = [math.log(bars[i]["c"] / bars[i - 1]["c"]) for i in range(1, len(bars))]
    if len(rets) < 30:
        return None
    mean = sum(rets) / len(rets)
    return math.sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
                     * TRADING_MINUTES_PER_YEAR)


def pct(x, digits=1):
    return "—" if x is None else f"{x:+.{digits}%}"


def med(xs):
    return statistics.median(xs) if xs else None


def main():
    api = Alpaca()
    end = datetime.now(ET) - timedelta(days=1)
    start = end - timedelta(days=365 * YEARS)
    events = []
    for sym in SYMBOLS:
        evs = rating_events(api, sym, start, end)
        print(f"{sym}: {len(evs)} pre-market rating changes", flush=True)
        events += [(sym, *e) for e in evs]
    bars = daily(api, SYMBOLS, start - timedelta(days=10), end)

    # stock move on event days vs all days, signed in the rating's direction
    rows, baseline = [], defaultdict(list)
    for sym, series in bars.items():
        for i in range(1, len(series)):
            d, o, c = series[i]
            baseline[sym].append((o / series[i - 1][2] - 1, c / o - 1))
    for sym, day, direction, headline in events:
        series = bars.get(sym, [])
        idx = next((i for i, (d, _, _) in enumerate(series) if d == day), None)
        if not idx:
            continue
        sign = 1 if direction == "call" else -1
        o, c, prev = series[idx][1], series[idx][2], series[idx - 1][2]
        rows.append({"sym": sym, "day": day, "dir": direction, "headline": headline,
                     "gap": sign * (o / prev - 1), "oc": sign * (c / o - 1)})

    # options: the sniper rule on same-day expiry days
    sims = defaultdict(list)
    for r in rows:
        if not same_day_expiry(r["sym"], r["day"].weekday()):
            continue
        mb = minute_bars(api, r["sym"], r["day"])
        iv = day_vol(mb)
        time.sleep(0.32)
        if not mb or not iv:
            continue
        ctx = {"events": [], "gap_pct": None, "weekday": r["day"].weekday(), "cross": {},
               "bias": {"sniper": {"symbol": r["sym"], "direction": r["dir"]}}}
        for label, legs in RULES.items():
            results = [simulate_day(mb, leg, iv * 1.15, 0.03, EXIT_AT, ctx) for leg in legs]
            if all(results):
                sims[label].append({**r, "pnl": sum(x["pnl_pct"] for x in results) / len(results),
                                    "entry_time": results[0]["entry_time"]})
            elif label == next(iter(RULES)):
                r["no_fire"] = True
        r["sim"] = True

    lines = [f"# Analyst rating changes as 0DTE catalysts — {len(rows)} pre-market events, "
             f"{len(SYMBOLS)} large caps, last {YEARS} years", "",
             "Moves are signed in the rating's direction (an upgrade counts the stock's rise as "
             "positive, a downgrade its fall). Baseline = every day of the same stocks, "
             "taking the open→close move in the gap's direction.", "",
             "## Stock moves", "",
             "| group | n | gap (median) | open→close (median) | open→close > 0 | > +1% | > +2% |",
             "|---|---|---|---|---|---|---|"]

    def stock_line(label, rs):
        oc = [r["oc"] for r in rs]
        if not oc:
            return f"| {label} | 0 | | | | | |"
        return (f"| {label} | {len(rs)} | {pct(med([r['gap'] for r in rs]))} | {pct(med(oc))} | "
                f"{sum(x > 0 for x in oc) / len(oc):.0%} | {sum(x > 0.01 for x in oc) / len(oc):.0%} "
                f"| {sum(x > 0.02 for x in oc) / len(oc):.0%} |")

    up = [r for r in rows if r["dir"] == "call"]
    down = [r for r in rows if r["dir"] == "put"]
    lines += [stock_line("all rating changes", rows), stock_line("upgrades", up),
              stock_line("downgrades", down),
              stock_line("small gap (< 2%)", [r for r in rows if r["gap"] < 0.02]),
              stock_line("big gap (>= 2%)", [r for r in rows if r["gap"] >= 0.02])]
    base = [(abs(g), oc if g >= 0 else -oc) for v in baseline.values() for g, oc in v]
    bo = [x for _, x in base]
    lines.append(f"| baseline: all days, follow the gap | {len(bo)} | {pct(med([g for g, _ in base]))} "
                 f"| {pct(med(bo))} | {sum(x > 0 for x in bo) / len(bo):.0%} | "
                 f"{sum(x > 0.01 for x in bo) / len(bo):.0%} | {sum(x > 0.02 for x in bo) / len(bo):.0%} |")

    n_sim = sum(1 for r in rows if r.get("sim"))
    lines += ["", "## Sniper rule with options (same-day expiry days only)", "",
              f"{n_sim} events fell on a same-day expiry day. The rule fires when the stock is "
              ">= 1% from the open in the rating's direction between 09:45 and 12:00. Options are "
              "priced with Black-Scholes at 1.15x the day's realized intraday vol, 3% slippage. "
              "\"half at 2x\" sells half at +100% and trails the rest.", "",
              "| rule | trades | fired | win% | avg / trade | median | best | ≥ 2x |",
              "|---|---|---|---|---|---|---|---|"]
    for label, ts in sims.items():
        p = [t["pnl"] for t in ts]
        if not p:
            continue
        lines.append(f"| {label} | {len(p)} | {len(p) / n_sim:.0%} | "
                     f"{sum(x > 0 for x in p) / len(p):.0%} | {pct(sum(p) / len(p), 0)} | "
                     f"{pct(med(p), 0)} | {pct(max(p), 0)} | {sum(x >= 1 for x in p)} |")
    for label in RULES:
        ts = sims.get(label, [])
        for name, keep in (("upgrades", "call"), ("downgrades", "put")):
            p = [t["pnl"] for t in ts if t["dir"] == keep]
            if p:
                lines.append(f"| ↳ {label}, {name} | {len(p)} | | {sum(x > 0 for x in p) / len(p):.0%} "
                             f"| {pct(sum(p) / len(p), 0)} | {pct(med(p), 0)} | {pct(max(p), 0)} | "
                             f"{sum(x >= 1 for x in p)} |")

    lines += ["", "## By stock (stock moves)", "",
              "| stock | events | upgrades | open→close median | > 0 |", "|---|---|---|---|---|"]
    by = defaultdict(list)
    for r in rows:
        by[r["sym"]].append(r)
    for sym, rs in sorted(by.items(), key=lambda kv: -(med([r["oc"] for r in kv[1]]) or 0)):
        oc = [r["oc"] for r in rs]
        lines.append(f"| {sym} | {len(rs)} | {sum(r['dir'] == 'call' for r in rs)} | "
                     f"{pct(med(oc))} | {sum(x > 0 for x in oc) / len(oc):.0%} |")

    first = next(iter(RULES))
    pnl_by = {(t["sym"], t["day"]): t["pnl"] for t in sims.get(first, [])}
    lines += ["", f"## Every event (option column: {first})", "",
              "| day | stock | rating | gap | open→close | option | headline |",
              "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["day"]):
        opt = pnl_by.get((r["sym"], r["day"]))
        opt_s = pct(opt, 0) if opt is not None else ("no fire" if r.get("no_fire") else "—")
        lines.append(f"| {r['day']} | {r['sym']} | {'up' if r['dir'] == 'call' else 'down'} | "
                     f"{pct(r['gap'])} | {pct(r['oc'])} | {opt_s} | "
                     f"{r['headline'].replace('|', '/')[:90]} |")
    text = "\n".join(lines) + "\n"
    out = journal.ROOT / "journal" / "research"
    out.mkdir(parents=True, exist_ok=True)
    (out / "ANALYST.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
