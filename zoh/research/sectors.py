"""Sector rotation follow on real option prices (Sunday test 22a).

Each day at 10:00 ET, the sector ETF with the biggest move from its open beyond SPY's (XLV, XLF,
XLE, XLY, XLI, XLP, IWM) is bought if that lead is >= 0.8%: a ~0.2-delta call (also 0.10 / 0.30),
nearest expiry. "Heating" adds the condition that the ETF's prior 5-day return beat SPY's.
Contracts, exits and costs as in zoh/research/exits.py (10% each way). 2026-10-20 was the
example: XLV +2.2% with no single-stock news while QQQ was flat.

    python -m zoh.research.sectors
"""
import json
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca
from ..realopt import START, daily_raw
from ..strategy import ET
from . import exits
from .opendrive import macro_days
from .scanners import bar_at, opening_bars

ETFS = ["XLV", "XLF", "XLE", "XLY", "XLI", "XLP", "IWM"]
DAILY = {"IWM"}
LEAD = 0.008
OUT = journal.ROOT / "journal" / "research"
exits.DELTAS["sector"] = (0.10, 0.20, 0.30)


def expiry_for(sym, day):
    if sym in DAILY:
        return day
    return exits.nearest_expiry(sym, day)  # Friday weeklies


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    macro = macro_days()
    closes = {s: {d: c for d, _, c in daily_raw(api, s, START - timedelta(days=20), end)}
              for s in ETFS + ["SPY"]}
    days = sorted(d for d in closes["SPY"] if d >= START)
    rows = []
    for i, day in enumerate(days):
        bars = opening_bars(api, ETFS + ["SPY"], day, 31)
        spy = bars.get("SPY") or []
        ref = bar_at(spy, 30)
        if not spy or not ref:
            continue
        spy_ret = ref["c"] / spy[0]["o"] - 1
        prior = [d for d in days[:i]][-6:]
        best = None
        for s in ETFS:
            b = bar_at(bars.get(s) or [], 30)
            if not b:
                continue
            lead = b["c"] / bars[s][0]["o"] - 1 - spy_ret
            if lead >= LEAD and (best is None or lead > best[1]):
                best = (s, lead, b)
        if not best:
            continue
        s, lead, b = best
        heating = None
        if len(prior) == 6 and all(prior[k] in closes[s] for k in (0, 5)):
            wk = closes[s][prior[5]] / closes[s][prior[0]] - 1
            wk_spy = closes["SPY"][prior[5]] / closes["SPY"][prior[0]] - 1
            heating = wk > wk_spy
        exp = expiry_for(s, day)
        if not exp:
            continue
        r = exits.price(api, s, day, exp, (b["t"] + timedelta(minutes=1)).time(), b["c"], "call",
                        "sector", None, lead=round(lead, 4), heating=heating,
                        macro=",".join(macro.get(day.isoformat(), [])))
        if r:
            rows.append(r)
        if i % 40 == 0:
            print(day, len(rows), flush=True)
    (OUT / "sectors.json").write_text(json.dumps(rows, indent=0) + "\n")
    (OUT / "SECTORS.md").write_text(report(rows, end))
    print(report(rows, end))


def report(rows, end):
    recent = (end - timedelta(days=91)).isoformat()
    year = (end - timedelta(days=365)).isoformat()
    lines = ["# Sector rotation follow on real option prices", "",
             f"Rule in the module docstring (zoh/research/sectors.py). Data {START} to {end}. Costs 10% "
             "each way. Columns: n | win% | avg | without the best | without the best two.", ""]
    groups = {"all signals": lambda r: True,
              "heating (prior week beat SPY)": lambda r: r.get("heating") is True,
              "not heating": lambda r: r.get("heating") is False,
              "no macro release": lambda r: not r.get("macro"),
              "lead >= 1.2%": lambda r: r["lead"] >= 0.012}
    for name, f in groups.items():
        lines += [f"## {name}", "", "| contract | exit | last 3 months | last year | all |", "|---|---|---|---|---|"]
        for lab in ("d0.10", "d0.20", "d0.30"):
            for rule in ("trail2x", "half3_trail", "hold"):
                cells = []
                for cut in (recent, year, ""):
                    cells.append(exits.stats([r["picks"][lab]["exits_10"][rule] for r in rows
                                              if f(r) and r["day"] >= cut and lab in r["picks"]]))
                lines.append(f"| {lab} | {rule} | " + " | ".join(cells) + " |")
        lines.append("")
    by_sym = {}
    for r in rows:
        if "d0.20" in r["picks"]:
            by_sym.setdefault(r["sym"], []).append(r["picks"]["d0.20"]["exits_10"]["trail2x"])
    lines += ["## By ETF (0.20 delta, trail2x, all)", "", "| ETF | n | win% | avg | w/o best | w/o best 2 |",
              "|---|---|---|---|---|---|"]
    for s, xs in sorted(by_sym.items()):
        lines.append(f"| {s} | {exits.stats(xs)} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
