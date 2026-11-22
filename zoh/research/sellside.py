"""The other side of our own trades: selling SPY same-day options instead of buying them
(SUNDAY_TESTS 82, owner 2026-11-20: "if I want to find the gold mine, what methods do you have?").

Every session since 2024-02: at 10:00 a credit spread on each side of SPY. Sell the same-day
option whose delta (from the implied vol of its own 10:00 price) is nearest 0.30, buy the one five
points further out. Out at 15:45, or earlier when buying the spread back costs twice the credit.
Defined risk only: the worst case is the width minus the credit.

Prices are 1-minute option bar closes (trades, not quotes). Costs are a share of each leg's price
each way, at least one cent a leg; "none" is the trade price both ways. Reported per spread,
without the best five and without the worst five (a seller's risk sits in the worst days), by
rising and falling months (SPY's close the evening before against 22 sessions earlier), by year,
by month, and as a $5,000 account doing one spread a side a day next to SPY held.

    python -m zoh.research.sellside --cache DIR      # DIR keeps one pickle a day; a rerun is offline
"""
import argparse
import json
import math
import pickle
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from .. import journal
from ..alpaca import DATA_URL, Alpaca
from ..realopt import implied_vol, last_day, occ
from ..strategy import ET, bs_delta

START = date(2024, 2, 1)
RECENT_DAYS = 63                 # the last three months lead
ENTRY, EXIT = 600, 945           # minutes after midnight: 10:00 and 15:45
TARGET, WIDTH, STOP = 0.30, 5, 2.0
REACH = 15                       # strikes fetched each side of the money
Y = 252 * 390
ACCOUNT = 5000.0
# label -> (share of the price each way, least cost a leg in dollars)
COSTS = {"10%": (0.10, 0.01), "5%": (0.05, 0.01), "2%": (0.02, 0.01), "a cent a leg": (0.0, 0.01),
         "none": (0.0, 0.0)}
DIR = journal.ROOT / "journal" / "research"


def sell(price, cost):
    share, least = cost
    return max(min(price * (1 - share), price - least), 0.0)


def buy(price, cost):
    share, least = cost
    return max(price * (1 + share), price + least)


def spread_result(short, long_, ps, pl, start, cost, stop=STOP, width=WIDTH, end=EXIT):
    """One credit spread from minute closes. short and long_ map minute -> close after the entry;
    ps and pl are the entry prices. Returns None when the costs leave no credit, else
    {credit, back, minute, why, pnl, risk} in dollars per share (pnl and risk per contract)."""
    credit = sell(ps, cost) - buy(pl, cost)
    if credit <= 0.02:
        return None
    cs, cl, out = ps, pl, None
    for m in range(start + 1, end + 1):
        cs, cl = short.get(m, cs), long_.get(m, cl)
        back = min(max(buy(cs, cost) - sell(cl, cost), 0.0), width)
        if stop and m in short and back >= stop * credit:
            out = (m, back, "stop")
            break
    if out is None:
        back = min(max(buy(cs, cost) - sell(cl, cost), 0.0), width)
        out = (end, back, "time")
    return {"credit": round(credit, 3), "back": round(out[1], 3), "minute": out[0], "why": out[2],
            "pnl": round((credit - out[1]) * 100, 1), "risk": round((width - credit) * 100, 1)}


def nearest_delta(quotes, kind, target=TARGET):
    """quotes: [(strike, price, spot, minute)] of out-of-the-money contracts at the entry. The one
    whose |delta| is nearest the target, as (strike, delta), or None."""
    best = None
    for strike, price, spot, minute in quotes:
        years = (960 - minute) / Y
        iv = implied_vol(price, spot, strike, years, kind) if price > 0 else None
        if not iv:
            continue
        delta = abs(bs_delta(spot, strike, years, iv, kind))
        if best is None or abs(delta - target) < abs(best[1] - target):
            best = (strike, delta)
    return best


def day_spread(day, kind, opt, spot, cost, stop=STOP, target=TARGET, width=WIDTH):
    """The spread of one side on one day. opt: {contract: [(minute, close)]}; spot: {minute: close}."""
    s0 = spot.get(ENTRY) or next((spot[m] for m in sorted(spot) if m >= ENTRY), None)
    if not s0:
        return None

    def first(sym):
        return next(((m, c) for m, c in opt.get(sym, []) if ENTRY <= m <= ENTRY + 5), None)

    strikes = (range(math.floor(s0) + 1, math.floor(s0) + 11) if kind == "call"
               else range(math.ceil(s0) - 10, math.ceil(s0)))
    quotes = []
    for k in strikes:
        b = first(occ("SPY", day, k, kind))
        if b:
            quotes.append((k, b[1], spot.get(b[0], s0), b[0]))
    pick = nearest_delta(quotes, kind, target)
    if not pick:
        return None
    ks, delta = pick
    kl = ks + width if kind == "call" else ks - width
    short_sym, long_sym = occ("SPY", day, ks, kind), occ("SPY", day, kl, kind)
    bs, bl = first(short_sym), first(long_sym)
    if not bl:  # the far leg may not print in those five minutes: its last print before them
        bl = next(((m, c) for m, c in reversed(opt.get(long_sym, [])) if m < ENTRY), None)
    if not bl:
        return None
    start = max(bs[0], bl[0])
    r = spread_result(dict(opt.get(short_sym, [])), dict(opt.get(long_sym, [])), bs[1], bl[1], start,
                      cost, stop, width)
    if not r:
        return None
    open_ = spot[min(spot)]
    return {"day": day.isoformat(), "kind": kind, "short": ks, "long": kl, "delta": round(delta, 3),
            "move10": round(s0 / open_ - 1, 5), **r}


# --- data ------------------------------------------------------------------------------------------

def spy_minutes(api, cache, end):
    f = cache / "spy_min.pkl"
    days = pickle.loads(f.read_bytes()) if f.exists() else {}
    cur = max(days) + timedelta(days=1) if days else START
    while cur <= end:
        nxt = min(cur + timedelta(days=45), end + timedelta(days=1))
        for b in api.stock_bars("SPY", datetime(cur.year, cur.month, cur.day, 4, tzinfo=ET),
                                datetime(nxt.year, nxt.month, nxt.day, 3, tzinfo=ET), feed="sip"):
            t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
            m = t.hour * 60 + t.minute
            if 570 <= m < 960:
                days.setdefault(t.date(), []).append((m, b["o"], b["h"], b["l"], b["c"]))
        cur = nxt
    f.write_bytes(pickle.dumps(days))
    return days


def option_day(api, cache, day, s0):
    """{contract: [(minute, o, h, l, c, v)]} for the strikes around the money, cached by day."""
    f = cache / f"{day}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())["bars"]
    syms = [occ("SPY", day, k, "call") for k in range(math.floor(s0) - 1, math.floor(s0) + REACH + 1)]
    syms += [occ("SPY", day, k, "put") for k in range(math.ceil(s0) - REACH, math.ceil(s0) + 2)]
    params = {"symbols": ",".join(syms), "timeframe": "1Min", "start": f"{day}T13:55:00Z",
              "end": f"{day + timedelta(days=1)}T00:00:00Z", "limit": 10000}
    out = {}
    while True:
        page = api._request("GET", f"{DATA_URL}/v1beta1/options/bars", params) or {}
        for sym, bars in (page.get("bars") or {}).items():
            for b in bars:
                t = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)
                m = t.hour * 60 + t.minute
                if t.date() == day and 595 <= m < 960:
                    out.setdefault(sym, []).append((m, b["o"], b["h"], b["l"], b["c"], b["v"]))
        if not page.get("next_page_token"):
            break
        params["page_token"] = page["next_page_token"]
    f.write_bytes(pickle.dumps({"spot10": s0, "bars": out}))
    return out


def collect(api, cache, log=print):
    cache.mkdir(parents=True, exist_ok=True)
    spy = spy_minutes(api, cache, last_day())
    days = sorted(spy)
    close = {d: spy[d][-1][4] for d in days}
    rows = {label: [] for label in COSTS}
    hold = []
    for i, day in enumerate(days):
        at10 = [b for b in spy[day] if b[0] >= ENTRY]
        if not at10:
            continue
        bars = option_day(api, cache, day, at10[0][1])
        opt = {s: [(b[0], b[4]) for b in v] for s, v in bars.items()}
        spot = {b[0]: b[4] for b in spy[day]}
        spot[ENTRY] = at10[0][1]
        rising = close[days[i - 1]] > close[days[i - 22]] if i >= 22 else None
        for kind in ("call", "put"):
            for label, cost in COSTS.items():
                r = day_spread(day, kind, opt, spot, cost)
                if r:
                    rows[label].append({**r, "rising": rising})
            r = day_spread(day, kind, opt, spot, COSTS["a cent a leg"], stop=None)
            if r:
                hold.append({**r, "rising": rising})
        if i % 100 == 0:
            log(f"{day}: {len(rows['none'])} spreads", flush=True)
    return {"through": days[-1].isoformat(), "days": len(days), "rows": rows, "hold": hold,
            "spy": {d.isoformat(): close[d] for d in days}}


# --- report ----------------------------------------------------------------------------------------

def versions(rows):
    against = [r for r in rows if (r["kind"] == "call") == (r["move10"] > 0)]
    return {"(a) both sides, every day": rows,
            "(b) only the side against the 10:00 move": against,
            "the side with the 10:00 move": [r for r in rows if r not in against],
            "(c) days within 0.5% of the open at 10:00": [r for r in rows if abs(r["move10"]) < 0.005]}


def summary(rows):
    if not rows:
        return None
    p = sorted(r["pnl"] for r in rows)
    months = defaultdict(float)
    for r in rows:
        months[r["day"][:7]] += r["pnl"]
    worst = min(months, key=months.get)
    cut = lambda xs: round(statistics.mean(xs), 1) if xs else None  # noqa: E731
    return {"n": len(p), "win": round(sum(x > 0 for x in p) / len(p), 3), "avg": cut(p),
            "risk": cut([r["risk"] for r in rows]),
            "no_best5": cut(p[:-5]) if len(p) > 10 else None, "no_worst5": cut(p[5:]) if len(p) > 10 else None,
            "stopped": round(sum(r["why"] == "stop" for r in rows) / len(p), 3), "worst": p[0],
            "months": len(months), "months_up": sum(v > 0 for v in months.values()),
            "month_avg": round(statistics.mean(months.values())), "worst_month": worst,
            "worst_month_pnl": round(months[worst])}


def account(rows, spy):
    """One spread a side a day from $5,000, stopping when the account cannot cover the width."""
    by_day = defaultdict(float)
    for r in rows:
        by_day[r["day"]] += r["pnl"]
    eq, peak, fall, ended = ACCOUNT, ACCOUNT, 0.0, None
    for d in sorted(by_day):
        if eq < WIDTH * 100 * 2:
            ended = d
            break
        eq += by_day[d]
        peak = max(peak, eq)
        fall = min(fall, eq / peak - 1)
    first, last = min(by_day), max(by_day)
    years = (date.fromisoformat(last) - date.fromisoformat(first)).days / 365.25
    held = [v for d, v in sorted(spy.items()) if first <= d <= last]
    top, spy_fall = 0.0, 0.0
    for v in held:
        top = max(top, v)
        spy_fall = min(spy_fall, v / top - 1)
    return {"end": round(eq), "per_year": round((max(eq, 1) / ACCOUNT) ** (1 / years) - 1, 3),
            "worst_fall": round(fall, 3), "out_of_money_on": ended,
            "spy_per_year": round((held[-1] / held[0]) ** (1 / years) - 1, 3), "spy_worst_fall": round(spy_fall, 3)}


def money(x):
    return "-" if x is None else f"{'-' if x < 0 else '+'}${abs(x):,.1f}" if isinstance(x, float) else f"{'-' if x < 0 else '+'}${abs(x):,}"


def report(data):
    rows, spy = data["rows"], data["spy"]
    days = sorted(spy)
    recent = days[-RECENT_DAYS]
    lines = ["# The selling side: SPY same-day credit spreads (SUNDAY_TESTS 82)", "",
             f"Every session {days[0]} to {data['through']} ({data['days']} days). At 10:00 sell the same-day SPY "
             f"option nearest {TARGET:.2f} delta and buy the one {WIDTH} points further out, on each side; out at "
             f"15:45 or when buying it back costs {STOP:g} times the credit. Real 1-minute option bars; dollars per "
             f"spread (one contract a leg; the most a spread can lose is about ${summary(rows['none'])['risk']:.0f}). "
             "`python -m zoh.research.sellside`.", "",
             "## What the cost assumption does", "",
             "| cost each leg, each way | spreads | win | per spread | without best 5 | without worst 5 | stopped | "
             "last 3 months | rising months | falling months | months up |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    out = {"through": data["through"], "days": data["days"], "costs": {}}
    for label, rs in rows.items():
        s = summary(rs)
        cut = {k: summary([r for r in rs if f(r)]) for k, f in (
            ("recent", lambda r: r["day"] >= recent), ("rising", lambda r: r["rising"]),
            ("falling", lambda r: r["rising"] is False))}
        out["costs"][label] = {"all": s, **cut, "versions": {k: summary(v) for k, v in versions(rs).items()},
                               "years": {y: summary([r for r in rs if r["day"][:4] == y]) for y in ("2024", "2025", "2026")},
                               "account": account(rs, spy)}
        lines.append(f"| {label} | {s['n']} | {s['win']:.0%} | {money(s['avg'])} | {money(s['no_best5'])} | "
                     f"{money(s['no_worst5'])} | {s['stopped']:.0%} | {money(cut['recent']['avg'])} | "
                     f"{money(cut['rising']['avg'])} | {money(cut['falling']['avg'])} | {s['months_up']} of {s['months']} |")
    lines += ["", "The bar was written at 10% (5% as a bracket). A cent a leg is what a SPY same-day option's "
              "quote usually costs to cross; `none` is the trade price both ways, which nobody gets.", ""]
    for label in ("10%", "5%", "a cent a leg", "none"):
        c = out["costs"][label]
        lines += [f"## Cost: {label}", "",
                  "| version | spreads | win | per spread | without best 5 | without worst 5 | worst month | "
                  "average month |", "|---|---|---|---|---|---|---|---|"]
        for name, s in c["versions"].items():
            lines.append(f"| {name} | {s['n']} | {s['win']:.0%} | {money(s['avg'])} | {money(s['no_best5'])} | "
                         f"{money(s['no_worst5'])} | {s['worst_month']} {money(s['worst_month_pnl'])} | "
                         f"{money(s['month_avg'])} |")
        a = c["account"]
        lines += ["", "By year, both sides: " + ", ".join(
            f"{y} {money(s['avg'])} ({s['n']})" for y, s in c["years"].items() if s) + ".",
            f"As a ${ACCOUNT:,.0f} account, one spread a side a day: ends at ${a['end']:,}"
            + (f" (it could no longer cover a spread on {a['out_of_money_on']})" if a["out_of_money_on"] else
               f", {a['per_year']:+.1%} a year, worst fall {a['worst_fall']:.0%}")
            + f"; SPY held over the same span {a['spy_per_year']:+.1%} a year, worst fall {a['spy_worst_fall']:.0%}.", ""]
    lines += ["## The bar", "",
              "Written before the run: positive after costs over the whole span and over the last 3 months, in "
              "rising and in falling months, every calendar year above zero, and the worst month no worse than "
              "three average months of gain. Version (a):", "",
              "| cost | whole span | last 3 months | rising | falling | every year | worst month | met |",
              "|---|---|---|---|---|---|---|---|"]
    for label, c in out["costs"].items():
        s = c["all"]
        checks = [s["avg"] > 0, c["recent"]["avg"] > 0, c["rising"]["avg"] > 0, c["falling"]["avg"] > 0,
                  all(y["avg"] > 0 for y in c["years"].values() if y),
                  s["month_avg"] > 0 and -s["worst_month_pnl"] <= 3 * s["month_avg"]]
        c["bar_met"] = all(checks)
        lines.append(f"| {label} | " + " | ".join("yes" if x else "no" for x in checks)
                     + f" | {'yes' if all(checks) else 'no'} |")
    lines.append("")
    hold = summary(data["hold"])
    out["hold_to_1545"] = hold
    lines += ["## Without the stop", "",
              f"Held to 15:45 whatever happens, a cent a leg: {hold['n']} spreads, {hold['win']:.0%} win, "
              f"{money(hold['avg'])} a spread, {money(hold['no_worst5'])} without the worst five, worst single spread "
              f"{money(hold['worst'])}, worst month {hold['worst_month']} {money(hold['worst_month_pnl'])}. The stop "
              "changes how the losses arrive (many small ones instead of a few near the full width), not the sum.", ""]
    return "\n".join(lines) + "\n", out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory for the daily bar pickles")
    args = ap.parse_args()
    data = collect(Alpaca(), Path(args.cache))
    text, out = report(data)
    (DIR / "SELLSIDE.md").write_text(text)
    (DIR / "sellside.json").write_text(json.dumps(out, indent=1) + "\n")
    print(text)


if __name__ == "__main__":
    main()
