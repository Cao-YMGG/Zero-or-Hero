"""megacap_reclaim on real option prices (it had no real-price study; Sunday review 2026-11-01).

The live rule: one of seven mega caps falls >= 0.5% below its open in the first 15 minutes, then
takes back the whole flush (back to the open) before 12:00 -> buy a ~0.15-delta call on the
nearest expiry; no CPI/NFP/FOMC days. The first trigger per stock per day, entered the next
minute. Contracts, exits and costs (10% each way) as in zoh/research/exits.py.

    python -m zoh.research.reclaim
"""
import json
from datetime import date, datetime, timedelta

from .. import journal
from ..alpaca import Alpaca
from ..strategy import ET, hhmm, parse_bar, signal_flush
from . import exits
from .opendrive import macro_days
from .scanners import opening_bars

UNIVERSE = ["AAPL", "AMZN", "MSFT", "GOOGL", "META", "NVDA", "TSLA"]
VARIANT = {"flush_minutes": 15, "flush_pct": 0.5, "reclaim": 1.0, "sides": ["down"]}
START = date(2026, 5, 1)
OUT = journal.ROOT / "journal" / "research"
exits.DELTAS["reclaim"] = (0.10, 0.15, 0.30)


def trading_days(api, start, end):
    bars = api.stock_bars("SPY", datetime.combine(start, hhmm("09:30"), ET),
                          datetime.combine(end, hhmm("16:00"), ET), timeframe="1Day", feed="sip")
    return sorted({parse_bar(b)["t"].astimezone(ET).date() for b in bars})


def trigger(bars):
    """First minute from 09:45 to 11:59 at which the live flush signal fires, or None."""
    for i, b in enumerate(bars):
        t = b["t"].time()
        if t < hhmm("09:45"):
            continue
        if t >= hhmm("12:00"):
            break
        if signal_flush(bars[:i + 1], VARIANT):
            return b
    return None


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    macro = macro_days()
    rows = []
    for day in trading_days(api, START, end):
        if macro.get(day.isoformat()):
            continue
        raw = opening_bars(api, UNIVERSE, day, 150)
        for sym in UNIVERSE:
            bars = raw.get(sym, [])
            b = trigger(bars)
            if not b:
                continue
            expiry = exits.nearest_expiry(sym, day)
            if not expiry:
                continue
            r = exits.price(api, sym, day, expiry, (b["t"] + timedelta(minutes=1)).time(), b["c"], "call",
                            "reclaim", None, at=b["t"].strftime("%H:%M"))
            if r:
                rows.append(r)
        print(f"{day}: {len(rows)}", flush=True)
    recent = (end - timedelta(days=91)).isoformat()
    lines = ["# megacap_reclaim on real option prices", "",
             f"{START} to {end}; {', '.join(UNIVERSE)}; flush >= 0.5% in 15 minutes, back to the open before "
             "12:00, nearest expiry, no macro days. Costs 10% each way. Columns: n | win% | avg | without "
             "the best | without the best two. The live rule is d0.15 with `trail2x`. See zoh/research/reclaim.py.",
             "", "| contract | exit | last 3 months | all since May |", "|---|---|---|---|"]
    for lab in ("d0.10", "d0.15", "d0.30"):
        for rule in ("trail2x", "trail1.5x", "half3_trail", "hold"):
            xs = [r["picks"][lab]["exits_10"][rule] for r in rows if lab in r["picks"] and r["day"] >= recent]
            ys = [r["picks"][lab]["exits_10"][rule] for r in rows if lab in r["picks"]]
            lines.append(f"| {lab} | {rule} | {exits.stats(xs)} | {exits.stats(ys)} |")
    (OUT / "reclaim.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    (OUT / "RECLAIM.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
