"""Quick validation: replay every variant on historical SPY 1-minute bars.

Option prices are modelled with Black-Scholes at a flat IV (config backtest.iv) plus
slippage, because free historical 0DTE option quotes are not available. Treat results as
a ranking of ideas, not a P&L forecast: real 0DTE skew, spreads and IV crush differ.

    python -m zoh.backtest --days 365 [--out journal/BACKTEST.md]
"""
import argparse
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca
from .strategy import (ET, LIVE_ONLY_SIGNALS, TRADING_MINUTES_PER_YEAR, bs_delta, bs_price,
                       check_exit, contracts_for, current_phase, day_context, evaluate_signal,
                       hhmm, parse_bar, regular_session, years_to_close)


def pick_strike(spot, years, iv, kind, target_delta):
    strikes = [round(spot) + k for k in range(-20, 21)]
    return min(strikes, key=lambda k: abs(abs(bs_delta(spot, k, years, iv, kind)) - target_delta))


def simulate_day(bars, variant, iv, slip, exit_at, ctx=None):
    """One variant on one day. Returns a trade dict or None."""
    pos = None
    for i, bar in enumerate(bars):
        now = bar["t"] + timedelta(minutes=1)
        years = years_to_close(now)
        if pos is None:
            if now.time() > hhmm(variant.get("entry_cutoff", "13:00")) or now.time() >= exit_at:
                return None
            direction = evaluate_signal(bars[:i + 1], variant, ctx)
            if not direction:
                continue
            strike = pick_strike(bar["c"], years, iv, direction, variant.get("target_delta", 0.3))
            fair = bs_price(bar["c"], strike, years, iv, direction)
            entry = fair * (1 + slip) + 0.01
            if entry < 0.05:
                continue
            pos = {"kind": direction, "strike": strike, "entry": entry, "peak": entry,
                   "entry_time": now}
            continue
        bid = max(bs_price(bar["c"], pos["strike"], years, iv, pos["kind"]) * (1 - slip) - 0.01,
                  0.0)
        pos["peak"] = max(pos["peak"], bid)
        pos["last"] = bid
        reason = "time" if now.time() >= exit_at else check_exit(pos["entry"], pos["peak"], bid,
                                                                  variant)
        if reason:
            return {**pos, "exit": bid, "reason": reason, "pnl_pct": bid / pos["entry"] - 1}
    if pos:  # data ended before the exit time (gaps)
        last = pos.get("last", pos["entry"])
        return {**pos, "exit": last, "reason": "eod", "pnl_pct": last / pos["entry"] - 1}
    return None


def compound(trades_by_day, days, config):
    """Run the account forward with phase-based sizing. Returns equity stats."""
    equity = peak = config["backtest"]["start_equity"]
    max_dd = 0.0
    milestones = {}
    ruined_on = None
    for day in days:
        trade = trades_by_day.get(day)
        if equity < config["dead_equity"]:
            ruined_on = ruined_on or day
            break
        if trade:
            budget = equity * current_phase(config, equity)["risk_per_trade"]
            qty = contracts_for(budget, trade["entry"])
            if qty == 0 and trade["entry"] * 100 <= equity:
                qty = 1  # hero fallback: one contract if the whole account can buy it
            equity += qty * 100 * (trade["exit"] - trade["entry"])
        peak = max(peak, equity)
        max_dd = max(max_dd, 1 - equity / peak if peak else 0)
        for mult in (2, 5, 10):
            if equity >= mult * config["backtest"]["start_equity"] and mult not in milestones:
                milestones[mult] = day
    return {"final": equity, "peak": peak, "max_dd": max_dd, "milestones": milestones,
            "ruined_on": ruined_on}


HERO_TARGET = 2000
SIZINGS = (0.3, 0.5, 1.0)


def hero_odds(pnl, risk, start, target, dead, paths=4000, max_trades=500, seed=7):
    """P(equity reaches target before falling below dead), resampling trade returns.

    Each trade stakes `risk` of current equity; a trade returning r changes equity by
    stake * r. Contract granularity is ignored.
    """
    if not pnl:
        return 0.0
    rng = random.Random(seed)
    wins = 0
    for _ in range(paths):
        equity = start
        for _ in range(max_trades):
            equity += equity * risk * rng.choice(pnl)
            if equity >= target:
                wins += 1
                break
            if equity < dead:
                break
    return wins / paths


def load_days(api, symbol, days_back):
    end = datetime.now(ET) - timedelta(minutes=20)
    start = end - timedelta(days=days_back)
    bars = regular_session([parse_bar(b) for b in api.stock_bars(symbol, start, end)])
    by_day = defaultdict(list)
    for bar in bars:
        by_day[bar["t"].date()].append(bar)
    # drop thin days (half sessions / data gaps)
    return {d: b for d, b in sorted(by_day.items()) if len(b) >= 300}


def run(config, by_day):
    iv, slip = config["backtest"]["iv"], config["backtest"]["slippage"]
    exit_at = hhmm(config["exit_time"])
    days = list(by_day)
    events = journal.load_events()
    contexts, prev = {}, None
    for day, bars in by_day.items():
        contexts[day] = day_context(day, events, prev, bars[0]["o"])
        prev = bars[-1]["c"]
    results = []
    for variant in config["variants"]:
        if variant["signal"] in LIVE_ONLY_SIGNALS:
            continue
        trades = {}
        for day, bars in by_day.items():
            trade = simulate_day(bars, variant, iv, slip, exit_at, contexts[day])
            if trade:
                trades[day] = trade
        pnl = [t["pnl_pct"] for t in trades.values()]
        on_event = [t["pnl_pct"] for d, t in trades.items() if contexts[d]["events"]]
        off_event = [t["pnl_pct"] for d, t in trades.items() if not contexts[d]["events"]]
        wins = [p for p in pnl if p > 0]
        losses = [p for p in pnl if p <= 0]
        start = config["backtest"]["start_equity"]
        results.append({
            "id": variant["id"], "trades": len(pnl),
            "hero": {r: hero_odds(pnl, r, start, HERO_TARGET, config["dead_equity"])
                     for r in SIZINGS},
            "win_rate": len(wins) / len(pnl) if pnl else 0,
            "avg_win": sum(wins) / len(wins) if wins else 0,
            "avg_loss": sum(losses) / len(losses) if losses else 0,
            "expectancy": sum(pnl) / len(pnl) if pnl else 0,
            "best": max(pnl) if pnl else 0,
            "event": (len(on_event), sum(on_event) / len(on_event) if on_event else 0),
            "non_event": (len(off_event), sum(off_event) / len(off_event) if off_event else 0),
            "reasons": _count(t["reason"] for t in trades.values()),
            **compound(trades, days, config),
        })
    return days, sorted(results, key=lambda r: r["expectancy"], reverse=True)


def _count(items):
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1
    return dict(counts)


def realized_vol(by_day):
    """Annualised intraday (09:30-16:00) volatility from 1-minute log returns."""
    rets = [math.log(b[i]["c"] / b[i - 1]["c"]) for b in by_day.values() for i in range(1, len(b))]
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var * TRADING_MINUTES_PER_YEAR)


def report(config, days, results, rv=None):
    lines = [
        f"# Backtest — {config['underlying']} 0DTE, {days[0]} → {days[-1]} ({len(days)} days)",
        "",
        f"Model: Black-Scholes at IV {config['backtest']['iv']:.0%}, slippage "
        f"{config['backtest']['slippage']:.0%} + $0.01 each side, start "
        f"${config['backtest']['start_equity']}, phase sizing from config. "
        "Option prices are modelled, not real quotes — use this to rank ideas.",
        "",
        f"Realised intraday vol over the period: {rv:.1%} (if far from the IV above, "
        "recalibrate `backtest.iv` against live quotes from `python -m zoh.check`)."
        if rv is not None else "",
        "",
        "| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | "
        "peak $ | max DD | 2x / 5x / 10x | ruined |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        ms = " / ".join(str(r["milestones"].get(m, "—")) for m in (2, 5, 10))
        lines.append(
            f"| {r['id']} | {r['trades']} | {r['win_rate']:.0%} | {r['avg_win']:+.0%} | "
            f"{r['avg_loss']:+.0%} | {r['expectancy']:+.1%} | {r['best']:+.0%} | "
            f"{r['final']:,.0f} | {r['peak']:,.0f} | {r['max_dd']:.0%} | {ms} | "
            f"{r['ruined_on'] or '—'} |")
    lines += ["", f"## Odds of $500 → ${HERO_TARGET:,} before ruin (bootstrap of each variant's "
              "trades, stake = % of equity per trade)", "",
              "| variant | " + " | ".join(f"{r:.0%} stake" for r in SIZINGS) + " |",
              "|---|" + "---|" * len(SIZINGS)]
    for r in sorted(results, key=lambda r: max(r["hero"].values()), reverse=True):
        lines.append(f"| {r['id']} | " + " | ".join(f"{r['hero'][s]:.1%}" for s in SIZINGS)
                     + " |")
    lines += ["", "## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade", "",
              "| variant | macro-day trades | macro-day avg | other trades | other avg |",
              "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {r['event'][0]} | {r['event'][1]:+.1%} | "
                     f"{r['non_event'][0]} | {r['non_event'][1]:+.1%} |")
    live_only = [v["id"] for v in config["variants"] if v["signal"] in LIVE_ONLY_SIGNALS]
    if live_only:
        lines += ["", f"Live-only variants (no history to backtest): {', '.join(live_only)}"]
    lines += ["", "Exit reasons:", ""]
    lines += [f"- {r['id']}: {r['reasons']}" for r in results]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365, help="calendar days of history")
    parser.add_argument("--out", help="also write the markdown report here")
    args = parser.parse_args()
    config = journal.load_config()
    by_day = load_days(Alpaca(), config["underlying"], args.days)
    days, results = run(config, by_day)
    text = report(config, days, results, realized_vol(by_day))
    print(text)
    if args.out:
        out = journal.ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)


if __name__ == "__main__":
    main()
