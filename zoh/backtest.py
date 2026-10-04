"""Quick validation: replay every variant on historical SPY 1-minute bars.

Option prices are modelled with Black-Scholes at a flat IV (config backtest.iv) plus
slippage, because free historical 0DTE option quotes are not available. Treat results as
a ranking of ideas, not a P&L forecast: real 0DTE skew, spreads and IV crush differ.

    python -m zoh.backtest --days 365 [--out journal/BACKTEST.md]
"""
import argparse
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .strategy import (ET, LIVE_ONLY_SIGNALS, cross_assets, TRADING_MINUTES_PER_YEAR, bs_delta, bs_price,
                       check_exit, contracts_for, current_phase, day_context, evaluate_signal,
                       hhmm, parse_bar, regular_session, years_to_close)


def pick_strike(spot, years, iv, kind, target_delta):
    width = max(20, int(spot * 0.08))  # $1 strikes within ±8% (±$20 minimum)
    strikes = [round(spot) + k for k in range(-width, width + 1)]
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
                   "entry_time": now, "spot": bar["c"]}
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
            trade["qty"], trade["equity_after"] = qty, equity
        peak = max(peak, equity)
        max_dd = max(max_dd, 1 - equity / peak if peak else 0)
        for mult in (2, 5, 10):
            if equity >= mult * config["backtest"]["start_equity"] and mult not in milestones:
                milestones[mult] = day
    return {"final": equity, "peak": peak, "max_dd": max_dd, "milestones": milestones,
            "ruined_on": ruined_on}


HERO_TARGET = 2000
ULTRA_TARGETS = (50_000, 500_000)  # the "500 -> 500k" question
SIZINGS = (0.3, 0.5, 1.0)
RECENT_DAYS = 63  # ~3 months: does the edge still hold in the current regime?


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


def load_days(api, symbol, days_back, min_bars=250):
    end = datetime.now(ET) - timedelta(minutes=20)
    start = end - timedelta(days=days_back)
    try:  # full consolidated tape, split-adjusted; IEX is thin for smaller names
        raw = api.stock_bars(symbol, start, end, feed="sip", adjustment="split")
    except AlpacaError as e:
        print(f"{symbol}: SIP unavailable ({e.status}), falling back to IEX")
        raw = api.stock_bars(symbol, start, end, adjustment="split")
    bars = regular_session([parse_bar(b) for b in raw])
    by_day = defaultdict(list)
    for bar in bars:
        by_day[bar["t"].date()].append(bar)
    # drop thin days (half sessions / data gaps)
    return {d: b for d, b in sorted(by_day.items()) if len(b) >= min_bars}


def run(config, by_day, cross_by_day=None, weekdays=None):
    iv, slip = config["backtest"]["iv"], config["backtest"]["slippage"]
    exit_at = hhmm(config["exit_time"])
    days = list(by_day)
    events = journal.load_events()
    contexts, prev = {}, None
    for day, bars in by_day.items():
        cross = {sym: days_.get(day, []) for sym, days_ in (cross_by_day or {}).items()}
        contexts[day] = day_context(day, events, prev, bars[0]["o"], cross=cross)
        prev = bars[-1]["c"]
    results = []
    for variant in config["variants"]:
        if variant["signal"] in LIVE_ONLY_SIGNALS:
            continue
        if variant.get("underlying", config["underlying"]) != config["underlying"]:
            continue  # runs on another stock; backtest it with --underlying
        trades = {}
        for day, bars in by_day.items():
            if weekdays is not None and day.weekday() not in weekdays:
                continue  # no same-day expiry that day (single stocks: Mon/Wed/Fri only)
            trade = simulate_day(bars, variant, iv, slip, exit_at, contexts[day])
            if trade:
                trade["day_oc"] = bars[-1]["c"] / bars[0]["o"] - 1
                trade["gap"] = contexts[day]["gap_pct"]
                trades[day] = trade
        pnl = [t["pnl_pct"] for t in trades.values()]
        on_event = [t["pnl_pct"] for d, t in trades.items() if contexts[d]["events"]]
        off_event = [t["pnl_pct"] for d, t in trades.items() if not contexts[d]["events"]]
        wins = [p for p in pnl if p > 0]
        losses = [p for p in pnl if p <= 0]
        start = config["backtest"]["start_equity"]
        recent_days = set(days[-RECENT_DAYS:])
        recent = [t["pnl_pct"] for d, t in trades.items() if d in recent_days]
        results.append({
            "recent": (len(recent), sum(recent) / len(recent) if recent else 0,
                       hero_odds(recent, 1.0, start, HERO_TARGET, config["dead_equity"])),
            "id": variant["id"], "trades": len(pnl),
            "hero": {r: hero_odds(pnl, r, start, HERO_TARGET, config["dead_equity"])
                     for r in SIZINGS},
            "ultra": {t: hero_odds(pnl, 1.0, start, t, config["dead_equity"], max_trades=1000)
                      for t in ULTRA_TARGETS},
            "multiples": sorted((t["exit"] / t["entry"] for t in trades.values()), reverse=True)[:5],
            "win_rate": len(wins) / len(pnl) if pnl else 0,
            "avg_win": sum(wins) / len(wins) if wins else 0,
            "avg_loss": sum(losses) / len(losses) if losses else 0,
            "expectancy": sum(pnl) / len(pnl) if pnl else 0,
            "best": max(pnl) if pnl else 0,
            "event": (len(on_event), sum(on_event) / len(on_event) if on_event else 0),
            "non_event": (len(off_event), sum(off_event) / len(off_event) if off_event else 0),
            "reasons": _count(t["reason"] for t in trades.values()),
            **compound(trades, days, config),
            "log": sorted(trades.items()),
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


def trade_log(results):
    lines = ["", "## Trade by trade", "",
             "Each variant on its own, $500 start, phase sizing (all-in below $2,000).", ""]
    for r in results:
        if not r["log"]:
            continue
        lines += [f"### {r['id']} — {len(r['log'])} trades, $500 → ${r['final']:,.0f}", "",
                  "| date | gap | stock open→close | entry | side | strike / spot | option in → out "
                  "| multiple | exit | contracts | equity after |",
                  "|---|---|---|---|---|---|---|---|---|---|---|"]
        for day, t in r["log"]:
            gap = f"{t['gap']:+.1f}%" if t.get("gap") is not None else "—"
            lines.append(
                f"| {day} | {gap} | {t['day_oc']:+.1%} | {t['entry_time']:%H:%M} | {t['kind']} | "
                f"{t['strike']} / {t['spot']:.2f} | {t['entry']:.2f} → {t['exit']:.2f} | "
                f"{t['exit'] / t['entry']:.2f}x | {t['reason']} | {t.get('qty', '—')} | "
                f"{'$' + format(t['equity_after'], ',.0f') if 'equity_after' in t else '(not traded: ruined)'} |")
        lines.append("")
    return lines


def report(config, days, results, rv=None, detail=False):
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
    lines += ["", "## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples", "",
              "| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |",
              "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: (r["ultra"][500_000], r["ultra"][50_000]), reverse=True):
        tops = ", ".join(f"{m:.0f}x" for m in r["multiples"])
        lines.append(f"| {r['id']} | {r['trades']} | {r['win_rate']:.0%} | {r['ultra'][50_000]:.2%} | "
                     f"{r['ultra'][500_000]:.2%} | {tops} |")
    lines += ["", f"## Regime check: last {RECENT_DAYS} trading days vs full period", "",
              "If a variant only works in the old part of the sample, the market has moved on.",
              "",
              "| variant | full: trades | full: avg | full: odds (100%) | recent: trades | "
              "recent: avg | recent: odds (100%) | verdict |",
              "|---|---|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: r["recent"][2], reverse=True):
        n, avg, odds = r["recent"]
        full = r["hero"][1.0]
        verdict = ("no recent trades" if n == 0 else "holding up" if odds >= full * 0.8
                   else "fading" if odds >= full * 0.4 else "broken")
        lines.append(f"| {r['id']} | {r['trades']} | {r['expectancy']:+.1%} | {full:.1%} | {n} | "
                     f"{avg:+.1%} | {odds:.1%} | {verdict} |")
    lines += ["", "## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade", "",
              "| variant | macro-day trades | macro-day avg | other trades | other avg |",
              "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['id']} | {r['event'][0]} | {r['event'][1]:+.1%} | "
                     f"{r['non_event'][0]} | {r['non_event'][1]:+.1%} |")
    live_only = [v["id"] for v in config["variants"] if v["signal"] in LIVE_ONLY_SIGNALS]
    if live_only:
        lines += ["", f"Live-only variants (no history to backtest): {', '.join(live_only)}"]
    if detail:
        lines += trade_log(results)
    lines += ["", "Exit reasons:", ""]
    lines += [f"- {r['id']}: {r['reasons']}" for r in results]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365, help="calendar days of history")
    parser.add_argument("--out", help="also write the markdown report here")
    parser.add_argument("--underlying", help="override config underlying, e.g. AMD")
    parser.add_argument("--iv", help="option IV: a number, or 'auto' = realised vol x 1.15")
    parser.add_argument("--slippage", type=float, help="override slippage (single stocks ~0.03)")
    parser.add_argument("--trades", action="store_true", help="append a trade-by-trade log")
    parser.add_argument("--fri", action="store_true",
                        help="trade only Fridays (stocks with weekly options only)")
    parser.add_argument("--json-out", help="also write a machine-readable summary here")
    parser.add_argument("--variants", help="JSON file with a variant list to test instead of config")
    parser.add_argument("--mwf", action="store_true",
                        help="trade only Mon/Wed/Fri (single-stock same-day expiries)")
    args = parser.parse_args()
    config = journal.load_config()
    if args.underlying:
        config["underlying"] = args.underlying
    if args.variants:
        config["variants"] = json.loads((journal.ROOT / args.variants).read_text())
    api = Alpaca()
    by_day = load_days(api, config["underlying"], args.days)
    if args.iv:
        config["backtest"]["iv"] = (round(realized_vol(by_day) * 1.15, 3) if args.iv == "auto"
                                    else float(args.iv))
    if args.slippage is not None:
        config["backtest"]["slippage"] = args.slippage
    cross = {sym: load_days(api, sym, args.days, min_bars=100)
             for sym in cross_assets(config["variants"])}
    weekdays = {0, 2, 4} if args.mwf else {4} if args.fri else None
    days, results = run(config, by_day, cross, weekdays)
    text = report(config, days, results, realized_vol(by_day), args.trades)
    print(text)
    if args.out:
        out = journal.ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    if args.json_out:
        summary = {"underlying": config["underlying"], "iv": config["backtest"]["iv"],
                   "days": len(days), "start": str(days[0]), "end": str(days[-1]),
                   "weekdays": sorted(weekdays) if weekdays else None,
                   "variants": [{
                       "id": r["id"], "trades": r["trades"], "win_rate": r["win_rate"],
                       "expectancy": r["expectancy"], "best": r["best"],
                       "hero": {str(k): v for k, v in r["hero"].items()},
                       "ultra": {str(k): v for k, v in r["ultra"].items()},
                       "recent_n": r["recent"][0], "recent_avg": r["recent"][1],
                       "recent_odds": r["recent"][2], "multiples": r["multiples"],
                   } for r in results]}
        out = journal.ROOT / args.json_out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
