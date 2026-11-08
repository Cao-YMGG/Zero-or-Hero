"""The gap-down put (nvda_gapdown_put) on real option prices, every weekday (Sunday tests 36, 46).

Rule as configured: the stock opens below the prior close and is still >= 0.1% under its open
at 10:00 -> buy the put nearest 0.40 delta at 10:00, sell at 3x (take_profit 2.0) or 15:45.
Replayed since 2024-02 on Alpaca option minute bars with the nearest expiry: same day on
Mon/Wed/Fri (Fridays only before 2026-01-26), the next listed expiry on Tue/Thu (1-2 DTE), so
the Tue/Thu days the live bot skips (`same_day_expiry`) get their own column. Contracts:
- `ledger`: what a $500 ledger can buy (one contract <= $150 incl. costs, |delta| >= 0.06),
  nearest 0.40 delta -- the real variant's choice;
- `d0.40`, `d0.25`, `d0.15`: the delta without a budget.
Exits: take3 (live), take2, half3_trail, trail2x, hold (15:45). Costs 10% of the option price
each way. Item 36: the same rule on AMD, AVGO, MU, TSLA, META, AMZN, GOOGL, MSFT, AAPL and
"the biggest gap-down of the group that day".

    python -m zoh.research.gapdown [--syms NVDA AMD ...] [--from-json]
"""
import argparse
import json
import statistics
import time
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import START, at_or_after, daily_raw
from ..strategy import ET, hhmm
from .exits import bid, candidates, nearest_expiry, run
from .opendrive import macro_days
from .snipers import stock_minutes

SLIP = 0.10
OUT = journal.ROOT / "journal" / "research"
SYMS = ["NVDA", "AMD", "AVGO", "MU", "TSLA", "META", "AMZN", "GOOGL", "MSFT", "AAPL"]
CONFIRM = 0.001      # still 0.1% under the open at 10:00 (confirm_pct)
BUDGET = 150.0       # one contract on a $500 ledger (one_contract_cap 0.3)
MIN_DELTA = 0.06     # the 2026-11-08 floor
TARGET = 0.40
DELTAS = (0.40, 0.25, 0.15)
RULES = ("take3", "take2", "half3_trail", "trail2x", "hold")
EXIT_AT = hhmm("15:45")


def take(path, entry, slip, k):
    """Sell everything at the first bid >= k x entry, else at 15:45 (value per $1)."""
    last = 0.0
    for t, c in path:
        b = bid(c, slip)
        last = b
        if t.time() >= EXIT_AT:
            return b / entry
        if b >= k * entry:
            return b / entry
    return last / entry


def pnl(path, entry, rule):
    if rule == "take3":
        return take(path, entry, SLIP, 3.0) - 1
    if rule == "take2":
        return take(path, entry, SLIP, 2.0) - 1
    return run(path, entry, SLIP, rule) - 1


def pick_contracts(cands):
    """{label: (contract, strike, delta, bar)} for the ledger rule and the plain deltas."""
    picks = {}
    afford = [c for c in cands if max(c[3]["c"] * (1 + SLIP), c[3]["c"] + 0.01) * 100 <= BUDGET
              and c[2] >= MIN_DELTA]
    if afford:
        picks["ledger"] = min(afford, key=lambda x: (abs(x[2] - TARGET), x[3]["c"]))
    for d in DELTAS:
        picks[f"d{d:.2f}"] = min(cands, key=lambda x: abs(x[2] - d))
    return picks


def study_symbol(api, sym, end, macro):
    rows = []
    daily = daily_raw(api, sym, datetime.combine(START - timedelta(days=5), hhmm("00:00"), ET),
                      datetime.combine(end + timedelta(days=1), hhmm("00:00"), ET))
    for i in range(1, len(daily)):
        day, o, c = daily[i]
        prev_close = daily[i - 1][2]
        if day < START or day > end or day.weekday() >= 5 or not prev_close:
            continue
        gap = o / prev_close - 1
        if gap >= 0 or gap < -0.3:    # not a gap down, or a split day
            continue
        bars = stock_minutes(api, sym, day)
        if not bars:
            continue
        b10 = at_or_after(bars, hhmm("09:59"), 3)
        if not b10:
            continue
        open_, spot = bars[0]["o"], b10["c"]
        if spot > open_ * (1 - CONFIRM):
            continue
        expiry = nearest_expiry(sym, day)
        if not expiry:
            continue
        entry_t = (b10["t"] + timedelta(minutes=1)).time()
        try:
            cands, opts = candidates(api, sym, day, expiry, entry_t, spot, "put")
        except AlpacaError as e:
            print(f"{sym} {day}: {e}", flush=True)
            continue
        row = {"sym": sym, "day": day.isoformat(), "weekday": day.weekday(), "dte": (expiry - day).days,
               "expiry": expiry.isoformat(), "gap": round(gap, 4), "move10": round(spot / open_ - 1, 4),
               "open": open_, "spot": spot, "close": bars[-1]["c"], "macro": day.isoformat() in macro,
               "picks": {}}
        if cands:
            for label, (s, k, d, b) in pick_contracts(cands).items():
                path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
                if not path:
                    continue
                entry = max(b["c"] * (1 + SLIP), b["c"] + 0.01)
                row["picks"][label] = {
                    "contract": s, "strike": k, "delta": round(d, 3), "px": b["c"],
                    "peak": round(max(bid(c, SLIP) for _, c in path) / entry, 3),
                    "exits": {r: round(pnl(path, entry, r), 4) for r in RULES}}
        rows.append(row)
        print(f"{sym} {day} wd{day.weekday()} dte{row['dte']} gap {gap:+.2%} 10:00 {row['move10']:+.2%} "
              f"{'ledger ' + str(row['picks']['ledger']['exits']['take3']) if 'ledger' in row['picks'] else 'no ledger contract'}",
              flush=True)
        time.sleep(0.1)
    return rows


# --- report ---------------------------------------------------------------

def stats(xs):
    if not xs:
        return "-"
    xs = sorted(xs, reverse=True)
    avg = statistics.mean(xs)
    wo1 = statistics.mean(xs[1:]) if len(xs) > 1 else float("nan")
    wo2 = statistics.mean(xs[2:]) if len(xs) > 2 else float("nan")
    win = sum(1 for x in xs if x > 0) / len(xs)
    return f"{len(xs)} | {win:.0%} | {avg:+.0%} / {wo1:+.0%} / {wo2:+.0%} | {statistics.median(xs):+.0%}"


def periods(end):
    return (("last 3 months", end - timedelta(days=91)), ("last year", end - timedelta(days=365)),
            ("since 2024-02", START))


def table(rows, end, pick, rules=("take3", "hold", "trail2x", "half3_trail")):
    head = "| days | period | " + " | ".join(f"{r}: n \\| win \\| avg / -best / -best2 \\| median" for r in rules) + " |\n"
    head += "|---|---|" + "---|" * len(rules) + "\n"
    out = head
    classes = (("all weekdays", lambda r: True), ("Mon/Wed/Fri (same-day expiry)", lambda r: r["dte"] == 0),
               ("Tue/Thu (next expiry, 1-2 DTE)", lambda r: r["dte"] >= 1 and r["weekday"] in (1, 3)),
               ("macro days", lambda r: r["macro"]), ("non-macro days", lambda r: not r["macro"]))
    for cname, cf in classes:
        for pname, since in periods(end):
            sel = [r for r in rows if cf(r) and r["day"] >= since.isoformat() and pick in r["picks"]]
            cells = [stats([r["picks"][pick]["exits"][rule] for r in sel]) for rule in rules]
            out += f"| {cname} | {pname} | " + " | ".join(cells) + " |\n"
    return out


def biggest_gap(rows):
    """One trade a day: the symbol with the largest gap down among the qualifying ones."""
    by_day = {}
    for r in rows:
        if r["day"] not in by_day or r["gap"] < by_day[r["day"]]["gap"]:
            by_day[r["day"]] = r
    return list(by_day.values())


def report(rows, end):
    syms = sorted({r["sym"] for r in rows}, key=lambda s: SYMS.index(s) if s in SYMS else 99)
    out = ["# The gap-down put on real option prices, every weekday\n",
           f"Rule: the stock opens below the prior close and is still >= 0.1% under its open at 10:00 -> put at 10:00, "
           f"nearest expiry (same day on Mon/Wed/Fri, the next listed expiry on Tue/Thu), sold at 3x (`take3`, the live "
           f"nvda_gapdown_put rule) or 15:45. Costs {SLIP:.0%} each way. `ledger` = the contract a $500 ledger buys "
           f"(one contract <= ${BUDGET:.0f}, |delta| >= {MIN_DELTA}), nearest 0.40 delta; `d0.40` = that delta without a "
           f"budget. Columns: n | win% | avg / without the best / without the best two | median. Data through {end}. "
           f"Sunday tests 36 and 46. See zoh/research/gapdown.py.\n"]
    skipped = sum(1 for r in rows if "ledger" not in r["picks"])
    out.append(f"Qualifying days: {len(rows)} ({skipped} with no contract the ledger could buy).\n")
    for sym in syms:
        sel = [r for r in rows if r["sym"] == sym]
        out.append(f"\n## {sym} ({len(sel)} days)\n")
        out.append("### `ledger` contract\n\n" + table(sel, end, "ledger"))
        out.append("\n### 0.40 delta, no budget\n\n" + table(sel, end, "d0.40"))
        out.append("\n### 0.25 delta, no budget\n\n" + table(sel, end, "d0.25", rules=("take3", "hold")))
    if len(syms) > 1:
        out.append(f"\n## All symbols pooled ({len(rows)} trades)\n")
        out.append("### `ledger` contract\n\n" + table(rows, end, "ledger"))
        out.append("\n### 0.40 delta, no budget\n\n" + table(rows, end, "d0.40"))
        bg = biggest_gap(rows)
        out.append(f"\n## One a day: the biggest gap-down of the group ({len(bg)} days)\n")
        out.append("### `ledger` contract\n\n" + table(bg, end, "ledger"))
        out.append("\n### 0.40 delta, no budget\n\n" + table(bg, end, "d0.40"))
        counts = {}
        for r in bg:
            counts[r["sym"]] = counts.get(r["sym"], 0) + 1
        out.append("\nPicked: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])) + "\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--syms", nargs="*", default=SYMS)
    ap.add_argument("--from-json", action="store_true", help="rebuild the report from gapdown.json")
    ap.add_argument("--end", default=None)
    args = ap.parse_args()
    end = datetime.fromisoformat(args.end).date() if args.end else datetime.now(ET).date() - timedelta(days=1)
    path = OUT / "gapdown.json"
    rows = json.loads(path.read_text()) if path.exists() else []
    if not args.from_json:
        api = Alpaca()
        macro = macro_days()
        for sym in args.syms:
            rows = [r for r in rows if r["sym"] != sym]
            rows.extend(study_symbol(api, sym, end, macro))
            rows.sort(key=lambda r: (r["day"], r["sym"]))
            path.write_text(json.dumps(rows, indent=0, default=str) + "\n")
            (OUT / "GAPDOWN.md").write_text(report(rows, end))
            print(f"== {sym} done, {len(rows)} rows so far", flush=True)
    text = report(rows, end)
    (OUT / "GAPDOWN.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
