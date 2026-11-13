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
about chips.

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
    """The ledgers' own trades so far, with the light of the evening before."""
    path = journal.ROOT / "journal" / "trades.csv"
    out = ["| day | ledger | mode | contract | result | chip breadth the evening before |", "|---|---|---|---|---|---|"]
    if not path.exists():
        return out + [""]
    with path.open() as f:
        for r in csv.DictReader(f):
            if r["variant"] in ("stock_open_drive", "spy_open_drive", "spy_open_drive_put") and r["date"] in state:
                s = state[r["date"]]
                out.append(f"| {r['date']} | {r['variant']} | {r['mode']} | {r['contract']} | "
                           f"{pct(float(r['pnl_pct']))} | {pct(s['share'])}{' (lit)' if s['breadth'] else ''} |")
    return out + [""]


def report(saved, data):
    state = evenings(data)
    rows = [r for r in saved["rows"] if r["day"] in state]
    end = date.fromisoformat(saved["through"])
    day_of = lambda t: date.fromisoformat(t["day"])
    clean = [r for r in rows if not r["macro"]]
    stock = [r for r in clean if family(r) == "stock" and "d35" in r]
    calls = [r for r in clean if family(r) == "spy_call" and "d35" in r]
    puts = [r for r in clean if family(r) == "spy_put" and "d35" in r]
    val = lambda strike, key: (lambda t: t[strike]["exits"][key])
    hold35 = val("d35", "hold")
    lit_day = {d: s["breadth"] for d, s in state.items()}
    tonight = state.get("next", {})
    out = ["# Chip breadth as a gate for the open-drive calls, and the put hand (SUNDAY_TESTS 62)", "",
           f"Signals of the live ledgers at 10:00 ET, real 1-minute option closes, 10% costs each way, {START} to "
           f"{end}: {len(rows)} signals priced ({len(rows) - len(clean)} on macro days, left out below). `d35` is the "
           "contract nearest 0.35 delta at 10:00 (what the ledgers buy since 2026-11-09); `otm07` is the strike about "
           "0.7% out of the money of OPENDRIVE.md. Exits to 15:30: hold, take3 (all out at 3x), trail (arms at 2x, out "
           "at 60% of the peak, never below the entry), half3_trail. `lit` = at least 75% of twelve chip names closed "
           "below their own 20-day average the evening before (DROPS.md). Rebuild: `python -m zoh.research.opengate`.", "",
           f"State at the last close ({tonight.get('evening', '-')}): chip breadth {pct(tonight.get('share'))}"
           f"{' (lit)' if tonight.get('breadth') else ' (not lit)'}.", "",
           "## 1. NVDA / TSLA calls at +0.8% or more", "",
           f"{len(stock)} trades. Median entry {st.median(t['d35']['px'] for t in stock):.2f} at delta "
           f"{st.median(t['d35']['delta'] for t in stock):.2f}, "
           f"{pct(st.median(t['d35']['strike'] / t['spot'] - 1 for t in stock), 1)} out of the money (d35); "
           f"{st.median(t['otm07']['px'] for t in stock):.2f} for otm07." if stock else "No trades.", ""]
    for strike in ("d35", "otm07"):
        out += [f"Strike {strike}, lit against not lit, by exit:", ""]
        out += plain_table([("lit", [t for t in stock if lit_day[t["day"]]]),
                            ("not lit", [t for t in stock if not lit_day[t["day"]]])],
                           lambda t, key, s=strike: t[s]["exits"][key])
    out += ["Strike d35, exit hold (what the ledger does with its one contract), by slice:", ""]
    slices = [(label, (lambda t, k=keep: k(day_of(t)))) for label, keep in periods(end)]
    slices += [(str(y), (lambda t, y=y: day_of(t).year == y)) for y in sorted({day_of(t).year for t in stock})]
    slices += [("NVDA", lambda t: t["sym"] == "NVDA"), ("TSLA", lambda t: t["sym"] == "TSLA"),
               ("Fridays", lambda t: day_of(t).weekday() == 4),
               ("Mondays and Wednesdays", lambda t: day_of(t).weekday() in (0, 2)),
               ("new days (after 2026-10-15, not in DROPS.md)", lambda t: day_of(t) > date(2026, 10, 15))]
    out += slice_table(stock, state, hold35, slices)
    live = live_rule(rows, "stock")
    live = [t for t in live if "d35" in t]
    out += ["The ledger's own rule (Mondays and Wednesdays, the stronger of the two, no macro day, no monthly-expiry "
            "week), strike d35:", ""]
    out += plain_table([("lit", [t for t in live if lit_day[t["day"]]]),
                        ("not lit", [t for t in live if not lit_day[t["day"]]])],
                       lambda t, key: t["d35"]["exits"][key])
    test = shuffle_test(stock, lit_day, hold35)
    if test:
        out += [f"Shuffle test (lit days reassigned at random, {SHUFFLES:,} times, d35 hold): the real gap in the "
                f"average is {pct(test[0])} and {pct(test[1], 1)} of shuffles reach it; the gap in the win rate is "
                f"{test[2] * 100:.0f} points and {pct(test[3], 1)} of shuffles reach it. The cell was found among 48 "
                "(6 lights x 2 sides x 4 exits) on the otm07 strike, so read a single 5% as 1 in 20, not as proof.", ""]
    out += ["### Is it about chips? The same trades split by plainer states (d35, hold)", ""]
    out += gate_table(stock, state, hold35)
    out += ["### By chip breadth share (d35, hold)", "", "| chips below their 20-day average | trades | win% | avg | "
            "w/o best 2 |", "|---|---|---|---|---|"]
    for label, lo, hi in (("under 25%", 0, 0.25), ("25% to 49%", 0.25, 0.5), ("50% to 74%", 0.5, 0.75),
                          ("75% to 99%", 0.75, 0.999), ("all twelve", 0.999, 2)):
        xs = [hold35(t) for t in stock if state[t["day"]]["share"] is not None and lo <= state[t["day"]]["share"] < hi]
        out.append(f"| {label} | {cells(xs)} |")
    out += ["", "## 2. SPY calls at +0.5% or more", "",
            f"{len(calls)} trades; the ledger takes 3x on its one contract (take3).", ""]
    out += plain_table([("lit", [t for t in calls if lit_day[t["day"]]]),
                        ("not lit", [t for t in calls if not lit_day[t["day"]]])],
                       lambda t, key: t["d35"]["exits"][key])
    out += ["## 3. SPY puts at -0.5% or less (the put hand)", "",
            f"{len(puts)} trades; the ledger trails (arms at 2x, 40% giveback).", ""]
    groups = [(f"{strike}, {label}", [t for t in puts if keep(day_of(t))])
              for strike in ("d35",) for label, keep in periods(end)]
    out += plain_table(groups, lambda t, key: t["d35"]["exits"][key])
    out += ["Strike otm07 for comparison:", ""]
    out += plain_table([(label, [t for t in puts if keep(day_of(t))]) for label, keep in periods(end)[:3]],
                       lambda t, key: t["otm07"]["exits"][key])
    live_puts = [t for t in live_rule(rows, "spy_put") if "d35" in t]
    out += ["The ledger's own days (Monday to Thursday, no macro day, no monthly-expiry week), strike d35:", ""]
    out += plain_table([(label, [t for t in live_puts if keep(day_of(t))]) for label, keep in periods(end)[:3]],
                       lambda t, key: t["d35"]["exits"][key])
    out += ["Does any evening state make the puts pay? (d35, trail)", ""]
    out += gate_table(puts, state, val("d35", "trail"))
    out += ["## 4. The ledgers' own trades so far", ""]
    out += journal_trades(state)
    return "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--report", action="store_true", help="rebuild OPENGATE.md from opengate.json, no option data")
    a = p.parse_args()
    api = Alpaca()
    saved = json.loads(DATA.read_text()) if DATA.exists() else {}
    if not a.report:
        saved = collect(api, saved)
        DIR.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(saved, indent=1) + "\n")
    text = report(saved, study(api, START - timedelta(days=20)))
    OUT.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
