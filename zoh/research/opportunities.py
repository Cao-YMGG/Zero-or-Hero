"""Score the day's opportunity list (no orders).

Sources, all for one US/Eastern date:
- journal/bias/<date>.json: the sniper and an optional "opportunities" list (pre-market),
- journal/bias/intraday/<date>.json: the picks and an optional "opportunities" list,
- journal/opportunities/<date>.json: entries added later in the day or at the review.

Each entry: {"type", "symbol", "direction": "call"|"put", "time": "HH:MM" (default 10:00),
"why", "action": "real"|"shadow"|"none"}. The score is the stock move from the entry time to the
close, signed by direction, plus open->close and the best move after entry, from IEX minute
bars. Written to journal/opportunities.csv so each type builds a record (owner, 2026-10-29:
"list every kind of opportunity").
"""
import csv
import json
import sys
from datetime import datetime, time, timedelta
from pathlib import Path

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..strategy import ET

CSV_PATH = journal.JOURNAL_DIR / "opportunities.csv"
FIELDS = ["date", "time", "type", "symbol", "direction", "action", "source", "open", "entry",
          "close", "open_close_pct", "entry_close_pct", "best_after_entry_pct", "why"]


def collect(day, root=None):
    root = Path(root or journal.JOURNAL_DIR)
    out = []
    bias_path = root / "bias" / f"{day}.json"
    if bias_path.exists():
        bias = json.loads(bias_path.read_text())
        sniper = bias.get("sniper")
        if sniper and sniper.get("symbol"):
            out.append({"type": sniper.get("catalyst_type") or "sniper", "symbol": sniper["symbol"],
                        "direction": sniper.get("direction", "call"), "time": "09:31",
                        "why": sniper.get("catalyst", ""), "action": "real", "source": "sniper"})
        out += [dict(o, source="premarket") for o in bias.get("opportunities") or []]
    intraday_path = root / "bias" / "intraday" / f"{day}.json"
    if intraday_path.exists():
        intraday = json.loads(intraday_path.read_text())
        for p in intraday.get("picks") or []:
            out.append({"type": p.get("catalyst_type") or "intraday", "symbol": p["symbol"],
                        "direction": p.get("direction", "call"), "time": p.get("time", "10:00"),
                        "why": p.get("catalyst", ""), "action": "real", "source": "intraday"})
        out += [dict(o, source="intraday") for o in intraday.get("opportunities") or []]
    extra_path = root / "opportunities" / f"{day}.json"
    if extra_path.exists():
        extra = json.loads(extra_path.read_text())
        out += [dict(o, source=o.get("source", "review")) for o in extra.get("opportunities") or []]
    return out


def score(bars, entry_hhmm, direction):
    """bars: [{"t": iso, "o", "h", "l", "c"}] for the regular session, oldest first."""
    if not bars:
        return None
    sign = 1 if direction == "call" else -1
    h, m = (int(x) for x in entry_hhmm.split(":"))
    after = [b for b in bars if datetime.fromisoformat(b["t"].replace("Z", "+00:00"))
             .astimezone(ET).time() >= time(h, m)]
    if not after:
        return None
    open_, close, entry = bars[0]["o"], bars[-1]["c"], after[0]["o"]
    best = max(b["h"] for b in after) if sign > 0 else min(b["l"] for b in after)
    return {"open": round(open_, 2), "entry": round(entry, 2), "close": round(close, 2),
            "open_close_pct": round(sign * (close / open_ - 1) * 100, 2),
            "entry_close_pct": round(sign * (close / entry - 1) * 100, 2),
            "best_after_entry_pct": round(sign * (best / entry - 1) * 100, 2)}


def session_bars(api, symbol, day):
    start = datetime.combine(day, time(9, 30), ET)
    end = datetime.combine(day, time(16, 0), ET)
    return [b for b in api.stock_bars(symbol, start, end)
            if datetime.fromisoformat(b["t"].replace("Z", "+00:00")) < end]


def main(day=None):
    day = day or datetime.now(ET).date()
    items = collect(day.isoformat())
    if not items:
        print(f"opportunities: none listed for {day}")
        return
    done = set()
    if CSV_PATH.exists():
        done = {(r["date"], r["time"], r["type"], r["symbol"]) for r in csv.DictReader(CSV_PATH.open())}
    api, rows = Alpaca(), []
    for it in items:
        key = (day.isoformat(), it.get("time", "10:00"), it.get("type", ""), it["symbol"])
        if key in done:
            continue
        try:
            s = score(session_bars(api, it["symbol"], day), it.get("time", "10:00"), it.get("direction", "call"))
        except AlpacaError as e:
            print(f"opportunities: {it['symbol']} bars failed: {e}")
            continue
        if not s:
            continue
        rows.append({"date": key[0], "time": key[1], "type": key[2], "symbol": key[3],
                     "direction": it.get("direction", "call"), "action": it.get("action", "none"),
                     "source": it.get("source", ""), **s, "why": (it.get("why") or "")[:200]})
    new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"opportunities: {len(rows)} scored for {day}")


if __name__ == "__main__":
    main(datetime.fromisoformat(sys.argv[1]).date() if len(sys.argv) > 1 else None)
