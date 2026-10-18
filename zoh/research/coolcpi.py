"""Buy a call at the close of a cool CPI day, sell one or two days later (Sunday test 21).

MACRO_SURPRISE.md: SPY rose over the two days after a cool CPI on 74% of 34 prints since 2019-12,
positive in every period. Here the option version on real prices (Alpaca option bars, 2024-02+):
at 15:50 on the release day buy the SPY / QQQ call expiring about a week later, at the money and
1% out of the money; sell at 15:50 one and two trading days later. HOT and INLINE CPIs and the NFP
classes are the controls. Classes: claude-c's calendar (exchange/claude-c/...macro-surprises-2019-12.json).

    python -m zoh.research.coolcpi
"""
import json
from datetime import date, datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import START, at_or_after, daily_raw, occ, option_minutes
from ..strategy import ET, MARKET_OPEN, hhmm, parse_bar, regular_session

CAL = journal.ROOT / "exchange" / "claude-c" / "2026-10-16.macro-surprises-2019-12.json"
OUT = journal.ROOT / "journal" / "research"
SLIPS = (0.10, 0.05)
AT = hhmm("15:50")


def bid(c, slip):
    return max(0.0, min(c * (1 - slip), c - 0.01))


def close_at(api, sym, day):
    start = datetime.combine(day, MARKET_OPEN, ET)
    try:
        bars = regular_session([parse_bar(b) for b in api.stock_bars(
            sym, start + timedelta(hours=6), start + timedelta(hours=6, minutes=25), feed="sip", adjustment="raw")])
    except AlpacaError:
        return None
    b = at_or_after(bars, hhmm("15:49"), 3)
    return b["c"] if b else None


def option_close(api, contract, day):
    try:
        bars = option_minutes(api, [contract], day).get(contract, [])
    except AlpacaError:
        return None
    b = at_or_after(bars, AT, 9)
    return b["c"] if b else None


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    events = [e for e in json.loads(CAL.read_text())["events"]
              if e["class"] and date.fromisoformat(e["date"]) >= START]
    rows = []
    for sym in ("SPY", "QQQ"):
        days = [d for d, _, _ in daily_raw(api, sym, START, end)]
        for e in events:
            day = date.fromisoformat(e["date"])
            if day not in days or days.index(day) + 2 >= len(days):
                continue
            i = days.index(day)
            spot = close_at(api, sym, day)
            if not spot:
                continue
            for label, k in (("atm", round(spot)), ("otm1", round(spot * 1.01))):
                for add in range(7, 13):  # first listed expiry about a week out
                    expiry = day + timedelta(days=add)
                    if expiry.weekday() >= 5:
                        continue
                    c = occ(sym, expiry, k)
                    px = option_close(api, c, day)
                    if px:
                        break
                else:
                    continue
                row = {"sym": sym, "day": e["date"], "event": e["event"], "class": e["class"], "pick": label,
                       "contract": c, "px": px, "spot": spot}
                for n in (1, 2):
                    later = option_close(api, c, days[i + n])
                    if later is None:
                        continue
                    for slip in SLIPS:
                        entry = max(px * (1 + slip), px + 0.01)
                        row[f"d{n}_{int(slip * 100)}"] = round(bid(later, slip) / entry - 1, 4)
                rows.append(row)
        print(sym, sum(r["sym"] == sym for r in rows), flush=True)
    (OUT / "coolcpi.json").write_text(json.dumps(rows, indent=0) + "\n")

    def st(xs):
        if not xs:
            return "- | - | - | - | -"
        s = sorted(xs)
        a = lambda v: f"{sum(v) / len(v):+.0%}" if v else "-"
        return f"{len(s)} | {sum(x > 0 for x in s) / len(s):.0%} | {a(s)} | {a(s[:-1])} | {a(s[:-2])}"

    recent = (end - timedelta(days=183)).isoformat()
    lines = ["# Call bought at the close of a release day, sold one or two days later", "",
             "Real option prices (Alpaca), 2024-02+. Entry 15:50 on the release day, exit 15:50 one (d1) or "
             "two (d2) trading days later, ~1-week expiry. Costs 10% each way. Columns: n | win% | avg | "
             "without the best | without the best two.", "",
             "| event | class | stock | pick | period | d1: n | win | avg | -best | -best2 | d2: n | win | avg | -best | -best2 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for ev in ("CPI", "NFP"):
        for cl in ("COOL", "INLINE", "HOT"):
            for sym in ("SPY", "QQQ"):
                for pick in ("atm", "otm1"):
                    for period, cut in (("all", "0000"), ("last 6 months", recent)):
                        sel = [r for r in rows if r["event"] == ev and r["class"] == cl and r["sym"] == sym
                               and r["pick"] == pick and r["day"] >= cut]
                        if sel:
                            lines.append(f"| {ev} | {cl} | {sym} | {pick} | {period} | "
                                         f"{st([r['d1_10'] for r in sel if 'd1_10' in r])} | "
                                         f"{st([r['d2_10'] for r in sel if 'd2_10' in r])} |")
    (OUT / "COOLCPI.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
