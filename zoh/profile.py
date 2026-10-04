"""Stock personality profile: how AMD / META actually behave intraday (2026 to date).

For each stock: daily move distribution, gap behaviour, how early a trend day can be
recognised (move from the open at 10:00/10:30/11:00 vs the rest of the day), which half
hours carry the volatility, day-of-week, co-movement and lead/lag with peers, and the
modelled multiple of a 2% OTM same-day option bought at each check time by move bucket.

    python -m zoh.profile AMD META
"""
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime, time, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .strategy import ET, bs_price, parse_bar, regular_session

START = datetime(2026, 1, 2, 9, 30, tzinfo=ET)
PEERS = {"AMD": ["NVDA", "INTC", "SMH", "QQQ", "SPY"],
         "META": ["GOOGL", "AMZN", "MSFT", "QQQ", "SPY"]}
CHECKS = [time(10, 0), time(10, 30), time(11, 0)]
BUCKETS = [0.005, 0.01, 0.015, 0.02, 0.03, 1.0]
OTM = 0.02
IV_MULT = 1.15
SLIP = 0.03


def load(api, sym, end):
    try:
        raw = api.stock_bars(sym, START, end)
    except AlpacaError as e:
        print(f"{sym}: {e}")
        return {}
    by_day = defaultdict(list)
    for b in regular_session([parse_bar(r) for r in raw]):
        by_day[b["t"].date()].append(b)
    return {d: bs for d, bs in sorted(by_day.items()) if len(bs) >= 300}


def price_at(bars, t):
    before = [b for b in bars if b["t"].time() < t]
    return before[-1]["c"] if before else None


def bucket_label(x):
    lo = 0.0
    for hi in BUCKETS:
        if x < hi:
            return f"{lo:.1%}–{hi:.1%}" if hi < 1 else f"≥{lo:.1%}"
        lo = hi
    return f"≥{lo:.1%}"


def pct(x):
    return "—" if x is None else f"{x:+.1%}"


def corr(a, b):
    if len(a) < 10:
        return float("nan")
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return num / den if den else float("nan")


def five_min(bars):
    out = {}
    for b in bars:
        key = b["t"].replace(minute=b["t"].minute - b["t"].minute % 5, second=0)
        out[key] = b["c"]
    keys = sorted(out)
    return {k: out[k] / out[p] - 1 for p, k in zip(keys, keys[1:])}


def profile(sym, data, peers):
    days = list(data)
    closes = {d: data[d][-1]["c"] for d in days}
    rows = []
    for prev, d in zip(days, days[1:]):
        bars = data[d]
        o, c = bars[0]["o"], bars[-1]["c"]
        hi, lo = max(b["h"] for b in bars), min(b["l"] for b in bars)
        pc = closes[prev]
        rows.append({"d": d, "gap": o / pc - 1, "oc": c / o - 1, "rng": (hi - lo) / o,
                     "filled": (lo <= pc) if o > pc else (hi >= pc), "bars": bars, "o": o, "c": c,
                     "pc": pc})
    rv = statistics.pstdev([math.log(r["c"] / r["pc"]) for r in rows]) * math.sqrt(252)
    iv = rv * IV_MULT
    oc = [abs(r["oc"]) for r in rows]
    L = [f"# {sym} personality — {rows[0]['d']} → {rows[-1]['d']} ({len(rows)} days)", "",
         f"Daily realised vol {rv:.0%} (option model IV {iv:.0%}). Median |open→close| "
         f"{statistics.median(oc):.1%}, median range {statistics.median(r['rng'] for r in rows):.1%}. "
         f"Days with |open→close| ≥ 3%: {sum(x >= .03 for x in oc)}; ≥ 5%: {sum(x >= .05 for x in oc)}.",
         "", "## 1. Gaps: does the open's gap continue or fill?", "",
         "| gap | days | filled same day | open→close (median) | continued (same sign) |",
         "|---|---|---|---|---|"]
    gap_bins = [(-1, -0.02), (-0.02, -0.01), (-0.01, -0.003), (-0.003, 0.003), (0.003, 0.01),
                (0.01, 0.02), (0.02, 1)]
    for lo, hi in gap_bins:
        g = [r for r in rows if lo <= r["gap"] < hi]
        if not g:
            continue
        cont = [r for r in g if r["oc"] * r["gap"] > 0]
        label = f"< {hi:+.0%}" if lo <= -1 else f"≥ {lo:+.0%}" if hi >= 1 else f"{lo:+.1%} … {hi:+.1%}"
        L.append(f"| {label} | {len(g)} | {sum(r['filled'] for r in g) / len(g):.0%} | "
                 f"{pct(statistics.median(r['oc'] for r in g))} | "
                 f"{len(cont) / len(g):.0%} |")
    L += ["", "## 2. Recognising trend days early", "",
          "Move from the open at the check time (absolute) → what the rest of the day did, in the "
          "same direction. 'x' = modelled multiple of a 2% OTM same-day option bought at the check "
          "time in that direction and sold at 15:45.", "",
          "| check | move by then | days | kept going (close beyond check price) | rest-of-day move "
          "(median) | became ≥3% day | option x (median / mean) | ≥5x |",
          "|---|---|---|---|---|---|---|---|"]
    for t in CHECKS:
        groups = defaultdict(list)
        for r in rows:
            p = price_at(r["bars"], t)
            if not p:
                continue
            m = p / r["o"] - 1
            sgn = 1 if m >= 0 else -1
            rest = (r["c"] / p - 1) * sgn
            exit_bar = price_at(r["bars"], time(15, 45)) or r["c"]
            kind = "call" if sgn > 0 else "put"
            K = p * (1 + OTM * sgn)
            left = (datetime.combine(r["d"], time(16), ET) - datetime.combine(r["d"], t, ET)).seconds / 60
            entry = bs_price(p, K, left / (252 * 390), iv, kind) * (1 + SLIP) + 0.02
            out = max(bs_price(exit_bar, K, 15 / (252 * 390), iv, kind) * (1 - SLIP) - 0.02, 0)
            groups[bucket_label(abs(m))].append({"rest": rest, "big": abs(r["oc"]) >= .03 and r["oc"] * sgn > 0,
                                                 "x": out / entry if entry > 0 else 0})
        for label in [bucket_label(b - 1e-9) for b in BUCKETS]:
            g = groups.get(label)
            if not g:
                continue
            xs = [e["x"] for e in g]
            L.append(f"| {t:%H:%M} | {label} | {len(g)} | {sum(e['rest'] > 0 for e in g) / len(g):.0%} | "
                     f"{pct(statistics.median(e['rest'] for e in g))} | {sum(e['big'] for e in g)} | "
                     f"{statistics.median(xs):.2f} / {statistics.mean(xs):.2f} | {sum(x >= 5 for x in xs)} |")
    L += ["", "## 3. When does it move? (mean |30-min return| by slot)", "", "| slot | mean |move| | share of day |",
          "|---|---|---|"]
    slots = defaultdict(list)
    for r in rows:
        bars = r["bars"]
        for i in range(13):
            a = datetime.combine(r["d"], time(9, 30), ET) + timedelta(minutes=30 * i)
            seg = [b for b in bars if a <= b["t"] < a + timedelta(minutes=30)]
            if len(seg) > 5:
                slots[i].append(abs(seg[-1]["c"] / seg[0]["o"] - 1))
    total = sum(statistics.mean(v) for v in slots.values())
    for i in sorted(slots):
        a = (datetime(2000, 1, 1, 9, 30) + timedelta(minutes=30 * i)).time()
        m = statistics.mean(slots[i])
        L.append(f"| {a:%H:%M} | {m:.2%} | {m / total:.0%} |")
    L += ["", "## 4. Day of week (single-stock same-day expiries: Mon/Wed/Fri)", "",
          "| day | days | median |open→close| | ≥3% days |", "|---|---|---|---|"]
    for wd, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri"]):
        g = [abs(r["oc"]) for r in rows if r["d"].weekday() == wd]
        if g:
            L.append(f"| {name} | {len(g)} | {statistics.median(g):.1%} | {sum(x >= .03 for x in g)} |")
    L += ["", "## 5. Who does it move with?", "",
          "| peer | daily open→close corr | 5-min corr | peer leads by 5 min (corr) | stock leads peer |",
          "|---|---|---|---|---|"]
    own5 = {}
    for r in rows:
        own5.update(five_min(r["bars"]))
    for peer, pdata in peers.items():
        a, b = [], []
        for r in rows:
            if r["d"] in pdata:
                pb = pdata[r["d"]]
                a.append(r["oc"])
                b.append(pb[-1]["c"] / pb[0]["o"] - 1)
        p5 = {}
        for d in pdata:
            p5.update(five_min(pdata[d]))
        common = sorted(set(own5) & set(p5))
        s5 = [own5[k] for k in common]
        q5 = [p5[k] for k in common]
        lag_pairs = [(own5[k], p5[k - timedelta(minutes=5)]) for k in common
                     if k - timedelta(minutes=5) in p5]
        lead_pairs = [(own5[k - timedelta(minutes=5)], p5[k]) for k in common
                      if k - timedelta(minutes=5) in own5]
        L.append(f"| {peer} | {corr(a, b):.2f} | {corr(s5, q5):.2f} | "
                 f"{corr([x for x, _ in lag_pairs], [y for _, y in lag_pairs]):+.3f} | "
                 f"{corr([y for _, y in lead_pairs], [x for x, _ in lead_pairs]):+.3f} |")
    big = sorted(rows, key=lambda r: -abs(r["oc"]))[:15]
    L += ["", "## 6. The 15 biggest open→close days", "",
          "| date | gap | open→close | move by 10:00 | by 10:30 | " +
          " | ".join(peers) + " (open→close) |", "|---|---|---|---|---|" + "---|" * len(peers)]
    for r in sorted(big, key=lambda r: r["d"]):
        m10 = (price_at(r["bars"], time(10)) or r["o"]) / r["o"] - 1
        m1030 = (price_at(r["bars"], time(10, 30)) or r["o"]) / r["o"] - 1
        pm = []
        for peer, pdata in peers.items():
            pb = pdata.get(r["d"])
            pm.append(pct(pb[-1]["c"] / pb[0]["o"] - 1) if pb else "—")
        L.append(f"| {r['d']} | {pct(r['gap'])} | {pct(r['oc'])} | {pct(m10)} | {pct(m1030)} | "
                 + " | ".join(pm) + " |")
    return "\n".join(L) + "\n"


def main():
    syms = sys.argv[1:] or ["AMD", "META"]
    api = Alpaca()
    end = datetime.now(ET) - timedelta(minutes=20)
    cache = {}
    out = journal.ROOT / "journal" / "research"
    out.mkdir(parents=True, exist_ok=True)
    for sym in syms:
        for s in [sym] + PEERS.get(sym, []):
            if s not in cache:
                cache[s] = load(api, s, end)
                print(f"{s}: {len(cache[s])} days", flush=True)
        text = profile(sym, cache[sym], {p: cache[p] for p in PEERS.get(sym, [])})
        (out / f"PROFILE_{sym}.md").write_text(text)
        print(text)


if __name__ == "__main__":
    main()
