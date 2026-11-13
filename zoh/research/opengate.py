"""SUNDAY_TESTS 62: is chip breadth a gate for the open-drive calls, and does the put hand earn its ledger?

Same signals as the live ledgers: at 10:00 ET, SPY at least 0.5% from its open either way, NVDA/TSLA at
least 0.8% above their open on a same-day-expiry day. Real 1-minute option closes, 10% costs each way, and
two strikes per signal from the same request: about 0.7% out of the money (OPENDRIVE.md) and the contract
nearest 0.35 delta at 10:00 (what the ledgers buy since 2026-11-09). Exits come from opendrive.exits, to
15:30. Every trade carries the state of the evening before: the five lights of DROPS.md, the chip breadth
share, and plainer stand-ins (SMH, SPY and the name itself against their 20-day averages, 5-day returns,
SPY's realized volatility), to see whether chip breadth says anything the stand-ins do not.

The bar, written before the 0.35-delta prices were read: on that strike and the live exit, calls after a
lit evening must beat calls after an unlit one on win rate and on the average without the best two, over
the whole sample, in the last 3 months and for NVDA and TSLA separately, and shuffling the lit days must
reach the gap less than 5% of the time. A stand-in that splits the trades as well means the light is not
about chip breadth.

Two checks were added after the first read, because the option sample cannot test itself: how many
calendar quarters carry the result, and the same 10:00 signals on the stock alone back to 2020 (30-minute
bars, no option prices), four years the light was not found in.

    python -m zoh.research.opengate            # scan new days, price them, write OPENGATE.md
    python -m zoh.research.opengate --report   # rebuild the report from opengate.json
"""
import argparse
import csv
import json
import random
import statistics as st
import time
from datetime import date, datetime, timedelta, timezone

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import Y, at_or_after, daily_raw, implied_vol, occ, option_minutes, strike_grid
from ..strategy import ET, MARKET_OPEN, bs_delta, hhmm, opex_week, parse_bar, regular_session
from .drops import SINGLE, breadth_share, pct, study
from .opendrive import ENTRY, OTM, START, exits, expiry_today, macro_days

DIR = journal.ROOT / "journal" / "research"
DATA, OUT = DIR / "opengate.json", DIR / "OPENGATE.md"
SYMBOLS = ["SPY", "NVDA", "TSLA"]
SPY_MOVE, STOCK_MOVE = 0.005, 0.008
TARGET_DELTA = 0.35
REACH = {"SPY": 0.025}      # how far past the money the strike grid goes; stocks 6%
YEARS = (16 * 60 - (ENTRY.hour * 60 + ENTRY.minute)) / Y
LIVE_EXIT = {"stock": "hold", "spy_call": "take3", "spy_put": "trail"}   # what each ledger does with one contract
LIVE_DAYS = {"stock": (0, 2), "spy_call": (0, 1, 2, 3), "spy_put": (0, 1, 2, 3)}
SHUFFLES = 20000


def signal(sym, move):
    """The side a live ledger would buy at 10:00, or None."""
    if sym == "SPY":
        return ("call" if move > 0 else "put") if abs(move) >= SPY_MOVE else None
    return "call" if move >= STOCK_MOVE else None


def family(t):
    return "stock" if t["sym"] != "SPY" else f"spy_{t['kind']}"


def leg(sym_bars, bar, strike, delta=None, iv=None):
    entry = max(bar["c"] * 1.10, bar["c"] + 0.01)
    path = [(x["t"], x["c"]) for x in sym_bars if x["t"] > bar["t"]]
    out = {"strike": strike, "px": bar["c"], "exits": exits(path, entry, 0.10),
           "max_x": round(max([c for _, c in path] or [bar["c"]]) / bar["c"], 2)}
    if delta is not None:
        out.update(delta=round(delta, 3), iv=round(iv, 3))
    return out


def price(api, sym, day, spot, kind):
    """Both strikes for one signal: nearest 0.7% out of the money and nearest 0.35 delta at 10:00."""
    grid = {occ(sym, day, k, kind): k for k in strike_grid(spot, kind, REACH.get(sym, 0.06))}
    keys, opts = list(grid), {}
    for j in range(0, len(keys), 100):
        opts.update(option_minutes(api, keys[j:j + 100], day))
    quotes = {}
    for s, bars in opts.items():
        b = at_or_after(bars, ENTRY, 5)
        if b and b["c"] > 0:
            quotes[s] = b
    if not quotes:
        return None
    target = spot * (1 + OTM) if kind == "call" else spot * (1 - OTM)
    far = min(quotes, key=lambda s: abs(grid[s] - target))
    out = {"otm07": dict(leg(opts[far], quotes[far], grid[far]), contract=far)}
    greeks = {}
    for s, b in quotes.items():
        iv = implied_vol(b["c"], spot, grid[s], YEARS, kind)
        if iv:
            greeks[s] = (abs(bs_delta(spot, grid[s], YEARS, iv, kind)), iv)
    if greeks:
        near = min(greeks, key=lambda s: abs(greeks[s][0] - TARGET_DELTA))
        out["d35"] = dict(leg(opts[near], quotes[near], grid[near], *greeks[near]), contract=near)
    return out


def collect(api, saved):
    """Scan every same-day-expiry day after `saved['through']`, price the signals, return the new state."""
    events = macro_days()
    end = datetime.now(timezone.utc) - timedelta(minutes=20)
    through = date.fromisoformat(saved["through"]) if saved.get("through") else START - timedelta(days=1)
    rows, last = list(saved.get("rows", [])), through
    for sym in SYMBOLS:
        days = daily_raw(api, sym, START - timedelta(days=7), end)
        n = 0
        for i in range(1, len(days)):
            day, o, _ = days[i]
            if day < START or day <= through or not expiry_today(sym, day):
                continue
            last = max(last, day)
            start = datetime.combine(day, MARKET_OPEN, ET)
            try:
                stock = regular_session([parse_bar(b) for b in api.stock_bars(
                    sym, start, start + timedelta(minutes=32), feed="sip", adjustment="raw")])
            except AlpacaError:
                continue
            bar = at_or_after(stock, hhmm("09:59"), 2)
            if not stock or not bar:
                continue
            move = bar["c"] / stock[0]["o"] - 1
            kind = signal(sym, move)
            if not kind:
                continue
            try:
                legs = price(api, sym, day, bar["c"], kind)
            except AlpacaError:
                legs = None
            time.sleep(0.1)
            if not legs:
                continue
            rows.append(dict({"sym": sym, "day": day.isoformat(), "kind": kind, "spot": bar["c"],
                              "move10": round(move, 4), "gap": round(o / days[i - 1][2] - 1, 4),
                              "macro": ",".join(events.get(day.isoformat(), []))}, **legs))
            n += 1
        print(f"{sym}: {n} new signals", flush=True)
    rows.sort(key=lambda r: (r["day"], r["sym"]))
    return {"through": last.isoformat(), "rows": rows}


# ---- the evening before -------------------------------------------------------------------------

def below_average(c, i):
    xs = [x for x in c[i - 19:i + 1] if x]
    return bool(c[i] and len(xs) >= 10 and c[i] < st.mean(xs))


def above_long(c, i, n=100):
    xs = [x for x in c[max(0, i - n + 1):i + 1] if x]
    return bool(c[i] and len(xs) >= 0.8 * n and c[i] >= st.mean(xs))


CELLS = ["dip in an uptrend", "dip in a downtrend", "above its 20-day average"]


def cell_of(below20, above100):
    """Where the chip ETF stands: below its 20-day average with the 100-day average under it or over it,
    or not in a dip at all."""
    if not below20:
        return CELLS[2]
    return CELLS[0] if above100 else CELLS[1]


def evenings(data):
    """State at each close, keyed by the next session (the day a trade would be placed); the last close
    is keyed "next"."""
    days, spy, smh = data["days"], data["spy"], data["smh"]
    closes = {s: {d: c for d, _, c in data["bars"].get(s, [])} for s in ("NVDA", "TSLA")}
    names = {}
    for s, m in closes.items():
        last, col = None, []
        for d in days:
            last = m.get(d, last)
            col.append(last)
        names[s] = col
    rets = [None] + [spy[i] / spy[i - 1] - 1 if spy[i] and spy[i - 1] else None for i in range(1, len(days))]
    vol = [None] * len(days)
    for i in range(10, len(days)):
        xs = [r for r in rets[i - 9:i + 1] if r is not None]
        vol[i] = st.pstdev(xs) if len(xs) >= 8 else None
    out = {}
    for row in data["rows"]:
        i = row["i"]
        past = [v for v in vol[max(0, i - 250):i] if v is not None]
        state = dict({k: bool(row["lights"][k]) for k in SINGLE},
                     share=breadth_share(i, days, data["members"]),
                     smh_below=below_average(smh, i), spy_below=below_average(spy, i),
                     smh_down5=bool(smh[i] and smh[i - 5] and smh[i] < smh[i - 5]),
                     vol_high=bool(vol[i] is not None and len(past) >= 60 and vol[i] > st.median(past)),
                     evening=row["day"].isoformat())
        state["smh_up100"] = above_long(smh, i)
        state["cell"] = cell_of(state["smh_below"], state["smh_up100"])
        for s, col in names.items():
            state[f"{s}_below"] = below_average(col, i)
            state[f"{s}_down5"] = bool(col[i] and col[i - 5] and col[i] < col[i - 5])
        out[days[i + 1].isoformat() if i + 1 < len(days) else "next"] = state
    return out


GATES = [
    ("chip breadth >= 75% (the light)", lambda t, s: s["breadth"]),
    ("chip breadth >= 50%", lambda t, s: s["share"] is not None and s["share"] >= 0.5),
    ("chip breadth = 100%", lambda t, s: s["share"] is not None and s["share"] >= 0.999),
    ("SMH below its 20-day average", lambda t, s: s["smh_below"]),
    ("SMH above its 100-day average", lambda t, s: s["smh_up100"]),
    ("SMH below its 20-day and above its 100-day average", lambda t, s: s["cell"] == CELLS[0]),
    ("SPY below its 20-day average", lambda t, s: s["spy_below"]),
    ("the name below its own 20-day average", lambda t, s: s.get(f"{t['sym']}_below", s["spy_below"])),
    ("the name down over 5 sessions", lambda t, s: s.get(f"{t['sym']}_down5", s["smh_down5"])),
    ("SMH down over 5 sessions", lambda t, s: s["smh_down5"]),
    ("SPY 10-day volatility above its 1-year median", lambda t, s: s["vol_high"]),
    ("light: turning", lambda t, s: s["turning"]),
    ("light: rates", lambda t, s: s["rates"]),
    ("light: stretched", lambda t, s: s["stretched"]),
    ("light: diverge", lambda t, s: s["diverge"]),
]


# ---- numbers ------------------------------------------------------------------------------------

def stats(xs):
    """(n, win rate, average, average without the best, without the best two) of a list of results."""
    xs = sorted(xs)
    if not xs:
        return 0, None, None, None, None
    cut = lambda k: st.mean(xs[:-k]) if len(xs) > k else None
    return len(xs), sum(x > 0 for x in xs) / len(xs), st.mean(xs), cut(1), cut(2)


def cells(xs):
    n, win, avg, _, cut2 = stats(xs)
    return f"{n} | {pct(win)} | {pct(avg)} | {pct(cut2)}"


def shuffle_test(trades, lit, value, shuffles=SHUFFLES, seed=62):
    """Share of day-level shuffles of the lit label whose gap (lit minus unlit) is at least the real one,
    for the average and for the win rate. Both names of one day keep the same label."""
    days = sorted({t["day"] for t in trades})
    by_day = {d: [value(t) for t in trades if t["day"] == d] for d in days}
    labels = [bool(lit[d]) for d in days]

    def gaps(marks):
        a = [x for d, m in zip(days, marks) if m for x in by_day[d]]
        b = [x for d, m in zip(days, marks) if not m for x in by_day[d]]
        if not a or not b:
            return None
        return st.mean(a) - st.mean(b), sum(x > 0 for x in a) / len(a) - sum(x > 0 for x in b) / len(b)
    real = gaps(labels)
    if real is None:
        return None
    rng, hits = random.Random(seed), [0, 0]
    for _ in range(shuffles):
        rng.shuffle(labels)
        g = gaps(labels)
        hits[0] += g[0] >= real[0]
        hits[1] += g[1] >= real[1]
    return real[0], hits[0] / shuffles, real[1], hits[1] / shuffles


def live_rule(trades, fam):
    """The subset the ledger itself would have traded: its weekdays, no macro day, no monthly-expiry week,
    and for the stocks one name a day, the stronger at 10:00."""
    keep = [t for t in trades if family(t) == fam and not t["macro"]
            and date.fromisoformat(t["day"]).weekday() in LIVE_DAYS[fam]
            and not opex_week(date.fromisoformat(t["day"]))]
    if fam != "stock":
        return keep
    best = {}
    for t in keep:
        if t["day"] not in best or t["move10"] > best[t["day"]]["move10"]:
            best[t["day"]] = t
    return sorted(best.values(), key=lambda t: t["day"])


def periods(end):
    return [("since 2024-02", lambda d: True),
            ("last 3 months", lambda d: d > end - timedelta(days=92)),
            ("last year", lambda d: d > end - timedelta(days=365)),
            ("before the last year", lambda d: d <= end - timedelta(days=365))]


def gate_table(trades, state, value, gates=GATES):
    out = ["| state of the evening before | lit: trades | win% | avg | w/o best 2 | not lit: trades | win% | avg | "
           "w/o best 2 |", "|---|---|---|---|---|---|---|---|---|"]
    for label, test in gates:
        lit = [value(t) for t in trades if test(t, state[t["day"]])]
        off = [value(t) for t in trades if not test(t, state[t["day"]])]
        out.append(f"| {label} | {cells(lit)} | {cells(off)} |")
    return out + [""]


def slice_table(trades, state, value, slices):
    out = ["| slice | lit: trades | win% | avg | w/o best 2 | not lit: trades | win% | avg | w/o best 2 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for label, keep in slices:
        ts = [t for t in trades if keep(t)]
        out.append(f"| {label} | {cells([value(t) for t in ts if state[t['day']]['breadth']])} | "
                   f"{cells([value(t) for t in ts if not state[t['day']]['breadth']])} |")
    return out + [""]


def plain_table(groups, value_of):
    out = ["| group | exit | trades | win% | avg | w/o best | w/o best 2 |", "|---|---|---|---|---|---|---|"]
    for label, ts in groups:
        for key in ("hold", "take3", "trail", "half3_trail"):
            n, win, avg, cut1, cut2 = stats([value_of(t, key) for t in ts])
            out.append(f"| {label} | {key} | {n} | {pct(win)} | {pct(avg)} | {pct(cut1)} | {pct(cut2)} |")
    return out + [""]


def journal_trades(state):
    """The ledgers' own trades so far, with the state of the evening before."""
    path = journal.ROOT / "journal" / "trades.csv"
    out = ["| day | ledger | mode | contract | result | chip breadth the evening before | SMH against its 20-day average |",
           "|---|---|---|---|---|---|---|"]
    if not path.exists():
        return out + [""]
    with path.open() as f:
        for r in csv.DictReader(f):
            if r["variant"] in ("stock_open_drive", "spy_open_drive", "spy_open_drive_put") and r["date"] in state:
                s = state[r["date"]]
                out.append(f"| {r['date']} | {r['variant']} | {r['mode']} | {r['contract']} | "
                           f"{pct(float(r['pnl_pct']))} | {pct(s['share'])}{' (lit)' if s['breadth'] else ''} | "
                           f"{'below' if s['smh_below'] else 'above'} |")
    return out + [""]


# ---- the underlying alone, back to 2020 -----------------------------------------------------------

def half_hours(api, sym, start, end):
    """(day, open to 10:00, 10:00 to 15:30) for every session, from 30-minute bars."""
    out = []
    for year in range(start.year, end.year + 1):
        a = max(datetime(year, 1, 1, tzinfo=timezone.utc), datetime.combine(start, MARKET_OPEN, ET))
        b = min(datetime(year + 1, 1, 1, tzinfo=timezone.utc), end)
        by = {}
        for x in api.stock_bars(sym, a, b, timeframe="30Min", feed="sip", adjustment="raw"):
            bar = parse_bar(x)
            by.setdefault(bar["t"].date(), {})[bar["t"].strftime("%H:%M")] = bar
        for day, m in sorted(by.items()):
            if "09:30" in m and "15:00" in m and m["09:30"]["o"] and m["09:30"]["c"]:
                out.append((day, m["09:30"]["c"] / m["09:30"]["o"] - 1, m["15:00"]["c"] / m["09:30"]["c"] - 1))
    return out


def underlying(api, start=date(2020, 1, 1)):
    """The same 10:00 signals on every session since 2020, option data or not: what the stock did from
    10:00 to 15:30, signed the way of the trade. Four years the option sample never saw."""
    end = datetime.now(timezone.utc) - timedelta(minutes=20)
    rows = []
    for sym in SYMBOLS:
        for day, move, rest in half_hours(api, sym, start, end):
            kind = signal(sym, move)
            if kind:
                rows.append({"sym": sym, "day": day.isoformat(), "kind": kind, "move10": round(move, 4),
                             "rest": round(rest if kind == "call" else -rest, 4)})
    return sorted(rows, key=lambda r: (r["day"], r["sym"]))


def drift(xs):
    """signals | average continuation | share continuing | share +1% or more | share -1% or worse"""
    if not xs:
        return "0 | - | - | - | -"
    rs = [x["rest"] for x in xs]
    share = lambda test: pct(sum(test(r) for r in rs) / len(rs))
    return (f"{len(rs)} | {st.mean(rs) * 100:+.2f}% | {share(lambda r: r > 0)} | {share(lambda r: r >= 0.01)} | "
            f"{share(lambda r: r <= -0.01)}")


SPLITS = [("SMH below its 20-day average", lambda s: s["smh_below"]),
          ("SMH above its 20-day average", lambda s: not s["smh_below"]),
          ("chip breadth lit", lambda s: s["breadth"]), ("chip breadth not lit", lambda s: not s["breadth"]),
          ("dip in an uptrend", lambda s: s["cell"] == CELLS[0]), ("dip in a downtrend", lambda s: s["cell"] == CELLS[1])]


def drift_table(signals, state, fam):
    cut = START.isoformat()
    last_month = (START - timedelta(days=1)).strftime("%Y-%m")
    ts = [x for x in signals if family(x) == fam and x["day"] in state]
    out = ["| period | state of the evening before | signals | avg 10:00 to 15:30 | continued | +1% or more | "
           "-1% or worse |", "|---|---|---|---|---|---|---|"]
    for label, keep in ((f"2020-01 to {last_month} (before the option data)", lambda d: d < cut),
                        (f"{cut[:7]} on (the option sample's years)", lambda d: d >= cut)):
        part = [x for x in ts if keep(x["day"])]
        out.append(f"| {label} | all | {drift(part)} |")
        for name, test in SPLITS:
            out.append(f"| {label} | {name} | {drift([x for x in part if test(state[x['day']])])} |")
    return out + [""]


def year_table(signals, state):
    ts = [x for x in signals if family(x) == "stock" and x["day"] in state]
    out = ["| year | SMH below: signals | avg | +1% or more | SMH above: signals | avg | +1% or more | breadth lit: "
           "signals | avg | +1% or more | not lit: signals | avg | +1% or more |", "|---|" + "---|" * 12]
    short = lambda xs: " | ".join(drift(xs).split(" | ")[i] for i in (0, 1, 3))
    for y in sorted({x["day"][:4] for x in ts}):
        part = [x for x in ts if x["day"][:4] == y]
        out.append(f"| {y} | {short([x for x in part if state[x['day']]['smh_below']])} | "
                   f"{short([x for x in part if not state[x['day']]['smh_below']])} | "
                   f"{short([x for x in part if state[x['day']]['breadth']])} | "
                   f"{short([x for x in part if not state[x['day']]['breadth']])} |")
    return out + [""]


def quarter_table(trades, state, value):
    out = ["| quarter | trades | win% | avg | after a lit evening: trades | wins | after SMH below its 20-day average: "
           "trades | wins |", "|---|---|---|---|---|---|---|---|"]
    for q in sorted({quarter_of(t) for t in trades}):
        ts = [t for t in trades if quarter_of(t) == q]
        n, win, avg, _, _ = stats([value(t) for t in ts])
        lit = [t for t in ts if state[t["day"]]["breadth"]]
        dip = [t for t in ts if state[t["day"]]["smh_below"]]
        out.append(f"| {q} | {n} | {pct(win)} | {pct(avg)} | {len(lit)} | {sum(value(t) > 0 for t in lit)} | "
                   f"{len(dip)} | {sum(value(t) > 0 for t in dip)} |")
    return out + [""]


def quarter_of(t):
    return f"{t['day'][:4]} Q{(int(t['day'][5:7]) - 1) // 3 + 1}"


def best_quarters(trades, value, k=2):
    """The k calendar quarters with the largest summed result, and how many quarters averaged above zero."""
    total = {}
    for t in trades:
        total[quarter_of(t)] = total.get(quarter_of(t), 0) + value(t)
    best = sorted(total, key=total.get, reverse=True)[:k]
    return sorted(best), sum(v > 0 for v in total.values()), len(total)


def report(saved, data):
    state = evenings(data)
    rows = [r for r in saved["rows"] if r["day"] in state]
    signals = saved.get("underlying", [])
    end = date.fromisoformat(saved["through"])
    day_of = lambda t: date.fromisoformat(t["day"])
    clean = [r for r in rows if not r["macro"]]
    stock = [r for r in clean if family(r) == "stock" and "d35" in r]
    calls = [r for r in clean if family(r) == "spy_call" and "d35" in r]
    puts = [r for r in clean if family(r) == "spy_put" and "d35" in r]
    val = lambda strike, key: (lambda t: t[strike]["exits"][key])
    hold35 = val("d35", "hold")
    lit_day = {d: s["breadth"] for d, s in state.items()}
    dip_day = {d: s["smh_below"] for d, s in state.items()}
    tonight = state.get("next", {})
    lit_groups = lambda ts: [("lit", [t for t in ts if lit_day[t["day"]]]), ("not lit", [t for t in ts if not lit_day[t["day"]]])]
    dip_groups = lambda ts: [("SMH below its 20-day average", [t for t in ts if dip_day[t["day"]]]),
                             ("SMH above it", [t for t in ts if not dip_day[t["day"]]])]
    d35 = lambda t, key: t["d35"]["exits"][key]
    out = ["# Chip breadth as a gate for the open-drive calls, and the put hand (SUNDAY_TESTS 62)", "",
           f"Signals of the live ledgers at 10:00 ET, real 1-minute option closes, 10% costs each way, {START} to "
           f"{end}: {len(rows)} signals priced ({len(rows) - len(clean)} on macro days, left out below). `d35` is the "
           "contract nearest 0.35 delta at 10:00 (what the ledgers buy since 2026-11-09); `otm07` is the strike about "
           "0.7% out of the money of OPENDRIVE.md. Exits to 15:30: hold, take3 (all out at 3x), trail (arms at 2x, out "
           "at 60% of the peak, never below the entry), half3_trail. `lit` = at least 75% of twelve chip names closed "
           "below their own 20-day average the evening before (DROPS.md). Rebuild: `python -m zoh.research.opengate`.", "",
           "How to read it: sections 1 to 3 are the sample the light was found in, re-priced at the strike the ledgers "
           "buy; they can only show whether the split survives a strike change, not whether it is real. Sections 4 and "
           "5 are the checks that could break it: how few stretches of the calendar carry the result, and the same "
           "10:00 signals on the stock alone in 2020 to 2023, years the option data does not reach.", "",
           f"State at the last close ({tonight.get('evening', '-')}): chip breadth {pct(tonight.get('share'))}"
           f"{' (lit)' if tonight.get('breadth') else ' (not lit)'}, SMH "
           f"{'below' if tonight.get('smh_below') else 'above'} its 20-day average and "
           f"{'above' if tonight.get('smh_up100') else 'below'} its 100-day average.", "",
           "## 1. NVDA / TSLA calls at +0.8% or more", ""]
    if stock:
        out += [f"{len(stock)} trades. Median entry {st.median(t['d35']['px'] for t in stock):.2f} at delta "
                f"{st.median(t['d35']['delta'] for t in stock):.2f}, "
                f"{pct(st.median(t['d35']['strike'] / t['spot'] - 1 for t in stock), 1)} out of the money (d35); "
                f"{st.median(t['otm07']['px'] for t in stock):.2f} for otm07.", ""]
    for strike in ("d35", "otm07"):
        out += [f"Strike {strike}, lit against not lit, by exit:", ""]
        out += plain_table(lit_groups(stock), lambda t, key, s=strike: t[s]["exits"][key])
    out += ["Strike d35, exit hold (what the ledger does with its one contract), by slice:", ""]
    slices = [(label, (lambda t, k=keep: k(day_of(t)))) for label, keep in periods(end)]
    slices += [(str(y), (lambda t, y=y: day_of(t).year == y)) for y in sorted({day_of(t).year for t in stock})]
    slices += [("NVDA", lambda t: t["sym"] == "NVDA"), ("TSLA", lambda t: t["sym"] == "TSLA"),
               ("Fridays", lambda t: day_of(t).weekday() == 4),
               ("Mondays and Wednesdays", lambda t: day_of(t).weekday() in (0, 2)),
               ("new days (after 2026-10-15, not in DROPS.md)", lambda t: day_of(t) > date(2026, 10, 15))]
    out += slice_table(stock, state, hold35, slices)
    live = [t for t in live_rule(rows, "stock") if "d35" in t]
    out += ["The ledger's own rule (Mondays and Wednesdays, the stronger of the two, no macro day, no monthly-expiry "
            "week), strike d35:", ""]
    out += plain_table(lit_groups(live) + dip_groups(live), d35)
    test, test_dip = shuffle_test(stock, lit_day, hold35), shuffle_test(stock, dip_day, hold35)
    if test and test_dip:
        out += [f"Shuffle test (lit days reassigned at random, {SHUFFLES:,} times, d35 hold): the real gap in the "
                f"average is {test[0] * 100:.0f} points and {pct(test[1], 1)} of shuffles reach it; the gap in the win "
                f"rate is {test[2] * 100:.0f} points and {pct(test[3], 1)} of shuffles reach it. The cell was found "
                "among 48 (6 lights x 2 sides x 4 exits) on the otm07 strike, so read a single 5% as 1 in 20, not as "
                f"proof. The same test for `SMH below its 20-day average`, picked from the {len(GATES)} states of "
                f"section 2 after reading them: {test_dip[0] * 100:.0f} points, {pct(test_dip[1], 1)}; "
                f"{test_dip[2] * 100:.0f} points, {pct(test_dip[3], 1)}.", ""]
    out += ["## 2. Is it about chip breadth? The same trades split by plainer states (d35, hold)", ""]
    out += gate_table(stock, state, hold35)
    out += ["Breadth light against the plain state, the four combinations:", "",
            "| chip breadth | SMH against its 20-day average | trades | win% | avg | w/o best 2 |", "|---|---|---|---|---|---|"]
    for lit in (True, False):
        for dip in (True, False):
            xs = [hold35(t) for t in stock if lit_day[t["day"]] == lit and dip_day[t["day"]] == dip]
            out.append(f"| {'lit' if lit else 'not lit'} | {'below' if dip else 'above'} | {cells(xs)} |")
    out += ["", "## 3. By chip breadth share (d35, hold)", "", "| chips below their 20-day average | trades | win% | avg | "
            "w/o best 2 |", "|---|---|---|---|---|"]
    for label, lo, hi in (("under 25%", 0, 0.25), ("25% to 49%", 0.25, 0.5), ("50% to 74%", 0.5, 0.75),
                          ("75% to 99%", 0.75, 0.999), ("all twelve", 0.999, 2)):
        xs = [hold35(t) for t in stock if state[t["day"]]["share"] is not None and lo <= state[t["day"]]["share"] < hi]
        out.append(f"| {label} | {cells(xs)} |")
    out += ["", "## 4. How many stretches of the calendar carry it (NVDA / TSLA calls, d35, hold)", ""]
    out += quarter_table(stock, state, hold35)
    best, up, n_q = best_quarters(stock, hold35)
    keep = [t for t in stock if quarter_of(t) not in best]
    rest = stats([hold35(t) for t in keep])
    out += [f"{up} of {n_q} quarters averaged above zero. Without the best two ({' and '.join(best)}): {rest[0]} trades, "
            f"{pct(rest[1])} win, {pct(rest[2])} average, {pct(rest[4])} without the best two. Lit against not lit in "
            f"what is left: {cells([hold35(t) for t in keep if lit_day[t['day']]])} against "
            f"{cells([hold35(t) for t in keep if not lit_day[t['day']]])} (trades | win% | avg | w/o best 2); SMH below "
            f"its 20-day average against above: {cells([hold35(t) for t in keep if dip_day[t['day']]])} against "
            f"{cells([hold35(t) for t in keep if not dip_day[t['day']]])}.", ""]
    out += ["The three places the chip ETF can stand, same trades (a split found after reading section 2, kept here "
            "because section 5 breaks it):", "", "| SMH the evening before | trades | win% | avg | w/o best 2 |",
            "|---|---|---|---|---|"]
    for c in CELLS:
        out.append(f"| {c} | {cells([hold35(t) for t in stock if state[t['day']]['cell'] == c])} |")
    out += ["", "## 5. The same signals on the stock alone, back to 2020", "",
            "Every session, expiry day or not: the stock at least 0.8% above its open at 10:00 (SPY 0.5% either way), and "
            "what it did from 10:00 to 15:30, signed the way of the trade. No option prices, so no costs and no fat "
            "tails; the question is only whether the evening state moves the odds of the follow-through a 0.35-delta "
            "call needs."]
    by = {(x["sym"], x["day"]): x["rest"] for x in signals}
    pairs = [(by[(t["sym"], t["day"])], hold35(t)) for t in stock if (t["sym"], t["day"]) in by]
    if len(pairs) > 2:
        big = [o for r, o in pairs if r >= 0.01]
        small = [o for r, o in pairs if r < 0.01]
        out += [f"Against the real option results where both exist ({len(pairs)} trades): correlation "
                f"{st.correlation([r for r, _ in pairs], [o for _, o in pairs]):.2f}; the call made money on "
                f"{sum(o > 0 for o in big)} of {len(big)} days when the stock added 1% or more after 10:00 and on "
                f"{sum(o > 0 for o in small)} of {len(small)} other days."]
    out += ["", "NVDA / TSLA at +0.8% or more:", ""] + drift_table(signals, state, "stock")
    out += ["By year (signals, average 10:00 to 15:30, share adding 1% or more):", ""] + year_table(signals, state)
    out += ["SPY at +0.5% or more:", ""] + drift_table(signals, state, "spy_call")
    out += ["SPY at -0.5% or less, signed for a put (`continued` = fell further, `-1% or worse` = bounced 1% or more):",
            ""] + drift_table(signals, state, "spy_put")
    out += ["## 6. SPY calls at +0.5% or more", "",
            f"{len(calls)} trades; the ledger takes 3x on its one contract (take3).", ""]
    out += plain_table(lit_groups(calls) + dip_groups(calls), d35)
    out += ["## 7. SPY puts at -0.5% or less (the put hand)", "",
            f"{len(puts)} trades; the ledger trails (arms at 2x, 40% giveback).", ""]
    out += plain_table([(f"d35, {label}", [t for t in puts if keep(day_of(t))]) for label, keep in periods(end)], d35)
    out += ["Strike otm07 for comparison:", ""]
    out += plain_table([(label, [t for t in puts if keep(day_of(t))]) for label, keep in periods(end)[:3]],
                       lambda t, key: t["otm07"]["exits"][key])
    live_puts = [t for t in live_rule(rows, "spy_put") if "d35" in t]
    out += ["The ledger's own days (Monday to Thursday, no macro day, no monthly-expiry week), strike d35:", ""]
    out += plain_table([(label, [t for t in live_puts if keep(day_of(t))]) for label, keep in periods(end)[:3]], d35)
    out += ["Trade by trade on the ledger's own days (d35; entry, result under trail, result held to 15:30):", "",
            "| day | entry | trail | hold | SMH against its 20-day average |", "|---|---|---|---|---|"]
    for t in live_puts:
        out.append(f"| {t['day']} | {t['d35']['px']:.2f} | {pct(d35(t, 'trail'))} | {pct(d35(t, 'hold'))} | "
                   f"{'below' if dip_day[t['day']] else 'above'} |")
    out += ["", "Does any evening state make the puts pay? (d35, trail)", ""]
    out += gate_table(puts, state, val("d35", "trail"))
    out += ["## 8. The ledgers' own trades so far", ""]
    out += journal_trades(state)
    return "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", action="store_true", help="rebuild OPENGATE.md from opengate.json, no option data")
    a = p.parse_args()
    api = Alpaca()
    saved = json.loads(DATA.read_text()) if DATA.exists() else {}
    if not a.report:
        saved = dict(collect(api, saved), underlying=underlying(api))
        DIR.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(saved, indent=1) + "\n")
    text = report(saved, study(api, date(2019, 9, 1)))
    OUT.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
