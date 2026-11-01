"""Our own catalyst picks on real option prices: delta, exits and entry time (Sunday tests 25, 29, 34).

Every pre-market sniper (journal/bias/<date>.json) and every intraday pick
(journal/bias/intraday/<date>.json) since 2026-10-01, priced from Alpaca option minute bars:
- contracts at |delta| 0.10 / 0.20 / 0.30 / 0.45 on the nearest expiry (same day, else carried);
- snipers entered at the first minute from 09:32 to 10:00 where the stock is not against the pick
  (the live catalyst_open rule), and also at 09:40 and 10:00; intraday picks 2 minutes after the
  pick time;
- each contract runs the live exit (half at 3x, trail armed at 2x, 40% giveback) and alternatives,
  sold at 15:45 on day one and carried to expiry (news picks may be carried live).
Costs 10% of the option price each way.

    python -m zoh.research.snipers
"""
import json
import time
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import at_or_after, option_minutes
from ..strategy import ET, MARKET_OPEN, hhmm, parse_bar, regular_session
from . import exits
from .exits import EXITS, bid, candidates, nearest_expiry, run

SLIP = 0.10
OUT = journal.ROOT / "journal" / "research"
DELTAS = (0.10, 0.20, 0.30, 0.45)
EXITS.update({
    "half3_arm1.5": (1.5, 0.4, None, 3.0),
    "half2_arm1.5": (1.5, 0.4, None, 2.0),
    "half1.7_arm1.5": (1.5, 0.4, None, 1.7),
    "half3_give0.5": (2.0, 0.5, None, 3.0),
})
RULES = ("half3_trail", "half3_arm1.5", "half2_arm1.5", "half1.7_arm1.5", "half3_give0.5", "trail2x",
         "hold")
LIVE = "half3_trail"


def picks(root=journal.ROOT):
    """[(day, sym, kind, source, time or None)] from the bias and intraday files."""
    out = []
    for f in sorted((root / "journal" / "bias").glob("2026-*.json")):
        s = json.loads(f.read_text()).get("sniper") or {}
        if s.get("symbol"):
            out.append((f.stem, s["symbol"], s.get("direction", "call"), "sniper", None))
    for f in sorted((root / "journal" / "bias" / "intraday").glob("2026-*.json")):
        for p in json.loads(f.read_text()).get("picks") or []:
            out.append((f.stem, p["symbol"], p["direction"], "intraday", p["time"]))
    return out


def stock_minutes(api, sym, day):
    start = datetime.combine(day, MARKET_OPEN, ET)
    try:
        return regular_session([parse_bar(b) for b in api.stock_bars(
            sym, start, datetime.combine(day, hhmm("16:00"), ET), feed="sip", adjustment="raw")])
    except AlpacaError:
        return []


def live_entry(bars, kind):
    """First minute 09:32-10:00 where the stock is at/above its open (call) or at/below (put)."""
    if not bars:
        return None
    o = bars[0]["o"]
    for b in bars:
        if hhmm("09:31") <= b["t"].time() <= hhmm("09:59"):
            if (b["c"] >= o) if kind == "call" else (b["c"] <= o):
                return b
    return None


def later_path(api, contract, day, expiry):
    out, d = [], day + timedelta(days=1)
    while d <= expiry:
        if d.weekday() < 5:
            try:
                out += [(x["t"], x["c"]) for x in option_minutes(api, [contract], d).get(contract, [])]
            except AlpacaError:
                pass
        d += timedelta(days=1)
    return out


def price_entry(api, sym, day, expiry, entry_bar, kind):
    t = (entry_bar["t"] + timedelta(minutes=1)).time()
    try:
        cands, opts = candidates(api, sym, day, expiry, t, entry_bar["c"], kind)
    except AlpacaError:
        return None
    res = {}
    for d in DELTAS:
        if not cands:
            break
        s, k, dl, b = min(cands, key=lambda x: abs(x[2] - d))
        path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
        if not path:
            continue
        entry = max(b["c"] * (1 + SLIP), b["c"] + 0.01)
        later = later_path(api, s, day, expiry) if expiry > day else []
        res[f"d{d:.2f}"] = {
            "contract": s, "strike": k, "delta": round(dl, 3), "px": b["c"],
            "peak": round(max(bid(c, SLIP) for _, c in path + later) / entry, 3),
            "day1": {r: round(run(path, entry, SLIP, r) - 1, 4) for r in RULES},
            "carry": {r: round(run(path + later, entry, SLIP, r) - 1, 4) for r in RULES} if later else None,
        }
    return res


def study(api, root=journal.ROOT):
    rows = []
    for day_s, sym, kind, source, at in picks(root):
        day = datetime.fromisoformat(day_s).date()
        expiry = nearest_expiry(sym, day)
        if not expiry:
            continue
        bars = stock_minutes(api, sym, day)
        if not bars:
            continue
        entries = {}
        if source == "sniper":
            b = live_entry(bars, kind)
            if b:
                entries["live"] = b
            for label, hm in (("09:40", "09:39"), ("10:00", "09:59")):
                b = at_or_after(bars, hhmm(hm), 3)
                if b:
                    entries[label] = b
        else:
            h, m = map(int, at.split(":"))
            b = at_or_after(bars, (datetime.combine(day, hhmm("00:00")) + timedelta(hours=h, minutes=m + 1)).time(), 3)
            if b:
                entries["live"] = b
        row = {"day": day_s, "sym": sym, "kind": kind, "source": source, "expiry": expiry.isoformat(),
               "open": bars[0]["o"], "close": bars[-1]["c"], "entries": {}}
        for label, b in entries.items():
            r = price_entry(api, sym, day, expiry, b, kind)
            if r:
                row["entries"][label] = {"t": b["t"].strftime("%H:%M"), "spot": b["c"], "picks": r}
        rows.append(row)
        print(f"{day_s} {source} {sym} {kind}: {list(row['entries'])}", flush=True)
        time.sleep(0.2)
    return rows


def stats(xs):
    if not xs:
        return "- | - | - | - | -"
    s = sorted(xs)
    a = lambda v: f"{sum(v) / len(v):+.0%}" if v else "-"
    return f"{len(s)} | {sum(x > 0 for x in s) / len(s):.0%} | {a(s)} | {a(s[:-1])} | {a(s[:-2])}"


def best(p, carried):
    """The live outcome: carried to expiry when the contract outlives the day (news picks)."""
    return p["carry"] if carried and p.get("carry") else p["day1"]


def report(rows):
    lines = ["# Our catalyst picks on real option prices", "",
             "Every pre-market sniper and intraday pick since 2026-10-01, Alpaca option minute bars, "
             "costs 10% each way. Columns: trades | win% | avg | without the best | without the best "
             "two. Live rule: half at 3x, trail armed at 2x with a 40% giveback (`half3_trail`). "
             "See zoh/research/snipers.py.", ""]
    for source in ("sniper", "intraday"):
        sel = [r for r in rows if r["source"] == source and "live" in r["entries"]]
        if not sel:
            continue
        lines += [f"## {source} ({len(sel)} picks), live entry", "",
                  "### delta x exit, sold 15:45 day one", "",
                  "| delta | exit | n | win% | avg | -best | -best2 |", "|---|---|---|---|---|---|---|"]
        for d in DELTAS:
            lab = f"d{d:.2f}"
            for rule in RULES:
                xs = [r["entries"]["live"]["picks"][lab]["day1"][rule] for r in sel
                      if lab in r["entries"]["live"]["picks"]]
                lines.append(f"| {lab} | {rule} | {stats(xs)} |")
        lines += ["", "### delta x exit, carried to expiry when the contract outlives the day", "",
                  "| delta | exit | n | win% | avg | -best | -best2 |", "|---|---|---|---|---|---|---|"]
        for d in DELTAS:
            lab = f"d{d:.2f}"
            for rule in RULES:
                xs = [best(r["entries"]["live"]["picks"][lab], True)[rule] for r in sel
                      if lab in r["entries"]["live"]["picks"]]
                lines.append(f"| {lab} | {rule} | {stats(xs)} |")
        if source == "sniper":
            lines += ["", "### entry time (live exit, sold 15:45 day one)", "",
                      "| entry | delta | n | win% | avg | -best | -best2 |", "|---|---|---|---|---|---|---|"]
            for label in ("live", "09:40", "10:00"):
                for d in DELTAS:
                    lab = f"d{d:.2f}"
                    xs = [r["entries"][label]["picks"][lab]["day1"][LIVE] for r in rows
                          if r["source"] == source and label in r["entries"]
                          and lab in r["entries"][label]["picks"]]
                    lines.append(f"| {label} | {lab} | {stats(xs)} |")
        lines += ["", "### each pick (live entry, live exit, day one / carried)", "",
                  "| day | sym | dir | entry | stock open->close | " + " | ".join(f"d{d:.2f}" for d in DELTAS) + " |",
                  "|---|---|---|---|---|" + "---|" * len(DELTAS)]
        for r in sel:
            e = r["entries"]["live"]
            cells = []
            for d in DELTAS:
                p = e["picks"].get(f"d{d:.2f}")
                if not p:
                    cells.append("-")
                    continue
                c = f"{p['day1'][LIVE]:+.0%}"
                if p.get("carry"):
                    c += f" / {p['carry'][LIVE]:+.0%}"
                cells.append(f"{c} (pk {p['peak']:.1f}x)")
            lines.append(f"| {r['day']} | {r['sym']} | {r['kind']} | {e['t']} @ {e['spot']:.2f} | "
                         f"{r['close'] / r['open'] - 1:+.1%} | " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    rows = study(Alpaca())
    (OUT / "snipers.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    (OUT / "SNIPERS_REAL.md").write_text(report(rows))
    print(report(rows)[:6000])


if __name__ == "__main__":
    main()
