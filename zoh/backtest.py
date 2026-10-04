"""Quick validation: replay every variant on historical SPY 1-minute bars.

Option prices are modelled with Black-Scholes at a flat IV (config backtest.iv) plus
slippage, because free historical 0DTE option quotes are not available. Treat results as
a ranking of ideas, not a P&L forecast: real 0DTE skew, spreads and IV crush differ.

    python -m zoh.backtest --days 365 [--out journal/BACKTEST.md]
"""
import argparse
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca
from .strategy import (ET, MARKET_CLOSE, bs_delta, bs_price, check_exit, contracts_for,
                       current_phase, evaluate_signal, hhmm, parse_bar, regular_session,
                       years_to_close)


def pick_strike(spot, years, iv, kind, target_delta):
    strikes = [round(spot) + k for k in range(-20, 21)]
    return min(strikes, key=lambda k: abs(abs(bs_delta(spot, k, years, iv, kind)) - target_delta))


def simulate_day(bars, variant, iv, slip, exit_at):
    """One variant on one day. Returns a trade dict or None."""
    pos = None
    for i, bar in enumerate(bars):
        now = bar["t"] + timedelta(minutes=1)
        years = years_to_close(now)
        if pos is None:
            if now.time() > hhmm(variant.get("entry_cutoff", "13:00")) or now.time() >= exit_at:
                return None
            direction = evaluate_signal(bars[:i + 1], variant)
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
    results = []
    for variant in config["variants"]:
        trades = {}
        for day, bars in by_day.items():
            trade = simulate_day(bars, variant, iv, slip, exit_at)
            if trade:
                trades[day] = trade
        pnl = [t["pnl_pct"] for t in trades.values()]
        wins = [p for p in pnl if p > 0]
        losses = [p for p in pnl if p <= 0]
        results.append({
            "id": variant["id"], "trades": len(pnl),
            "win_rate": len(wins) / len(pnl) if pnl else 0,
            "avg_win": sum(wins) / len(wins) if wins else 0,
            "avg_loss": sum(losses) / len(losses) if losses else 0,
            "expectancy": sum(pnl) / len(pnl) if pnl else 0,
            "best": max(pnl) if pnl else 0,
            "reasons": _count(t["reason"] for t in trades.values()),
            **compound(trades, days, config),
        })
    return days, sorted(results, key=lambda r: r["expectancy"], reverse=True)


def _count(items):
    counts = defaultdict(int)
    for item in items:
        counts[item] += 1
    return dict(counts)


def report(config, days, results):
    lines = [
        f"# Backtest — {config['underlying']} 0DTE, {days[0]} → {days[-1]} ({len(days)} days)",
        "",
        f"Model: Black-Scholes at IV {config['backtest']['iv']:.0%}, slippage "
        f"{config['backtest']['slippage']:.0%} + $0.01 each side, start "
        f"${config['backtest']['start_equity']}, phase sizing from config. "
        "Option prices are modelled, not real quotes — use this to rank ideas.",
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
    text = report(config, days, results)
    print(text)
    if args.out:
        (journal.ROOT / args.out).write_text(text)


if __name__ == "__main__":
    main()
