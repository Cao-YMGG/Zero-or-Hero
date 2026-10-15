"""Does the night session tell us anything about the next day?

Each trading day is split with Alpaca SIP 5-minute bars (extended hours, 2024-02+):
  ah    = prior close (16:00) -> last after-hours print (by 20:00)
  ovn   = last after-hours print -> first pre-market print (04:00); the overnight session itself
  pre   = first pre-market print -> last print before 09:30
  night = prior close -> last print before 09:30 (= the opening gap, before the auction)
  day   = open -> close;  first = open -> 10:30;  rest = 10:30 -> close

Questions: does the night's direction carry into the day? Does a night move that the pre-market
gives back (night up, pre-market down, or the reverse) predict the day? Is it different on macro
release days (8:30 data overrides the night)? Buckets report the average and median day move,
how often the day goes the night's way, and n. Last 3 months first, then last year, then all.

    python -m zoh.research.overnight
"""
import json
import statistics
from datetime import date, datetime, time, timedelta
from pathlib import Path

from ..alpaca import DATA_URL, Alpaca
from ..strategy import ET
from .opendrive import macro_days

SYMBOLS = ["SPY", "QQQ", "NVDA", "META", "TSLA", "AMD", "AAPL", "MSFT", "AMZN", "GOOGL"]
START = date(2024, 2, 1)
OUT = Path(__file__).resolve().parents[2] / "journal" / "research"


def bars_5min(api, sym, start, end):
    params = {"symbols": sym, "timeframe": "5Min", "start": start.isoformat(),
              "end": end.isoformat(), "feed": "sip", "limit": 10000, "adjustment": "raw"}
    out = []
    for page in api._paged(f"{DATA_URL}/v2/stocks/bars", params, "bars"):
        out.extend((page or {}).get(sym, []))
    rows = []
    for b in out:
        t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
        rows.append((t, b["o"], b["c"]))
    return rows


def split_days(rows):
    """{date: {"pre": [(t,o,c)...], "rth": [...], "ah": [...]}} by session."""
    days = {}
    for t, o, c in rows:
        d = days.setdefault(t.date(), {"pre": [], "rth": [], "ah": []})
        tt = t.time()
        if time(4) <= tt < time(9, 30):
            d["pre"].append((t, o, c))
        elif time(9, 30) <= tt < time(16):
            d["rth"].append((t, o, c))
        elif time(16) <= tt < time(20):
            d["ah"].append((t, o, c))
    return days


def day_rows(sym, days, events):
    out = []
    dates = sorted(d for d, s in days.items() if s["rth"])
    for prev, cur in zip(dates, dates[1:]):
        p, c = days[prev], days[cur]
        if not p["rth"] or not c["rth"] or not c["pre"]:
            continue
        close_prev = p["rth"][-1][2]
        ah_last = p["ah"][-1][2] if p["ah"] else close_prev
        pre_first = c["pre"][0][1]
        pre_last = c["pre"][-1][2]
        open_ = c["rth"][0][1]
        close = c["rth"][-1][2]
        at_1030 = next((x[2] for x in c["rth"] if x[0].time() >= time(10, 25)), None)
        if at_1030 is None:
            continue
        out.append({"sym": sym, "day": cur.isoformat(), "macro": bool(events.get(cur.isoformat())),
                    "ah": ah_last / close_prev - 1, "ovn": pre_first / ah_last - 1,
                    "pre": pre_last / pre_first - 1, "night": pre_last / close_prev - 1,
                    "gap": open_ / close_prev - 1, "day_": close / open_ - 1,
                    "first": at_1030 / open_ - 1, "rest": close / at_1030 - 1})
    return out


def bucket(x):
    if x <= -0.005:
        return "night <= -0.5%"
    if x <= -0.002:
        return "-0.5% .. -0.2%"
    if x < 0.002:
        return "flat (|night| < 0.2%)"
    if x < 0.005:
        return "+0.2% .. +0.5%"
    return "night >= +0.5%"


ORDER = ["night <= -0.5%", "-0.5% .. -0.2%", "flat (|night| < 0.2%)", "+0.2% .. +0.5%", "night >= +0.5%"]


def summarize(rows, key="day_", sign_of="night"):
    if not rows:
        return None
    v = [r[key] for r in rows]
    same = [r for r in rows if r[sign_of] != 0]
    agree = sum((r[key] > 0) == (r[sign_of] > 0) for r in same) / len(same) if same else float("nan")
    return {"n": len(v), "avg": statistics.mean(v), "med": statistics.median(v),
            "up": sum(x > 0 for x in v) / len(v), "agree": agree}


def corr(xs, ys):
    if len(xs) < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sx = sum((x - mx) ** 2 for x in xs) ** 0.5
    sy = sum((y - my) ** 2 for y in ys) ** 0.5
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx and sy else float("nan")


def report(rows, end):
    recent = (end - timedelta(days=91)).isoformat()
    year = (end - timedelta(days=365)).isoformat()
    periods = [("last 3 months", recent), ("last year", year), ("since 2024-02", "")]

    def pct(x):
        return f"{x:+.2%}"

    lines = ["# Night session vs the next day", "",
             "Alpaca SIP 5-minute bars, extended hours. night = prior close -> last print before 09:30; "
             "ah = 16:00-20:00; ovn = 20:00-04:00 (last after-hours print -> first pre-market print); "
             "pre = 04:00-09:30; day = open -> close; first = open -> 10:30; rest = 10:30 -> close. "
             "'agree' = share of days whose move went the same way as the night.", "",
             f"Data through {end}.", ""]
    for sym in ["SPY", "QQQ", "single stocks (8)"]:
        sub = [r for r in rows if (r["sym"] == sym) or (sym.startswith("single") and r["sym"] not in ("SPY", "QQQ"))]
        lines += [f"## {sym}", "",
                  "### Correlations with the day (open -> close)", "",
                  "| period | n | night | ah | ovn | pre | night vs first hour | first hour vs rest |",
                  "|---|---|---|---|---|---|---|---|"]
        for name, cut in periods:
            s = [r for r in sub if r["day"] >= cut]
            if not s:
                continue
            lines.append(f"| {name} | {len(s)} | {corr([r['night'] for r in s], [r['day_'] for r in s]):+.2f} | "
                         f"{corr([r['ah'] for r in s], [r['day_'] for r in s]):+.2f} | "
                         f"{corr([r['ovn'] for r in s], [r['day_'] for r in s]):+.2f} | "
                         f"{corr([r['pre'] for r in s], [r['day_'] for r in s]):+.2f} | "
                         f"{corr([r['night'] for r in s], [r['first'] for r in s]):+.2f} | "
                         f"{corr([r['first'] for r in s], [r['rest'] for r in s]):+.2f} |")
        lines += ["", "### Day move by night bucket", "",
                  "| period | night bucket | n | day avg | day median | day up% | agree with night |",
                  "|---|---|---|---|---|---|---|"]
        for name, cut in periods:
            s = [r for r in sub if r["day"] >= cut]
            for b in ORDER:
                t = summarize([r for r in s if bucket(r["night"]) == b])
                if t:
                    lines.append(f"| {name} | {b} | {t['n']} | {pct(t['avg'])} | {pct(t['med'])} | "
                                 f"{t['up']:.0%} | {t['agree']:.0%} |")
        lines += ["", "### Night move given back in the pre-market", "",
                  "| period | pattern | n | day avg | day median | day up% |", "|---|---|---|---|---|---|"]
        patterns = {
            "night up (ah+ovn >= +0.3%), pre-market gives back >= 0.2%":
                lambda r: r["ah"] + r["ovn"] >= 0.003 and r["pre"] <= -0.002,
            "night up, pre-market extends >= 0.2%":
                lambda r: r["ah"] + r["ovn"] >= 0.003 and r["pre"] >= 0.002,
            "night down (ah+ovn <= -0.3%), pre-market recovers >= 0.2%":
                lambda r: r["ah"] + r["ovn"] <= -0.003 and r["pre"] >= 0.002,
            "night down, pre-market extends <= -0.2%":
                lambda r: r["ah"] + r["ovn"] <= -0.003 and r["pre"] <= -0.002,
        }
        for name, cut in periods:
            s = [r for r in sub if r["day"] >= cut]
            for pname, f in patterns.items():
                t = summarize([r for r in s if f(r)])
                if t:
                    lines.append(f"| {name} | {pname} | {t['n']} | {pct(t['avg'])} | {pct(t['med'])} | {t['up']:.0%} |")
        lines += ["", "### Macro days vs other days (night >= 0.2% either way)", "",
                  "| period | days | n | agree with night | day avg in night's direction |", "|---|---|---|---|---|"]
        for name, cut in periods:
            for label, m in (("macro", True), ("other", False)):
                s = [r for r in sub if r["day"] >= cut and r["macro"] == m and abs(r["night"]) >= 0.002]
                if s:
                    agree = sum((r["day_"] > 0) == (r["night"] > 0) for r in s) / len(s)
                    signed = statistics.mean([r["day_"] * (1 if r["night"] > 0 else -1) for r in s])
                    lines.append(f"| {name} | {label} | {len(s)} | {agree:.0%} | {pct(signed)} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    api = Alpaca()
    events = macro_days()
    end = datetime.now(ET).date() - timedelta(days=1)
    start = datetime.combine(START - timedelta(days=5), time(4), ET)
    stop = datetime.combine(end, time(20), ET)
    rows = []
    for sym in SYMBOLS:
        days = split_days(bars_5min(api, sym, start, stop))
        r = day_rows(sym, days, events)
        print(f"{sym}: {len(r)} days", flush=True)
        rows.extend(r)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "overnight.json").write_text(json.dumps(
        [{k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()} for r in rows]) + "\n")
    text = report(rows, end)
    (OUT / "OVERNIGHT.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
