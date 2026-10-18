"""Exits, strike choice, Tue/Thu next-day expiry and overnight carry on real option prices.

Sunday tests 7, 8, 13 and 18 (journal/research/SUNDAY_TESTS.md) on the same entries:
- rebound: a universe stock opens <= -2% vs the prior close, no macro release; 09:45 call.
  Mon/Wed/Fri with a same-day expiry (the champion), and Tue/Thu with the next day's expiry
  (rebound_scanner_any) as a separate study.
- meta_follow2: META on same-day expiry days, first 1-minute close 10:00-14:00 >= 2% from the open,
  follow it.
- upgrade: strict "<firm> Upgrades|Downgrades <stock> to <rating>" headlines before 09:30, buy at
  09:32 if the stock is not against the rating; nearest expiry (often carried overnight).
For each entry several contracts are priced from the same option minute bars (target deltas, and
strikes 0.5x / 1x the stock's 20-day average daily move out of the money), and each contract runs
every exit rule in EXITS. Contracts expiring after the entry day are also run carried to their
expiry (the live rule since 2026-10-07) next to "sold at 15:45 the first day".

Costs: buy at close x (1 + slip), sell at close x (1 - slip), at least $0.01 each way.

    python -m zoh.research.exits
"""
import json
import re
import statistics
import time
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..analyst import SYMBOLS as RATED
from ..analyst import rating_events
from ..realopt import (MWF, MWF_SINCE, START, UNIVERSE, Y, at_or_after, daily_raw,
                       has_same_day_expiry, implied_vol, occ, option_minutes, strike_grid)
from ..strategy import ET, MARKET_OPEN, bs_delta, hhmm, parse_bar, regular_session
from .opendrive import macro_days

SLIPS = (0.10, 0.05)
EXIT_AT = hhmm("15:45")
STRICT = re.compile(r"\b(upgrades|downgrades)\b .+ \bto\b", re.I)
OUT = journal.ROOT / "journal" / "research"

# rule -> (arm multiple, giveback, tight giveback once >= 5x or None, half-out multiple or None)
EXITS = {
    "trail2x": (2.0, 0.4, None, None),      # live rule
    "trail1.5x": (1.5, 0.4, None, None),    # trail_after 0.5
    "trail1.6x": (1.6, 0.4, None, None),
    "trail2x_tight5x": (2.0, 0.4, 0.25, None),
    "half2_trail": (2.0, 0.4, None, 2.0),
    "half3_trail": (2.0, 0.4, None, 3.0),
    "hold": (None, None, None, None),       # 15:45 only
}
DELTAS = {"rebound": (0.05, 0.08, 0.15, 0.30), "rebound_tt": (0.05, 0.08, 0.15, 0.30),
          "meta_follow2": (0.10, 0.20, 0.30), "upgrade": (0.10, 0.20, 0.30)}
SWINGS = (0.5, 1.0)


def bid(c, slip):
    return max(0.0, min(c * (1 - slip), c - 0.01))


def run(path, entry, slip, rule):
    """path [(datetime, close)] after the entry; exits at 15:45 of the path's last day.
    Returns the exit value per $1 of entry cost."""
    arm, give, tight, half = EXITS[rule]
    last_day = path[-1][0].date() if path else None
    peak, sold, value = entry, 0.0, 0.0  # sold = fraction already out, value = proceeds so far
    for t, c in path:
        b = bid(c, slip)
        if t.date() == last_day and t.time() >= EXIT_AT:
            return (value + (1 - sold) * b) / entry
        if half and not sold and b >= half * entry:
            value, sold = 0.5 * b, 0.5
        peak = max(peak, b)
        if arm and peak >= arm * entry:
            g = tight if tight and peak >= 5 * entry else give
            if b <= max(entry, peak * (1 - g)):
                return (value + (1 - sold) * b) / entry
    b = bid(path[-1][1], slip) if path else 0.0
    return (value + (1 - sold) * b) / entry


def nearest_expiry(sym, day, after=False):
    d = day + timedelta(days=1) if after else day
    for _ in range(8):
        if d.weekday() < 5 and has_same_day_expiry(sym, d):
            return d
        d += timedelta(days=1)
    return None


def candidates(api, sym, day, expiry, entry_t, spot, kind):
    """[(contract, strike, delta, entry_bar)] with a quote within 5 minutes of entry_t, and the
    day's minute bars by contract."""
    mins_left = 16 * 60 - (entry_t.hour * 60 + entry_t.minute) + (expiry - day).days * 390
    years = mins_left / Y
    strikes = {occ(sym, expiry, k, kind): k for k in strike_grid(spot, kind)}
    keys, opts = list(strikes), {}
    for j in range(0, len(keys), 100):
        opts.update(option_minutes(api, keys[j:j + 100], day))
    out = []
    for s, bars in opts.items():
        b = at_or_after(bars, entry_t, 5)
        if not b or b["c"] <= 0:
            continue
        iv = implied_vol(b["c"], spot, strikes[s], years, kind)
        if iv:
            out.append((s, strikes[s], abs(bs_delta(spot, strikes[s], years, iv, kind)), b))
    return out, opts


def choose(cands, spot, kind, study, swing):
    picks = {}
    for d in DELTAS[study]:
        if cands:
            picks[f"d{d:.2f}"] = min(cands, key=lambda x: abs(x[2] - d))
    for k in SWINGS:
        if cands and swing:
            target = spot * (1 + k * swing) if kind == "call" else spot * (1 - k * swing)
            picks[f"swing{k}"] = min(cands, key=lambda x: abs(x[1] - target))
    return picks


def price(api, sym, day, expiry, entry_t, spot, kind, study, swing, **extra):
    try:
        cands, opts = candidates(api, sym, day, expiry, entry_t, spot, kind)
    except AlpacaError:
        return None
    if not cands:
        return None
    row = {"study": study, "sym": sym, "day": day.isoformat(), "expiry": expiry.isoformat(),
           "kind": kind, "spot": round(spot, 2), "swing": round(swing, 4) if swing else None,
           **extra, "picks": {}}
    for label, (s, k, d, b) in choose(cands, spot, kind, study, swing).items():
        path = [(x["t"], x["c"]) for x in opts[s] if x["t"] > b["t"]]
        if not path:
            continue
        pick = {"contract": s, "strike": k, "delta": round(d, 3), "px": b["c"]}
        for slip in SLIPS:
            entry = max(b["c"] * (1 + slip), b["c"] + 0.01)
            pick[f"exits_{int(slip * 100)}"] = {r: round(run(path, entry, slip, r) - 1, 4) for r in EXITS}
            pick[f"peak_{int(slip * 100)}"] = round(max(bid(c, slip) for _, c in path) / entry, 3)
        if expiry > day:  # carried to expiry (live rule) vs sold at 15:45 on day one
            later = []
            d2 = day + timedelta(days=1)
            while d2 <= expiry:
                if d2.weekday() < 5:
                    try:
                        later += [(x["t"], x["c"]) for x in option_minutes(api, [s], d2).get(s, [])]
                    except AlpacaError:
                        pass
                d2 += timedelta(days=1)
            if later:
                for slip in SLIPS:
                    entry = max(b["c"] * (1 + slip), b["c"] + 0.01)
                    pick[f"carry_{int(slip * 100)}"] = {r: round(run(path + later, entry, slip, r) - 1, 4)
                                                       for r in ("trail2x", "hold")}
        row["picks"][label] = pick
    time.sleep(0.1)
    return row if row["picks"] else None


def swing_of(days, i):
    """20-day average absolute daily move before day i."""
    xs = [abs(days[j][2] / days[j - 1][2] - 1) for j in range(max(1, i - 20), i)]
    return sum(xs) / len(xs) if xs else None


def spot_at(api, sym, day, t):
    start = datetime.combine(day, MARKET_OPEN, ET)
    try:
        bars = regular_session([parse_bar(b) for b in api.stock_bars(
            sym, start, datetime.combine(day, t, ET) + timedelta(minutes=3), feed="sip", adjustment="raw")])
    except AlpacaError:
        return None, []
    return bars, bars


def study_rebound(api, rows, end, macro):
    for sym in UNIVERSE:
        days = daily_raw(api, sym, START - timedelta(days=40), end)
        n = 0
        for i in range(1, len(days)):
            day, o, _ = days[i]
            if day < START or macro.get(day.isoformat()) or o / days[i - 1][2] - 1 > -0.02:
                continue
            if has_same_day_expiry(sym, day):
                study, expiry = "rebound", day
            elif sym in MWF and day >= MWF_SINCE and day.weekday() in (1, 3):
                study, expiry = "rebound_tt", nearest_expiry(sym, day, after=True)
            else:
                continue
            bars, _ = spot_at(api, sym, day, hhmm("09:45"))
            b = at_or_after(bars, hhmm("09:44"), 3)
            if not b:
                continue
            r = price(api, sym, day, expiry, hhmm("09:45"), b["c"], "call", study, swing_of(days, i),
                      gap=round(o / days[i - 1][2] - 1, 4))
            if r:
                rows.append(r)
                n += 1
        print(f"rebound {sym}: {n}", flush=True)


def study_meta(api, rows, end):
    d = START
    while d <= end:
        if d.weekday() < 5 and has_same_day_expiry("META", d):
            start = datetime.combine(d, MARKET_OPEN, ET)
            try:
                bars = regular_session([parse_bar(b) for b in api.stock_bars(
                    "META", start, datetime.combine(d, hhmm("14:01"), ET), feed="sip", adjustment="raw")])
            except AlpacaError:
                bars = []
            if len(bars) >= 40:
                o = bars[0]["o"]
                hit = next((b for b in bars if hhmm("10:00") <= b["t"].time() <= hhmm("14:00")
                            and abs(b["c"] / o - 1) >= 0.02), None)
                if hit:
                    kind = "call" if hit["c"] > o else "put"
                    r = price(api, "META", d, d, (hit["t"] + timedelta(minutes=1)).time(), hit["c"], kind,
                              "meta_follow2", None)
                    if r:
                        rows.append(r)
        d += timedelta(days=1)
    print(f"meta_follow2: {sum(r['study'] == 'meta_follow2' for r in rows)}", flush=True)


def study_upgrades(api, rows, end):
    for sym in RATED:
        try:
            events = rating_events(api, sym, START, end)
        except AlpacaError:
            continue
        daily = {d: (o, c) for d, o, c in daily_raw(api, sym, START - timedelta(days=40), end)}
        order = sorted(daily)
        for day, kind, head in events:
            if not STRICT.search(head) or day not in daily:
                continue
            expiry = nearest_expiry(sym, day)
            if not expiry:
                continue
            bars, _ = spot_at(api, sym, day, hhmm("09:32"))
            b = at_or_after(bars, hhmm("09:31"), 3)
            if not b:
                continue
            sign = 1 if kind == "call" else -1
            if sign * (b["c"] / bars[0]["o"] - 1) < 0:
                continue
            i = order.index(day)
            xs = [abs(daily[order[j]][1] / daily[order[j - 1]][1] - 1) for j in range(max(1, i - 20), i)]
            r = price(api, sym, day, expiry, hhmm("09:32"), b["c"], kind, "upgrade",
                      sum(xs) / len(xs) if xs else None, headline=head[:90])
            if r:
                rows.append(r)
        print(f"upgrades {sym}: {sum(r['study'] == 'upgrade' and r['sym'] == sym for r in rows)}", flush=True)


def stats(xs):
    if not xs:
        return "-"
    s = sorted(xs)
    a = lambda v: f"{sum(v) / len(v):+.0%}" if v else "-"
    return f"{len(s)} | {sum(x > 0 for x in s) / len(s):.0%} | {a(s)} | {a(s[:-1])} | {a(s[:-2])}"


def report(rows, end):
    recent = (end - timedelta(days=91)).isoformat()
    lines = ["# Exits, strikes, Tue/Thu expiry and overnight carry on real option prices", "",
             f"Data {START} to {end}. Costs 10% of the option price each way. Columns: trades | win% | "
             "avg | avg without the best trade | without the best two. See zoh/research/exits.py.", ""]
    for study in ("rebound", "rebound_tt", "meta_follow2", "upgrade"):
        sel = [r for r in rows if r["study"] == study]
        if not sel:
            continue
        labels = sorted({k for r in sel for k in r["picks"]})
        lines += [f"## {study}", ""]
        for period, cut in (("last 3 months", recent), ("all", "0000")):
            lines += [f"### {period}", "", "| contract | exit | n | win% | avg | -best | -best2 |",
                      "|---|---|---|---|---|---|---|"]
            for lab in labels:
                for rule in EXITS:
                    xs = [r["picks"][lab]["exits_10"][rule] for r in sel
                          if r["day"] >= cut and lab in r["picks"]]
                    lines.append(f"| {lab} | {rule} | {stats(xs)} |")
            lines.append("")
        carried = [r for r in sel if any("carry_10" in p for p in r["picks"].values())]
        if carried:
            lines += ["### carried to expiry vs sold 15:45 day one (trail2x; same trades)", "",
                      "| contract | period | sold 15:45 | carried | carried, no trail |", "|---|---|---|---|---|"]
            for lab in labels:
                for period, cut in (("last 3 months", recent), ("all", "0000")):
                    ps = [r["picks"][lab] for r in carried if r["day"] >= cut and "carry_10" in r["picks"].get(lab, {})]
                    if ps:
                        lines.append(f"| {lab} | {period} | {stats([p['exits_10']['trail2x'] for p in ps])} | "
                                     f"{stats([p['carry_10']['trail2x'] for p in ps])} | "
                                     f"{stats([p['carry_10']['hold'] for p in ps])} |")
            lines.append("")
        affordable = [r["picks"][lab]["px"] for r in sel for lab in r["picks"]]
        if affordable:
            lines += [f"Median entry price over all picks: ${statistics.median(affordable):.2f}", ""]
    return "\n".join(lines) + "\n"


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    macro = macro_days()
    rows = []
    study_meta(api, rows, end)
    study_upgrades(api, rows, end)
    study_rebound(api, rows, end, macro)
    (OUT / "exits.json").write_text(json.dumps(rows, indent=0) + "\n")
    (OUT / "EXITS.md").write_text(report(rows, end))
    print(report(rows, end)[:4000])


if __name__ == "__main__":
    main()
