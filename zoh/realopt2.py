"""The other live rules re-tested on real historical option prices (Alpaca option bars, 2024-02+).

A. Analyst rating changes before the open (catalyst_open / catalyst_sniper style):
   open: buy at 09:31 if the stock is not against the rating, ~0.1 delta;
   confirm: buy when the stock is >= 1% from the open in the rating's direction (09:45-12:00),
   ~0.2 delta. Upgrades -> calls, downgrades -> puts. Nearest expiry on or after the day.
B. semis_flush: AMD/NVDA/MU, same-day expiry days; the first 15 minutes push >= 2% beyond the
   open, then price takes back half -> reversal option, ~0.08 delta, before 11:00.
C. meta_follow2: META, same-day expiry days, after 10:00 and before 14:00 a move of >= 2% from the
   open -> follow it, ~0.2 delta.

Exits as in the live bot: trail after doubling (40% giveback, not below cost) or 15:45.
Costs: option close +/-10% (and 5%), at least $0.01.

    python -m zoh.realopt2
"""
import json
import statistics
import time
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .analyst import SYMBOLS, rating_events
from .backtest import hero_odds
from .realopt import SLIPS, START, has_same_day_expiry, pick_and_trade
from .strategy import ET, MARKET_OPEN, hhmm, parse_bar, regular_session, signal_flush


def minutes(api, sym, day, until="16:00"):
    start = datetime.combine(day, MARKET_OPEN, ET)
    end = datetime.combine(day, hhmm(until), ET)
    try:
        raw = api.stock_bars(sym, start, end, feed="sip", adjustment="raw")
    except AlpacaError:
        return []
    return regular_session([parse_bar(b) for b in raw])


def next_expiry(sym, day):
    d = day
    for _ in range(7):
        if d.weekday() < 5 and has_same_day_expiry(sym, d):
            return d
        d += timedelta(days=1)
    return None


def trade(api, rows, label, sym, day, t, spot, kind, delta, expiry=None, **extra):
    try:
        r = pick_and_trade(api, sym, day, t, spot, kind, delta, expiry)
    except AlpacaError:
        r = None
    time.sleep(0.15)
    if r:
        rows.append({"study": label, "sym": sym, "day": day.isoformat(), "kind": kind, **extra, **r})


def study_analyst(api, rows, end):
    for sym in SYMBOLS:
        for day, direction, headline in rating_events(api, sym, START, end):
            exp = next_expiry(sym, day)
            if not exp:
                continue
            bars = minutes(api, sym, day, "12:05")
            if len(bars) < 20:
                continue
            o = bars[0]["o"]
            sign = 1 if direction == "call" else -1
            b931 = next((b for b in bars if b["t"].time() >= hhmm("09:31")), None)
            if b931 and sign * (b931["c"] / o - 1) >= 0:
                trade(api, rows, f"analyst_open_{'up' if sign > 0 else 'down'}", sym, day,
                      (b931["t"] + timedelta(minutes=1)).time(), b931["c"], direction, 0.10, exp,
                      expiry_day=exp.isoformat(), headline=headline[:80])
            hit = next((b for b in bars if hhmm("09:45") <= b["t"].time() <= hhmm("12:00")
                        and sign * (b["c"] / o - 1) >= 0.01), None)
            if hit:
                trade(api, rows, f"analyst_confirm_{'up' if sign > 0 else 'down'}", sym, day,
                      (hit["t"] + timedelta(minutes=1)).time(), hit["c"], direction, 0.20, exp,
                      expiry_day=exp.isoformat(), headline=headline[:80])
        print(f"analyst {sym}: {sum(1 for r in rows if r['sym'] == sym and r['study'].startswith('analyst'))}",
              flush=True)


def expiry_days(sym, start, end):
    d = start
    while d <= end:
        if d.weekday() < 5 and has_same_day_expiry(sym, d):
            yield d
        d += timedelta(days=1)


def study_flush(api, rows, end):
    variant = {"flush_minutes": 15, "flush_pct": 2.0, "reclaim": 0.5}
    for sym in ("AMD", "NVDA", "MU"):
        for day in expiry_days(sym, START, end):
            bars = minutes(api, sym, day, "11:01")
            if len(bars) < 30:
                continue
            for i in range(15, len(bars)):
                if bars[i]["t"].time() > hhmm("11:00"):
                    break
                d = signal_flush(bars[:i + 1], variant)
                if d:
                    trade(api, rows, "semis_flush", sym, day, (bars[i]["t"] + timedelta(minutes=1)).time(),
                          bars[i]["c"], d, 0.08)
                    break
        print(f"flush {sym}: {sum(1 for r in rows if r['sym'] == sym and r['study'] == 'semis_flush')}",
              flush=True)


def study_meta_follow(api, rows, end):
    for day in expiry_days("META", START, end):
        bars = minutes(api, "META", day, "14:01")
        if len(bars) < 40:
            continue
        o = bars[0]["o"]
        hit = next((b for b in bars if hhmm("10:00") <= b["t"].time() <= hhmm("14:00")
                    and abs(b["c"] / o - 1) >= 0.02), None)
        if hit:
            kind = "call" if hit["c"] > o else "put"
            trade(api, rows, "meta_follow2", "META", day, (hit["t"] + timedelta(minutes=1)).time(),
                  hit["c"], kind, 0.20)
    print(f"meta_follow2: {sum(1 for r in rows if r['study'] == 'meta_follow2')}", flush=True)


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    rows = []
    study_analyst(api, rows, end)
    study_flush(api, rows, end)
    study_meta_follow(api, rows, end)
    recent = (end - timedelta(days=91)).isoformat()

    def pct(x):
        return f"{x:+.0%}"

    lines = ["# Live rules on real option prices (Alpaca option bars)", "",
             "See the module docstring of zoh/realopt2.py for the exact rules. Exits: trail after "
             "doubling (40% giveback, not below cost) or 15:45. Costs: option close +/-10% (5% in "
             "brackets).", "",
             "| rule | period | trades | win% | avg / trade (5%) | median | best | >= 2x | odds $500->$2k (50%) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for study in sorted({r["study"] for r in rows}):
        for name, cut in (("all", "0000"), ("last 3 months", recent), ("since 2026-01-26", "2026-01-26")):
            sel = [r for r in rows if r["study"] == study and r["day"] >= cut]
            if not sel:
                continue
            p = [r["pnl_10"] for r in sel]
            p5 = [r["pnl_5"] for r in sel]
            lines.append(f"| {study} | {name} | {len(p)} | {sum(x > 0 for x in p) / len(p):.0%} | "
                         f"{pct(sum(p) / len(p))} ({pct(sum(p5) / len(p5))}) | {pct(statistics.median(p))} | "
                         f"{pct(max(p))} | {sum(x >= 1 for x in p)} | {hero_odds(p, 0.5, 500, 2000, 50):.0%} |")
    lines += ["", "## Every trade (10% costs)", "", "| rule | day | stock | contract | delta | entry px | pnl | why |",
              "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["study"], r["day"])):
        lines.append(f"| {r['study']} | {r['day']} | {r['sym']} | {r['contract']} | {r['delta']} | {r['px']} | "
                     f"{pct(r['pnl_10'])} | {r['why_10']} |")
    out = journal.ROOT / "journal" / "research"
    (out / "REALOPT2.md").write_text("\n".join(lines) + "\n")
    (out / "realopt2.json").write_text(json.dumps(rows, indent=1))
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
