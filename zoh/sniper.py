"""Mega-cap 0DTE "sniper": can trend days on single mega caps be caught after the open?

Idea (from META 2026: 3/26 -6%, 7/09 +8%, 9/21 +9% open-to-close, each a 25-50x 0DTE):
skip earnings-style gaps, wait for the stock to move X% from its open, then buy a ~3% OTM
nearest-expiry option in that direction and hold to the exit time. At most one trade per
day: the strongest qualifying mover.

Single-stock Mon/Wed/Fri expirations started 2026-01-26 for the largest names; on Tue/Thu
the nearest expiry is the next day. Option prices are Black-Scholes at each stock's trailing
realised vol x IV_MULT plus slippage, so treat results as a ranking, not a P&L forecast.

    python -m zoh.sniper --out journal/research
"""
import argparse
import math
import random
import statistics
from collections import defaultdict
from datetime import date, datetime, time, timedelta

from . import journal
from .alpaca import Alpaca
from .strategy import ET, bs_price, parse_bar, regular_session

SYMBOLS = ["META", "NVDA", "TSLA", "AAPL", "AMZN", "MSFT", "GOOGL", "AVGO", "AMD", "MU"]
CONFIRM_ONLY = ["INTC", "ARM", "QCOM", "SMH"]  # theme peers used for confirmation, not traded
# Theme groups: a move confirmed by peers in the same group is a theme day, not noise.
GROUPS = {
    "cpu": ["AMD", "INTC", "ARM", "QCOM"],
    "ai_semis": ["NVDA", "AVGO", "MU", "AMD", "SMH"],
    "internet": ["META", "GOOGL", "AMZN", "MSFT", "AAPL"],
}
START = date(2026, 1, 26)
IV_MULT = 1.15
IV_FLOOR = 0.25
SLIP = 0.03
EXIT = time(15, 45)
TRADING_MINUTES = 252 * 390

RULES = [
    {"id": "theme_t1000_m15_p2", "check": time(10, 0), "move": 0.015, "peers": 2, "peer_move": 0.01,
     "max_gap": 0.06},
    {"id": "theme_t1030_m20_p2", "check": time(10, 30), "move": 0.020, "peers": 2, "peer_move": 0.01,
     "max_gap": 0.06},
    {"id": "theme_t1030_m20_p3", "check": time(10, 30), "move": 0.020, "peers": 3, "peer_move": 0.01,
     "max_gap": 0.06},
    {"id": "t1000_m15", "check": time(10, 0), "move": 0.015},
    {"id": "t1000_m20", "check": time(10, 0), "move": 0.020},
    {"id": "t1030_m20", "check": time(10, 30), "move": 0.020},
    {"id": "t1030_m25", "check": time(10, 30), "move": 0.025},
    {"id": "t1100_m30", "check": time(11, 0), "move": 0.030},
]
MAX_GAP = 0.04   # bigger gaps are mostly earnings / overnight news already priced
OTM = 0.03


def minutes_left(now, expiry_days):
    close = datetime.combine(now.date(), time(16, 0), now.tzinfo)
    return (close - now).total_seconds() / 60 + 390 * expiry_days


def expiry_days(day):
    """0 on Mon/Wed/Fri (same-day expiry), else 1 (next day)."""
    return 0 if day.weekday() in (0, 2, 4) else 1


def realised_vol(closes):
    rets = [math.log(b / a) for a, b in zip(closes, closes[1:])]
    return statistics.pstdev(rets) * math.sqrt(252) if len(rets) > 5 else 0.4


def load(api, start, end):
    data = {}
    for sym in SYMBOLS + CONFIRM_ONLY:
        bars = regular_session([parse_bar(b) for b in api.stock_bars(sym, start, end)])
        by_day = defaultdict(list)
        for b in bars:
            by_day[b["t"].date()].append(b)
        data[sym] = {d: bs for d, bs in by_day.items() if len(bs) >= 300}
        print(f"{sym}: {len(data[sym])} days", flush=True)
    return data


def move_at(data, sym, day, check):
    bars = data.get(sym, {}).get(day)
    if not bars:
        return None
    at = [b for b in bars if b["t"].time() < check]
    return at[-1]["c"] / bars[0]["o"] - 1 if at else None


def peers_confirm(data, sym, day, rule, direction):
    """How many same-group peers moved >= peer_move in the same direction by the check time."""
    peers = {p for g in GROUPS.values() if sym in g for p in g if p != sym}
    count = 0
    for peer in peers:
        m = move_at(data, peer, day, rule["check"])
        if m is not None and m * direction >= rule["peer_move"]:
            count += 1
    return count


def simulate(data, rule):
    days = sorted(set().union(*(set(d) for sym, d in data.items() if sym in SYMBOLS)))
    days = [d for d in days if d >= START]
    trades = []
    for day in days:
        best = None
        for sym, by_day in data.items():
            if sym not in SYMBOLS or day not in by_day:
                continue
            prior = [d for d in sorted(by_day) if d < day]
            if len(prior) < 21:
                continue
            prev_close = by_day[prior[-1]][-1]["c"]
            bars = by_day[day]
            o = bars[0]["o"]
            if abs(o / prev_close - 1) > rule.get("max_gap", MAX_GAP):
                continue
            at = [b for b in bars if b["t"].time() < rule["check"]]
            if not at:
                continue
            spot = at[-1]["c"]
            move = spot / o - 1
            if abs(move) < rule["move"]:
                continue
            if rule.get("peers") and peers_confirm(data, sym, day, rule,
                                                   1 if move > 0 else -1) < rule["peers"]:
                continue
            if best is None or abs(move) > abs(best["move"]):
                closes = [by_day[d][-1]["c"] for d in prior[-21:]]
                best = {"sym": sym, "move": move, "spot": spot, "bars": bars,
                        "iv": max(realised_vol(closes) * IV_MULT, IV_FLOOR), "gap": o / prev_close - 1}
        if not best:
            continue
        kind = "call" if best["move"] > 0 else "put"
        strike = best["spot"] * (1 + OTM if kind == "call" else 1 - OTM)
        exp = expiry_days(day)
        entry_t = datetime.combine(day, rule["check"], ET)
        entry = bs_price(best["spot"], strike, minutes_left(entry_t, exp) / TRADING_MINUTES,
                         best["iv"], kind) * (1 + SLIP) + 0.02
        exit_bar = [b for b in best["bars"] if b["t"].time() < EXIT][-1]
        exit_t = datetime.combine(day, EXIT, ET)
        exit_px = max(bs_price(exit_bar["c"], strike, minutes_left(exit_t, exp) / TRADING_MINUTES,
                               best["iv"], kind) * (1 - SLIP) - 0.02, 0.0)
        trades.append({"date": day, "sym": best["sym"], "kind": kind, "gap": best["gap"],
                       "move_at_entry": best["move"], "day_move": exit_bar["c"] / best["bars"][0]["o"] - 1,
                       "expiry_days": exp, "entry": entry, "exit": exit_px,
                       "multiple": exit_px / entry if entry > 0 else 0})
    return days, trades


def chain_all_in(trades, start=500.0, dead=50.0):
    equity, path = start, []
    for t in trades:
        if equity < dead:
            break
        equity *= t["multiple"]
        path.append((t["date"], t["sym"], round(equity)))
    return equity, path


def odds(multiples, target, start=500.0, dead=50.0, paths=4000, seed=7):
    if not multiples:
        return 0.0
    rng = random.Random(seed)
    wins = 0
    for _ in range(paths):
        equity = start
        for _ in range(300):
            equity *= rng.choice(multiples)
            if equity >= target:
                wins += 1
                break
            if equity < dead:
                break
    return wins / paths


def report(days, results):
    lines = [f"# Mega-cap 0DTE sniper — {days[0]} → {days[-1]} ({len(days)} trading days)", "",
             f"Universe: {', '.join(SYMBOLS)}. Skip days with |gap| > {MAX_GAP:.0%}; at the check "
             f"time take the strongest mover whose move from the open exceeds the threshold; buy "
             f"{OTM:.0%} OTM nearest expiry (same day Mon/Wed/Fri, next day Tue/Thu); exit 15:45. "
             f"Black-Scholes at trailing realised vol x {IV_MULT}, {SLIP:.0%} slippage + $0.02. "
             "Modelled prices — rank ideas, don't trust the dollar figures.", "",
             "`theme_*` rules also require >= N same-group peers (CPU: AMD/INTC/ARM/QCOM; AI semis: "
             "NVDA/AVGO/MU/AMD/SMH; internet: META/GOOGL/AMZN/MSFT/AAPL) to have moved >= 1% the same "
             "way by the check time, and allow gaps up to 6% (theme days gap more).", "",
             "| rule | trades | trade days % | win % (>1x) | ≥5x | ≥10x | median x | mean x | "
             "P($500→$2k) | P($500→$50k) | all-in chain, actual order |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for rule, trades in results:
        m = [t["multiple"] for t in trades]
        final, _ = chain_all_in(trades)
        lines.append(
            f"| {rule['id']} | {len(m)} | {len(m) / len(days):.0%} | "
            f"{sum(x > 1 for x in m) / len(m):.0%} | {sum(x >= 5 for x in m)} | "
            f"{sum(x >= 10 for x in m)} | {statistics.median(m):.2f} | {statistics.mean(m):.2f} | "
            f"{odds(m, 2000):.1%} | {odds(m, 50000):.2%} | ${final:,.0f} |" if m else
            f"| {rule['id']} | 0 | | | | | | | | | |")
    for rule, trades in results:
        lines += ["", f"## {rule['id']} — trades", "",
                  "| date | stock | side | gap | move at entry | open→close | expiry | multiple |",
                  "|---|---|---|---|---|---|---|---|"]
        for t in trades:
            lines.append(f"| {t['date']} | {t['sym']} | {t['kind']} | {t['gap']:+.1%} | "
                         f"{t['move_at_entry']:+.1%} | {t['day_move']:+.1%} | "
                         f"{'0DTE' if t['expiry_days'] == 0 else '1DTE'} | {t['multiple']:.1f}x |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="journal/research")
    args = parser.parse_args()
    api = Alpaca()
    end = datetime.now(ET) - timedelta(minutes=20)
    data = load(api, datetime.combine(START - timedelta(days=45), time(9, 30), ET), end)
    results = []
    days = None
    for rule in RULES:
        days, trades = simulate(data, rule)
        results.append((rule, trades))
    text = report(days, results)
    out = journal.ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "SNIPER.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
