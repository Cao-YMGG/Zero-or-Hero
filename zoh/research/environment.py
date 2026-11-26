"""The market environment in seven readings, written every evening (owner, 2026-11-26: "judge the environment you are
in and notice where it is moving"). The readings describe; what they imply is said in journal/forecasts/ (day, week
and month), and those forecasts are scored (zoh/research/forecasts.py). Nothing here is a rule or a reason to trade.

Readings at the last close, from Alpaca daily bars (split- and dividend-adjusted):
  trend        SPY against its 20-, 50- and 200-day averages, one-month and three-month return, distance from its
               one-year high
  volatility   SPY's realized volatility (annualized) over 10, 20 and 60 sessions and one year; sessions of the last
               20 that moved 1% or more close to close
  breadth      share of the large caps (zoh.news.WATCH + RATED_ONLY) above their 20-, 50- and 200-day averages
  correlation  average pairwise correlation of daily returns, last 20 sessions against the 60 before: the AI chain
               and the 14 sector ETFs (everything moving as one block = a single-stock idea is a market bet, R5)
  leadership   one-week and one-month returns of the 14 ETFs and the cross-asset ETFs; best and worst large caps
  cross_asset  20-day SPY-TLT correlation against the 60 days before (negative = bonds hedge again)
  gaps         SPY gaps of 0.5% or more in the last 10 sessions and how many closed against the gap
Base rates (SPY closes from 2016, plus an optional long-history file for earlier years): on the days whose trend,
volatility and drawdown were near today's (`near`), how often SPY was higher 6 and 24 sessions later, the 10th to 90th
percentile, and how often a close 3% under came within 6 sessions. Context for the forecasts, never a rule.
Changes: which readings crossed a line since the previous file (the "movement" part).

    python -m zoh.research.environment --today [--long SPY_yahoo.json]
"""
import argparse
import json
import math
import statistics as st
from datetime import datetime, timedelta, timezone

from .. import journal

OUT_DIR = journal.JOURNAL_DIR / "environment"
ETFS = ["SPY", "QQQ", "IWM", "DIA", "SMH", "XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "IGV"]
CROSS = ["TLT", "GLD", "USO", "UUP", "VIXY"]
AI_CHAIN = ["NVDA", "AMD", "AVGO", "MU", "TSM", "ORCL", "MRVL", "ARM", "INTC", "LITE", "CIEN", "WDC", "STX", "SNDK",
            "DELL", "AMAT", "LRCX", "KLAC"]
DEFENSIVE, TECH = ["XLP", "XLV", "XLU"], ["SMH", "XLK", "IGV"]
HORIZONS = (6, 24)          # a week from Wednesday to the next Friday; about a month


def sma(closes, n):
    return sum(closes[-n:]) / n


def ret(closes, n):
    return closes[-1] / closes[-1 - n] - 1


def returns(closes):
    return [b / a - 1 for a, b in zip(closes, closes[1:])]


def realized_vol(rets, n):
    return st.pstdev(rets[-n:]) * math.sqrt(252)


def trend(closes):
    return {"close": round(closes[-1], 2),
            "vs_20d": round(closes[-1] / sma(closes, 20) - 1, 4),
            "vs_50d": round(closes[-1] / sma(closes, 50) - 1, 4),
            "vs_200d": round(closes[-1] / sma(closes, 200) - 1, 4),
            "ret_1m": round(ret(closes, 21), 4), "ret_3m": round(ret(closes, 63), 4),
            "from_1y_high": round(closes[-1] / max(closes[-252:]) - 1, 4)}


def volatility(closes):
    r = returns(closes)
    return {"vol_10d": round(realized_vol(r, 10), 4), "vol_20d": round(realized_vol(r, 20), 4),
            "vol_60d": round(realized_vol(r, 60), 4), "vol_1y": round(realized_vol(r, 252), 4),
            "big_days_20": sum(1 for x in r[-20:] if abs(x) >= 0.01),
            "big_day_share_1y": round(sum(1 for x in r[-252:] if abs(x) >= 0.01) / 252, 3)}


def breadth(closes_by_symbol):
    """Share of the symbols above each average; symbols with too short a history are left out."""
    out = {}
    for n in (20, 50, 200):
        names = [c for c in closes_by_symbol.values() if len(c) >= n]
        out[f"above_{n}d"] = round(sum(1 for c in names if c[-1] > sma(c, n)) / len(names), 3) if names else None
    out["names"] = len(closes_by_symbol)
    return out


def avg_corr(return_lists, last, skip=0):
    """Average pairwise correlation over `last` returns ending `skip` returns before the end."""
    cut = [r[len(r) - skip - last:len(r) - skip] for r in return_lists if len(r) >= last + skip]
    vals = []
    for i in range(len(cut)):
        for j in range(i + 1, len(cut)):
            if st.pstdev(cut[i]) and st.pstdev(cut[j]):
                vals.append(st.correlation(cut[i], cut[j]))
    return round(sum(vals) / len(vals), 3) if vals else None


def gaps(opens, closes, n=10, min_gap=0.005):
    """SPY gaps of `min_gap` or more in the last n sessions, and how many closed against the gap."""
    seen = against = 0
    for k in range(1, n + 1):
        gap = opens[-k] / closes[-k - 1] - 1
        if abs(gap) >= min_gap:
            seen += 1
            against += (closes[-k] / opens[-k] - 1) * gap < 0
    return {"sessions": n, "gaps": seen, "closed_against": against}


def near(now):
    """States like `now`: within 3 points of its distance from the 200-day and of its one-month return, 20-day
    volatility within a quarter below to a third above, within 4 points of its distance from the one-year high."""
    def test(s):
        return (abs(s["vs_200d"] - now["vs_200d"]) <= 0.03 and abs(s["ret_1m"] - now["ret_1m"]) <= 0.03
                and now["vol_20d"] * 0.75 <= s["vol_20d"] <= now["vol_20d"] * 1.33
                and abs(s["from_1y_high"] - now["from_1y_high"]) <= 0.04)
    return test


def state_at(closes, t):
    window = closes[:t + 1]
    r = returns(window[-21:])
    return {"vs_200d": window[-1] / sma(window, 200) - 1, "ret_1m": window[-1] / window[-22] - 1,
            "vol_20d": st.pstdev(r[-20:]) * math.sqrt(252), "from_1y_high": window[-1] / max(window[-252:]) - 1}


def quantile(values, p):
    v = sorted(values)
    return v[min(len(v) - 1, int(p * len(v)))]


def base_rates(dates, closes, condition, horizons=HORIZONS):
    """Forward returns from the days whose state meets `condition`; episodes start after 10 sessions without one."""
    idx = [t for t in range(260, len(closes)) if condition(state_at(closes, t))]
    episodes, last = [], -99
    for t in idx:
        if t - last > 10:
            episodes.append(t)
        last = t
    out = {"days": len(idx), "episodes": len(episodes), "first": dates[idx[0]] if idx else None,
           "last": dates[idx[-1]] if idx else None}
    for h in horizons:
        fwd = [closes[t + h] / closes[t] - 1 for t in idx if t + h < len(closes)]
        ep = [closes[t + h] / closes[t] - 1 for t in episodes if t + h < len(closes)]
        out[f"h{h}"] = None if not fwd else {
            "n": len(fwd), "up": round(sum(1 for x in fwd if x > 0) / len(fwd), 3),
            "median": round(quantile(fwd, 0.5), 4), "p10": round(quantile(fwd, 0.1), 4),
            "p90": round(quantile(fwd, 0.9), 4),
            "episodes_up": round(sum(1 for x in ep if x > 0) / len(ep), 3) if ep else None}
    drop = [min(closes[t + 1:t + 7]) / closes[t] - 1 for t in idx if t + 6 < len(closes)]
    out["close_3pct_under_within_6"] = round(sum(1 for x in drop if x <= -0.03) / len(drop), 3) if drop else None
    return out


def label_zh(r):
    """One plain-Chinese line from fixed thresholds, the same words for the same numbers every evening."""
    t, v, c, lead = r["trend"], r["volatility"], r["correlation"], r["leadership"]
    if t["vs_200d"] < 0 and t["ret_1m"] <= -0.04:
        parts = ["回调中（在 200 日均线下方，一个月跌 {:.0%}）".format(-t["ret_1m"])]
    elif t["vs_200d"] > 0 and t["ret_1m"] >= 0.02:
        parts = ["上升中（在 200 日均线上方，一个月涨 {:.0%}）".format(t["ret_1m"])]
    else:
        parts = ["没有明显方向"]
    ratio = v["vol_20d"] / v["vol_1y"] if v["vol_1y"] else 1
    parts.append("颠簸很大（波动是一年平均的 {:.1f} 倍）".format(ratio) if ratio >= 1.5
                 else "很平静" if ratio <= 0.8 else "颠簸正常")
    if c.get("ai_20d") is not None and c["ai_20d"] >= 0.75:
        parts.append("AI 股一起涨一起跌")
    d1m, t1m = lead.get("defensive_1m"), lead.get("tech_1m")
    if d1m is not None and t1m is not None:
        if d1m - t1m >= 0.05:
            parts.append("钱躲进防守股")
        elif t1m - d1m >= 0.05:
            parts.append("钱在追科技股")
    if r["cross_asset"].get("spy_tlt_20d") is not None and r["cross_asset"]["spy_tlt_20d"] < 0:
        parts.append("股债反着走")
    g = r["gaps"]
    if g["gaps"] >= 3 and g["closed_against"] / g["gaps"] >= 0.6:
        parts.append("开盘方向常被盘中反过来")
    return "，".join(parts) + "。"


LINES = [  # (what, how to read it from a reading, the plain-Chinese name of the state when true)
    ("above_200d", lambda r: r["trend"]["vs_200d"] > 0, "标普在 200 日均线上方"),
    ("vol_high", lambda r: r["volatility"]["vol_20d"] >= 1.5 * r["volatility"]["vol_1y"], "波动是一年平均的 1.5 倍以上"),
    ("breadth_50", lambda r: (r["breadth"]["above_50d"] or 0) >= 0.5, "一半以上的大盘股在 50 日均线上方"),
    ("ai_lockstep", lambda r: (r["correlation"]["ai_20d"] or 0) >= 0.7, "AI 股一起涨一起跌（同步程度 0.7 以上）"),
    ("defensive_lead", lambda r: (r["leadership"]["defensive_1w"] or 0) > (r["leadership"]["tech_1w"] or 0),
     "这一周防守股跑赢科技股"),
    ("bonds_hedge", lambda r: (r["cross_asset"]["spy_tlt_20d"] or 0) < 0, "股债反着走"),
]


def changes(prev, cur):
    """The readings that crossed a line since the previous file, in plain Chinese."""
    if not prev:
        return []
    out = []
    for _key, test, name in LINES:
        try:
            a, b = test(prev), test(cur)
        except (KeyError, TypeError):
            continue
        if a != b:
            out.append(("变成：" if b else "不再：") + name)
    return out


def reading(bars, dates_spy, long_dates=None, long_closes=None):
    """bars: {symbol: [(date, open, close)]} ending at the same last session. Returns the reading dict."""
    closes = {s: [c for _, _, c in v] for s, v in bars.items()}
    spy, spy_open = closes["SPY"], [o for _, o, _ in bars["SPY"]]
    rets = {s: returns(c) for s, c in closes.items()}
    stocks = {s: c for s, c in closes.items() if s not in ETFS and s not in CROSS}
    lead = {s: {"ret_1w": round(ret(c, 5), 4), "ret_1m": round(ret(c, 21), 4)}
            for s, c in closes.items() if s in ETFS + CROSS and len(c) > 22}
    ranked = sorted((round(ret(c, 21), 4), s) for s, c in stocks.items() if len(c) > 22)
    mean = lambda xs: round(sum(xs) / len(xs), 4) if xs else None
    r = {"date": dates_spy[-1],
         "trend": trend(spy), "volatility": volatility(spy), "breadth": breadth(stocks),
         "correlation": {"ai_20d": avg_corr([rets[s] for s in AI_CHAIN if s in rets], 20),
                         "ai_60d_before": avg_corr([rets[s] for s in AI_CHAIN if s in rets], 60, 20),
                         "etf_20d": avg_corr([rets[s] for s in ETFS if s in rets], 20),
                         "etf_60d_before": avg_corr([rets[s] for s in ETFS if s in rets], 60, 20)},
         "leadership": {"etfs": lead,
                        "defensive_1w": mean([lead[s]["ret_1w"] for s in DEFENSIVE if s in lead]),
                        "defensive_1m": mean([lead[s]["ret_1m"] for s in DEFENSIVE if s in lead]),
                        "tech_1w": mean([lead[s]["ret_1w"] for s in TECH if s in lead]),
                        "tech_1m": mean([lead[s]["ret_1m"] for s in TECH if s in lead]),
                        "best_1m": [[s, v] for v, s in ranked[-5:][::-1]],
                        "worst_1m": [[s, v] for v, s in ranked[:5]]},
         "cross_asset": {"spy_tlt_20d": avg_corr([rets["SPY"], rets["TLT"]], 20) if "TLT" in rets else None,
                         "spy_tlt_60d_before": avg_corr([rets["SPY"], rets["TLT"]], 60, 20) if "TLT" in rets else None},
         "gaps": gaps(spy_open, spy)}
    all_dates, all_closes = list(dates_spy), list(spy)
    if long_dates:
        # earlier years from the long file, scaled to meet the Alpaca series on its first date (returns unchanged)
        pos = {d: i for i, d in enumerate(long_dates)}
        if dates_spy[0] in pos:
            k = pos[dates_spy[0]]
            scale = spy[0] / long_closes[k]
            all_dates = list(long_dates[:k]) + all_dates
            all_closes = [c * scale for c in long_closes[:k]] + all_closes
    now = state_at(all_closes, len(all_closes) - 1)
    r["base_rates"] = {"state": "within 3 points of today's distance from the 200-day and one-month return, 20-day "
                                "volatility from 0.75x to 1.33x today's, within 4 points of today's distance from "
                                "the one-year high",
                       "from": all_dates[0], **base_rates(all_dates[:-1], all_closes[:-1], near(now))}
    r["label_zh"] = label_zh(r)
    return r


def summary_zh(r):
    t, v, b, c = r["trend"], r["volatility"], r["breadth"], r["correlation"]
    lines = [f"【环境 {r['date']}】{r['label_zh']}",
             f"趋势：标普 {t['close']}，离 200 日均线 {t['vs_200d']:+.1%}，一个月 {t['ret_1m']:+.1%}，离一年高点 {t['from_1y_high']:+.1%}。",
             f"颠簸：20 天波动 {v['vol_20d']:.0%}（一年平均 {v['vol_1y']:.0%}），20 天里 {v['big_days_20']} 天涨跌超过 1%。",
             f"广度：{b['above_20d']:.0%} 的大盘股在 20 日均线上方，{b['above_200d']:.0%} 在 200 日均线上方。",
             f"联动：AI 股同步程度 {c['ai_20d']:.2f}（之前 {c['ai_60d_before']:.2f}）。"]
    br = r["base_rates"]
    if br.get("h6") and br.get("h24"):
        lines.append(f"和今天相似的日子（{br['from'][:4]} 年起 {br['days']} 天，{br['episodes']} 段）："
                     f"6 个交易日后上涨 {br['h6']['up']:.0%}（八成在 {br['h6']['p10']:+.1%} 到 {br['h6']['p90']:+.1%}），"
                     f"24 个交易日后上涨 {br['h24']['up']:.0%}（{br['h24']['p10']:+.1%} 到 {br['h24']['p90']:+.1%}）。只是底数，不是规则。")
    for ch in r.get("changes_zh", []):
        lines.append("变化：" + ch)
    return "\n".join(lines)


def previous(day):
    files = sorted(p for p in OUT_DIR.glob("*.json") if p.stem < day)
    return json.loads(files[-1].read_text()) if files else None


def load_long(path):
    """A Yahoo chart JSON (adjusted closes) for the years before 2016; the study's own file, not fetched here."""
    d = json.loads(open(path).read())["chart"]["result"][0]
    dates = [datetime.fromtimestamp(t, timezone.utc).date().isoformat() for t in d["timestamp"]]
    adj = d["indicators"]["adjclose"][0]["adjclose"]
    pairs = [(a, c) for a, c in zip(dates, adj) if c]
    return [a for a, _ in pairs], [c for _, c in pairs]


def fetch(api, end):
    syms = sorted(set(ETFS + CROSS + AI_CHAIN + list(_large_caps())) - {"SPY"})
    out = {}
    for i in range(0, len(syms), 50):
        for s, v in api.daily_bars_multi(syms[i:i + 50], end - timedelta(days=420), end).items():
            out[s] = [(b["t"][:10], b["o"], b["c"]) for b in v]
    spy = api.daily_bars_multi(["SPY"], datetime(2016, 1, 1, tzinfo=timezone.utc), end)["SPY"]
    out["SPY"] = [(b["t"][:10], b["o"], b["c"]) for b in spy]
    return out


def _large_caps():
    from .. import news
    return list(news.WATCH) + list(news.RATED_ONLY)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", action="store_true", help="read the last close and write journal/environment/<date>.json")
    ap.add_argument("--long", help="a Yahoo chart JSON of SPY before 2016 for the base rates (optional)")
    args = ap.parse_args()
    if not args.today:
        ap.error("nothing to do without --today")
    from ..alpaca import Alpaca
    end = datetime.now(timezone.utc) - timedelta(minutes=20)
    bars = fetch(Alpaca(), end)
    last = bars["SPY"][-1][0]
    bars = {s: v for s, v in bars.items() if v and v[-1][0] == last}      # only symbols with today's bar
    dates_spy = [d for d, _, _ in bars["SPY"]]
    long_dates = long_closes = None
    if args.long:
        long_dates, long_closes = load_long(args.long)
    r = reading(bars, dates_spy, long_dates, long_closes)
    r["changes_zh"] = changes(previous(r["date"]), r)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{r['date']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n")
    print(summary_zh(r))


if __name__ == "__main__":
    main()
