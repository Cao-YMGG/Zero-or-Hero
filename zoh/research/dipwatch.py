"""Live shadow log of the dip-buy idea (Sunday test 24, owner approved 2026-10-26).

Runs after each trading day (Trade workflow, afternoon job). For the last completed session it
records every large cap that meets the zoh/research/dips.py signal (>= 8% below its 20-day
closing high, no single-day drop of 6% or more in the last 10 sessions, no signal in the last 20
sessions) with the ~0.40-delta call on the first monthly expiry 30-60 days out, its close, and the
5%-wider strike of the debit spread. Once 20 sessions have passed it fills in the real outcomes
(hold 10 / hold 20 / +50% take with a -50% stop, 3% costs each way) from Alpaca daily option bars.
No orders: this is the month of evidence before deciding whether to build a bot variant.

    python -m zoh.research.dipwatch
"""
import csv
from datetime import date, datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import daily_raw
from ..strategy import ET
from . import dips

PATH = journal.JOURNAL_DIR / "dipwatch.csv"
FIELDS = ["date", "sym", "dip", "spot", "expiry", "k1", "c1", "k2", "status", "call_hold10",
          "call_hold20", "call_tp50_sl50", "spread5_hold20", "stock_hold20"]


def load():
    if not PATH.exists():
        return []
    with PATH.open() as f:
        return list(csv.DictReader(f))


def save(rows):
    with PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def signal(dates, closes, i):
    hi = max(closes[dates[j]] for j in range(i - 19, i + 1))
    dip = closes[dates[i]] / hi - 1
    crash = min(closes[dates[j]] / closes[dates[j - 1]] - 1 for j in range(i - 9, i + 1))
    return dip, dip <= -dips.DIP and crash > dips.CRASH


def main(today=None):
    api = Alpaca()
    today = today or datetime.now(ET).date()
    rows = load()
    last_by_sym = {}
    for r in rows:
        last_by_sym[r["sym"]] = max(last_by_sym.get(r["sym"], ""), r["date"])
    added = filled = 0
    for sym in dips.UNIVERSE:
        try:
            days = daily_raw(api, sym, today - timedelta(days=120), today - timedelta(days=1))
        except AlpacaError as e:
            print(f"{sym}: bars failed: {e}")
            continue
        days = [d for d in days if d[0] < today]  # completed sessions only
        if len(days) < 30:
            continue
        dates = [d for d, _, _ in days]
        closes = {d: c for d, _, c in days}
        i = len(dates) - 1
        day = dates[i]
        prior = last_by_sym.get(sym)
        recent = prior and sum(1 for d in dates if d.isoformat() > prior) < dips.GAP_DAYS
        dip, hit = signal(dates, closes, i)
        if hit and not recent and not any(r["sym"] == sym and r["date"] == day.isoformat() for r in rows):
            t = dips.trade(api, sym, day, closes[day], [day], closes)
            if t:
                rows.append({"date": day.isoformat(), "sym": sym, "dip": round(dip, 4),
                             "spot": closes[day], "expiry": t["expiry"], "k1": t["k1"], "c1": t["c1"],
                             "k2": t.get("k2_spread5", ""), "status": "open"})
                last_by_sym[sym] = day.isoformat()
                added += 1
        for r in rows:
            if r["sym"] != sym or r["status"] != "open":
                continue
            d0 = date.fromisoformat(r["date"])
            path = [d for d in dates if d > d0][:20]
            if len(path) < 20:
                continue
            t = dips.trade(api, sym, d0, float(r["spot"]), path, closes)
            if not t:
                r["status"] = "no_data"
                continue
            r.update({"status": "done",
                      "call_hold10": t.get("call_3", {}).get("hold10", ""),
                      "call_hold20": t.get("call_3", {}).get("hold20", ""),
                      "call_tp50_sl50": t.get("call_3", {}).get("tp50_sl50", ""),
                      "spread5_hold20": t.get("spread5_3", {}).get("hold20", ""),
                      "stock_hold20": t["stock"]["hold20"]})
            filled += 1
    rows.sort(key=lambda r: (r["date"], r["sym"]))
    save(rows)
    print(f"dipwatch: {added} new signals, {filled} outcomes filled, {len(rows)} rows")


if __name__ == "__main__":
    main()
