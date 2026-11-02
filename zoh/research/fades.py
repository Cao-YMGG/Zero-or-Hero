"""Financing fade and acquirer fade on real option prices (Sunday tests 31 and 38; owner, 2026-11-02:
"today's kind of opportunity was huge": ORCL -5.9% open to close on a $20B stock + notes offering,
MRVL -10.8% as the all-stock buyer of Lumentum; both were in the opportunity list, neither traded).

Events come from the Alpaca (Benzinga) news feed, two years back, for large caps with liquid
weekly options. The company must be the subject of the headline:
- equity: it announces, prices or plans an offering of common stock or convertibles;
- debt: it prices or plans a notes / bond offering;
- acquirer: it agrees to buy another company for >= $5B with stock in the price (all-stock,
  cash-and-stock), or >= $20B in cash.
First qualifying headline per company per day. After 16:00 ET the event belongs to the next
trading day; before 09:30 it is "pre-market" (entries at the 09:31 close, like the live sniper, and
at 10:00); in the session up to 14:30 the entry is two minutes after the headline; later headlines
roll to the next day's pre-market. Stock: gap, open->close, entry->close, next close, SPY alongside,
and whether the stock was already below its open at entry (the live tape gate for a put). Puts at
|delta| 0.15 / 0.25 / 0.40 on the nearest expiry, every exit rule in exits.EXITS plus the live
catalyst rule since 11-01 (half at 3x, trail armed at 1.5x), costs 10% and 5% each way, sold at 15:45
on day one and carried to expiry.

    python -m zoh.research.fades --years 2
"""
import argparse
import json
import re
import time
from datetime import date, datetime, time as dtime, timedelta

from .. import journal
from ..alpaca import DATA_URL, Alpaca, AlpacaError
from ..realopt import at_or_after, daily_raw
from ..strategy import ET, hhmm
from . import exits
from .exits import EXITS, nearest_expiry, price, stats
from .snipers import stock_minutes

OUT = journal.ROOT / "journal" / "research"
exits.DELTAS["fade"] = (0.15, 0.25, 0.40)
EXITS.setdefault("half3_arm1.5", (1.5, 0.4, None, 3.0))
RULES = ("half3_arm1.5", "trail1.5x", "half3_trail", "trail2x", "hold")
PRIORITY = ("equity", "acquirer", "acquirer_cash", "debt")

NAMES = {
    "AAPL": "Apple", "AMZN": "Amazon", "MSFT": "Microsoft", "GOOGL": "Alphabet|Google", "META": "Meta",
    "NVDA": "Nvidia", "TSLA": "Tesla", "AVGO": "Broadcom", "AMD": r"\bAMD\b|Advanced Micro", "MU": "Micron",
    "INTC": "Intel", "ORCL": "Oracle", "CRM": "Salesforce", "NFLX": "Netflix", "PLTR": "Palantir",
    "COIN": "Coinbase", "HOOD": "Robinhood", "SMCI": "Super Micro|Supermicro", "MRVL": "Marvell",
    "ARM": r"\bArm\b", "QCOM": "Qualcomm", "LITE": "Lumentum", "CIEN": "Ciena", "GEV": "GE Vernova",
    "VST": "Vistra", "JPM": "JPMorgan", "GS": "Goldman", "BAC": "Bank of America", "UNH": "UnitedHealth",
    "LLY": "Lilly", "XOM": "Exxon", "CVX": "Chevron", "WMT": "Walmart", "COST": "Costco", "HD": "Home Depot",
    "CAT": "Caterpillar", "GE": "GE Aerospace|General Electric", "V": r"\bVisa\b", "MA": "Mastercard",
    "ADBE": "Adobe", "NOW": "ServiceNow", "UBER": r"\bUber\b", "SNDK": "Sandisk", "WDC": "Western Digital",
    "STX": "Seagate", "DELL": r"\bDell\b", "ANET": "Arista", "CRWV": "CoreWeave", "NBIS": "Nebius",
    "MSTR": r"\bStrategy\b|MicroStrategy", "RKLB": "Rocket Lab", "CRDO": r"\bCredo\b",
    "AMAT": "Applied Materials", "LRCX": "Lam Research", "KLAC": r"\bKLA\b", "BA": "Boeing",
    "DIS": "Disney", "NKE": "Nike", "PFE": "Pfizer", "MRNA": "Moderna", "SBUX": "Starbucks",
}
VERB = re.compile(r"\b(announces?|prices?|priced|pricing|launches|proposed|upsized|files|commences|"
                  r"intends|plans|readies|prepares|weighs|mulls|eyes|explores|exploring|considering|"
                  r"set to|sells?|raises|raising|taps|markets|offers)\b", re.I)
EQUITY = re.compile(r"\b(offering|sale)\b.{0,60}\b(common stock|shares|convertible|equity)\b|"
                    r"\b(common stock|shares|convertible|equity)\b.{0,60}\b(offering|sale)\b|"
                    r"\bconvertible (senior )?notes\b|\bat-the-market\b|\bequity (raise|offering)\b", re.I)
DEBT = re.compile(r"\b(notes?|bonds?|debentures|debt)\b.{0,60}\b(offering|sale|deal|issue)\b|"
                  r"\b(offering|sale|prices?|sells?|raises|issue)\b.{0,60}\b(notes|bonds?|debentures|debt)\b|"
                  r"\bbond (sale|market|deal|issue)\b", re.I)
ACQ = re.compile(r"\b(to acquire|to buy|agrees? to acquire|agrees? to buy|will acquire|acquiring|is buying|"
                 r"buys|acquires|nears deal (to|for)|in (advanced )?talks to (acquire|buy)|takeover of|"
                 r"to merge with|merger with)\b", re.I)
BILLION = re.compile(r"\$\s?(\d+(?:\.\d+)?)\s?(billion|bn|b)\b", re.I)
STOCK_DEAL = re.compile(r"all-stock|all stock|stock deal|in stock|cash-and-stock|stock-and-cash|"
                        r"cash and stock|stock and cash|share deal|all-share|in shares", re.I)
EXCLUDE = re.compile(r"buyback|repurchase|dividend|\betf\b|\bfund\b|secondary offering by|selling (share|stock)holder|"
                     r"exchangeable|tender|redeem|redemption|\bipo\b|spin-?off|stake sale|sell(s|ing)? (its |a )?stake|"
                     r"preferred|analyst|rating|price target|upgrade|downgrade|option|calls|puts|unusual|"
                     r"why .* (stock|shares) (is|are)|what's happening|stock (dips|rises|falls|jumps)", re.I)


def classify(sym, headline):
    """'equity', 'debt', 'acquirer', 'acquirer_cash' or None; the company must be the subject."""
    h = headline.strip()
    if EXCLUDE.search(h):
        return None
    m = re.search(NAMES[sym], h, re.I)
    if not m or m.start() > 45:
        return None
    v = VERB.search(h)
    if v and v.start() < m.start():  # "Meta announces that Nvidia ... will buy shares": Nvidia is not the issuer
        return None
    a = ACQ.search(h)
    if a and m.start() < a.start():
        b = BILLION.search(h)
        size = float(b.group(1)) if b else 0.0
        if size >= 5 and STOCK_DEAL.search(h):
            return "acquirer"
        if size >= 20:
            return "acquirer_cash"
    if EQUITY.search(h) and VERB.search(h):
        return "equity"
    if DEBT.search(h) and VERB.search(h):
        return "debt"
    return None


def headlines(api, symbol, start, end):
    """[(created_at ET, headline)] for one symbol, newest first, all pages."""
    params = {"symbols": symbol, "start": start.isoformat(), "end": end.isoformat(),
              "limit": 50, "sort": "desc", "include_content": "false"}
    out, tries = [], 0
    while True:
        try:
            page = api._request("GET", f"{DATA_URL}/v1beta1/news", params) or {}
        except AlpacaError as e:
            tries += 1
            if tries > 4:
                print(f"news {symbol}: giving up after {e}", flush=True)
                return out
            time.sleep(5 * tries)
            continue
        for it in page.get("news") or []:
            ts = datetime.fromisoformat(it["created_at"].replace("Z", "+00:00")).astimezone(ET)
            out.append((ts, it.get("headline", "")))
        token = page.get("next_page_token")
        if not token:
            return out
        params["page_token"] = token


def schedule(ts, trading_days):
    """(event day, entry label or time) for a headline time: 'pre' for 09:31/10:00 entries."""
    def next_day(d):
        d += timedelta(days=1)
        while d not in trading_days:
            d += timedelta(days=1)
            if d > max(trading_days):
                return None
        return d
    d, t = ts.date(), ts.time()
    if d not in trading_days or t >= dtime(16, 0):
        d = next_day(d) if (d in trading_days or d < max(trading_days)) else None
        return d, "pre"
    if t < dtime(9, 30):
        return d, "pre"
    if t <= dtime(14, 30):
        return d, (ts + timedelta(minutes=2)).time().replace(second=0, microsecond=0)
    return next_day(d), "pre"


def events(api, start, end, trading_days):
    found = {}
    for i, sym in enumerate(NAMES):
        heads = headlines(api, sym, start, end)
        n = 0
        for ts, h in sorted(heads):
            kind = classify(sym, h)
            if not kind:
                continue
            day, entry = schedule(ts, trading_days)
            if not day:
                continue
            key = (sym, day)
            ev = {"sym": sym, "day": day, "kind": kind, "headline": h, "at": ts.strftime("%Y-%m-%d %H:%M"),
                  "entry": entry}
            # one event per company-day: the strongest kind (ORCL 11-02 had the bond headline at 08:02
            # and the $10B stock offering at 08:20), the earliest headline of that kind
            if key not in found:
                found[key] = ev
                n += 1
            elif PRIORITY.index(kind) < PRIORITY.index(found[key]["kind"]):
                found[key] = ev
        print(f"[{i + 1}/{len(NAMES)}] {sym}: {len(heads)} headlines, {n} events", flush=True)
    return sorted(found.values(), key=lambda e: (e["day"], e["sym"]))


def closes_by_day(rows):
    return {d: (o, c) for d, o, c in rows}


def study(api, ev, spy_days, daily):
    sym, day = ev["sym"], ev["day"]
    bars = stock_minutes(api, sym, day)
    if not bars:
        return None
    o = bars[0]["o"]
    close = bars[-1]["c"]
    days = sorted(daily)
    i = days.index(day) if day in days else None
    prev = daily[days[i - 1]][1] if i else None
    month = daily[days[i - 21]][1] if i and i >= 21 else None
    nxt = daily[days[i + 1]][1] if i is not None and i + 1 < len(days) else None
    spy_o, spy_c = spy_days.get(day, (None, None))
    row = {**ev, "day": day.isoformat(), "entry": ev["entry"] if ev["entry"] == "pre" else ev["entry"].strftime("%H:%M"),
           "open": o, "close": close, "prev": prev, "gap": round(o / prev - 1, 4) if prev else None,
           "oc": round(close / o - 1, 4), "next": round(nxt / close - 1, 4) if nxt else None,
           "month": round(prev / month - 1, 4) if prev and month else None,
           "spy_oc": round(spy_c / spy_o - 1, 4) if spy_o else None, "entries": {}}
    labels = [("09:31", hhmm("09:31")), ("10:00", hhmm("09:59"))] if ev["entry"] == "pre" else [("news", ev["entry"])]
    expiry = nearest_expiry(sym, day)
    for label, t in labels:
        b = at_or_after(bars, t, 3)
        if not b:
            continue
        spot = b["c"]
        e = {"t": b["t"].strftime("%H:%M"), "spot": spot, "ec": round(close / spot - 1, 4),
             "against": spot > o, "low_after": round(min(x["l"] for x in bars if x["t"] >= b["t"]) / spot - 1, 4)}
        if expiry:
            r = price(api, sym, day, expiry, (b["t"] + timedelta(minutes=1)).time(), spot, "put", "fade", None)
            if r:
                e["expiry"] = expiry.isoformat()
                e["picks"] = r["picks"]
        row["entries"][label] = e
    return row


def pct(xs):
    return stats([x for x in xs if x is not None])


def report(rows, start, end):
    recent = (end - timedelta(days=91)).isoformat()
    year = (end - timedelta(days=365)).isoformat()
    periods = (("last 3 months", recent), ("last year", year), ("2 years", start.isoformat()))
    L = ["# Financing fade and acquirer fade on real option prices", "",
         f"{start} to {end}, {len(NAMES)} large caps, Alpaca/Benzinga headlines. Puts, costs 10% each way "
         "unless stated. Columns: n | win% | avg | without the best | without the best two. "
         "See zoh/research/fades.py for the rules.", ""]
    kinds = ("equity", "debt", "acquirer", "acquirer_cash")
    L += ["## Stock moves (a win is a fall)", "",
          "| type | period | gap | open->close | 09:31->close | 10:00->close | 10:00->close, below open at 10:00 | news->close | next day |",
          "|---|---|---|---|---|---|---|---|---|"]
    for k in kinds:
        for name, since in periods:
            sel = [r for r in rows if r["kind"] == k and r["day"] >= since]
            if not sel:
                continue
            g = lambda lab, cond=lambda e: True: [-(r["entries"][lab]["ec"]) for r in sel if lab in r["entries"] and cond(r["entries"][lab])]
            L.append(f"| {k} | {name} | {pct([-r['gap'] for r in sel if r['gap'] is not None])} | "
                     f"{pct([-r['oc'] for r in sel])} | "
                     f"{pct(g('09:31'))} | {pct(g('10:00'))} | {pct(g('10:00', lambda e: not e['against']))} | "
                     f"{pct(g('news'))} | {pct([-r['next'] for r in sel if r['next'] is not None])} |")
    L += ["", "## Puts, entry 10:00 (pre-market events) or 2 minutes after the headline, sold 15:45 day one", "",
          "| type | period | delta | " + " | ".join(RULES) + " |", "|---|---|---|" + "---|" * len(RULES)]
    for k in kinds:
        for name, since in periods:
            sel = [r for r in rows if r["kind"] == k and r["day"] >= since]
            for d in exits.DELTAS["fade"]:
                lab = f"d{d:.2f}"
                cells = []
                for rule in RULES:
                    xs = []
                    for r in sel:
                        e = r["entries"].get("10:00") or r["entries"].get("news")
                        if e and lab in e.get("picks", {}):
                            xs.append(e["picks"][lab]["exits_10"][rule])
                    cells.append(pct(xs))
                if any(c != "-" for c in cells):
                    L.append(f"| {k} | {name} | {lab} | " + " | ".join(cells) + " |")
    L += ["", "## Puts carried to expiry (trail2x / hold), same entries", "",
          "| type | period | delta | trail2x | hold |", "|---|---|---|---|---|"]
    for k in kinds:
        for name, since in periods:
            sel = [r for r in rows if r["kind"] == k and r["day"] >= since]
            for d in exits.DELTAS["fade"]:
                lab = f"d{d:.2f}"
                cells = []
                for rule in ("trail2x", "hold"):
                    xs = []
                    for r in sel:
                        e = r["entries"].get("10:00") or r["entries"].get("news")
                        p = e.get("picks", {}).get(lab) if e else None
                        if p:
                            xs.append((p.get("carry_10") or p["exits_10"])[rule])
                    cells.append(pct(xs))
                if any(c != "-" for c in cells):
                    L.append(f"| {k} | {name} | {lab} | " + " | ".join(cells) + " |")
    L += ["", "## Events", "", "| day | sym | type | headline time | entry | gap | open->close | entry->close | below open at entry | d0.25 live rule | headline |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    def f(x, fmt="{:+.1%}"):
        return fmt.format(x) if x is not None else "-"
    for r in rows:
        e = r["entries"].get("10:00") or r["entries"].get("news") or {}
        p = e.get("picks", {}).get("d0.25")
        L.append(f"| {r['day']} | {r['sym']} | {r['kind']} | {r['at']} | {e.get('t', '-')} | {f(r['gap'])} | "
                 f"{f(r['oc'])} | {f(e.get('ec'))} | {('yes' if not e['against'] else 'no') if e else '-'} | "
                 f"{f(p['exits_10']['half3_arm1.5'] if p else None, '{:+.0%}')} | {r['headline'][:90]} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=float, default=2)
    ap.add_argument("--limit", type=int, default=0, help="study only the last N events (smoke test)")
    ap.add_argument("--from-json", action="store_true", help="rebuild FADES.md from fades.json, no API calls")
    a = ap.parse_args()
    end = datetime.now(ET).date() - timedelta(days=1)
    start = end - timedelta(days=int(365 * a.years))
    if a.from_json:
        rows = json.loads((OUT / "fades.json").read_text())
        (OUT / "FADES.md").write_text(report(rows, start, end))
        print(report(rows, start, end)[:5000])
        return
    api = Alpaca()
    spy = closes_by_day(daily_raw(api, "SPY", start - timedelta(days=40), end))
    trading_days = set(spy)
    evs = events(api, datetime.combine(start, dtime(0), ET), datetime.combine(end, dtime(23, 59), ET), trading_days)
    evs = [e for e in evs if e["day"] <= end]
    if a.limit:
        evs = evs[-a.limit:]
    print(f"{len(evs)} events", flush=True)
    (OUT / "fades_events.json").write_text(json.dumps(evs, indent=0, default=str) + "\n")
    rows, dailies = [], {}
    for i, ev in enumerate(evs):
        if ev["sym"] not in dailies:
            dailies[ev["sym"]] = closes_by_day(daily_raw(api, ev["sym"], start - timedelta(days=40), end))  # not past yesterday: the free tier refuses "recent" SIP
        try:
            r = study(api, ev, spy, dailies[ev["sym"]])
        except AlpacaError as e:
            print(f"{ev['day']} {ev['sym']}: {e}", flush=True)
            r = None
        if r:
            rows.append(r)
        print(f"[{i + 1}/{len(evs)}] {ev['day']} {ev['sym']} {ev['kind']} {'ok' if r else 'skip'}", flush=True)
    (OUT / "fades.json").write_text(json.dumps(rows, indent=0, default=str) + "\n")
    (OUT / "FADES.md").write_text(report(rows, start, end))
    print(report(rows, start, end)[:5000])


if __name__ == "__main__":
    main()
