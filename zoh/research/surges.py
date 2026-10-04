"""Why did stocks surge in the last two years? Earnings, M&A, FDA, contracts, policy...?

1. Universe: active, fractionable US common stocks (Alpaca's fractionable flag is a decent
   liquidity filter), excluding ETFs/funds; price >= $5 and median dollar volume >= $10M.
2. Surge days: close-to-close gain >= SURGE_PCT.
3. Cause: headlines from Alpaca news (prior close -> event close), classified by keywords.
4. Tradability: how much of the move was already in the opening gap, and what happened over
   the next 1 / 5 / 20 trading days.
5. Two-year top gainers and how much of their gain came from surge days.

    python -m zoh.research.surges --out journal/research
"""
import argparse
import csv
import math
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..strategy import ET

SURGE_PCT = 0.15
MIN_PRICE = 5.0
MIN_DOLLAR_VOLUME = 10e6
NEWS_PAUSE = 0.32  # stay under 200 requests/minute
MAX_TAGGED_SYMBOLS = 3  # roundups ("20 stocks moving premarket") tag many tickers; skip them
ROUNDUP_WORDS = ("stocks moving", "here are", "movers", "stocks to watch", "mid-day",
                 "biggest gainers", "trading halt")

FUND_WORDS = ("etf", "fund", "trust", "proshares", "direxion", "ishares", "leveraged",
              " 2x", " 3x", "ultra", "bull ", "bear ", "notes", "depositary", "warrant",
              "acquisition corp", "units")

# Checked in order: the first category whose keywords appear in the day's headlines wins.
CATEGORIES = [
    ("M&A", ("to acquire", "acquisition", "acquired by", "merger", "buyout", "takeover",
             "to be acquired", "go private", "take private", "all-cash", "per share in cash")),
    ("FDA / clinical", ("fda", "phase 3", "phase 2", "phase iii", "phase ii", "phase 1",
                        "clinical trial", "topline", "top-line", "pdufa", "data readout",
                        "breakthrough therapy", "medicines agency")),
    ("earnings", ("earnings", "eps", "revenue", "quarter", " q1", " q2", " q3", " q4",
                  "results", "guidance", "beats", "fiscal", "outlook", "raises forecast")),
    ("index inclusion", ("s&p 500", "join the s&p", "added to the s&p", "nasdaq-100",
                         "index inclusion", "russell")),
    ("government / policy", ("government", "pentagon", "department of", "white house", "trump",
                             "tariff", "equity stake", "chips act", "federal", "administration",
                             "defense department", "sanction")),
    ("contract / partnership", ("contract", "partnership", "partner", "agreement", "award",
                                "collaboration", "order", "deal with", "selected by", "supply")),
    ("crypto", ("bitcoin", "crypto", "ethereum", "blockchain", "stablecoin", "token")),
    ("analyst", ("upgrade", "price target", "initiates", "outperform", "overweight",
                 "buy rating", "top pick")),
]


def classify(headlines):
    text = " " + " ".join(headlines).lower()
    if not headlines:
        return "no news found"
    for name, words in CATEGORIES:
        if any(w in text for w in words):
            return name
    return "other news"


def is_fund(asset):
    name = (asset.get("name") or "").lower()
    return any(w in name for w in FUND_WORDS)


def load_universe(api):
    assets = [a for a in api.assets()
              if a.get("tradable") and a.get("fractionable")
              and a.get("exchange") in ("NYSE", "NASDAQ", "AMEX", "ARCA", "BATS")
              and not is_fund(a) and "." not in a["symbol"] and "/" not in a["symbol"]]
    return {a["symbol"]: a.get("name", "") for a in assets}


def load_bars(api, symbols, start, end):
    bars = {}
    symbols = sorted(symbols)
    for i in range(0, len(symbols), 200):
        chunk = symbols[i:i + 200]
        try:
            got = api.daily_bars_multi(chunk, start, end, feed="sip")
        except AlpacaError as e:
            if e.status != 403:
                raise
            got = api.daily_bars_multi(chunk, start, end, feed="iex")
        bars.update(got)
        print(f"bars {min(i + 200, len(symbols))}/{len(symbols)}", flush=True)
    return bars


def day_of(bar):
    return datetime.fromisoformat(bar["t"].replace("Z", "+00:00")).astimezone(ET).date()


def liquid(series):
    dollar = [b["c"] * b["v"] for b in series]
    return statistics.median(dollar) >= MIN_DOLLAR_VOLUME if dollar else False


def find_surges(bars):
    events = []
    for symbol, series in bars.items():
        if len(series) < 60 or not liquid(series):
            continue
        for i in range(1, len(series)):
            prev, cur = series[i - 1], series[i]
            if prev["c"] < MIN_PRICE:
                continue
            gain = cur["c"] / prev["c"] - 1
            if gain < SURGE_PCT:
                continue
            fwd = {n: (series[i + n]["c"] / cur["c"] - 1 if i + n < len(series) else None)
                   for n in (1, 5, 20)}
            events.append({
                "symbol": symbol, "date": day_of(cur).isoformat(),
                "prev_date": day_of(prev).isoformat(), "gain": gain,
                "gap": cur["o"] / prev["c"] - 1,
                "gap_share": (cur["o"] - prev["c"]) / (cur["c"] - prev["c"]),
                "fwd1": fwd[1], "fwd5": fwd[5], "fwd20": fwd[20],
                "run_up20": prev["c"] / series[max(i - 21, 0)]["c"] - 1,
            })
    return sorted(events, key=lambda e: e["date"])


def attach_news(api, events):
    for n, ev in enumerate(events, 1):
        start = datetime.fromisoformat(ev["prev_date"]).replace(hour=16, tzinfo=ET)
        end = datetime.fromisoformat(ev["date"]).replace(hour=16, tzinfo=ET)
        try:
            items = api.news([ev["symbol"]], start, end)
        except AlpacaError as e:
            print(f"news failed {ev['symbol']} {ev['date']}: {e}")
            items = []
        items = [it for it in items if len(it.get("symbols") or []) <= MAX_TAGGED_SYMBOLS
                 and not any(w in it.get("headline", "").lower() for w in ROUNDUP_WORDS)]
        headlines = [it.get("headline", "") for it in items]
        ev["category"] = classify(headlines + [it.get("summary", "") for it in items])
        ev["headline"] = headlines[-1] if headlines else ""  # earliest (sorted desc)
        ev["news_count"] = len(items)
        if n % 100 == 0:
            print(f"news {n}/{len(events)}", flush=True)
        time.sleep(NEWS_PAUSE)


def top_gainers(bars, events, names, k=30):
    by_symbol = defaultdict(list)
    for ev in events:
        by_symbol[ev["symbol"]].append(ev)
    rows = []
    for symbol, series in bars.items():
        if len(series) < 400 or series[0]["c"] < MIN_PRICE or not liquid(series):
            continue
        total = series[-1]["c"] / series[0]["c"] - 1
        log_total = math.log(series[-1]["c"] / series[0]["c"])
        surge_log = sum(math.log(1 + e["gain"]) for e in by_symbol[symbol])
        rows.append({"symbol": symbol, "name": names.get(symbol, ""), "total": total,
                     "surge_days": len(by_symbol[symbol]),
                     "surge_share": surge_log / log_total if log_total > 0 else 0,
                     "top": sorted(by_symbol[symbol], key=lambda e: -e["gain"])[:3]})
    return sorted(rows, key=lambda r: -r["total"])[:k]


def pct(x):
    return "—" if x is None else f"{x:+.0%}"


def med(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def report(events, gainers, start, end, universe_size):
    lines = [f"# 暴涨原因研究 — {start} → {end}", "",
             f"股票池：{universe_size} 只可碎股交易的美股（剔除 ETF/基金），股价 ≥ ${MIN_PRICE:.0f}、"
             f"日成交额中位数 ≥ ${MIN_DOLLAR_VOLUME / 1e6:.0f}M。暴涨日 = 收盘较前收盘涨 ≥ "
             f"{SURGE_PCT:.0%}。原因 = 前一日收盘到当日收盘之间的新闻标题按关键词归类"
             "（按顺序取第一个命中的类别，存在误判）。", "",
             f"共 {len(events)} 次暴涨。", "",
             "## 按原因分类", "",
             "| 原因 | 次数 | 占比 | 当日涨幅中位数 | 开盘跳空占当日涨幅 | 次日 | 5 日后 | 20 日后 | 20 日后仍上涨的比例 |",
             "|---|---|---|---|---|---|---|---|---|"]
    by_cat = defaultdict(list)
    for ev in events:
        by_cat[ev["category"]].append(ev)
    for cat, evs in sorted(by_cat.items(), key=lambda kv: -len(kv[1])):
        f20 = [e["fwd20"] for e in evs if e["fwd20"] is not None]
        lines.append(
            f"| {cat} | {len(evs)} | {len(evs) / len(events):.0%} | {pct(med(e['gain'] for e in evs))} "
            f"| {med(min(max(e['gap_share'], -1), 2) for e in evs):.0%} "
            f"| {pct(med(e['fwd1'] for e in evs))} | {pct(med(e['fwd5'] for e in evs))} "
            f"| {pct(med(f20))} | {sum(x > 0 for x in f20) / len(f20):.0%} |"
            if f20 else f"| {cat} | {len(evs)} | {len(evs) / len(events):.0%} | | | | | | |")
    weekday = Counter(datetime.fromisoformat(e["date"]).strftime("%a") for e in events)
    month = Counter(e["date"][:7] for e in events)
    lines += ["", "## 时间分布", "",
              "按星期：" + "、".join(f"{d} {weekday[d]}" for d in ("Mon", "Tue", "Wed", "Thu", "Fri")),
              "", "暴涨最多的月份：" + "、".join(f"{m}（{c}）" for m, c in month.most_common(6)), "",
              "## 两年涨幅榜（前 30）", "",
              "| 股票 | 名称 | 两年涨幅 | 暴涨日数 | 暴涨日贡献的涨幅占比 | 最大的几次暴涨 |",
              "|---|---|---|---|---|---|"]
    for g in gainers:
        tops = "；".join(f"{e['date']} {e['gain']:+.0%} {e['category']}" for e in g["top"])
        lines.append(f"| {g['symbol']} | {g['name'][:28]} | {g['total']:+,.0%} | {g['surge_days']} "
                     f"| {g['surge_share']:.0%} | {tops} |")
    lines += ["", "## 单日涨幅最大的 40 次", "",
              "| 日期 | 股票 | 当日 | 跳空 | 20 日后 | 原因 | 标题 |", "|---|---|---|---|---|---|---|"]
    for e in sorted(events, key=lambda e: -e["gain"])[:40]:
        lines.append(f"| {e['date']} | {e['symbol']} | {e['gain']:+.0%} | {e['gap']:+.0%} "
                     f"| {pct(e['fwd20'])} | {e['category']} | {e['headline'][:90]} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=float, default=2)
    parser.add_argument("--out", default="journal/research")
    args = parser.parse_args()
    api = Alpaca()
    end = datetime.now(ET).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start = end - timedelta(days=int(365 * args.years))
    names = load_universe(api)
    print(f"universe {len(names)} symbols")
    bars = load_bars(api, list(names), start, end)
    events = find_surges(bars)
    print(f"{len(events)} surge days")
    attach_news(api, events)
    gainers = top_gainers(bars, events, names)
    out = journal.ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    fields = ["date", "symbol", "gain", "gap", "gap_share", "fwd1", "fwd5", "fwd20", "run_up20",
              "category", "news_count", "headline"]
    with (out / "surges.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for ev in events:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v)
                             for k, v in ev.items()})
    text = report(events, gainers, start.date(), end.date(), len(names))
    (out / "SURGES.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
