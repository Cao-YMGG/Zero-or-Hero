"""The weekly review of 2026-11-15 (week 46): where the week's losses came from.

SPY +2.6% on the week, three real trades lost $285 and 5 of 26 shadows won. Nine tables, each a
SUNDAY_TESTS item (57, 59, 60, 63, 64, 66, 67, 68 and the hero pairs):

    python -m zoh.research.week46              # collect (Alpaca) and write WEEK46.md / week46.json
    python -m zoh.research.week46 --upgrades   # also re-run the two-year rating-change replay (slow)
    python -m zoh.research.week46 --report     # rebuild WEEK46.md from week46.json

Option numbers are real option minute bars with 10% costs each way; every average is followed by
the average without the best trade and without the best two.
"""
import argparse
import csv
import glob
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import ET, hhmm
from ..runup import daily
from . import exits, opengate, opportunities, snipers, themes

DIR = journal.ROOT / "journal" / "research"
OUT, DATA, UPGRADES = DIR / "WEEK46.md", DIR / "week46.json", DIR / "week46_upgrades.json"
RECENT = "2026-08-13"          # the last three months lead
WEEK = ("2026-11-09", "2026-11-13")

# Class of every pre-market sniper before the bias file carried `sniper.class` (read from its catalyst):
# upgrade = a rating change, target = a target raise with the rating kept, news = the company's own news.
CLASSES = {"2026-10-06": "target", "2026-10-07": "upgrade", "2026-10-08": "upgrade", "2026-10-09": "news",
           "2026-10-12": "upgrade", "2026-10-13": "target", "2026-10-14": "target", "2026-10-15": "none",
           "2026-10-16": "news", "2026-10-19": "target", "2026-10-20": "news", "2026-10-21": "news",
           "2026-10-22": "target", "2026-10-26": "upgrade", "2026-10-27": "news", "2026-10-29": "news",
           "2026-10-30": "upgrade", "2026-11-05": "news", "2026-11-06": "news", "2026-11-09": "target",
           "2026-11-10": "news", "2026-11-11": "upgrade", "2026-11-12": "upgrade", "2026-11-13": "news"}
RATING = ("upgrade", "target")

# The hand-written rotation map names themes in free text; the first words of each line are matched here.
MAP = {"gpu": ["NVDA"], "cpu": ["AMD", "INTC", "ARM"], "memory": ["MU", "SNDK"], "disk": ["WDC", "STX"],
       "storage": ["WDC", "STX"], "optical": ["LITE", "CIEN"], "power": ["GEV", "VST"],
       "internet": ["META", "GOOGL", "MSFT", "AMZN", "AAPL"], "banks": ["JPM", "GS", "BAC"],
       "health": ["UNH", "LLY"], "energy": ["XOM", "CVX"], "consumer": ["WMT", "COST", "HD"],
       "industrials": ["CAT", "GE"], "custom": ["AVGO", "MRVL", "TSM"], "foundry": ["AVGO", "MRVL", "TSM"],
       "software": ["ORCL", "CRM", "NOW", "ADBE", "PLTR"], "chips": ["NVDA", "AMD", "AVGO", "MU", "INTC", "TSM"],
       "semis": ["NVDA", "AMD", "AVGO", "MU", "INTC", "TSM"], "staples": ["WMT", "COST"],
       "defensive": ["WMT", "COST", "UNH", "LLY"]}


def trio(xs):
    """(n, win share, avg, avg without the best, avg without the best two); None where nothing is left."""
    xs = sorted(xs)
    mean = lambda v: sum(v) / len(v) if v else None
    return (len(xs), (sum(x > 0 for x in xs) / len(xs)) if xs else None, mean(xs), mean(xs[:-1]), mean(xs[:-2]))


def cell(xs, digits=0):
    n, win, a, b, c = trio(xs)
    f = lambda v: "-" if v is None else f"{v * 100:+.{digits}f}%"
    return f"{n} | {'-' if win is None else f'{win:.0%}'} | {f(a)} / {f(b)} / {f(c)}"


def sign(kind):
    return 1 if kind == "call" else -1


# --- 60: exits of the open-drive ledgers on 0.35-delta contracts ---------------------------------

def open_drive_exits(rows):
    out = {}
    for fam in ("stock", "spy_call", "spy_put"):
        live = opengate.live_rule(rows, fam)
        for label, rs in (("all", live), ("last 3 months", [t for t in live if t["day"] >= RECENT])):
            out[f"{fam} | {label}"] = {
                "n": len(rs), "x2": sum(t["d35"]["max_x"] >= 2 for t in rs), "x3": sum(t["d35"]["max_x"] >= 3 for t in rs),
                "exits": {ex: [t["d35"]["exits"][ex] for t in rs] for ex in ("hold", "take3", "trail", "half3_trail")}}
    return out


# --- heroes: full stake held to expiry against the small leg with a trail ------------------------

def hero_pairs(root=journal.ROOT):
    with open(root / "journal" / "trades.csv") as f:
        trades = list(csv.DictReader(f))
    with open(root / "journal" / "exits.csv") as f:
        peaks = {(r["date"], r["variant"], r["contract"]): float(r["peak"] or 0) for r in csv.DictReader(f)}
    out = []
    for r in trades:
        if not r["variant"].endswith("_hero"):
            continue
        base = r["variant"][:-len("_hero")]
        entry, qty = float(r["entry_price"]), int(float(r["qty"]))
        peak = peaks.get((r["date"], r["variant"], r["contract"]), entry)
        twin = [t for t in trades if t["variant"] == base and t["mode"] == "shadow"
                and t["entry_time"][:10] == r["entry_time"][:10]]
        # a trail armed at 1.5x that gives back 40% of the peak, never below the entry: what the bot's
        # check_exit would have booked had the hero carried the small leg's rule (from the peak alone)
        mult = peak / entry if entry else 0
        trail = max(1.0, 0.6 * mult) - 1 if mult >= 1.5 else float(r["pnl_pct"])
        out.append({"day": r["entry_time"][:10], "variant": r["variant"], "contract": r["contract"], "entry": entry,
                    "qty": qty, "stake": round(entry * qty * 100), "peak_x": round(mult, 2),
                    "pnl_pct": float(r["pnl_pct"]), "pnl": float(r["pnl"]), "trail_pct": round(trail, 3),
                    "twin_pct": float(twin[0]["pnl_pct"]) if twin else None,
                    "twin_same": bool(twin and twin[0]["contract"] == r["contract"])})
    return out


# --- 66: the SPY call ----------------------------------------------------------------------------

def bias_calibration(api, root=journal.ROOT):
    files = sorted(glob.glob(str(root / "journal" / "bias" / "2026-*.json")))
    first = date.fromisoformat(json.loads(Path(files[0]).read_text())["date"])
    spy = daily(api, ["SPY"], first - timedelta(days=7), date.today())["SPY"]
    oc = {d.isoformat(): c / o - 1 for d, o, c in spy}
    cc = {b[0].isoformat(): b[2] / a[2] - 1 for a, b in zip(spy, spy[1:])}
    rows = []
    for f in files:
        b = json.loads(Path(f).read_text())
        if b["date"] in oc:
            rows.append({"date": b["date"], "bias": b["bias"], "p_up": b.get("p_up"), "oc": oc[b["date"]],
                         "cc": cc.get(b["date"])})
    return rows


# --- 67: the opportunity log, split -------------------------------------------------------------

def opportunity_splits(api):
    ideas = opportunities.ideas(opportunities.load_rows())
    days = sorted({r["date"] for r in ideas})
    spy = daily(api, ["SPY"], date.fromisoformat(days[0]) - timedelta(days=3), date.fromisoformat(days[-1]))["SPY"]
    up = {d.isoformat(): c > o for d, o, c in spy}

    def ext(r):
        try:
            return (float(r["entry"]) / float(r["open"]) - 1) * 100 * sign(r["direction"])
        except (ValueError, ZeroDivisionError):
            return None

    def tally(rs):
        g = Counter(r["grade"] for r in rs)
        vs = [float(r["vs_spy_pct"]) for r in rs if r.get("vs_spy_pct") not in ("", None)]
        return {"n": len(rs), "paid": g["paid"], "right": g["right"], "wrong": g["wrong"],
                "vs_spy": round(statistics.mean(vs), 2) if vs else None,
                "vs_spy_cut": round(statistics.mean(sorted(vs)[:-1]), 2) if len(vs) > 1 else None}

    groups = {"all": ideas,
              "listed by 10:00": [r for r in ideas if r["time"] <= "10:00"],
              "listed 10:01-12:00": [r for r in ideas if "10:00" < r["time"] <= "12:00"],
              "listed after 12:00": [r for r in ideas if r["time"] > "12:00"],
              "call on a day SPY closed above its open": [r for r in ideas if r["direction"] == "call" and up.get(r["date"])],
              "put on a day SPY closed above its open": [r for r in ideas if r["direction"] == "put" and up.get(r["date"])],
              "call on a day SPY closed below its open": [r for r in ideas if r["direction"] == "call" and up.get(r["date"]) is False],
              "put on a day SPY closed below its open": [r for r in ideas if r["direction"] == "put" and up.get(r["date"]) is False],
              "after 10:00, under 1% its way from the open": [r for r in ideas if r["time"] > "10:00" and ext(r) is not None and 0 <= ext(r) < 1],
              "after 10:00, 1-3% its way": [r for r in ideas if r["time"] > "10:00" and ext(r) is not None and 1 <= ext(r) < 3],
              "after 10:00, 3% or more its way": [r for r in ideas if r["time"] > "10:00" and ext(r) is not None and ext(r) >= 3],
              "this week": [r for r in ideas if WEEK[0] <= r["date"] <= WEEK[1]],
              "this week, calls": [r for r in ideas if WEEK[0] <= r["date"] <= WEEK[1] and r["direction"] == "call"],
              "this week, puts": [r for r in ideas if WEEK[0] <= r["date"] <= WEEK[1] and r["direction"] == "put"]}
    by_type = defaultdict(list)
    for r in ideas:
        by_type[r["type"]].append(r)
    for t, rs in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        if len(rs) >= 8:
            groups[f"type: {t}"] = rs
    return {"days": len(days), "groups": {k: tally(v) for k, v in groups.items()}}


# --- 68: the rotation map ------------------------------------------------------------------------

def rotation_model(api):
    """The theme model's state at a close against the basket's next open-to-close, less SPY's."""
    data = themes.study(api, 2)
    spy = {d.isoformat(): c / o - 1
           for d, o, c in daily(api, ["SPY"], date.fromisoformat(data["days"][0]), date.fromisoformat(data["days"][-1]))["SPY"]}
    res = defaultdict(list)
    for th in data["themes"].values():
        for a, b in zip(th["rows"], th["rows"][1:]):
            ex = b["oc"] - spy.get(b["day"], 0)
            res[f"two years | {a['state']}"].append(ex)
            if b["day"] >= RECENT:
                res[f"last 3 months | {a['state']}"].append(ex)
    return {k: {"n": len(v), "avg": round(statistics.mean(v) * 100, 3), "beat": round(sum(x > 0 for x in v) / len(v), 3)}
            for k, v in sorted(res.items())}


def rotation_map(api, root=journal.ROOT):
    """My own heating / cooling lists against the same day's open-to-close, less SPY's."""
    syms = sorted({s for v in MAP.values() for s in v} | {"SPY"})
    files = sorted(glob.glob(str(root / "journal" / "bias" / "2026-*.json")))
    first = date.fromisoformat(json.loads(Path(files[0]).read_text())["date"])
    oc = {s: {d.isoformat(): c / o - 1 for d, o, c in v} for s, v in daily(api, syms, first, date.today()).items()}

    def side(lines, d):
        names = set()
        for text in lines or []:
            if isinstance(text, str):
                head = re.split(r"[:(]", text, 1)[0].lower()
                for k in MAP:
                    if re.search(rf"\b{k}\b", head):
                        names.update(MAP[k])
        v = [oc[s][d] - oc["SPY"][d] for s in names if d in oc.get(s, {})]
        return statistics.mean(v) if v else None

    rows = []
    for f in files:
        b = json.loads(Path(f).read_text())
        d, r = b["date"], b.get("rotation") or {}
        if d in oc["SPY"]:
            h, c = side(r.get("heating"), d), side(r.get("cooling"), d)
            if h is not None and c is not None:
                rows.append({"date": d, "heating": round(h * 100, 2), "cooling": round(c * 100, 2)})
    return rows


# --- 57 and 59: the picks at the stock, by class and by extension --------------------------------

def class_of(day, root=journal.ROOT):
    try:
        cls = (json.loads((root / "journal" / "bias" / f"{day}.json").read_text()).get("sniper") or {}).get("class")
    except (OSError, ValueError):
        cls = None
    return cls or CLASSES.get(day, "news")


def pick_tables(api, rows):
    out = {"snipers": [], "intraday": []}
    for r in rows:
        s = sign(r["kind"])
        live = r["entries"].get("live")
        item = {"day": r["day"], "sym": r["sym"], "kind": r["kind"], "oc": s * (r["close"] / r["open"] - 1),
                "entered": bool(live)}
        if live:
            item["entry_t"] = live["t"]
            item["ext"] = s * (live["spot"] / r["open"] - 1)
            item["fwd"] = s * (r["close"] / live["spot"] - 1)
            item["opt"] = {d: {"day1": p["day1"], "carry": p.get("carry") or p["day1"]} for d, p in live["picks"].items()}
        if r["source"] == "sniper":
            item["class"] = class_of(r["day"])
            out["snipers"].append(item)
        else:
            out["intraday"].append(item)
    syms = sorted({i["sym"] for i in out["intraday"]})
    try:
        bars = api.daily_bars_multi(syms, date(2026, 8, 20), date.today())
    except AlpacaError:
        bars = {}
    for i in out["intraday"]:
        b = [x for x in bars.get(i["sym"], []) if x["t"][:10] < i["day"]][-20:]
        if b and i["entered"]:
            rng = statistics.mean((x["h"] / x["o"] - 1) if i["kind"] == "call" else (1 - x["l"] / x["o"]) for x in b)
            i["own_range"] = rng
    return out


# --- 64: the gate of the open sniper, on the stock -----------------------------------------------

def entry_gates(api, rows):
    """Three ways into the same sniper before 10:00: the first minute at or beyond the open (live), five
    closed minutes in a row beyond the open, or a close beyond the first five minutes' extreme."""
    out = []
    for r in rows:
        if r["source"] != "sniper":
            continue
        day = date.fromisoformat(r["day"])
        bars = snipers.stock_minutes(api, r["sym"], day)
        if not bars:
            continue
        s, o, close = sign(r["kind"]), bars[0]["o"], bars[-1]["c"]
        win = [b for b in bars if hhmm("09:31") <= b["t"].time() <= hhmm("09:59")]
        first5 = [b for b in bars if b["t"].time() < hhmm("09:35")]
        edge = max(b["h"] for b in first5) if s > 0 else min(b["l"] for b in first5)
        got = {}
        for i, b in enumerate(win):
            beyond = s * (b["c"] - o) >= 0
            if "live" not in got and beyond:
                got["live"] = b
            if "five" not in got and i >= 4 and all(s * (x["c"] - o) > 0 for x in win[i - 4:i + 1]):
                got["five"] = b
            if "break" not in got and b["t"].time() >= hhmm("09:35") and s * (b["c"] - edge) > 0:
                got["break"] = b
        out.append({"day": r["day"], "sym": r["sym"], "class": class_of(r["day"]),
                    "gates": {k: {"t": b["t"].strftime("%H:%M"), "ext": s * (b["c"] / o - 1), "fwd": s * (close / b["c"] - 1)}
                              for k, b in got.items()}})
    return out


# --- 63: a release pop that fades before the bell ------------------------------------------------

def release_fade(api, root=journal.ROOT):
    cal = json.loads(Path(root / "config" / "macro_events.json").read_text())
    days = sorted({d for k in ("CPI", "NFP") for d in cal.get(k, [])} | {"2026-11-13"})   # 11-13 = PPI, the case
    spy = {d.isoformat(): (o, c) for d, o, c in daily(api, ["SPY"], date(2025, 10, 1), date.today())["SPY"]}
    out = []
    for d in days:
        if d not in spy:
            continue
        day = date.fromisoformat(d)
        try:
            raw = api.stock_bars("SPY", datetime.combine(day, hhmm("08:00"), ET), datetime.combine(day, hhmm("09:31"), ET),
                                 feed="sip", adjustment="raw")
        except AlpacaError:
            continue
        bars = [(datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).time(), b) for b in raw]
        before = [b for t, b in bars if t < hhmm("08:30")]
        react = [b for t, b in bars if hhmm("08:30") <= t <= hhmm("08:40")]
        opening = [b for t, b in bars if t >= hhmm("09:30")]
        if not before or not react or not opening:
            continue
        # the 08:29 print, the reaction and the opening print all come from the same unadjusted minute
        # bars: the daily bars are dividend-adjusted, and a quarter's dividend is as large as the pops
        pre, first = before[-1]["c"], opening[0]["o"]
        hi, lo = max(b["h"] for b in react) / pre - 1, min(b["l"] for b in react) / pre - 1
        s, pop = (1, hi) if hi >= -lo else (-1, -lo)
        o, c = spy[d]
        kept = s * (first / pre - 1) / pop if pop else None
        out.append({"day": d, "pop": s * pop, "kept": kept, "oc_with": s * (c / o - 1)})
    return out


# --- the two-year replay of rating headlines near the money --------------------------------------

def upgrades_near(api, since=date(2026, 10, 13), log=print):
    """The rating headlines of EXITS.md (the events exits.py already found and priced at 0.10-0.30
    delta, to 2026-10-12) plus the ones since, re-priced at 0.30 and 0.45 delta with the half-at-2x
    rule carried to expiry. Paging two years of news again takes hours; the event list is reused.
    Saved after every event, so an interrupted run resumes."""
    exits.DELTAS["upgrade"] = (0.30, 0.45)
    exits.CARRY_RULES = ("half2_arm1.5", "half3_arm1.5", "trail2x", "hold")
    done = json.loads(UPGRADES.read_text()) if UPGRADES.exists() else []
    seen = {(r["sym"], r["day"]) for r in done}
    events = [(r["sym"], date.fromisoformat(r["day"]), r["kind"], r.get("headline", ""))
              for r in json.loads((DIR / "exits.json").read_text()) if r["study"] == "upgrade"]
    end = datetime.now(ET).date() - timedelta(days=1)
    for sym in exits.RATED:
        try:
            events += [(sym, d, kind, head[:90]) for d, kind, head in exits.rating_events(api, sym, since, end)
                       if exits.STRICT.search(head)]
        except AlpacaError:
            continue
    for sym, day, kind, head in sorted(set(events), key=lambda e: (e[1], e[0])):
        if (sym, day.isoformat()) in seen:
            continue
        seen.add((sym, day.isoformat()))
        expiry = exits.nearest_expiry(sym, day)
        try:
            bars, _ = exits.spot_at(api, sym, day, hhmm("09:32"))
        except AlpacaError:
            continue
        b = exits.at_or_after(bars, hhmm("09:31"), 3) if bars else None
        if not expiry or not b or sign(kind) * (b["c"] / bars[0]["o"] - 1) < 0:
            continue                       # the same gate as the sniper: not against the rating at 09:32
        r = exits.price(api, sym, day, expiry, hhmm("09:32"), b["c"], kind, "upgrade", None, headline=head)
        if r:
            done.append(r)
            UPGRADES.write_text(json.dumps(done, indent=0) + "\n")
            log(f"{day} {sym} {kind}: {list(r['picks'])}", flush=True)
    return done


def upgrade_stats(rows):
    out = {}
    for label, rs in (("all", rows), ("last 3 months", [r for r in rows if r["day"] >= RECENT]),
                      ("calls (upgrades), all", [r for r in rows if r["kind"] == "call"]),
                      ("calls (upgrades), last 3 months", [r for r in rows if r["kind"] == "call" and r["day"] >= RECENT]),
                      ("puts (downgrades), all", [r for r in rows if r["kind"] == "put"])):
        for d in ("d0.30", "d0.45"):
            for rule in ("half2_arm1.5", "half3_arm1.5", "hold"):
                day1 = [r["picks"][d]["exits_10"][rule] for r in rs if d in r["picks"]]
                carried = [(r["picks"][d].get("carry_10") or r["picks"][d]["exits_10"])[rule] for r in rs if d in r["picks"]]
                out[f"{label} | {d} | {rule}"] = {"day1": day1, "carried": carried}
    return out


# --- collect and report --------------------------------------------------------------------------

def collect(api):
    rows = json.loads((DIR / "snipers.json").read_text())
    data = {"through": WEEK[1],
            "open_drive": open_drive_exits(json.loads((DIR / "opengate.json").read_text())["rows"]),
            "heroes": hero_pairs(),
            "bias": bias_calibration(api),
            "opportunities": opportunity_splits(api),
            "rotation_model": rotation_model(api),
            "rotation_map": rotation_map(api),
            "picks": pick_tables(api, rows),
            "gates": entry_gates(api, rows),
            "release": release_fade(api)}
    return data


def pct(x, digits=1):
    return "-" if x is None else f"{x * 100:+.{digits}f}%"


def report(data, upgrades=None):
    L = [f"# Week 46: where the week went (to {data['through']})", "",
         "SPY +2.6% on the week (open to close +1.5%, +0.2%, +0.4%, +0.4%, -0.8%), SMH +4.9%. Real: 3 trades, 0 wins, "
         "-$285. Shadows: 26 closed, 5 wins. Option tables are real option minute bars, 10% costs each way; "
         "`a / b / c` = average / without the best trade / without the best two. See zoh/research/week46.py.", ""]

    # 57 + picks at the stock
    sn, it = data["picks"]["snipers"], data["picks"]["intraday"]
    L += ["## 1. The picks at the stock: right at the open, late in the session (items 57, 59)", "",
          "| group | picks | right open to close | avg open to close | entered | right from the entry | avg from the entry | 1% or more from the entry |",
          "|---|---|---|---|---|---|---|---|"]
    for label, rs in (("pre-market sniper", sn), ("intraday pick", it),
                      ("sniper, rating change (upgrade or target)", [r for r in sn if r["class"] in RATING]),
                      ("sniper, company news", [r for r in sn if r["class"] == "news"]),
                      ("sniper, this week", [r for r in sn if r["day"] >= WEEK[0]])):
        if not rs:
            continue
        e = [r for r in rs if r["entered"]]
        L.append(f"| {label} | {len(rs)} | {sum(r['oc'] > 0 for r in rs)} | {pct(statistics.mean(r['oc'] for r in rs), 2)} | "
                 f"{len(e)} | {sum(r['fwd'] > 0 for r in e)} | {pct(statistics.mean(r['fwd'] for r in e), 2) if e else '-'} | "
                 f"{sum(r['fwd'] >= 0.01 for r in e)} |")
    L += ["", "An intraday pick is right about the day and late for it: the stock had made its move before the pick. "
          "By how far it had already gone (its way from the open at the entry; d0.20, half at 3x, trail from 1.5x, sold day one):", "",
          "| at the entry | picks | right from the entry | avg from the entry | option: n / win / a / b / c |", "|---|---|---|---|---|"]
    e = [r for r in it if r["entered"]]
    opt = lambda r, d="d0.20", rule="half3_arm1.5", how="day1": r["opt"].get(d, {}).get(how, {}).get(rule)
    for label, rs in (("under 2% its way", [r for r in e if r["ext"] < 0.02]), ("2-3%", [r for r in e if 0.02 <= r["ext"] < 0.03]),
                      ("3% or more", [r for r in e if r["ext"] >= 0.03]),
                      ("under one of its own average ranges", [r for r in e if r.get("own_range") and r["ext"] / r["own_range"] < 1]),
                      ("one average range or more", [r for r in e if r.get("own_range") and r["ext"] / r["own_range"] >= 1]),
                      ("picked before 11:00", [r for r in e if r["entry_t"] < "11:00"]),
                      ("picked 11:00-13:00", [r for r in e if "11:00" <= r["entry_t"] < "13:00"]),
                      ("picked after 13:00", [r for r in e if r["entry_t"] >= "13:00"])):
        if rs:
            L.append(f"| {label} | {len(rs)} | {sum(r['fwd'] > 0 for r in rs)} | {pct(statistics.mean(r['fwd'] for r in rs), 2)} | "
                     f"{cell([x for x in (opt(r) for r in rs) if x is not None])} |")
    L += ["", "## 2. The sniper by class, on real option prices (item 57)", "",
          "Live entry (first minute 09:32-10:00 at or beyond the open). `carried` = held past day one to the expiry where "
          "the contract outlives the day, the trail still on.", "",
          "| class | strike | exit | sold day one: n / win / a / b / c | carried: n / win / a / b / c |", "|---|---|---|---|---|"]
    for label, rs in (("rating change", [r for r in sn if r["class"] in RATING and r["entered"]]),
                      ("company news", [r for r in sn if r["class"] == "news" and r["entered"]]),
                      ("every sniper", [r for r in sn if r["entered"]])):
        for d in ("d0.10", "d0.30", "d0.45"):
            for rule in ("half3_arm1.5", "half2_arm1.5", "hold"):
                L.append(f"| {label} | {d} | {rule} | {cell([x for x in (opt(r, d, rule) for r in rs) if x is not None])} | "
                         f"{cell([x for x in (opt(r, d, rule, 'carry') for r in rs) if x is not None])} |")
    L += ["", "Each rating-change sniper (0.45 delta, half at 2x and a trail from 1.5x, sold day one):", "",
          "| day | stock | class | open to close | entered | option |", "|---|---|---|---|---|---|"]
    for r in sn:
        if r["class"] in RATING:
            L.append(f"| {r['day']} | {r['sym']} | {r['class']} | {pct(r['oc'])} | {r.get('entry_t', 'no (against the pick until 10:00)')} | "
                     f"{pct(opt(r, 'd0.45', 'half2_arm1.5'), 0) if r['entered'] else '-'} |")
    if upgrades:
        st = upgrade_stats(upgrades)
        L += ["", f"The same question on every rating headline of two years, not only the ones I picked ({len(upgrades)} events since "
              "2024-02 on 25 large caps: a strict '<firm> upgrades / downgrades <stock>' headline before 09:30, bought at 09:32 "
              "when the stock is not against the rating, nearest expiry):", "",
              "| events | strike | exit | sold day one: n / win / a / b / c | carried: n / win / a / b / c |", "|---|---|---|---|---|"]
        for k, v in st.items():
            label, d, rule = k.split(" | ")
            L.append(f"| {label} | {d} | {rule} | {cell(v['day1'])} | {cell(v['carried'])} |")

    # 64
    g = data["gates"]
    L += ["", "## 3. The gate of the open sniper, on the stock (item 64)", "",
          "| gate | entered | avg its way from the open at the entry | right from the entry | avg from the entry |", "|---|---|---|---|---|"]
    for key, label in (("live", "first minute at or beyond the open (live)"), ("five", "five closed minutes in a row beyond the open"),
                       ("break", "a close beyond the first five minutes' extreme")):
        v = [x["gates"][key] for x in g if key in x["gates"]]
        if v:
            L.append(f"| {label} | {len(v)} of {len(g)} | {pct(statistics.mean(x['ext'] for x in v), 2)} | "
                     f"{sum(x['fwd'] > 0 for x in v)} | {pct(statistics.mean(x['fwd'] for x in v), 2)} |")
    both = [x for x in g if "live" in x["gates"] and "five" in x["gates"]]
    if both:
        L += ["", f"On the {len(both)} days both gates entered: live {pct(statistics.mean(x['gates']['live']['fwd'] for x in both), 2)} from the "
              f"entry, five minutes {pct(statistics.mean(x['gates']['five']['fwd'] for x in both), 2)}."]

    # 60
    L += ["", "## 4. Exits of the open-drive ledgers on 0.35-delta contracts (item 60)", "",
          "The ledgers' own days from opengate.json (NVDA / TSLA calls at +0.8%, SPY calls at +0.5%, SPY puts at -0.5%), "
          "exits to 15:30.", "", "| family | period | trades (2x / 3x reached) | hold | all out at 3x | trail from 2x | half at 3x + trail |",
          "|---|---|---|---|---|---|---|"]
    for k, v in data["open_drive"].items():
        fam, per = k.split(" | ")
        c3 = lambda ex: " / ".join(cell(v["exits"][ex]).split(" | ")[1:])
        L.append(f"| {fam} | {per} | {v['n']} ({v['x2']} / {v['x3']}) | {c3('hold')} | {c3('take3')} | {c3('trail')} | {c3('half3_trail')} |")

    # heroes
    h = data["heroes"]
    L += ["", "## 5. The full-stake shadows: held to expiry against a trail on the same contract", "",
          "| entered | variant | contract | stake | peak | held to expiry | with the small leg's trail (from the peak) | small leg that day |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(h, key=lambda r: r["day"]):
        twin = "-" if r["twin_pct"] is None else pct(r["twin_pct"], 0) + ("" if r["twin_same"] else " (another strike)")
        L.append(f"| {r['day']} | {r['variant']} | {r['contract']} | ${r['stake']} | {r['peak_x']:.2f}x | {pct(r['pnl_pct'], 0)} | "
                 f"{pct(r['trail_pct'], 0)} | {twin} |")
    L += ["", f"{len(h)} trades, {sum(r['pnl'] > 0 for r in h)} wins, ${sum(r['pnl'] for r in h):,.0f}; "
          f"{sum(r['peak_x'] >= 1.5 for r in h)} traded at 1.5x or better first. With the trail the same stakes come to about "
          f"${sum(r['stake'] * r['trail_pct'] for r in h):,.0f} (an estimate from the recorded peak: a trail sells after the peak, "
          "at 60% of it or the entry, whichever is higher)."]

    # 66
    b = data["bias"]
    p = [r for r in b if r["p_up"] is not None]
    lean = [r for r in p if r["p_up"] != 0.5]
    called = [r for r in b if r["bias"] != "none"]
    L += ["", "## 6. The SPY call (item 66)", "",
          f"{len(b)} mornings since {b[0]['date']}; {len(called)} took a side (the last on {called[-1]['date'] if called else '-'}), "
          f"right open to close on {sum((r['bias'] == 'call') == (r['oc'] > 0) for r in called)}. Since the bar went to 0.60 / 0.40 "
          f"on 2026-10-23: {len(p)} mornings with a p_up, between {min(r['p_up'] for r in p):.2f} and {max(r['p_up'] for r in p):.2f}, "
          f"so none reached the bar, and none would have at 0.57 / 0.43. Brier {statistics.mean((r['p_up'] - (r['oc'] > 0)) ** 2 for r in p):.3f} "
          f"(0.250 for always 0.50). SPY closed above its open on {sum(r['oc'] > 0 for r in p)} of the {len(p)}; the side I leaned to "
          f"was right on {sum((r['p_up'] > 0.5) == (r['oc'] > 0) for r in lean)} of {len(lean)}; 'always up' on "
          f"{sum(r['oc'] > 0 for r in lean)} of the same {len(lean)}.", "",
          "| p_up | mornings | closed above the open | avg open to close |", "|---|---|---|---|"]
    for lo, hi in ((0, 0.45), (0.45, 0.50), (0.50, 0.55), (0.55, 0.60), (0.60, 1.01)):
        v = [r for r in p if lo <= r["p_up"] < hi]
        if v:
            L.append(f"| {lo:.2f}-{min(hi, 1):.2f} | {len(v)} | {sum(r['oc'] > 0 for r in v)} | {pct(statistics.mean(r['oc'] for r in v), 2)} |")

    # 67
    o = data["opportunities"]
    L += ["", f"## 7. The opportunity log, split ({o['days']} sessions; item 67)", "",
          "| group | ideas | paid (1% or more its way) | right | wrong | avg against SPY | without the best |", "|---|---|---|---|---|---|---|"]
    for k, v in o["groups"].items():
        if v["n"]:
            cut = "-" if v["vs_spy_cut"] is None else f"{v['vs_spy_cut']:+.2f}%"
            L.append(f"| {k} | {v['n']} | {v['paid']} ({v['paid'] / v['n']:.0%}) | {v['right']} | {v['wrong']} ({v['wrong'] / v['n']:.0%}) | "
                     f"{v['vs_spy']:+.2f}% | {cut} |")

    # 68
    m, rm = data["rotation_map"], data["rotation_model"]
    wk = [r for r in m if r["date"] >= WEEK[0]]
    L += ["", "## 8. The rotation map as a same-day forecast (item 68)", "",
          f"My own lists, {len(m)} mornings: the heating names beat the cooling names open to close on "
          f"{sum(r['heating'] > r['cooling'] for r in m)} (this week {sum(r['heating'] > r['cooling'] for r in wk)} of {len(wk)}); "
          f"against SPY the heating names averaged {statistics.mean(r['heating'] for r in m):+.2f}% and the cooling names "
          f"{statistics.mean(r['cooling'] for r in m):+.2f}% (below SPY on {sum(r['cooling'] < 0 for r in m)} mornings).", "",
          "The theme model's state at a close against the basket's next open-to-close, less SPY's:", "",
          "| period | state | theme-days | avg against SPY | beat SPY |", "|---|---|---|---|---|"]
    for k, v in rm.items():
        per, st = k.split(" | ")
        L.append(f"| {per} | {st} | {v['n']} | {v['avg']:+.3f}% | {v['beat']:.0%} |")

    # 63
    rel = data["release"]
    big = [r for r in rel if abs(r["pop"]) >= 0.0015]
    faded, held = [r for r in big if r["kept"] is not None and r["kept"] <= 0.5], [r for r in big if r["kept"] is not None and r["kept"] > 0.5]
    L += ["", "## 9. A release pop that fades before the bell (item 63)", "",
          f"{len(rel)} release days in the calendar (CPI and jobs since 2025-10, plus the 2026-11-13 PPI); the first reaction is the "
          f"larger of the 08:30-08:40 extremes against the 08:29 print, {len(big)} days with 0.15% or more.", "",
          "| at the 09:30 open | days | open to close with the first reaction: right | avg | open to close against it by 0.5% or more |",
          "|---|---|---|---|---|"]
    for label, rs in (("half or more of the reaction gone", faded), ("more than half still there", held)):
        if rs:
            L.append(f"| {label} | {len(rs)} | {sum(r['oc_with'] > 0 for r in rs)} | {pct(statistics.mean(r['oc_with'] for r in rs), 2)} | "
                     f"{sum(r['oc_with'] <= -0.005 for r in rs)} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="rebuild WEEK46.md from week46.json")
    ap.add_argument("--upgrades", action="store_true", help="re-run the two-year rating-change replay (slow)")
    a = ap.parse_args()
    if a.report:
        data = json.loads(DATA.read_text())
    else:
        api = Alpaca()
        data = collect(api)
        DATA.write_text(json.dumps(data, indent=0) + "\n")
        if a.upgrades:
            OUT.write_text(report(data, json.loads(UPGRADES.read_text()) if UPGRADES.exists() else None))
            upgrades_near(api)
    upgrades = json.loads(UPGRADES.read_text()) if UPGRADES.exists() else None
    text = report(data, upgrades)
    OUT.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
