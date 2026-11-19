"""The oversold-ETF rule as a shadow record: one line a trade, stock only, no orders (on trial since 2026-11-19).

Rule, as published and not tuned (journal/research/OVERSOLD.md: +0.37% a trade on 2005-2016 and on 2017-2026):
  buy the close when RSI(2) is under 10 and the close is above its 200-day average;
  sell the first close above the 5-day average, or the tenth close after the entry.
Every signal on the 14 ETFs is recorded, without a slot limit, so the log is the per-trade number; the account view
(five slots, against SPY held) is computed from it. The entry is that day's official close, which a person only gets
with an order in the last minutes; the note says how much is lost by buying the next open.

    python -m zoh.research.oversold --today      # after the close: exits first, then new signals
"""
import argparse
import csv
import statistics as st
from datetime import datetime, timedelta, timezone

from .. import journal

ETFS = ["SPY", "QQQ", "IWM", "DIA", "SMH", "XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "IGV"]
LOG = journal.ROOT / "journal" / "oversold.csv"
FIELDS = ["symbol", "entry_date", "entry_close", "exit_date", "exit_close", "days", "pct"]
COST_PCT = 0.05          # a round trip, as in the study
RSI_UNDER, LONG_AVG, EXIT_AVG, MAX_DAYS, RUN_IN = 10.0, 200, 5, 10, 30


def rsi2(closes):
    """RSI(2) at the last close, smoothed over the last RUN_IN changes (the study's own version)."""
    gain = loss = None
    for a, b in zip(closes[-RUN_IN - 2:-1], closes[-RUN_IN - 1:]):
        up, down = max(b - a, 0.0), max(a - b, 0.0)
        gain, loss = (up, down) if gain is None else ((gain + up) / 2, (loss + down) / 2)
    if not loss:
        return 100.0
    return 100.0 - 100.0 / (1.0 + gain / loss)


def is_signal(closes):
    return len(closes) >= LONG_AVG + 1 and rsi2(closes) < RSI_UNDER and closes[-1] > st.mean(closes[-LONG_AVG:])


def is_exit(closes):
    return closes[-1] > st.mean(closes[-EXIT_AVG:])


def step(rows, bars, today):
    """Apply one close to the log. `bars` is {symbol: [(date, close), ...]} ending at `today`; rows are dicts.
    Running it twice for the same day changes nothing."""
    rows = [dict(r) for r in rows]
    for sym in ETFS:
        series = [(d, c) for d, c in bars.get(sym, []) if d <= today]
        if not series or series[-1][0] != today:
            continue
        closes = [c for _, c in series]
        held = next((r for r in rows if r["symbol"] == sym and not r.get("exit_date")), None)
        if held:
            if held["entry_date"] == today:
                continue
            days = sum(1 for d, _ in series if d > held["entry_date"])
            if is_exit(closes) or days >= MAX_DAYS:
                entry = float(held["entry_close"])
                held.update(exit_date=today, exit_close=f"{closes[-1]:.2f}", days=str(days),
                            pct=f"{(closes[-1] / entry - 1) * 100 - COST_PCT:.2f}")
            continue
        if is_signal(closes):
            rows.append({"symbol": sym, "entry_date": today, "entry_close": f"{closes[-1]:.2f}", "exit_date": "",
                         "exit_close": "", "days": "", "pct": ""})
    return rows


def load():
    if not LOG.exists():
        return []
    with LOG.open() as f:
        return list(csv.DictReader(f))


def save(rows):
    with LOG.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def summary(rows, today):
    done = [float(r["pct"]) for r in rows if r.get("pct")]
    held = [r for r in rows if not r.get("exit_date")]
    new = [r["symbol"] for r in held if r["entry_date"] == today]
    out = [f"oversold-ETF shadow record at the {today} close: new {', '.join(new) or 'none'}; "
           f"held {', '.join(r['symbol'] + ' since ' + r['entry_date'] for r in held) or 'none'}"]
    closed_today = [r for r in rows if r.get("exit_date") == today]
    for r in closed_today:
        out.append(f"  closed {r['symbol']} {r['entry_date']} {r['entry_close']} -> {r['exit_close']} "
                   f"({r['days']} days, {float(r['pct']):+.2f}%)")
    if done:
        out.append(f"  closed so far: {len(done)}, {sum(1 for x in done if x > 0)} winners, average {st.mean(done):+.2f}%")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", action="store_true", help="apply the last close to journal/oversold.csv")
    args = ap.parse_args()
    if not args.today:
        ap.error("nothing to do without --today")
    from ..alpaca import Alpaca
    end = datetime.now(timezone.utc) - timedelta(minutes=20)
    raw = Alpaca().daily_bars_multi(ETFS, end - timedelta(days=330), end)
    bars = {s: [(b["t"][:10], b["c"]) for b in v] for s, v in raw.items()}
    today = max(v[-1][0] for v in bars.values() if v)
    rows = step(load(), bars, today)
    save(rows)
    print(summary(rows, today))


if __name__ == "__main__":
    main()
