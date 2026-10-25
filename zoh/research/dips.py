"""Buy the dip with longer-dated options (the owner's idea, 2026-10-21) on real option prices.

Signal at a close: a large cap is >= 8% below its 20-day closing high, it has not had a single-day
drop of 6% or more in the last 10 sessions (a crash day is usually its own bad news or earnings),
and it has not signalled in the last 20 sessions. Bought at that close, on the first monthly
expiry 30-60 days out:
  call     ~0.40-delta call
  spread25 the same call minus the next listed strike >= 2.5% higher (debit spread)
  spread5  the same call minus the next listed strike >= 5% higher
  stock    the shares, for comparison
Exits: hold 10 or 20 sessions (closes), or take +50% / stop -50% with a 20-session limit.
Costs: 3% of each option leg each way (liquid long-dated mega-cap options), 10% as a stress
column. Control: the same contracts bought every 15th session per stock without the dip rule.
Daily option closes (Alpaca, 2024-02+); a leg with no bar on a day keeps its last close.

    python -m zoh.research.dips
"""
import json
import statistics
import time
from datetime import date, datetime, timedelta

from .. import journal
from ..alpaca import DATA_URL, Alpaca, AlpacaError
from ..realopt import START, daily_raw, implied_vol, occ
from ..strategy import ET, bs_delta

UNIVERSE = ["META", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "AVGO", "AMD", "MU", "NFLX", "ORCL",
            "CRM", "PLTR", "INTC", "UNH", "LLY", "JPM", "XOM", "WMT", "COST", "V"]
DIP, CRASH, GAP_DAYS = 0.08, -0.06, 20
HOLDS = (10, 20)
SLIPS = (0.03, 0.10)
OUT = journal.ROOT / "journal" / "research"


def third_friday(y, m):
    first = date(y, m, 1)
    return first + timedelta(days=(4 - first.weekday()) % 7 + 14)


def monthly_expiry(day):
    y, m = day.year, day.month
    for _ in range(4):
        e = third_friday(y, m)
        if 30 <= (e - day).days <= 60:
            return e
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return None


def strikes(spot):
    out = set()
    for step in (1, 2.5, 5, 10):
        k = round(spot * 0.97 / step) * step
        while k <= spot * 1.22:
            out.add(round(k, 2))
            k += step
    return sorted(out)


def option_daily(api, symbols, start, end):
    out = {}
    for j in range(0, len(symbols), 100):
        params = {"symbols": ",".join(symbols[j:j + 100]), "timeframe": "1Day",
                  "start": start.isoformat(), "end": end.isoformat(), "limit": 10000}
        while True:
            page = api._request("GET", f"{DATA_URL}/v1beta1/options/bars", params) or {}
            for s, bars in (page.get("bars") or {}).items():
                for b in bars:
                    d = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date()
                    out.setdefault(s, {})[d] = b["c"]
            token = page.get("next_page_token")
            if not token:
                break
            params["page_token"] = token
    return out


def series(prices, path_days, first):
    """Closes along path_days, carrying the last known close forward (from `first`)."""
    out, last = [], first
    for d in path_days:
        last = prices.get(d, last)
        out.append(last)
    return out


def outcomes(entry_cost, values, slip_exit):
    """values[k] = position value at close k+1 (before exit costs); returns P&L per $1."""
    res = {}
    for h in HOLDS:
        v = values[min(h, len(values)) - 1]
        res[f"hold{h}"] = slip_exit(v) / entry_cost - 1
    for tp in (0.5, 1.0):
        r = None
        for v in values[:20]:
            x = slip_exit(v) / entry_cost - 1
            if x >= tp or x <= -0.5:
                r = x
                break
        res[f"tp{int(tp * 100)}_sl50"] = r if r is not None else slip_exit(values[min(20, len(values)) - 1]) / entry_cost - 1
    return {k: round(v, 4) for k, v in res.items()}


def trade(api, sym, day, spot, path_days, closes):
    exp = monthly_expiry(day)
    if not exp:
        return None
    ks = strikes(spot)
    syms = {occ(sym, exp, k, "call"): k for k in ks}
    try:
        px = option_daily(api, list(syms), day, path_days[-1])
    except AlpacaError:
        return None
    years = (exp - day).days / 365
    cands = []
    for s, k in syms.items():
        c0 = px.get(s, {}).get(day)
        if not c0:
            continue
        iv = implied_vol(c0, spot, k, years, "call")
        if iv:
            cands.append((abs(bs_delta(spot, k, years, iv, "call") - 0.40), s, k, c0))
    if not cands:
        return None
    _, s1, k1, c1 = min(cands)
    listed = sorted((k, s) for s, k in syms.items() if px.get(s, {}).get(day))
    row = {"sym": sym, "day": day.isoformat(), "expiry": exp.isoformat(), "spot": spot, "k1": k1, "c1": c1}
    legs = {"call": (s1, None)}
    for name, width in (("spread25", 0.025), ("spread5", 0.05)):
        k2 = next(((k, s) for k, s in listed if k >= k1 * (1 + width)), None)
        if k2:
            legs[name] = (s1, k2[1])
            row[f"k2_{name}"] = k2[0]
    p1 = series(px.get(s1, {}), path_days, c1)
    for slip in SLIPS:
        tag = int(slip * 100)
        for name, (a, b) in legs.items():
            pa = p1
            if b is None:
                cost = c1 * (1 + slip)
                vals = pa
                row[f"{name}_{tag}"] = outcomes(cost, vals, lambda v: (v or 0) * (1 - slip))
            else:
                c2 = px[b][day]
                pb = series(px.get(b, {}), path_days, c2)
                cost = c1 * (1 + slip) - c2 * (1 - slip)
                if cost <= 0.05:
                    continue
                vals = list(zip(pa, pb))
                row[f"{name}_{tag}"] = outcomes(
                    cost, vals, lambda v: max(0.0, (v[0] or 0) * (1 - slip) - (v[1] or 0) * (1 + slip)))
    row["stock"] = outcomes(spot, [closes[d] for d in path_days], lambda v: v)
    return row


def main():
    api = Alpaca()
    end = datetime.now(ET).date() - timedelta(days=1)
    rows = []
    for sym in UNIVERSE:
        days = daily_raw(api, sym, START - timedelta(days=60), end)
        closes = {d: c for d, _, c in days}
        dates = [d for d, _, _ in days]
        last_sig = -999
        n = 0
        for i in range(25, len(dates) - 1):
            day = dates[i]
            if day < START:
                continue
            path_days = dates[i + 1:i + 21]
            if len(path_days) < 10:
                break
            hi = max(closes[dates[j]] for j in range(i - 19, i + 1))
            dip = closes[day] / hi - 1
            crash = min(closes[dates[j]] / closes[dates[j - 1]] - 1 for j in range(i - 9, i + 1))
            kind = None
            if dip <= -DIP and crash > CRASH and i - last_sig >= GAP_DAYS:
                kind, last_sig = "dip", i
            elif i % 15 == 0:
                kind = "control"
            if not kind:
                continue
            r = trade(api, sym, day, closes[day], path_days, closes)
            time.sleep(0.1)
            if r:
                r.update({"kind": kind, "dip": round(dip, 4)})
                rows.append(r)
                n += kind == "dip"
        print(f"{sym}: {n} dips, {len(rows)} rows so far", flush=True)
    (OUT / "dips.json").write_text(json.dumps(rows, indent=0) + "\n")
    (OUT / "DIPS.md").write_text(report(rows, end))
    print(report(rows, end))


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    s = sorted(xs)
    a = lambda v: f"{sum(v) / len(v):+.0%}" if v else "-"
    return f"{len(s)} | {sum(x > 0 for x in s) / len(s):.0%} | {a(s)} | {a(s[:-1])} | {a(s[:-2])} | {statistics.median(s):+.0%}"


def report(rows, end):
    recent = (end - timedelta(days=91)).isoformat()
    year = (end - timedelta(days=365)).isoformat()
    lines = ["# Buying the dip with 30-60 day options (owner's idea, 2026-10-21)", "",
             "Rule and costs in the module docstring (zoh/research/dips.py). Signals at the close; "
             f"data {START} to {end}. Cells: n | win% | avg | without the best | without the best two | median.", ""]
    for kind in ("dip", "control"):
        lines += [f"## {kind}", ""]
        for tag in (3, 10):
            lines += [f"### costs {tag}% of each option leg each way", "",
                      "| instrument | exit | last 3 months | last year | all |", "|---|---|---|---|---|"]
            for inst in ("call", "spread25", "spread5", "stock"):
                key = inst if inst == "stock" else f"{inst}_{tag}"
                if inst == "stock" and tag == 10:
                    continue
                for ex in ("hold10", "hold20", "tp50_sl50", "tp100_sl50"):
                    cells = [stats([r[key][ex] for r in rows if r["kind"] == kind and r["day"] >= cut and key in r])
                             for cut in (recent, year, "")]
                    lines.append(f"| {inst} | {ex} | " + " | ".join(cells) + " |")
            lines.append("")
    dips = [r for r in rows if r["kind"] == "dip"]
    lines += ["## Every dip signal in the last 3 months", "",
              "| day | stock | dip | call hold20 | spread5 hold20 | stock hold20 |", "|---|---|---|---|---|---|"]
    for r in sorted(dips, key=lambda r: r["day"]):
        if r["day"] >= recent:
            def g(k):
                return f"{r[k]['hold20']:+.0%}" if k in r else "-"
            lines.append(f"| {r['day']} | {r['sym']} | {r['dip']:+.1%} | {g('call_3')} | {g('spread5_3')} | {g('stock')} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
