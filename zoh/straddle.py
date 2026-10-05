"""Buy both sides on days likely to move: does a same-day strangle beat guessing direction?

Day types (large caps, same-day expiry days only, last 2 years):
- gap: |open vs previous close| >= 2%
- rating: pre-market analyst upgrade/downgrade (see zoh/analyst.py)
- after_big: the day after a >= 7% one-day move
- control: a random sample of the remaining days

At 09:45 the strangle buys a ~0.3-delta call and a ~0.3-delta put for equal dollars; each leg
exits on its own (trail after doubling, or sell at 2x) or is held to 15:45. Directional
comparisons buy one 0.3-delta leg: with the gap, against the gap, with the rating.

Options are priced with Black-Scholes at the stock's trailing intraday vol (Parkinson
high/low estimate over the previous 20 days), times 1.15 (normal) and times 1.5 (stress:
on event days the market prices options richer than usual). Pricing at the day's own
realized vol would make every strangle roughly fair by construction, so it is avoided.

    python -m zoh.straddle
"""
import math
import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .analyst import SYMBOLS, minute_bars, rating_events
from .backtest import hero_odds, simulate_day
from .strategy import ET, hhmm, same_day_expiry

YEARS = 2
EXIT_AT = hhmm("15:45")
CONTROL_N = 250
IV_MULTS = (1.15, 1.5)
LEG = {"signal": "bias", "after_minutes": 15, "entry_cutoff": "10:00", "target_delta": 0.3,
       "stop_loss": None}
EXITS = {"trail": {"take_profit": None, "trail_after": 1.0, "trail_giveback": 0.4},
         "2x": {"take_profit": 1.0}}


def daily_hl(api, symbols, start, end):
    out = {}
    for sym in symbols:
        try:
            got = api.daily_bars_multi([sym], start, end, feed="sip")
        except AlpacaError:
            got = api.daily_bars_multi([sym], start, end, feed="iex")
        out[sym] = [(datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date(),
                     b["o"], b["h"], b["l"], b["c"]) for b in got.get(sym, [])]
    return out


def parkinson(rows):
    """Annualised volatility from daily high/low ranges."""
    xs = [math.log(h / l) ** 2 for _, _, h, l, _ in rows if l > 0]
    return math.sqrt(sum(xs) / len(xs) / (4 * math.log(2)) * 252) if xs else None


def leg(bars, direction, exit_name, iv):
    ctx = {"events": [], "gap_pct": None, "weekday": bars[0]["t"].weekday(), "cross": {},
           "bias": {"bias": direction}}
    return simulate_day(bars, {**LEG, **EXITS[exit_name]}, iv, 0.03, EXIT_AT, ctx)


def stats(pnls):
    if not pnls:
        return None
    return {"n": len(pnls), "avg": sum(pnls) / len(pnls), "med": statistics.median(pnls),
            "win": sum(p > 0 for p in pnls) / len(pnls), "best": max(pnls),
            "odds": hero_odds(pnls, 0.5, 500, 2000, 50)}


def pct(x):
    return "—" if x is None else f"{x:+.0%}"


def main():
    api = Alpaca()
    random.seed(7)
    end = datetime.now(ET) - timedelta(days=1)
    start = end - timedelta(days=365 * YEARS)
    daily = daily_hl(api, SYMBOLS, start - timedelta(days=40), end)
    rated = {}
    for sym in SYMBOLS:
        for day, direction, _ in rating_events(api, sym, start, end):
            rated[(sym, day)] = direction
        print(f"{sym}: daily {len(daily[sym])}, ratings so far {len(rated)}", flush=True)

    days = []  # (sym, day, kinds, gap, rating, trailing vol)
    control_pool = []
    for sym, rows in daily.items():
        for i in range(21, len(rows)):
            day, o = rows[i][0], rows[i][1]
            if day < start.date() or not same_day_expiry(sym, day.weekday()):
                continue
            prev_c = rows[i - 1][4]
            gap = o / prev_c - 1
            prev_move = rows[i - 1][4] / rows[i - 2][4] - 1
            kinds = []
            if abs(gap) >= 0.02:
                kinds.append("gap")
            if (sym, day) in rated:
                kinds.append("rating")
            if abs(prev_move) >= 0.07:
                kinds.append("after_big")
            item = (sym, day, kinds, gap, rated.get((sym, day)), parkinson(rows[i - 20:i]))
            (days if kinds else control_pool).append(item)
    days += [(s, d, ["control"], g, r, v) for s, d, _, g, r, v in
             random.sample(control_pool, min(CONTROL_N, len(control_pool)))]
    print(f"{len(days)} days to simulate", flush=True)

    # results[(iv_mult, strategy, kind)] -> [pnl]
    results = defaultdict(list)
    moves = defaultdict(list)
    for n, (sym, day, kinds, gap, rating, vol) in enumerate(days):
        if not vol:
            continue
        bars = minute_bars(api, sym, day)
        time.sleep(0.3)
        if len(bars) < 300:
            continue
        move = abs(bars[-1]["c"] / bars[15]["c"] - 1)  # |09:45 -> close|
        for kind in kinds:
            moves[kind].append(move)
        for mult in IV_MULTS:
            iv = vol * mult
            legs = {(d, e): leg(bars, d, e, iv) for d in ("call", "put") for e in EXITS}
            for e in EXITS:
                c, p = legs[("call", e)], legs[("put", e)]
                if not (c and p):
                    continue
                strangle = (c["pnl_pct"] + p["pnl_pct"]) / 2
                for kind in kinds:
                    results[(mult, f"strangle {e}", kind)].append(strangle)
                    results[(mult, f"call only {e}", kind)].append(c["pnl_pct"])
                    results[(mult, f"put only {e}", kind)].append(p["pnl_pct"])
                    if "gap" == kind:
                        with_gap = c if gap > 0 else p
                        fade = p if gap > 0 else c
                        results[(mult, f"with gap {e}", kind)].append(with_gap["pnl_pct"])
                        results[(mult, f"fade gap {e}", kind)].append(fade["pnl_pct"])
                    if kind == "rating" and rating:
                        results[(mult, f"with rating {e}", kind)].append(
                            legs[(rating, e)]["pnl_pct"])
        if n % 50 == 0:
            print(f"  {n}/{len(days)}", flush=True)

    kinds_order = ["gap", "rating", "after_big", "control"]
    lines = [f"# Strangle vs direction on big-move days — {len(SYMBOLS)} large caps, last {YEARS} "
             "years", "",
             "Same-day expiry days only. Entry 09:45, ~0.3 delta per leg, 3% slippage. A strangle "
             "is a call and a put for equal dollars; its return is the average of the two legs. "
             "\"trail\": each leg trails after doubling; \"2x\": each leg sells at +100%. Odds = "
             "bootstrap P($500 → $2,000) staking 50% per trade.", "",
             "## How far the stock moves after 09:45 (median |09:45 → close|)", "",
             "| day type | days | median move | > 2% | > 3% |", "|---|---|---|---|---|"]
    for kind in kinds_order:
        m = moves.get(kind, [])
        if m:
            lines.append(f"| {kind} | {len(m)} | {statistics.median(m):.2%} | "
                         f"{sum(x > 0.02 for x in m) / len(m):.0%} | "
                         f"{sum(x > 0.03 for x in m) / len(m):.0%} |")
    for mult in IV_MULTS:
        lines += ["", f"## Options priced at {mult}x trailing intraday vol", "",
                  "| day type | strategy | trades | win% | avg / trade | median | best | odds $2k |",
                  "|---|---|---|---|---|---|---|---|"]
        for kind in kinds_order:
            for strat in ("strangle trail", "strangle 2x", "with gap trail", "fade gap trail",
                          "with rating trail", "with rating 2x", "call only trail",
                          "put only trail"):
                s = stats(results.get((mult, strat, kind), []))
                if s:
                    lines.append(f"| {kind} | {strat} | {s['n']} | {s['win']:.0%} | "
                                 f"{pct(s['avg'])} | {pct(s['med'])} | {pct(s['best'])} | "
                                 f"{s['odds']:.0%} |")
    text = "\n".join(lines) + "\n"
    out = journal.ROOT / "journal" / "research"
    out.mkdir(parents=True, exist_ok=True)
    (out / "STRADDLE.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
