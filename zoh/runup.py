"""Pre-earnings run-up: do stocks rise into earnings and sell the news?

Earnings dates come from Alpaca (Benzinga) news headlines like
"NVIDIA Q2 Adj. EPS $2.46 Beats $2.06 Estimate". A report after the close reacts the next
trading day; before the open, the same day. For each event we measure, versus SPY over the
same window: the 10- and 5-day run-up into the report, the reaction (gap and day), and the
drift 5 and 20 days after.

    python -m zoh.runup
"""
import re
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .strategy import ET

SYMBOLS = ["NVDA", "AMD", "AVGO", "MU", "INTC", "ARM", "QCOM", "META", "MSFT", "GOOGL", "AMZN",
           "AAPL", "TSLA", "NFLX", "ORCL", "PLTR", "CRM", "ADBE", "LITE", "CRDO", "ANET", "SMCI",
           "COIN", "SNOW", "UBER"]
EPS_HEADLINE = re.compile(r"\bQ[1-4]\b.*\bEPS \$?\(?-?\d", re.I)  # actuals, not previews
YEARS = 2


def earnings_events(api, symbol, start, end):
    """[(reaction_date, headline, surprise)] from EPS headlines, one per quarter."""
    found = []
    params = {"symbols": symbol, "start": start.isoformat(), "end": end.isoformat(),
              "limit": 50, "sort": "asc", "include_content": "false"}
    url = "https://data.alpaca.markets/v1beta1/news"
    while True:
        page = api._request("GET", url, params)
        for item in page.get("news") or []:
            if len(item.get("symbols") or []) > 2 or not EPS_HEADLINE.search(item["headline"]):
                continue
            t = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")).astimezone(ET)
            if found and (t.date() - found[-1][0]).days < 40:
                continue  # same quarter, later headline
            react = t.date() if t.hour < 9 or (t.hour == 9 and t.minute < 30) else (
                t.date() if t.hour < 16 else t.date() + timedelta(days=1))
            h = item["headline"].lower()
            surprise = "beat" if "beats" in h else "miss" if "misses" in h else "inline"
            found.append((react, item["headline"], surprise))
        token = page.get("next_page_token")
        if not token:
            return found
        params["page_token"] = token
        time.sleep(0.32)


def daily(api, symbols, start, end):
    out = {}
    for i in range(0, len(symbols), 50):
        chunk = symbols[i:i + 50]
        try:
            got = api.daily_bars_multi(chunk, start, end, feed="sip")
        except AlpacaError:
            got = api.daily_bars_multi(chunk, start, end, feed="iex")
        for sym, bars in got.items():
            out[sym] = [(datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date(),
                         b["o"], b["c"]) for b in bars]
    return out


def measure(bars, spy, react):
    days = [d for d, _, _ in bars]
    if react not in days:
        later = [d for d in days if d >= react]
        if not later:
            return None
        react = later[0]
    i = days.index(react)
    if i < 11 or i + 20 >= len(bars):
        return None
    spy_by = {d: (o, c) for d, o, c in spy}

    def ret(a, b, field_b="c"):
        da, db = days[a], days[b]
        pa = bars[a][2]
        pb = bars[b][2] if field_b == "c" else bars[b][1]
        sa = spy_by.get(da, (None, None))[1]
        sb = spy_by.get(db, (None, None))[1 if field_b == "c" else 0]
        if not sa or not sb:
            return None
        return (pb / pa - 1) - (sb / sa - 1)

    return {"react": react, "run10": ret(i - 11, i - 1), "run5": ret(i - 6, i - 1),
            "gap": ret(i - 1, i, "o"), "day": ret(i - 1, i), "post5": ret(i, i + 5),
            "post20": ret(i, i + 20)}


def pct(x):
    return "—" if x is None else f"{x:+.1%}"


def summarize(rows, label):
    def col(k):
        return [r[k] for r in rows if r[k] is not None]
    run10 = col("run10")
    return (f"| {label} | {len(rows)} | {pct(statistics.median(run10)) if run10 else '—'} | "
            f"{sum(x > 0 for x in run10) / len(run10):.0%} | "
            f"{pct(statistics.median(col('run5')))} | {pct(statistics.median(col('gap')))} | "
            f"{pct(statistics.median(col('day')))} | "
            f"{sum(x > 0 for x in col('day')) / len(col('day')):.0%} | "
            f"{pct(statistics.median(col('post5')))} | {pct(statistics.median(col('post20')))} |")


def main():
    api = Alpaca()
    end = datetime.now(ET) - timedelta(days=1)
    start = end - timedelta(days=365 * YEARS + 40)
    events = {}
    for sym in SYMBOLS:
        events[sym] = earnings_events(api, sym, start, end)
        print(f"{sym}: {len(events[sym])} earnings", flush=True)
    bars = daily(api, SYMBOLS + ["SPY"], start - timedelta(days=30), end)
    rows = []
    for sym, evs in events.items():
        for react, headline, surprise in evs:
            m = measure(bars.get(sym, []), bars["SPY"], react)
            if m:
                rows.append({**m, "sym": sym, "surprise": surprise, "headline": headline})
    hot = [r for r in rows if r["run10"] is not None and r["run10"] > 0.05]
    cold = [r for r in rows if r["run10"] is not None and r["run10"] < -0.05]
    lines = [f"# Pre-earnings run-up — {len(rows)} reports, {len(SYMBOLS)} large caps, "
             f"last {YEARS} years", "",
             "All returns are excess vs SPY over the same window. run-up = close 11 days before "
             "the reaction day → close the day before; gap = prior close → reaction-day open; "
             "day = prior close → reaction-day close.", "",
             "| group | n | run-up 10d (median) | run-up > 0 | run-up 5d | gap | reaction day | "
             "reaction > 0 | +5d after | +20d after |",
             "|---|---|---|---|---|---|---|---|---|---|",
             summarize(rows, "all"),
             summarize([r for r in rows if r["surprise"] == "beat"], "EPS beat"),
             summarize([r for r in rows if r["surprise"] == "miss"], "EPS miss"),
             summarize(hot, "ran up > 5% into it") if hot else "",
             summarize(cold, "fell > 5% into it") if cold else "",
             "", "## By stock (median 10-day run-up / reaction day)", "",
             "| stock | n | run-up 10d | reaction day | events with run-up>0 and reaction<0 |",
             "|---|---|---|---|---|"]
    by = defaultdict(list)
    for r in rows:
        by[r["sym"]].append(r)
    for sym, rs in sorted(by.items(), key=lambda kv: -statistics.median(
            [r["run10"] for r in kv[1] if r["run10"] is not None] or [0])):
        run = [r["run10"] for r in rs if r["run10"] is not None]
        day = [r["day"] for r in rs if r["day"] is not None]
        snl = sum(1 for r in rs if r["run10"] and r["day"] and r["run10"] > 0 > r["day"])
        lines.append(f"| {sym} | {len(rs)} | {pct(statistics.median(run)) if run else '—'} | "
                     f"{pct(statistics.median(day)) if day else '—'} | {snl} |")
    lines += ["", "## Every event", "", "| reaction day | stock | surprise | run-up 10d | gap | day | +20d |",
              "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["react"]):
        lines.append(f"| {r['react']} | {r['sym']} | {r['surprise']} | {pct(r['run10'])} | "
                     f"{pct(r['gap'])} | {pct(r['day'])} | {pct(r['post20'])} |")
    text = "\n".join(lines) + "\n"
    out = journal.ROOT / "journal" / "research"
    out.mkdir(parents=True, exist_ok=True)
    (out / "RUNUP.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
