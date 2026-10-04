"""Rank stocks for aggressive 0DTE play from the per-stock backtest summaries.

    python -m zoh.screen_report   # reads journal/research/screen/*.json
"""
import json

from . import journal

DIR = journal.ROOT / "journal" / "research" / "screen"


def main():
    rows = []
    for path in sorted(DIR.glob("*.json")):
        s = json.loads(path.read_text())
        for v in s["variants"]:
            rows.append({**v, "sym": s["underlying"], "iv": s["iv"],
                         "days": "M/W/F" if s["weekdays"] == [0, 2, 4] else
                         "Fri" if s["weekdays"] == [4] else "all"})
    syms = sorted({r["sym"] for r in rows})
    best = {}
    for sym in syms:
        mine = [r for r in rows if r["sym"] == sym]
        best[sym] = {
            "ultra": max(mine, key=lambda r: (r["ultra"]["500000"], r["ultra"]["50000"])),
            "hero": max(mine, key=lambda r: r["hero"]["0.3"]),
            "recent": max(mine, key=lambda r: r["recent_odds"]),
        }
    L = ["# Stock screen for aggressive 0DTE — last 2 years", "",
         f"{len(syms)} stocks × {len(rows) // max(len(syms), 1)} rules. Same-day expiries: "
         "Mon/Wed/Fri for the largest names, Fridays only for the rest. Black-Scholes at each "
         "stock's intraday vol ×1.15, 3% slippage + $0.01; deep OTM prices are flattered by the "
         "flat-IV model. Odds are all-in bootstraps from $500 unless noted.", "",
         "## Ultra: best rule per stock by P($500 → $500k)", "",
         "| stock | days | IV | rule | trades | win% | exp/trade | P(→$50k) | P(→$500k) | top multiples |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for sym in sorted(syms, key=lambda s: (-best[s]["ultra"]["ultra"]["500000"],
                                           -best[s]["ultra"]["ultra"]["50000"])):
        r = best[sym]["ultra"]
        tops = ", ".join(f"{m:.0f}x" for m in r["multiples"][:4])
        L.append(f"| {sym} | {r['days']} | {r['iv']:.0%} | {r['id']} | {r['trades']} | "
                 f"{r['win_rate']:.0%} | {r['expectancy']:+.0%} | {r['ultra']['50000']:.1%} | "
                 f"{r['ultra']['500000']:.2%} | {tops} |")
    L += ["", "## Positive expectancy: best rule per stock by P($500 → $2k) at a 30% stake", "",
          "| stock | rule | trades | win% | exp/trade | P(→$2k) 30% | P(→$2k) all-in | "
          "last 3 months: n / avg / odds |", "|---|---|---|---|---|---|---|---|"]
    for sym in sorted(syms, key=lambda s: -best[s]["hero"]["hero"]["0.3"]):
        r = best[sym]["hero"]
        L.append(f"| {sym} | {r['id']} | {r['trades']} | {r['win_rate']:.0%} | "
                 f"{r['expectancy']:+.0%} | {r['hero']['0.3']:.0%} | {r['hero']['1.0']:.0%} | "
                 f"{r['recent_n']} / {r['recent_avg']:+.0%} / {r['recent_odds']:.0%} |")
    L += ["", "## Rules that work across many stocks (count of stocks with positive expectancy)",
          "", "| rule | stocks > 0 | median exp/trade | best stock |", "|---|---|---|---|"]
    for rid in sorted({r["id"] for r in rows}):
        rs = [r for r in rows if r["id"] == rid and r["trades"] >= 8]
        if not rs:
            continue
        pos = [r for r in rs if r["expectancy"] > 0]
        exps = sorted(r["expectancy"] for r in rs)
        top = max(rs, key=lambda r: r["expectancy"])
        L.append(f"| {rid} | {len(pos)}/{len(rs)} | {exps[len(exps) // 2]:+.0%} | "
                 f"{top['sym']} ({top['expectancy']:+.0%}, {top['trades']} trades) |")
    (journal.ROOT / "journal" / "research" / "SCREEN.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
