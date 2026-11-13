"""One virtual $500 ledger per chosen variant, each trading real paper orders (owner, 2026-10-16).

The main ledger (journal/ledger.json) is the account's change since its anchor, and it belongs to
the champion and the snipers. A variant listed in config "ledgers" instead trades from its own
ledger in journal/ledgers.json: equity = base + the real P&L it has booked this generation. Below
`dead` a new generation starts at base the next morning. Its real P&L is moved out of the main
ledger by shifting the main anchor, so the two never count the same dollar.

A ledger pauses its real orders after `pause_after` losses in a row (shadow or real, newest
last) and resumes after the next win; the shadow keeps trading either way.

    "ledgers": {"base": 500, "dead": 50, "risk": 0.2, "one_contract_cap": 0.25,
                "pause_after": 5, "variants": ["meta_follow2", ...]}

A ledger variant may also carry `real_when`, a daily condition judged at the last close before
the session (`real_gate`): on a day it does not hold, the ledger places no real order and its
shadow trades as usual.
"""
import csv
import json
from datetime import date, datetime, timedelta

from . import journal
from .alpaca import AlpacaError
from .strategy import ET

PATH = journal.JOURNAL_DIR / "ledgers.json"
EQUITY_PATH = journal.JOURNAL_DIR / "ledger_equity.csv"
EQUITY_FIELDS = ["date", "variant", "generation", "equity", "real_trades", "paused"]


def load():
    return json.loads(PATH.read_text()) if PATH.exists() else {}


def save(ledgers):
    PATH.write_text(json.dumps(ledgers, indent=2, sort_keys=True) + "\n")


def closes_before(api, symbol, day, days):
    """The last `days` daily closes of `symbol` strictly before `day` (split-adjusted)."""
    start = day - timedelta(days=days * 2 + 20)
    try:
        bars = api.daily_bars_multi([symbol], start, day, feed="sip")
    except AlpacaError:
        bars = api.daily_bars_multi([symbol], start, day, feed="iex")
    out = [b["c"] for b in bars.get(symbol, [])
           if datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date() < day]
    return out[-days:]


def real_gate(api, variant, today):
    """(ok, note): may this ledger variant place real orders today?

    `"real_when": {"symbol": "SMH", "below_average": 20}` means the symbol closed below the average of
    its last 20 closes at the last close before today. No rule: always ok. Bars missing or the request
    failing: not ok, because a shadow-only day costs nothing and a real order on an unknown state does.

    stock_open_drive, 2026-11-13 (journal/research/OPENGATE.md): NVDA/TSLA calls at +0.8% by 10:00 won
    50% after an evening with SMH below its 20-day average and 20% after the others (44 and 51 trades
    on real 0.35-delta prices, 2024-02 to 2026-11; +38% against -56% a trade without the best two), and
    in 2020 to 2023, before the option data, the stock added the 1% the call needs on 44% of such days
    against 35% (231 and 342 signals, the same way in each of the four years). A tilt, not an edge."""
    rule = (variant or {}).get("real_when")
    if not rule:
        return True, ""
    symbol, days = rule["symbol"], int(rule["below_average"])
    day = date.fromisoformat(today) if isinstance(today, str) else today
    if api is None:
        return False, f"no market data for {symbol}"
    try:
        closes = closes_before(api, symbol, day, days)
    except Exception as e:  # a network error here must never stop the session from starting
        return False, f"{symbol} daily bars failed: {e}"
    if len(closes) < days:
        return False, f"only {len(closes)} daily closes for {symbol}"
    average = sum(closes) / days
    ok = closes[-1] < average
    return ok, f"{symbol} closed {closes[-1]:.2f}, {'below' if ok else 'above'} its {days}-day average {average:.2f}"


def members(config):
    return set((config.get("ledgers") or {}).get("variants", []))


def equity(ledgers, vid, cfg):
    led = ledgers.get(vid) or {}
    return cfg.get("base", 500) + led.get("realized", 0.0)


def roll(ledgers, cfg, today):
    """Open a ledger for every listed variant and start a new generation where one died."""
    base, dead = cfg.get("base", 500), cfg.get("dead", 50)
    for vid in cfg.get("variants", []):
        led = ledgers.setdefault(vid, {"generation": 1, "started": today, "realized": 0.0,
                                       "real_trades": 0, "history": []})
        if base + led["realized"] < dead:
            led["history"].append({"generation": led["generation"], "started": led["started"],
                                   "ended": today, "final_equity": round(base + led["realized"], 2),
                                   "real_trades": led["real_trades"]})
            led.update(generation=led["generation"] + 1, started=today, realized=0.0, real_trades=0)
    return ledgers


def losing_streak(trades, vid):
    """Losses in a row at the end of the variant's closed trades (one per entry: the real row
    when there is one, else the shadow). Keyed by contract and entry date: the real fill comes
    seconds after the shadow entry, and keying on the timestamp counted every live trade twice
    (leader_follow showed 7 in a row and was paused on 2026-10-26 when the true streak was 4)."""
    by_entry = {}
    for t in trades:
        if t["variant"] != vid or t["mode"] not in ("shadow", "real"):
            continue
        key = (t["contract"], t["entry_time"][:10])
        if t["mode"] == "real" or key not in by_entry:
            by_entry[key] = t
    streak = 0
    for t in sorted(by_entry.values(), key=lambda t: t["exit_time"]):
        streak = 0 if float(t["pnl"] or 0) > 0 else streak + 1
    return streak


def paused(trades, vid, cfg):
    k = cfg.get("pause_after")
    return bool(k) and losing_streak(trades, vid) >= k


def book(ledgers, vid, pnl):
    led = ledgers[vid]
    led["realized"] = round(led["realized"] + pnl, 2)
    led["real_trades"] += 1


def shift_main_anchor(pnl):
    """Keep a ledger variant's real P&L out of the main ledger (account change since anchor)."""
    main = journal.load_ledger()
    if main is not None:
        main["anchor"] = round(main["anchor"] + pnl, 2)
        journal.save_ledger(main)


def record_equity(ledgers, cfg, day, paused_ids):
    rows = []
    if EQUITY_PATH.exists():
        with EQUITY_PATH.open() as f:
            rows = [r for r in csv.DictReader(f) if r["date"] != day]
    for vid in cfg.get("variants", []):
        led = ledgers.get(vid) or {}
        rows.append({"date": day, "variant": vid, "generation": led.get("generation", 1),
                     "equity": round(equity(ledgers, vid, cfg), 2), "real_trades": led.get("real_trades", 0),
                     "paused": int(vid in paused_ids)})
    with EQUITY_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=EQUITY_FIELDS)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["date"], r["variant"])))
