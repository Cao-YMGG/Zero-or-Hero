"""IEX (what the live bot sees) vs SIP (full tape) vs OpenD (claude-c) at 09:30 and 10:00.

The live bot judges "the move since the open" on IEX 1-minute bars. IEX is a small slice of the
tape, so its first print and its 10:00 price can differ from the consolidated ones. Uses claude-c's
exchange/claude-c/2026-10-17.premarket-5m-2026-09-01.json (open_0930 = first regular bar open,
close_1000 = close of the 5-minute bar ending 10:00) for the same 15 symbols and days.

    python -m zoh.research.feeds
"""
import json
from datetime import date, datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..strategy import ET, MARKET_OPEN, parse_bar, regular_session

SRC = journal.ROOT / "exchange" / "claude-c" / "2026-10-17.premarket-5m-2026-09-01.json"
OUT = journal.ROOT / "journal" / "research"


def open_and_1000(api, sym, day, feed):
    start = datetime.combine(day, MARKET_OPEN, ET)
    try:
        bars = regular_session([{**parse_bar(b), "v": b.get("v", 0)} for b in api.stock_bars(
            sym, start, start + timedelta(minutes=31), feed=feed, adjustment="raw")])
    except AlpacaError:
        return None
    if not bars:
        return None
    upto = [b for b in bars if b["t"].hour == 9]  # bars starting 09:30-09:59
    return {"open": bars[0]["o"], "first_bar_min": bars[0]["t"].minute,
            "c1000": upto[-1]["c"] if upto else None,
            "vol": sum(b["v"] for b in upto) if upto and "v" in upto[0] else None}


def main():
    api = Alpaca()
    src = json.loads(SRC.read_text())["symbols"]
    rows = []
    for sym, days in src.items():
        for d, v in sorted(days.items()):
            day = date.fromisoformat(d)
            iex, sip = open_and_1000(api, sym, day, "iex"), open_and_1000(api, sym, day, "sip")
            if not iex or not sip or not iex["c1000"] or not sip["c1000"]:
                continue
            rows.append({"sym": sym, "day": d, "opend_open": v["open_0930"], "opend_1000": v["close_1000"],
                         "sip_open": sip["open"], "sip_1000": sip["c1000"], "iex_open": iex["open"],
                         "iex_1000": iex["c1000"], "iex_first_min": iex["first_bar_min"],
                         "iex_vol": iex["vol"], "sip_vol": sip["vol"]})
        print(sym, sum(r["sym"] == sym for r in rows), flush=True)
    (OUT / "feeds.json").write_text(json.dumps(rows, indent=0) + "\n")

    def move(r, src):
        return r[f"{src}_1000"] / r[f"{src}_open"] - 1

    lines = ["# IEX vs SIP vs OpenD: the open and the 10:00 move", "",
             f"{len(rows)} symbol-days ({len({r['day'] for r in rows})} days, 15 symbols, 2026-09-01+). "
             "Move = 10:00 price / open - 1. Differences in basis points (0.01%).", "",
             "| pair | median abs diff, open | median abs diff, 10:00 move | days the move's sign differs "
             "| of those, \\|move\\| < 0.3% | sign differs with \\|move\\| >= 0.5% |", "|---|---|---|---|---|---|"]
    for a, b in (("iex", "sip"), ("iex", "opend"), ("sip", "opend")):
        do = sorted(abs(r[f"{a}_open"] / r[f"{b}_open"] - 1) * 1e4 for r in rows)
        dm = sorted(abs(move(r, a) - move(r, b)) * 1e4 for r in rows)
        flip = [r for r in rows if move(r, a) * move(r, b) < 0]
        small = sum(abs(move(r, b)) < 0.003 for r in flip)
        big = sum(abs(move(r, b)) >= 0.005 for r in flip)
        lines.append(f"| {a} vs {b} | {do[len(do) // 2]:.1f} | {dm[len(dm) // 2]:.1f} | {len(flip)} of {len(rows)} | "
                     f"{small} | {big} |")
    share = [r["iex_vol"] / r["sip_vol"] for r in rows if r.get("iex_vol") and r.get("sip_vol")]
    if share:
        share.sort()
        lines += ["", f"IEX share of 09:30-10:00 volume: median {share[len(share) // 2]:.1%} "
                      f"(range {share[0]:.1%} to {share[-1]:.1%})."]
    late = sum(r["iex_first_min"] > 30 for r in rows)
    lines += [f"IEX's first regular bar starts after 09:30 on {late} of {len(rows)} symbol-days.", "",
              "## Largest 10:00-move differences, IEX vs SIP", "", "| day | stock | IEX move | SIP move | OpenD move |",
              "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -abs(move(r, "iex") - move(r, "sip")))[:12]:
        lines.append(f"| {r['day']} | {r['sym']} | {move(r, 'iex'):+.2%} | {move(r, 'sip'):+.2%} | {move(r, 'opend'):+.2%} |")
    (OUT / "FEEDS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
