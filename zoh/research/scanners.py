"""Two live scanners on real option prices (Sunday tests 12 and 15).

leader: each day, the large cap with the biggest move from the open beyond SPY's, after N minutes
  (5 / 10 / 15 / 30 with thresholds 1.0 / 1.5 / 1.5 / 2.0%), buys a ~0.2-delta call, nearest expiry.
  leader_follow trades the 15-minute / 1.5% version.
gapfade: a large cap gaps up >= 2%; 15 minutes after the open it is >= 0.2% below its open -> ~0.15
  delta put, nearest expiry (gapup_fade). Also without the confirmation, and by gap size.
Contracts, exits and costs as in zoh/research/exits.py (same price() helper, every exit rule).

    python -m zoh.research.scanners
"""
import json
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import DATA_URL, Alpaca, AlpacaError
from ..realopt import START
from ..strategy import ET, MARKET_OPEN, hhmm, parse_bar, regular_session
from . import exits
from .opendrive import macro_days

LEADERS = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "AVGO", "AMD", "MU", "NFLX", "ORCL",
           "CRM", "PLTR", "INTC", "COIN"]
FADERS = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "AVGO", "AMD", "MU", "NFLX", "ORCL",
          "CRM", "PLTR", "COIN", "UNH", "JPM", "GS"]
ENTRIES = ((5, 1.0), (10, 1.5), (15, 1.5), (30, 2.0))
OUT = journal.ROOT / "journal" / "research"
exits.DELTAS.update({"leader": (0.10, 0.20, 0.30), "gapfade": (0.10, 0.15, 0.30)})


def opening_bars(api, symbols, day, minutes):
    start = datetime.combine(day, MARKET_OPEN, ET)
    params = {"symbols": ",".join(symbols), "timeframe": "1Min", "start": start.isoformat(),
              "end": (start + timedelta(minutes=minutes + 1)).isoformat(), "feed": "sip",
              "limit": 10000, "adjustment": "raw"}
    out = {}
    try:
        for page in api._paged(f"{DATA_URL}/v2/stocks/bars", params, "bars"):
            for s, bars in (page or {}).items():
                out.setdefault(s, []).extend(bars)
    except AlpacaError:
        return {}
    return {s: regular_session([parse_bar(b) for b in bars]) for s, bars in out.items()}


def bar_at(bars, minute):
    t = (datetime.combine(datetime(2000, 1, 1), MARKET_OPEN) + timedelta(minutes=minute - 1)).time()
    return next((b for b in bars if b["t"].time() >= t), None)


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    macro = macro_days()
    daily = {}
    params = {"symbols": ",".join(sorted(set(LEADERS + FADERS + ["SPY"]))), "timeframe": "1Day",
              "start": (START - timedelta(days=10)).isoformat(), "end": end.isoformat(), "feed": "sip",
              "limit": 10000, "adjustment": "raw"}  # raw, like the minute bars: no split mismatch
    for page in api._paged(f"{DATA_URL}/v2/stocks/bars", params, "bars"):
        for sym, bars in (page or {}).items():
            daily.setdefault(sym, []).extend(bars)
    closes = {s: {datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date(): (b["o"], b["c"])
                  for b in bars} for s, bars in daily.items()}
    days = sorted(d for d in closes.get("SPY", {}) if d >= START)
    rows = []
    for i, day in enumerate(days):
        if macro.get(day.isoformat()):
            continue
        prev = days[i - 1] if i else None
        bars = opening_bars(api, sorted(set(LEADERS + FADERS + ["SPY"])), day, 31)
        spy = bars.get("SPY") or []
        for minutes, thr in ENTRIES:
            ref = bar_at(spy, minutes)
            if not ref or not spy:
                continue
            spy_ret = ref["c"] / spy[0]["o"] - 1
            best = None
            for s in LEADERS:
                b = bar_at(bars.get(s) or [], minutes)
                if not b:
                    continue
                rel = b["c"] / bars[s][0]["o"] - 1 - spy_ret
                if rel * 100 >= thr and (best is None or rel > best[1]):
                    best = (s, rel, b)
            if best:
                s, rel, b = best
                exp = exits.nearest_expiry(s, day)
                if exp:
                    r = exits.price(api, s, day, exp, (b["t"] + timedelta(minutes=1)).time(), b["c"], "call",
                                    "leader", None, entry_min=minutes, rel=round(rel, 4))
                    if r:
                        rows.append(r)
        if prev:
            for s in FADERS:
                pc = closes.get(s, {}).get(prev)
                sb = bars.get(s) or []
                b = bar_at(sb, 15)
                if not pc or not sb or not b:
                    continue
                gap = sb[0]["o"] / pc[1] - 1
                if gap < 0.02:
                    continue
                below = b["c"] / sb[0]["o"] - 1
                exp = exits.nearest_expiry(s, day)
                if exp:
                    r = exits.price(api, s, day, exp, (b["t"] + timedelta(minutes=1)).time(), b["c"], "put",
                                    "gapfade", None, gap=round(gap, 4), below_open=round(below, 4),
                                    confirmed=below <= -0.002)
                    if r:
                        rows.append(r)
        if i % 20 == 0:
            print(day, len(rows), flush=True)
    (OUT / "scanners.json").write_text(json.dumps(rows, indent=0) + "\n")

    recent = (end - timedelta(days=91)).isoformat()
    lines = ["# Leader follow and gap-up fade on real option prices", "",
             "Entries in the module docstring (zoh/research/scanners.py); contracts, exits and costs as in "
             "EXITS.md (10% each way). Columns: n | win% | avg | without the best | without the best two.", ""]

    def table(title, sel):
        nonlocal lines
        labs = sorted({k for r in sel for k in r["picks"]})
        lines += [f"## {title}", "", "| contract | exit | last 3 months | all |", "|---|---|---|---|"]
        for lab in labs:
            for rule in ("trail2x", "trail1.5x", "half3_trail", "hold"):
                rec = [r["picks"][lab]["exits_10"][rule] for r in sel if r["day"] >= recent and lab in r["picks"]]
                al = [r["picks"][lab]["exits_10"][rule] for r in sel if lab in r["picks"]]
                lines.append(f"| {lab} | {rule} | {exits.stats(rec)} | {exits.stats(al)} |")
        lines.append("")

    for minutes, thr in ENTRIES:
        table(f"leader, {minutes} minutes, >= {thr}% beyond SPY",
              [r for r in rows if r["study"] == "leader" and r["entry_min"] == minutes])
    fade = [r for r in rows if r["study"] == "gapfade"]
    table("gap-up fade, confirmed (>= 0.2% below the open at 09:45; the live rule)", [r for r in fade if r["confirmed"]])
    table("gap-up fade, no confirmation", fade)
    for lo, hi in ((0.02, 0.04), (0.04, 0.06), (0.06, 9)):
        table(f"gap-up fade, confirmed, gap {lo:.0%}-{hi:.0%}" if hi < 9 else "gap-up fade, confirmed, gap > 6%",
              [r for r in fade if r["confirmed"] and lo <= r["gap"] < hi])
    (OUT / "SCANNERS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:80]))


if __name__ == "__main__":
    main()
