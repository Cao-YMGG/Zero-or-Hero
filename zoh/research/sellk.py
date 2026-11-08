"""Sell at k x vs hold, pooled over our real and shadow trades (Sunday test 49).

Every trade in journal/exits.csv since 2026-10-19 (entry, exit, peak per contract, real and shadow
rows; one row per contract and mode) is replayed with the alternatives: sell everything at the first
k x (1.5, 2, 3, 5), half at k and hold the rest to 15:45, trail 40% once 2x, and hold to 15:45. The
peak tells whether k was reached; the hold value is the 15:45 close of the contract's real minute
bars (Alpaca), so trailed and half-out trades get a hold value too. Costs: the recorded entry (a
real fill or the shadow ask) and the 15:45 bid at 10% under the close. The other Claude's 2026-11-05
rows that carry both a k x leg and a held leg are listed as an appendix, not pooled (different
sizes and contracts).

    python -m zoh.research.sellk
"""
import csv
import json
import statistics
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import at_or_after, option_minutes
from ..strategy import ET, hhmm

OUT = journal.ROOT / "journal" / "research"
SINCE = "2026-10-19"
SLIP = 0.10
KS = (1.5, 2.0, 3.0, 5.0)
EXIT_AT = hhmm("15:45")

THEIRS = [  # (label, cost per contract, k sold, value per $1 of the k leg, value per $1 of the held/trailed leg, how held)
    ("TSLA 10-19 365C", 1.19, 3, 2.98, 2.69, "held to 15:30"),
    ("NVDA 10-22 215P", 1.24, 3, 2.98, 2.74, "held to 15:30"),
    ("SPY 10-30 758P", 2.37, 3, 3.00, 5.94, "held to 15:30"),
    ("SPY 11-05 757P", 5.24, 3, 3.02, 17.44, "held to 15:30"),
    ("SPY 10-20 773C", 0.44, 3, 3.00, 5.64, "trail 40% after 2x"),
    ("SPY 10-20 770C", 1.56, 3, 3.00, 2.37, "trail 40% after 2x"),
    ("SPY 11-02 756P", 20.75, 3, 3.00, 2.05, "trail 40% after 2x"),
    ("SPY 11-05 751P", 1.46, 3, 3.02, 4.41, "trail 40% after 2x (5x leg 5.01)"),
    ("HD 11-04 342.5C", 3.30, 2, 2.02, 3.02, "sold at 3x in the other ledger"),
]


def rows_since(root=journal.ROOT):
    out = []
    for r in csv.DictReader(open(root / "journal" / "exits.csv")):
        if r["date"] >= SINCE and float(r["entry_price"] or 0) > 0:
            out.append({"day": r["date"], "variant": r["variant"], "mode": r["mode"], "contract": r["contract"],
                        "entry": float(r["entry_price"]), "exit": float(r["exit_price"] or 0),
                        "peak": float(r["peak"] or 0), "reason": r["exit_reason"]})
    return out


def close_value(api, contract, day):
    """The 15:45 close of the contract's minute bars on `day` (None when there are none)."""
    try:
        bars = option_minutes(api, [contract], day).get(contract) or []
    except AlpacaError:
        return None
    b = at_or_after(bars, EXIT_AT, 10)
    if not b:
        later = [x for x in bars if x["t"].time() >= hhmm("15:30")]
        b = later[-1] if later else None
    return b["c"] if b else None


def replay(api, rows):
    for r in rows:
        day = datetime.fromisoformat(r["day"]).date()
        c = close_value(api, r["contract"], day)
        r["close_1545"] = c
        hold = max(0.0, min(c * (1 - SLIP), c - 0.01)) / r["entry"] if c is not None else (
            r["exit"] / r["entry"] if r["reason"] in ("time", "expired") else None)
        r["hold"] = round(hold, 4) if hold is not None else None
        r["recorded"] = round(r["exit"] / r["entry"], 4)
        pk = r["peak"] / r["entry"] if r["peak"] else 0.0
        r["peak_x"] = round(pk, 3)
        if hold is None:
            continue
        r["alts"] = {}
        for k in KS:
            r["alts"][f"sell{k:g}x"] = round(k * (1 - SLIP) if pk >= k else hold, 4)
            r["alts"][f"half{k:g}x_hold"] = round(0.5 * k * (1 - SLIP) + 0.5 * hold if pk >= k else hold, 4)
        r["alts"]["hold"] = round(hold, 4)
        r["alts"]["recorded"] = r["recorded"]
    return rows


def stats(xs):
    if not xs:
        return "-"
    xs = sorted(xs, reverse=True)
    wo1 = statistics.mean(xs[1:]) if len(xs) > 1 else float("nan")
    wo2 = statistics.mean(xs[2:]) if len(xs) > 2 else float("nan")
    return f"{statistics.mean(xs) - 1:+.0%} / {wo1 - 1:+.0%} / {wo2 - 1:+.0%}"


def report(rows):
    done = [r for r in rows if r.get("alts")]
    labels = ["recorded", "hold"] + [f"sell{k:g}x" for k in KS] + [f"half{k:g}x_hold" for k in KS]
    out = ["# Sell at k x vs hold, pooled\n",
           f"Our real and shadow contracts since {SINCE} (journal/exits.csv), {len(done)} with a 15:45 price "
           f"({len(rows) - len(done)} without one). Value per $1 of entry: average / without the best / without the best two. "
           f"`sell k x` sells everything at the first k x of the entry (10% under), else holds to 15:45; `half k x` sells half "
           f"there and holds the rest; `recorded` is what the journal booked (the live exit at the time). Sunday test 49; "
           f"see zoh/research/sellk.py.\n"]
    groups = [("all", lambda r: True), ("real fills", lambda r: r["mode"] == "real"), ("shadow", lambda r: r["mode"] == "shadow"),
              ("reached 2x", lambda r: r["peak_x"] >= 2), ("reached 3x", lambda r: r["peak_x"] >= 3),
              ("puts", lambda r: "P0" in r["contract"][-9:]), ("calls", lambda r: "C0" in r["contract"][-9:]),
              ("SPY", lambda r: r["contract"].startswith("SPY")), ("single stocks", lambda r: not r["contract"].startswith("SPY"))]
    out.append("\n| group | n | " + " | ".join(labels) + " |\n|---|---|" + "---|" * len(labels) + "\n")
    for name, f in groups:
        sel = [r for r in done if f(r)]
        out.append(f"| {name} | {len(sel)} | " + " | ".join(stats([r["alts"][l] for r in sel]) for l in labels) + " |\n")
    out.append("\nShare of trades that reached: " + ", ".join(f"{k:g}x {sum(1 for r in done if r['peak_x'] >= k) / max(1, len(done)):.0%}" for k in KS) + "\n")
    out.append("\n## Trades that reached 2x\n\n| day | variant | mode | contract | entry | peak x | recorded | hold | sell 2x | sell 3x | half 3x + hold |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in done:
        if r["peak_x"] >= 2:
            a = r["alts"]
            out.append(f"| {r['day']} | {r['variant']} | {r['mode']} | {r['contract']} | {r['entry']:.2f} | {r['peak_x']:.1f} | "
                       f"{a['recorded']:.2f} | {a['hold']:.2f} | {a['sell2x']:.2f} | {a['sell3x']:.2f} | {a['half3x_hold']:.2f} |\n")
    out.append("\n## The other Claude's rows with both legs (2026-11-05 exchange), per $1\n\n| contract | cost | k | k leg | held / trailed leg | how |\n|---|---|---|---|---|---|\n")
    for lab, cost, k, kv, hv, how in THEIRS:
        out.append(f"| {lab} | {cost:.2f} | {k}x | {kv:.2f} | {hv:.2f} | {how} |\n")
    kv = [t[3] for t in THEIRS]
    hv = [t[4] for t in THEIRS]
    out.append(f"\nTheir {len(THEIRS)} rows: k leg {statistics.mean(kv):.2f} per $1, held or trailed leg {statistics.mean(hv):.2f} "
               f"(median {statistics.median(hv):.2f}; {sum(1 for h in hv if h > 3):d} of {len(hv)} above 3x). Selection: these are the "
               f"trades that reached k, so both columns are conditional on a winner.\n")
    return "".join(out)


def main():
    api = Alpaca()
    rows = replay(api, rows_since())
    (OUT / "sellk.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    text = report(rows)
    (OUT / "SELLK.md").write_text(text)
    print(text[:6000])


if __name__ == "__main__":
    main()
