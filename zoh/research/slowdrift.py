"""The drift after a rating change, and which option holds it (2026-11-15, owner: "think: what else could work?").

Events: the rating headlines of journal/research/week46_upgrades.json (two years, 25 large caps, a
strict "<firm> upgrades / downgrades <stock>" headline before 09:30, the stock not against the rating
at 09:32). The stock: open of day 0 to the close of day 0, +1, +3, +5 and +10, against SPY and against
the same stocks on every other day. The options: instead of the nearest expiry far out of the money,
a call (put for a downgrade) on the Friday nearest three weeks out at about 0.60, 0.45 and 0.30 delta,
and the 0.60 / 0.30 debit vertical; bought at the first trade from 09:31 to 10:00 on day 0 or at the
day-0 close, sold at the close of day +3, +5 or +10. Real option bars (minute bars for the early
entry, daily closes after). A contract with no trade on its exit day is valued at its intrinsic value
(a floor) and counted. Costs: 5% of each leg's price each way (10% in a second table).

    python -m zoh.research.slowdrift            # collect and write SLOWDRIFT.md / slowdrift.json
    python -m zoh.research.slowdrift --report   # rebuild the report from slowdrift.json
"""
import argparse
import json
import statistics
from datetime import date, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..analyst import SYMBOLS
from ..realopt import daily_raw, hhmm, implied_vol, occ, option_minutes
from ..strategy import bs_delta
from .verticals import option_daily

DIR = journal.ROOT / "journal" / "research"
OUT, DATA, EVENTS = DIR / "SLOWDRIFT.md", DIR / "slowdrift.json", DIR / "week46_upgrades.json"
RECENT = "2026-08-13"
HORIZONS = (3, 5, 10)
TARGETS = (0.60, 0.45, 0.30)
WEEKS_OUT, LO, HI = 21, 12, 40          # calendar days to the expiry: nearest 21, between 12 and 40
COSTS = (0.05, 0.10)


def trio(xs):
    xs = sorted(xs)
    mean = lambda v: sum(v) / len(v) if v else None
    return len(xs), (sum(x > 0 for x in xs) / len(xs)) if xs else None, mean(xs), mean(xs[:-1]), mean(xs[:-2])


def cell(xs, digits=0):
    n, win, a, b, c = trio(xs)
    f = lambda v: "-" if v is None else f"{v * 100:+.{digits}f}%"
    return f"{n} | {'-' if win is None else f'{win:.0%}'} | {f(a)} / {f(b)} / {f(c)}"


def fridays(day, lo=LO, hi=HI, target=WEEKS_OUT):
    """The Fridays lo..hi calendar days out, the one nearest `target` first."""
    out, d = [], day + timedelta(days=lo)
    while d <= day + timedelta(days=hi):
        if d.weekday() == 4:
            out.append(d)
        d += timedelta(days=1)
    return sorted(out, key=lambda e: abs((e - day).days - target))


def strikes(spot, reach=0.15):
    steps = (0.5, 1) if spot < 50 else (1, 2.5, 5) if spot < 250 else (2.5, 5, 10)
    out = set()
    for step in steps:
        k = int(spot * (1 - reach) / step) * step
        while k <= spot * (1 + reach):
            if k > 0:
                out.add(round(k, 2))
            k += step
    return sorted(out)


def intrinsic(spot, strike, kind):
    return max(spot - strike, 0.0) if kind == "call" else max(strike - spot, 0.0)


def pick(table, target):
    """The strike whose |delta| is nearest the target: table = {strike: delta}."""
    return min(table, key=lambda k: abs(abs(table[k]) - target)) if table else None


def value_at(path, day, spot, strike, kind):
    """(price, traded): the contract's close that day, else its intrinsic value at the stock's close."""
    if path and path.get(day):
        return path[day], True
    return intrinsic(spot, strike, kind), False


def legs_return(entry, exit_, cost):
    """Return on one long leg bought at `entry` and sold at `exit_`, costs each way."""
    return exit_ * (1 - cost) / (entry * (1 + cost)) - 1 if entry > 0 else None


def vertical_return(long_in, short_in, long_out, short_out, cost):
    debit = long_in * (1 + cost) - short_in * (1 - cost)
    if debit <= 0.05:
        return None
    return (long_out * (1 - cost) - short_out * (1 + cost)) / debit - 1


def stock_paths(api, syms, start, end):
    """{sym: [(day, open, close)]}, unadjusted, so strikes and prices agree."""
    out = {}
    for s in syms:
        try:
            out[s] = daily_raw(api, s, start, end)
        except AlpacaError:
            out[s] = []
    return out


def one_event(api, ev, bars):
    """The option legs of one event, or None when no listed expiry has prices on day 0."""
    sym, day, kind = ev["sym"], date.fromisoformat(ev["day"]), ev["kind"]
    days = [d for d, _, _ in bars]
    if day not in days:
        return None
    i = days.index(day)
    close = {d: c for d, _, c in bars}
    spot_open, spot_close = ev["spot"], close[day]
    exits = {h: days[i + h] for h in HORIZONS if i + h < len(days)}
    if not exits:
        return None
    last = max(exits.values())
    for expiry in fridays(day)[:3]:
        if expiry <= last:
            continue
        grid = {occ(sym, expiry, k, kind): k for k in strikes(spot_open)}
        try:
            paths = option_daily(api, list(grid), day, last)
        except AlpacaError:
            continue
        by_strike = {grid[s]: p for s, p in paths.items() if p.get(day)}
        if len(by_strike) < 4:
            continue
        years = (expiry - day).days / 365
        d_open, d_close = {}, {}
        for k, p in by_strike.items():
            iv = implied_vol(p[day], spot_close, k, years, kind)
            if iv:
                d_open[k], d_close[k] = bs_delta(spot_open, k, years, iv, kind), bs_delta(spot_close, k, years, iv, kind)
        if len(d_open) < 4:
            continue
        row = {"sym": sym, "day": ev["day"], "kind": kind, "expiry": expiry.isoformat(), "spot": spot_open,
               "close0": spot_close, "headline": ev.get("headline", ""), "early": {}, "late": {}}
        # early: strikes chosen at the 09:32 stock price, bought at the first trade 09:31-10:00
        chosen = {f"d{t:.2f}": pick(d_open, t) for t in TARGETS}
        try:
            mins = option_minutes(api, [occ(sym, expiry, k, kind) for k in set(chosen.values())], day)
        except AlpacaError:
            mins = {}
        for label, k in chosen.items():
            first = next((b for b in mins.get(occ(sym, expiry, k, kind), [])
                          if hhmm("09:31") <= b["t"].time() <= hhmm("10:00") and b["c"] > 0), None)
            if first:
                row["early"][label] = {"strike": k, "delta": round(abs(d_open[k]), 3), "px": first["c"],
                                       "t": first["t"].strftime("%H:%M"),
                                       "out": {h: value_at(by_strike[k], d, close[d], k, kind) for h, d in exits.items()}}
        # late: strikes chosen at the day-0 close, bought at that close
        for t in TARGETS:
            k = pick(d_close, t)
            row["late"][f"d{t:.2f}"] = {"strike": k, "delta": round(abs(d_close[k]), 3), "px": by_strike[k][day],
                                        "out": {h: value_at(by_strike[k], d, close[d], k, kind) for h, d in exits.items()}}
        row["stock"] = {h: {"from_open": (close[d] / bars[i][1] - 1), "from_close": (close[d] / spot_close - 1)}
                        for h, d in exits.items()}
        return row
    return None


def collect(api, log=print):
    events = json.loads(EVENTS.read_text())
    syms = sorted({e["sym"] for e in events})
    first = min(date.fromisoformat(e["day"]) for e in events)
    end = date.today() - timedelta(days=1)
    paths = stock_paths(api, syms, first - timedelta(days=5), end)
    rows = []
    for ev in sorted(events, key=lambda e: e["day"]):
        r = one_event(api, ev, paths.get(ev["sym"], []))
        if r:
            rows.append(r)
            log(f"{ev['day']} {ev['sym']} {ev['kind']} expiry {r['expiry']} early {list(r['early'])}", flush=True)
    return {"rows": rows, "events": len(events), "drift": drift(api, events)}


def drift(api, events):
    """Open of day 0 to the close of day +k, signed the rating's way, against the same stocks on other days."""
    syms = sorted(set(SYMBOLS) | {"SPY"})
    bars = api.daily_bars_multi(syms, date(2024, 2, 1), date.today() - timedelta(days=1))
    B = {s: [(b["t"][:10], b["o"], b["c"]) for b in v] for s, v in bars.items()}
    idx = {s: {d: i for i, (d, _, _) in enumerate(v)} for s, v in B.items()}
    marked = {(e["sym"], e["day"]) for e in events}

    def move(sym, day, k):
        i = idx.get(sym, {}).get(day)
        if i is None or i + k >= len(B[sym]):
            return None
        return B[sym][i + k][2] / B[sym][i][1] - 1

    out = {}
    for label, sel in (("upgrades", lambda e: e["kind"] == "call"),
                       ("upgrades, last 3 months", lambda e: e["kind"] == "call" and e["day"] >= RECENT),
                       ("downgrades", lambda e: e["kind"] == "put")):
        for k in (0, 1, 3, 5, 10):
            raw, ex = [], []
            for e in events:
                a, q = move(e["sym"], e["day"], k), move("SPY", e["day"], k)
                if sel(e) and a is not None and q is not None:
                    s = 1 if e["kind"] == "call" else -1
                    raw.append(s * a)
                    ex.append(s * (a - q))
            out[f"{label} | {k}"] = {"raw": raw, "excess": ex}
    for k in (0, 1, 3, 5, 10):
        raw = [m for s in SYMBOLS for d in idx.get(s, {}) if (s, d) not in marked
               for m in [move(s, d, k)] if m is not None]
        out[f"baseline | {k}"] = {"n": len(raw), "avg": statistics.mean(raw), "up": sum(x > 0 for x in raw) / len(raw)}
    return out


def returns(rows, entry, label, horizon, cost, kind="call", since=None, vertical=False):
    xs, floor = [], 0
    for r in rows:
        if r["kind"] != kind or (since and r["day"] < since):
            continue
        legs = r[entry]
        h = str(horizon)
        if vertical:
            a, b = legs.get("d0.60"), legs.get("d0.30")
            if not a or not b or a["strike"] == b["strike"] or h not in a["out"] or h not in b["out"]:
                continue
            x = vertical_return(a["px"], b["px"], a["out"][h][0], b["out"][h][0], cost)
            floor += (not a["out"][h][1]) or (not b["out"][h][1])
        else:
            a = legs.get(label)
            if not a or h not in a["out"]:
                continue
            x = legs_return(a["px"], a["out"][h][0], cost)
            floor += not a["out"][h][1]
        if x is not None:
            xs.append(x)
    return xs, floor


def report(data):
    rows = json.loads(json.dumps(data["rows"]))        # horizons become string keys either way
    d = data["drift"]
    pct = lambda x, n=2: f"{x * 100:+.{n}f}%"
    L = ["# The drift after a rating change, and the option that holds it", "",
         f"{data['events']} rating headlines of two years on 25 large caps (journal/research/week46_upgrades.json: a strict "
         "'<firm> upgrades / downgrades <stock>' headline before 09:30, the stock not against the rating at 09:32). "
         "See zoh/research/slowdrift.py. `a / b / c` = average / without the best / without the best two.", "",
         "## 1. The stock, from the open of day 0, signed the rating's way", "",
         "| events | to the close of | n | up | avg / without the best / without the best two | against SPY | the same stocks on every other day |",
         "|---|---|---|---|---|---|---|"]
    for label in ("upgrades", "upgrades, last 3 months", "downgrades"):
        for k in (0, 1, 3, 5, 10):
            v, b = d[f"{label} | {k}"], d[f"baseline | {k}"]
            n, up, a, c1, c2 = trio(v["raw"])
            base = f"{pct(b['avg'])} ({b['up']:.0%} up)" if label != "downgrades" else f"{pct(-b['avg'])}"
            L.append(f"| {label} | day +{k} | {n} | {up:.0%} | {pct(a)} / {pct(c1)} / {pct(c2)} | {pct(statistics.mean(v['excess']))} | {base} |")
    for cost in COSTS:
        L += ["", f"## Options about three weeks out, costs {cost:.0%} of each leg each way", ""]
        for kind, name in (("call", "upgrades"), ("put", "downgrades")):
            for since, per in ((None, "two years"), (RECENT, "last 3 months")):
                if kind == "put" and since:
                    continue
                L += [f"### {name}, {per}", "",
                      "| entry | structure | sold at the close of day +3: n / win / a / b / c | day +5 | day +10 | exits valued at intrinsic (day +5) |",
                      "|---|---|---|---|---|---|"]
                for entry, ename in (("early", "first trade 09:31-10:00"), ("late", "the day-0 close")):
                    for label, sname in (("d0.60", "0.60 delta"), ("d0.45", "0.45 delta"), ("d0.30", "0.30 delta"), (None, "0.60 / 0.30 vertical")):
                        cells, fl = [], 0
                        for h in HORIZONS:
                            xs, f = returns(rows, entry, label, h, cost, kind, since, vertical=label is None)
                            cells.append(cell(xs))
                            fl = f if h == 5 else fl
                        L.append(f"| {ename} | {sname} | {cells[0]} | {cells[1]} | {cells[2]} | {fl} |")
                L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.report:
        data = json.loads(DATA.read_text())
    else:
        data = collect(Alpaca())
        DATA.write_text(json.dumps(data, indent=0, default=str) + "\n")
        data = json.loads(DATA.read_text())
    text = report(data)
    OUT.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
