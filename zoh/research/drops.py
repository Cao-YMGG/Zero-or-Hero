"""Were the drops traceable? Warning lights on the evening before vs what followed (owner, 2026-11-13).

The owner's claim after 10-30, 11-05, 11-09 and 11-12: "these drops all had signs you could follow".
Tested both ways on Alpaca daily bars: not only "were the lights on before the drops" (recall) but
"what happened on ALL the evenings the same lights were on" (hit rate, false alarms, lift over the
unconditional rate), and per episode, because lit evenings come in runs.

Lights, each known at the close (chips = the equal-weight basket of themes.THEMES['chips']):
  turning    chips theme state 'turning' (>= 3 of the five turn flags in zoh/research/themes.py)
  diverge    chips <= 95% of their 20-day high while SPY is within 2% of its own (themes' DIVERGE)
  stretched  SMH >= 12% below its 20-day closing high while SPY is down < 1.5% over five sessions
             (the other Claude's condition, chosen after 2026-11-05)
  breadth    >= 75% of the chip names below their own 20-day average
  rates      TLT down >= 2% over five sessions (long yields rising fast)
Drops: SPY <= -1.5% close to close, SMH <= -4%, within the next 1, 3 and 5 sessions.

Also: how single-name event gaps traded after the open (gap <= -5% and -3% on the mega caps, open ->
close), since 'seeing it coming' only pays if the move is still there after 09:30.

Finally the lights against our own open-drive rule on real 0DTE prices (opendrive.json), because a
light is only worth something to us if the trades differ on lit days.

    python -m zoh.research.drops [--start 2020-01-01]
    python -m zoh.research.drops --today        # the lights at the last close, for the pre-market file
"""
import argparse
import json
import statistics as st
from datetime import date, datetime, timedelta, timezone

from .. import journal
from ..alpaca import Alpaca
from ..runup import daily
from .themes import MONTH, QUIET, THEMES, basket, flags, state_of

OUT = journal.ROOT / "journal" / "research" / "DROPS.md"
GAPPERS = ["NVDA", "AMD", "AVGO", "MU", "INTC", "TSM", "TSLA", "META", "AAPL", "MSFT", "GOOGL", "AMZN",
           "NFLX", "ORCL", "PLTR", "COIN"]
SPY_DROP, SMH_DROP = -0.015, -0.04
HORIZONS = (1, 3, 5)
SINGLE = ("turning", "diverge", "stretched", "breadth", "rates")
EPISODE_START = date(2026, 10, 28)  # evenings whose 5-day window reaches this day are the known episode


def aligned(bars, days):
    """Closes on the SPY calendar, carrying the last close over a missing day."""
    m = {d: c for d, _, c in bars}
    out, last = [], None
    for d in days:
        last = m.get(d, last)
        out.append(last)
    return out


def returns(c):
    return [None] + [(c[i] / c[i - 1] - 1) if c[i] and c[i - 1] else None for i in range(1, len(c))]


def any_hit(rets, i, k, threshold):
    """True if any of the k sessions after index i fell to the threshold; None without a full window."""
    if i + k >= len(rets):
        return None
    return any(r is not None and r <= threshold for r in rets[i + 1:i + k + 1])


def runs(lit, quiet=QUIET):
    """First index of each run of lit evenings, a run ending after `quiet` unlit evenings."""
    out, gap = [], quiet
    for i, on in enumerate(lit):
        if on:
            if gap >= quiet:
                out.append(i)
            gap = 0
        else:
            gap += 1
    return out


def lights_at(i, days, spy_bars, spy, smh, tlt, idx, members):
    turn, heat = flags(idx, spy_bars, members, days, i)
    window = days[i - 19:i + 1]
    below = []
    for m in members:
        closes = [m[d][1] for d in window if d in m]
        if days[i] in m and len(closes) >= 10:
            below.append(m[days[i]][1] < st.mean(closes))
    got = {
        "turning": state_of(turn, heat) == "turning",
        "diverge": bool(turn["DIVERGE"]),
        "stretched": bool(smh[i] and smh[i] / max(x for x in smh[i - 19:i + 1] if x) - 1 <= -0.12
                          and spy[i] / spy[i - 5] - 1 > -0.015),
        "breadth": bool(below) and sum(below) / len(below) >= 0.75,
        "rates": bool(tlt[i] and tlt[i - 5] and tlt[i] / tlt[i - 5] - 1 <= -0.02),
    }
    n = sum(got[k] for k in SINGLE)
    got["two or more"] = n >= 2
    got["three or more"] = n >= 3
    got["turning + rates"] = got["turning"] and got["rates"]
    return got


def rate(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs), len(xs)) if xs else (None, 0)


def pct(x, digits=0):
    return "-" if x is None else f"{x * 100:.{digits}f}%"


def lift(p, base):
    return "-" if p is None or not base else f"{p / base:.1f}x"


def study(api, start):
    end = datetime.now(timezone.utc) - timedelta(minutes=30)
    syms = sorted(set(THEMES["chips"]) | set(GAPPERS) | {"SPY", "SMH", "TLT"})
    bars = daily(api, syms, datetime.combine(start, datetime.min.time(), timezone.utc) - timedelta(days=60), end)
    spy_bars = bars["SPY"]
    days = [d for d, _, _ in spy_bars]
    spy, smh, tlt = aligned(spy_bars, days), aligned(bars["SMH"], days), aligned(bars["TLT"], days)
    members = [{d: (o, c) for d, o, c in bars.get(s, [])} for s in THEMES["chips"]]
    idx = basket(days, members)
    rs, rm = returns(spy), returns(smh)
    rows = []
    for i in range(MONTH, len(days)):
        if days[i] < start:
            continue
        row = {"i": i, "day": days[i], "lights": lights_at(i, days, spy_bars, spy, smh, tlt, idx, members)}
        for k in HORIZONS:
            row[f"spy{k}"] = any_hit(rs, i, k, SPY_DROP)
            row[f"smh{k}"] = any_hit(rm, i, k, SMH_DROP)
        row["spy10"] = any_hit(rs, i, 10, SPY_DROP)
        row["up5"] = any_hit([None if r is None else -r for r in rs], i, 5, SPY_DROP)  # a +1.5% day
        row["next"] = rs[i + 1] if i + 1 < len(days) else None
        row["next_oc"] = (spy_bars[i + 1][2] / spy_bars[i + 1][1] - 1) if i + 1 < len(days) else None
        row["fwd_spy"] = spy[i + 5] / spy[i] - 1 if i + 5 < len(days) else None
        row["fwd_smh"] = smh[i + 5] / smh[i] - 1 if i + 5 < len(days) and smh[i] else None
        rows.append(row)
    return {"days": days, "bars": bars, "spy": spy, "smh": smh, "rs": rs, "rm": rm, "rows": rows}


def window_rows(rows, lo=None, hi=None):
    return [r for r in rows if (lo is None or r["day"] >= lo) and (hi is None or r["day"] <= hi)]


def light_table(rows, title):
    names = list(rows[0]["lights"]) if rows else []
    base = {key: rate([r[key] for r in rows])[0] for key in
            [f"spy{k}" for k in HORIZONS] + [f"smh{k}" for k in HORIZONS]}
    fs, fm = rate([r["fwd_spy"] for r in rows])[0], rate([r["fwd_smh"] for r in rows])[0]
    out = [f"### {title}", "",
           f"{len(rows)} evenings. Unconditional: SPY <= -1.5% within 1 / 3 / 5 sessions "
           f"{pct(base['spy1'])} / {pct(base['spy3'])} / {pct(base['spy5'])}; SMH <= -4% "
           f"{pct(base['smh1'])} / {pct(base['smh3'])} / {pct(base['smh5'])}; 5-day forward return SPY {pct(fs, 2)}, "
           f"SMH {pct(fm, 2)}.", "",
           "| light | lit evenings | share | SPY drop 1d | 3d | 5d (lift) | SMH drop 5d (lift) | fwd 5d SPY | fwd 5d SMH | "
           "episodes | episodes with an SPY drop in 5 / 10 sessions |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in names:
        lit = [r for r in rows if r["lights"][name]]
        if not lit:
            out.append(f"| {name} | 0 | 0% | - | - | - | - | - | - | 0 | - |")
            continue
        p1, p3, p5 = (rate([r[f"spy{k}"] for r in lit])[0] for k in HORIZONS)
        m5 = rate([r["smh5"] for r in lit])[0]
        starts = runs([r["lights"][name] for r in rows])
        e5 = rate([rows[s]["spy5"] for s in starts])
        e10 = rate([rows[s]["spy10"] for s in starts])
        out.append(f"| {name} | {len(lit)} | {pct(len(lit) / len(rows))} | {pct(p1)} | {pct(p3)} | "
                   f"{pct(p5)} ({lift(p5, base['spy5'])}) | {pct(m5)} ({lift(m5, base['smh5'])}) | "
                   f"{pct(rate([r['fwd_spy'] for r in lit])[0], 2)} | {pct(rate([r['fwd_smh'] for r in lit])[0], 2)} | "
                   f"{len(starts)} | {pct(e5[0])} of {e5[1]} / {pct(e10[0])} of {e10[1]} |")
    return out + [""]


def direction_table(rows, title):
    """Drops against rallies of the same size, and the next session: a light that raises both is a
    volatility state, not a direction call."""
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return st.mean(xs) if xs else None
    base_d, base_u = rate([r["spy5"] for r in rows])[0], rate([r["up5"] for r in rows])[0]
    out = [f"### {title}", "",
           f"Unconditional: a -1.5% SPY day within 5 sessions {pct(base_d)}, a +1.5% day {pct(base_u)}; next session "
           f"{pct(mean([r['next'] for r in rows]), 2)} close to close, {pct(mean([r['next_oc'] for r in rows]), 2)} open "
           f"to close, average size {pct(mean([abs(r['next']) for r in rows if r['next'] is not None]), 2)}.", "",
           "| light | lit | -1.5% day in 5 (lift) | +1.5% day in 5 (lift) | next session close-close | open->close | "
           "down days | average size | fwd 5d SPY median |", "|---|---|---|---|---|---|---|---|---|"]
    for name in rows[0]["lights"]:
        lit = [r for r in rows if r["lights"][name]]
        if not lit:
            continue
        d, u = rate([r["spy5"] for r in lit])[0], rate([r["up5"] for r in lit])[0]
        nxt = [r["next"] for r in lit if r["next"] is not None]
        fwd = [r["fwd_spy"] for r in lit if r["fwd_spy"] is not None]
        out.append(f"| {name} | {len(lit)} | {pct(d)} ({lift(d, base_d)}) | {pct(u)} ({lift(u, base_u)}) | "
                   f"{pct(mean(nxt), 2)} | {pct(mean([r['next_oc'] for r in lit]), 2)} | "
                   f"{pct(sum(x < 0 for x in nxt) / len(nxt)) if nxt else '-'} | {pct(mean([abs(x) for x in nxt]), 2)} | "
                   f"{pct(st.median(fwd), 2) if fwd else '-'} |")
    return out + [""]


def episode_table(data, rows, name):
    """Every run of one light: the first lit evening and what SPY and SMH did next."""
    days, spy, smh, rs = data["days"], data["spy"], data["smh"], data["rs"]
    lit = [r["lights"][name] for r in rows]
    out = [f"| first lit evening | lit evenings in the run | SMH vs its 20-day high | worst SPY day in the next 5 | in the next 10 | "
           "SPY 5 sessions later | 10 later | SMH 10 later |", "|---|---|---|---|---|---|---|---|"]
    starts = runs(lit)
    for n, s0 in enumerate(starts):
        i = rows[s0]["i"]
        stop = starts[n + 1] if n + 1 < len(starts) else len(rows)
        length = sum(lit[s0:stop])
        w5 = [x for x in rs[i + 1:i + 6] if x is not None]
        w10 = [x for x in rs[i + 1:i + 11] if x is not None]
        f = lambda c, k: pct(c[i + k] / c[i] - 1, 1) if i + k < len(days) else "-"
        out.append(f"| {days[i]} | {length} | {pct(smh[i] / max(x for x in smh[i - 19:i + 1] if x) - 1, 1)} | "
                   f"{pct(min(w5), 1) if w5 else '-'} | {pct(min(w10), 1) if w10 else '-'} | {f(spy, 5)} | {f(spy, 10)} | "
                   f"{f(smh, 10)} |")
    return out + [""]


def opendrive_split(rows):
    """Our own rule on real 0DTE prices (journal/research/opendrive.json: buy at 10:00 the way of the
    move from the open, ~0.7% out of the money, 10% costs), split by the lights of the evening before.
    Live-like = SPY at least 0.5% from its open at 10:00 either way, NVDA/TSLA calls at +0.8% or more,
    macro days out. One line per exit rule so the light is not judged on a single exit."""
    path = journal.ROOT / "journal" / "research" / "opendrive.json"
    if not path.exists():
        return ["(journal/research/opendrive.json not found)", ""]
    trades = json.loads(path.read_text())
    order = [r["day"] for r in rows]
    before = {order[i].isoformat(): rows[i - 1]["lights"] for i in range(1, len(order))}
    live = [t for t in trades if not t.get("macro") and t["day"] in before and (
        (t["sym"] == "SPY" and abs(t["move10"]) >= 0.005) or
        (t["sym"] in ("NVDA", "TSLA") and t["kind"] == "call" and t["move10"] >= 0.008))]

    def line(label, ts, key):
        xs = sorted(t["exits_10"][key] for t in ts)
        if not xs:
            return f"| {label} | {key} | 0 | - | - | - | - |"
        cut = lambda k: pct(st.mean(xs[:-k])) if len(xs) > k else "-"
        return (f"| {label} | {key} | {len(xs)} | {pct(sum(x > 0 for x in xs) / len(xs))} | {pct(st.mean(xs))} | "
                f"{cut(1)} | {cut(2)} |")
    groups = [("any light", lambda L: any(L[k] for k in SINGLE)), ("no light", lambda L: not any(L[k] for k in SINGLE)),
              ("stretched", lambda L: L["stretched"]), ("breadth", lambda L: L["breadth"]),
              ("turning", lambda L: L["turning"]), ("rates", lambda L: L["rates"])]
    span = f"{min(t['day'] for t in live)} to {max(t['day'] for t in live)}" if live else "-"
    out = [f"{len(live)} live-like trades, {span} (SPY calls and puts, NVDA/TSLA calls). Exits: hold = to 15:30, take3 = "
           "all out at 3x, half3_trail = half at 3x and a trail on the rest, trail = trail only (zoh/research/opendrive.py).",
           "", "| lights the evening before | exit | trades | win% | avg | w/o best | w/o best 2 |", "|---|---|---|---|---|---|---|"]
    for label, test in groups:
        ts = [t for t in live if test(before[t["day"]])]
        for key in ("hold", "take3", "half3_trail", "trail"):
            out.append(line(label, ts, key))
    out += ["", "By side, exit take3:", "", "| lights the evening before | side | trades | win% | avg | w/o best | w/o best 2 |",
            "|---|---|---|---|---|---|---|"]
    for label, test in groups[:4]:
        for side in ("call", "put"):
            ts = [t for t in live if test(before[t["day"]]) and t["kind"] == side]
            out.append(line(label, ts, "take3").replace("| take3 |", f"| {side} |"))
    # the one cell that stands out, checked by period and by underlying before anyone believes it
    last_day = date.fromisoformat(max(t["day"] for t in live)) if live else None
    out += ["", "Calls after a `breadth` evening against calls after any other evening (exit take3 / hold):", "",
            "| slice | breadth lit: trades | win% | avg take3 | w/o best 2 | avg hold | not lit: trades | win% | avg take3 | "
            "w/o best 2 | avg hold |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    calls = [t for t in live if t["kind"] == "call"]

    def half(ts):
        if not ts:
            return "0 | - | - | - | -"
        xs = sorted(t["exits_10"]["take3"] for t in ts)
        return (f"{len(xs)} | {pct(sum(x > 0 for x in xs) / len(xs))} | {pct(st.mean(xs))} | "
                f"{pct(st.mean(xs[:-2])) if len(xs) > 2 else '-'} | {pct(st.mean(t['exits_10']['hold'] for t in ts))}")
    slices = [("all", lambda t: True)]
    if last_day:
        slices += [("last 3 months of the data", lambda t: date.fromisoformat(t["day"]) > last_day - timedelta(days=92)),
                   ("last year of the data", lambda t: date.fromisoformat(t["day"]) > last_day - timedelta(days=365)),
                   ("before that", lambda t: date.fromisoformat(t["day"]) <= last_day - timedelta(days=365))]
    slices += [("SPY", lambda t: t["sym"] == "SPY"), ("NVDA / TSLA", lambda t: t["sym"] != "SPY")]
    for label, keep in slices:
        ts = [t for t in calls if keep(t)]
        out.append(f"| {label} | {half([t for t in ts if before[t['day']]['breadth']])} | "
                   f"{half([t for t in ts if not before[t['day']]['breadth']])} |")
    return out + [""]


def recall_table(data, rows):
    by_day = {r["day"]: r for r in rows}
    days, rs = data["days"], data["rs"]
    drops = [i for i in range(1, len(days)) if rs[i] is not None and rs[i] <= SPY_DROP and days[i - 1] in by_day]
    out = [f"{len(drops)} SPY drops of 1.5% or more. For each light: on how many of them it was lit the evening "
           "before (recall) against how often it is lit at all (prevalence). Recall near prevalence = no information.", "",
           "| light | lit before a drop | recall | prevalence | ratio |", "|---|---|---|---|---|"]
    for name in rows[0]["lights"]:
        hit = sum(by_day[days[i - 1]]["lights"][name] for i in drops)
        prev = sum(r["lights"][name] for r in rows) / len(rows)
        rec = hit / len(drops) if drops else None
        out.append(f"| {name} | {hit} of {len(drops)} | {pct(rec)} | {pct(prev)} | {lift(rec, prev)} |")
    none = sum(not any(by_day[days[i - 1]]["lights"][k] for k in SINGLE) for i in drops)
    out += ["", f"Drops with no light at all the evening before: {none} of {len(drops)}.", ""]
    return out


def gap_rows(data, start):
    """(symbol, day, gap, open->close) for every session of the mega caps and the two ETFs."""
    out = []
    for sym in GAPPERS + ["SPY", "SMH"]:
        b = data["bars"].get(sym, [])
        for j in range(1, len(b)):
            if b[j][0] >= start and b[j - 1][2] and b[j][1]:
                out.append((sym, b[j][0], b[j][1] / b[j - 1][2] - 1, b[j][2] / b[j][1] - 1))
    return out


def gap_table(gaps, since):
    def line(label, xs):
        if not xs:
            return f"| {label} | 0 | - | - | - | - |"
        oc = [x[3] for x in xs]
        return (f"| {label} | {len(xs)} | {pct(st.mean(x[2] for x in xs), 1)} | {pct(st.mean(oc), 2)} | "
                f"{pct(st.median(oc), 2)} | {pct(sum(o > 0 for o in oc) / len(oc))} |")
    stocks = [g for g in gaps if g[0] in GAPPERS and g[1] >= since]
    out = ["| group | events | mean gap | open->close mean | median | closed above the open |", "|---|---|---|---|---|---|",
           line("mega cap gap <= -5%", [g for g in stocks if g[2] <= -0.05]),
           line("mega cap gap -5% to -3%", [g for g in stocks if -0.05 < g[2] <= -0.03]),
           line("mega cap gap >= +5%", [g for g in stocks if g[2] >= 0.05]),
           line("mega cap, every session", stocks),
           line("NVDA gap <= -3%", [g for g in stocks if g[0] == "NVDA" and g[2] <= -0.03]),
           line("SMH gap <= -2%", [g for g in gaps if g[0] == "SMH" and g[1] >= since and g[2] <= -0.02]),
           line("SPY gap <= -0.7%", [g for g in gaps if g[0] == "SPY" and g[1] >= since and g[2] <= -0.007]),
           line("SPY, every session", [g for g in gaps if g[0] == "SPY" and g[1] >= since]), ""]
    return out


def recent_table(data, rows, since):
    by_day = {r["day"]: r for r in rows}
    days, rs, rm = data["days"], data["rs"], data["rm"]
    nv = {d: (o, c) for d, o, c in data["bars"].get("NVDA", [])}
    out = ["| day | SPY | SMH | NVDA close-close | NVDA gap | NVDA open->close | lights the evening before |",
           "|---|---|---|---|---|---|---|"]
    for i in range(1, len(days)):
        d, p = days[i], days[i - 1]
        if d < since or d not in nv or p not in nv:
            continue
        n_cc, n_gap, n_oc = nv[d][1] / nv[p][1] - 1, nv[d][0] / nv[p][1] - 1, nv[d][1] / nv[d][0] - 1
        if not ((rs[i] or 0) <= -0.01 or (rm[i] or 0) <= -0.03 or n_cc <= -0.04 or n_gap <= -0.05):
            continue
        on = [k for k in SINGLE if p in by_day and by_day[p]["lights"][k]]
        out.append(f"| {d} | {pct(rs[i], 2)} | {pct(rm[i], 2)} | {pct(n_cc, 1)} | {pct(n_gap, 1)} | {pct(n_oc, 1)} | "
                   f"{', '.join(on) or 'none'} |")
    return out + [""]


def report(data, start):
    rows = data["rows"]
    last = rows[-1]["day"]
    two = last - timedelta(days=730)
    known = [r for r in rows if r["day"] + timedelta(days=9) < EPISODE_START]  # 5 sessions stay before the episode
    out = ["# Were the drops traceable?", "",
           "How to read it: a light earns its name only if drops are clearly more frequent after it than on an average "
           "evening (lift well above 1), if the same is not true of rallies (otherwise it marks big days, not down days), and "
           "if our own trades differ on lit days. Recall alone (it was lit before the drop) proves nothing when the light is "
           "on a fifth of the time.", "",
           f"Alpaca daily bars {rows[0]['day']} to {last}. Lights are read at the close; a drop is SPY <= -1.5% "
           "(SMH <= -4%) close to close in the sessions after. Lift = rate on lit evenings / rate on all evenings. "
           "Episodes = runs of lit evenings (a run ends after 10 unlit sessions), counted from the first lit evening. "
           "See zoh/research/drops.py.", "",
           "## Hit rate and false alarms", ""]
    out += light_table(window_rows(rows, lo=two), f"Last two years ({two} on)")
    out += light_table(window_rows(rows, lo=date(last.year, 1, 1)), f"{last.year} only")
    out += light_table(known, f"Everything before the known episode ({rows[0]['day']} to mid-October 2026)")
    out += light_table(rows, f"Full sample ({rows[0]['day']} on)")
    now = [k for k in SINGLE if rows[-1]["lights"][k]]
    out.insert(6, f"Lit at the last close ({last}): {', '.join(now) or 'none'}.")
    out.insert(7, "")
    out += ["## Direction or just volatility?", ""]
    out += direction_table(window_rows(rows, lo=two), f"Last two years ({two} on)")
    out += direction_table(known, "Everything before the known episode")
    out += direction_table(rows, "Full sample")
    out += ["## Every 'stretched' episode", "",
            "SMH >= 12% below its 20-day closing high while SPY is down < 1.5% over five sessions; one row per run.", ""]
    out += episode_table(data, rows, "stretched")
    out += ["## Our open-drive rule on lit and unlit days", ""] + opendrive_split(rows)
    out += ["## Recall: were the lights on before the drops?", ""]
    out += [f"### Last two years"] + [""] + recall_table(data, window_rows(rows, lo=two))
    out += [f"### Full sample"] + [""] + recall_table(data, rows)
    gaps = gap_rows(data, start)
    out += ["## After the open: could a gap be traded?", "",
            "Gap = open vs the prior close; then the same day's open to close. Mega caps: " + ", ".join(GAPPERS) +
            " (earnings gaps included).", "", "### Last two years", ""] + gap_table(gaps, two)
    out += [f"### Full sample", ""] + gap_table(gaps, start)
    out += ["## The recent days", "",
            "Every session since 2026-10-01 with SPY <= -1%, SMH <= -3%, NVDA <= -4% or an NVDA gap <= -5%.", ""]
    out += recent_table(data, rows, date(2026, 10, 1))
    OUT.write_text("\n".join(out) + "\n")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", default="2020-01-01")
    p.add_argument("--today", action="store_true", help="print the lights at the last close and stop")
    a = p.parse_args()
    if a.today:
        rows = study(Alpaca(), date.today() - timedelta(days=120))["rows"]
        lit = [k for k in SINGLE if rows[-1]["lights"][k]]
        print(f"{rows[-1]['day']} lights: {', '.join(lit) or 'none'}")
        return
    start = date.fromisoformat(a.start)
    data = study(Alpaca(), start)
    print("\n".join(report(data, start)))


if __name__ == "__main__":
    main()
