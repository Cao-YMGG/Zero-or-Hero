"""Headline feed for the pre-market and intraday check-ins (Alpaca news = Benzinga, free).

Fetches headlines for the large caps we trade or watch since the prior session's close
(16:00 ET of the previous trading day, or since `--hours` ago) and writes:
  journal/news/YYYY-MM-DD.json  every headline, newest first, with a rating-change tag
  journal/news/LATEST.md        the same as a readable table (ratings first)

Rating changes ("X Upgrades Y to Buy", "Raises Price Target", ...) are the sniper's most
common catalyst (journal/research/ANALYST.md), and web search often cannot find them on the
day. Roundups that tag many symbols ("Stocks Moving In ...") are dropped.

    python -m zoh.news            # since the previous close
    python -m zoh.news --hours 6
"""
import json
import re
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

from .alpaca import DATA_URL, Alpaca
from .strategy import ET

WATCH = [
    # same-day-expiry mega caps and the scanner universes
    "AAPL", "AMZN", "MSFT", "META", "NVDA", "TSLA", "GOOGL", "AVGO", "AMD", "MU", "INTC", "ARM",
    "ORCL", "NFLX", "CRM", "PLTR", "COIN", "HOOD", "SMCI", "CRDO", "RKLB", "TSM", "ASML",
    "LITE", "CIEN", "WDC", "STX", "SNDK", "GEV", "VST",
    # non-tech mega caps (CLAUDE.md step 2b)
    "JPM", "GS", "BAC", "UNH", "LLY", "XOM", "CVX", "WMT", "COST", "HD", "CAT", "GE", "V",
]
# Other large caps with weekly options: only their upgrades and downgrades are listed. The sniper may be
# named on any of them (CLAUDE.md step 3b) and R4 was measured on them, but on 2026-11-23 Cantor's upgrade
# of TXN was not in the file because TXN was not watched. The same names as research.slowdrift.WIDE less
# the ones above (tests/test_news.py keeps the two lists in step).
RATED_ONLY = [
    "MS", "C", "WFC", "MA", "AXP", "SCHW", "BLK", "COF", "PYPL", "SOFI",
    "JNJ", "ABBV", "MRK", "PFE", "TMO", "ABT", "AMGN", "GILD", "BMY", "CVS", "ISRG", "MRNA",
    "COP", "SLB", "OXY", "HON", "DE", "RTX", "LMT", "BA", "UPS", "FDX",
    "LOW", "TGT", "MCD", "NKE", "SBUX", "DIS", "ABNB", "BKNG", "DASH", "CMG", "LULU", "KO",
    "PEP", "PG", "GM", "F", "RIVN", "NIO", "BABA", "PDD", "JD", "AMAT", "LRCX", "KLAC", "MRVL",
    "TXN", "ADI", "ON", "NOW", "INTU", "PANW", "CRWD", "SNOW", "SHOP", "DELL", "IBM", "CSCO", "NET", "DDOG", "ZS",
    "MDB", "TEAM", "WDAY", "RBLX", "ROKU", "SNAP", "PINS", "SPOT", "CVNA", "APP", "COHR", "MSTR", "T", "VZ",
    "QCOM", "ADBE", "ANET", "UBER",
]
RATED_KINDS = ("upgrade", "downgrade")
MAX_TAGGED = 4  # more symbols than this = a roundup, not news about the stock
ROUNDUP = re.compile(r"stocks moving|movers|mid-day|pre-market session|after-market session|"
                     r"top wall street analyst|what's going on|why is .* (up|down|trading)", re.I)
RATING = re.compile(r"\b(upgrade[sd]?|downgrade[sd]?|initiate[sd]?|reiterate[sd]?|maintains|"
                    r"raises price target|lowers price target|price target to|"
                    r"(raises|cuts|lowers|boosts) (its )?(pt|target))\b", re.I)
OUT = Path(__file__).resolve().parents[1] / "journal" / "news"


def rating_kind(headline):
    h = headline.lower()
    if not RATING.search(h):
        return ""
    if "upgrade" in h:
        return "upgrade"
    if "downgrade" in h:
        return "downgrade"
    if "initiat" in h:
        return "initiate"
    if re.search(r"raises|boosts", h):
        return "target up"
    if re.search(r"lowers|cuts", h):
        return "target down"
    return "rating"


def previous_close(now):
    day = now.date() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return datetime.combine(day, time(16), ET)


def fetch(api, symbols, start, end):
    params = {"symbols": ",".join(symbols), "start": start.isoformat(), "end": end.isoformat(),
              "limit": 50, "sort": "desc", "include_content": "false"}
    items = []
    for page in api._paged(f"{DATA_URL}/v1beta1/news", params, "news"):
        items.extend(page)
        if len(items) >= 500:
            break
    return items


def clean(items, watch):
    seen, rows = set(), []
    for it in items:
        tagged = it.get("symbols") or []
        headline = it.get("headline", "").strip()
        if not headline or it.get("id") in seen or len(tagged) > MAX_TAGGED or ROUNDUP.search(headline):
            continue
        seen.add(it.get("id"))
        t = datetime.fromisoformat(it["created_at"].replace("Z", "+00:00")).astimezone(ET)
        rows.append({"time": t.strftime("%m-%d %H:%M"), "symbols": [s for s in tagged if s in watch] or tagged,
                     "rating": rating_kind(headline), "headline": headline,
                     "source": it.get("source", ""), "url": it.get("url", "")})
    return rows


def rated_only(api, start, end):
    """Upgrades and downgrades on the large caps outside WATCH. Best effort: a failed request costs
    these rows, not the file."""
    items = []
    for k in range(0, len(RATED_ONLY), 15):
        try:
            items += fetch(api, RATED_ONLY[k:k + 15], start, end)
        except Exception as e:  # noqa: BLE001 - the watched names' headlines matter more than these
            print(f"news: rating scan of {RATED_ONLY[k]}... failed: {e}")
    rows = clean(sorted(items, key=lambda it: it.get("created_at", ""), reverse=True), set(RATED_ONLY))
    return [r for r in rows if r["rating"] in RATED_KINDS]


def merge(rows, extra):
    """rows plus the extra ones not already there (a headline tagged with a watched and an unwatched
    name comes back from both pulls), newest first."""
    seen = {(r["time"], r["headline"]) for r in rows}
    out = rows + [r for r in extra if (r["time"], r["headline"]) not in seen]
    return sorted(out, key=lambda r: r["time"], reverse=True)


def markdown(rows, start, now):
    lines = [f"# Headlines since {start:%Y-%m-%d %H:%M} ET (as of {now:%Y-%m-%d %H:%M} ET)", "",
             "Alpaca news (Benzinga). Rating changes first, then everything else, newest first.", "",
             "| time | symbols | rating | headline |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["rating"] == "",)):
        lines.append(f"| {r['time']} | {' '.join(r['symbols'])} | {r['rating']} | "
                     f"{r['headline'].replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def refresh(api=None, start=None, quiet=False):
    """Fetch and write the headline files; returns the rows. The live bot calls this before each
    30-minute journal publish (GitHub's own cron did not fire the News feed workflow on 10-16)."""
    now = datetime.now(ET)
    start = start or previous_close(now)
    api = api or Alpaca()
    items = []
    for k in range(0, len(WATCH), 15):  # keep each request's symbol list short
        items += fetch(api, WATCH[k:k + 15], start, now)
    rows = clean(sorted(items, key=lambda it: it.get("created_at", ""), reverse=True), set(WATCH))
    rows = merge(rows, rated_only(api, start, now))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{now.date()}.json").write_text(json.dumps(
        {"as_of": now.isoformat(timespec="minutes"), "since": start.isoformat(timespec="minutes"),
         "headlines": rows}, indent=1) + "\n")
    (OUT / "LATEST.md").write_text(markdown(rows, start, now))
    ratings = [r for r in rows if r["rating"]]
    print(f"news: {len(rows)} headlines since {start:%m-%d %H:%M}, {len(ratings)} rating changes")
    if not quiet:
        for r in ratings[:20]:
            print(f"  {r['time']} {' '.join(r['symbols'])} [{r['rating']}] {r['headline']}")
    return rows


def main():
    start = None
    if "--hours" in sys.argv:
        start = datetime.now(ET) - timedelta(hours=float(sys.argv[sys.argv.index("--hours") + 1]))
    refresh(start=start)


if __name__ == "__main__":
    main()
