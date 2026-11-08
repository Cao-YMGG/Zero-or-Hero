"""What the budget buys: our catalyst picks with the real stake, with and without the delta floor
(Sunday test 52; the 2026-11-06 LLY 1430C case).

For every sniper and intraday pick in snipers.json (live entry time and spot), the contracts quoted
at that minute are re-priced and three selection rules choose one:
- `old`: nearest the target delta (0.10 sniper, 0.20 intraday) among contracts the stake buys,
  one contract <= 20% of the main ledger that day (the live rule until 2026-11-06);
- `floor`: the same with |delta| >= 0.06, else no trade (live since 2026-11-08);
- `pct`: strike within 2% of the spot, nearest the target delta, the stake only caps quantity
  (skips when even one contract is out of reach);
- `nobudget`: the target delta with no stake limit (what the hero shadows see).
Exits: the live rule (half at 3x, trail armed at 1.5x, 40% giveback) and hold to 15:45 on day one.
Costs 10% each way. Also how far the chosen delta sat from the target under each rule.

    python -m zoh.research.strikebudget
"""
import csv
import json
import statistics
import time
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from .exits import bid, candidates, run
from .snipers import EXITS  # noqa: F401  (registers half3_arm1.5)

SLIP = 0.10
OUT = journal.ROOT / "journal" / "research"
TARGET = {"sniper": 0.10, "intraday": 0.20}
FLOOR = 0.06
PCT = 0.02
RISK = 0.2
RULES = ("half3_arm1.5", "hold")


def equity_by_day(root=journal.ROOT):
    eq = {}
    for r in csv.DictReader(open(root / "journal" / "equity.csv")):
        eq[r["date"]] = float(r["equity"])
    return eq


def stake_for(day, eq):
    prior = [d for d in sorted(eq) if d < day]
    return RISK * (eq[prior[-1]] if prior else 500.0)


def choose(cands, target, spot, kind, stake):
    cost = lambda c: max(c[3]["c"] * (1 + SLIP), c[3]["c"] + 0.01) * 100
    afford = [c for c in cands if cost(c) <= stake]
    out = {"nobudget": min(cands, key=lambda c: abs(c[2] - target)) if cands else None,
           "old": min(afford, key=lambda c: (abs(c[2] - target), c[3]["c"])) if afford else None}
    fl = [c for c in afford if c[2] >= FLOOR]
    out["floor"] = min(fl, key=lambda c: (abs(c[2] - target), c[3]["c"])) if fl else None
    near = [c for c in cands if (c[1] <= spot * (1 + PCT) if kind == "call" else c[1] >= spot * (1 - PCT))]
    near = [c for c in near if cost(c) <= stake]
    out["pct"] = min(near, key=lambda c: (abs(c[2] - target), c[3]["c"])) if near else None
    return out


def study(api):
    rows = []
    eq = equity_by_day()
    for p in json.loads((OUT / "snipers.json").read_text()):
        live = p["entries"].get("live")
        if not live:
            continue
        day = datetime.fromisoformat(p["day"]).date()
        expiry = datetime.fromisoformat(p["expiry"]).date()
        h, m = map(int, live["t"].split(":"))
        entry_t = (datetime.combine(day, datetime.min.time()) + timedelta(hours=h, minutes=m + 1)).time()
        try:
            cands, opts = candidates(api, p["sym"], day, expiry, entry_t, live["spot"], p["kind"])
        except AlpacaError as e:
            print(p["day"], p["sym"], e, flush=True)
            continue
        stake = stake_for(p["day"], eq)
        row = {"day": p["day"], "sym": p["sym"], "kind": p["kind"], "source": p["source"], "spot": live["spot"],
               "stake": round(stake, 2), "stock_move": round(p["close"] / live["spot"] - 1, 4), "rules": {}}
        for label, c in choose(cands, TARGET[p["source"]], live["spot"], p["kind"], stake).items():
            if c is None:
                row["rules"][label] = None
                continue
            s, k, d, b = c
            path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
            if not path:
                row["rules"][label] = None
                continue
            entry = max(b["c"] * (1 + SLIP), b["c"] + 0.01)
            row["rules"][label] = {"contract": s, "strike": k, "delta": round(d, 3), "px": b["c"],
                                   "otm": round(abs(k / live["spot"] - 1), 4),
                                   "qty": int(stake // (entry * 100)) if label != "nobudget" else 1,
                                   "peak": round(max(bid(c2, SLIP) for _, c2 in path) / entry, 3),
                                   "exits": {r: round(run(path, entry, SLIP, r) - 1, 4) for r in RULES}}
        rows.append(row)
        print(p["day"], p["source"], p["sym"], {k: (v["delta"] if v else None) for k, v in row["rules"].items()}, flush=True)
        time.sleep(0.2)
    return rows


def stats(xs):
    if not xs:
        return "-"
    xs = sorted(xs, reverse=True)
    wo1 = statistics.mean(xs[1:]) if len(xs) > 1 else float("nan")
    wo2 = statistics.mean(xs[2:]) if len(xs) > 2 else float("nan")
    return f"{len(xs)} | {sum(1 for x in xs if x > 0) / len(xs):.0%} | {statistics.mean(xs):+.0%} / {wo1:+.0%} / {wo2:+.0%}"


def report(rows):
    out = ["# What the stake buys: our picks under four strike rules\n",
           "Every sniper (target 0.10 delta) and intraday pick (0.20) since 2026-10-01 at its live entry minute, real option "
           "minute bars, costs 10% each way, one contract <= 20% of the main ledger that day. `old` = nearest the target among "
           "affordable contracts (live until 11-06); `floor` = the same with |delta| >= 0.06 (live since 11-08); `pct` = strike "
           "within 2% of the spot; `nobudget` = the target delta regardless of price. Per $1 of option: n | win% | avg / without "
           "the best / without the best two. Sunday test 52; see zoh/research/strikebudget.py.\n"]
    for src in ("sniper", "intraday", "all"):
        sel = [r for r in rows if src == "all" or r["source"] == src]
        out.append(f"\n## {src} ({len(sel)} picks)\n\n| rule | taken | skipped | median delta | median % OTM | delta < 0.06 | live exit | hold |\n|---|---|---|---|---|---|---|---|\n")
        for label in ("old", "floor", "pct", "nobudget"):
            taken = [r["rules"][label] for r in sel if r["rules"].get(label)]
            if not taken:
                out.append(f"| {label} | 0 | {len(sel)} | - | - | - | - | - |\n")
                continue
            out.append(f"| {label} | {len(taken)} | {len(sel) - len(taken)} | {statistics.median(t['delta'] for t in taken):.2f} | "
                       f"{statistics.median(t['otm'] for t in taken):.1%} | {sum(1 for t in taken if t['delta'] < FLOOR)} | "
                       f"{stats([t['exits']['half3_arm1.5'] for t in taken])} | {stats([t['exits']['hold'] for t in taken])} |\n")
        out.append("\nPer-ledger dollars (the stake's whole contracts x the exit): ")
        for label in ("old", "floor", "pct"):
            tot = sum(t["qty"] * t["px"] * (1 + SLIP) * 100 * t["exits"]["half3_arm1.5"] for r in sel for t in [r["rules"].get(label)] if t)
            out.append(f"{label} ${tot:+,.0f}; ")
        out.append("\n")
    out.append("\n## Pick by pick\n\n| day | pick | stock to close | old: delta / %OTM / live | floor | pct | nobudget |\n|---|---|---|---|---|---|---|\n")
    for r in rows:
        cells = []
        for label in ("old", "floor", "pct", "nobudget"):
            t = r["rules"].get(label)
            cells.append(f"{t['delta']:.2f} / {t['otm']:.1%} / {t['exits']['half3_arm1.5']:+.0%}" if t else "skip")
        out.append(f"| {r['day']} | {r['source']} {r['sym']} {r['kind']} | {r['stock_move']:+.1%} | " + " | ".join(cells) + " |\n")
    return "".join(out)


def main():
    api = Alpaca()
    rows = study(api)
    (OUT / "strikebudget.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    text = report(rows)
    (OUT / "STRIKEBUDGET.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
