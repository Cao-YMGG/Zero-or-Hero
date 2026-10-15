"""Auto-grade the day's closed trades (journal/GRADING.md) into journal/grades.csv.

Thesis, entry and exit are computed from prices: the underlying's minute bars between entry
and exit, and the peak the bot logged in journal/exits.csv. Discipline is pre-filled with the
rule-based deductions it can see (direction against the day's SPY call, a macro day without a
macro filter); the daily review checks it and adds the judgment calls.

    python -m zoh.grade            # today's trades (US/Eastern date)
    python -m zoh.grade 2026-10-15
"""
import csv
import json
import sys
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca, AlpacaError
from .strategy import ET, parse_bar, parse_occ

GRADES_PATH = journal.JOURNAL_DIR / "grades.csv"
GRADE_FIELDS = ["date", "variant", "mode", "contract", "direction", "pnl_pct", "thesis", "entry",
                "exit", "discipline", "score", "luck", "verdict", "note"]
FLAT = 0.002  # a 0.2% move either way counts as flat


def thesis_score(direction, strike, spot_entry, spot_exit, best):
    """0-3: did the underlying go our way, and far enough to reach the strike?
    best = the most favourable price between entry and exit (high for calls, low for puts)."""
    sign = 1 if direction == "call" else -1
    if sign * (best - strike) >= 0:
        return 3
    move = sign * (spot_exit / spot_entry - 1)
    if move >= FLAT:
        return 2
    if move > -FLAT:
        return 1
    return 0


def entry_score(entry, peak):
    if not entry or peak is None:
        return None
    x = peak / entry
    return 2 if x >= 2 else 1 if x >= 1.3 else 0


def exit_score(entry, exit_price, peak):
    if not entry or peak is None:
        return None
    if peak < 1.3 * entry:
        return 1  # never worth managing
    kept = exit_price / peak if peak else 0
    return 2 if kept >= 0.6 else 1 if kept >= 0.3 else 0


def discipline_auto(direction, variant_id, variant_cfg, spy_call, macro_day):
    """3 minus the deductions visible from the files; returns (score, reasons)."""
    reasons = []
    if spy_call in ("call", "put") and direction != spy_call and variant_id != "claude_bias":
        reasons.append(f"{direction} on a {spy_call} day")
    if macro_day and variant_cfg is not None and variant_cfg.get("days") != "non_event" \
            and variant_id not in ("claude_bias", "claude_confirm"):
        reasons.append("macro day without a filter")
    return max(0, 3 - len(reasons)), reasons


def luck_flag(pnl_pct, score):
    if score is None:
        return ""
    if pnl_pct > 0 and score <= 5:
        return "lucky"
    if pnl_pct < 0 and score >= 6:
        return "unlucky"
    return ""


def read_grades():
    if not GRADES_PATH.exists():
        return []
    with GRADES_PATH.open(newline="") as f:
        return list(csv.DictReader(f))


def peaks_by_trade():
    path = journal.EXITS_PATH
    if not path.exists():
        return {}
    with path.open(newline="") as f:
        return {(r["date"], r["variant"], r["mode"], r["contract"]): float(r["peak"])
                for r in csv.DictReader(f) if r.get("peak")}


def underlying_path(api, symbol, start, end):
    bars = [parse_bar(b) for b in api.stock_bars(symbol, start - timedelta(minutes=1),
                                                 end + timedelta(minutes=1), feed="sip")]
    return [b for b in bars if start - timedelta(minutes=1) <= b["t"] <= end + timedelta(minutes=1)]


def grade_day(day, api=None):
    graded = {(r["date"], r["variant"], r["mode"], r["contract"]) for r in read_grades()}
    trades = [t for t in journal.read_trades() if t["date"] == day
              and (t["date"], t["variant"], t["mode"], t["contract"]) not in graded]
    if not trades:
        print(f"grade: nothing new for {day}")
        return []
    config = {v["id"]: v for v in journal.load_config()["variants"]}
    events = journal.load_events()
    bias_file = journal.bias_path(datetime.fromisoformat(day).date())
    spy_call = json.loads(bias_file.read_text()).get("bias") if bias_file.exists() else None
    peaks = peaks_by_trade()
    api = api or Alpaca()
    rows = []
    for t in trades:
        und, _, kind, strike = parse_occ(t["contract"])
        start = datetime.fromisoformat(t["entry_time"]).astimezone(ET)
        end = datetime.fromisoformat(t["exit_time"]).astimezone(ET)
        entry, exit_price = float(t["entry_price"]), float(t["exit_price"])
        pnl = float(t["pnl_pct"] or 0)
        peak = peaks.get((t["date"], t["variant"], t["mode"], t["contract"]))
        thesis, notes = None, ["auto"]
        try:
            path = underlying_path(api, und, start, end)
        except AlpacaError as e:
            path, notes = [], notes + [f"no bars: {e}"]
        if path:
            best = max(b["h"] for b in path) if kind == "call" else min(b["l"] for b in path)
            thesis = thesis_score(kind, strike, path[0]["c"], path[-1]["c"], best)
            notes.append(f"{und} {path[0]['c']:.2f}->{path[-1]['c']:.2f}, best {best:.2f} vs strike {strike:g}")
        disc, why = discipline_auto(kind, t["variant"], config.get(t["variant"]), spy_call,
                                    bool(events.get(day)))
        notes += why
        e_s, x_s = entry_score(entry, peak), exit_score(entry, exit_price, peak)
        if peak is not None:
            notes.append(f"peak {peak:g}")
        parts = [thesis, e_s, x_s, disc]
        score = sum(parts) if None not in parts else None
        rows.append({"date": day, "variant": t["variant"], "mode": t["mode"],
                     "contract": t["contract"], "direction": kind, "pnl_pct": pnl,
                     "thesis": "" if thesis is None else thesis, "entry": "" if e_s is None else e_s,
                     "exit": "" if x_s is None else x_s, "discipline": disc,
                     "score": "" if score is None else score, "luck": luck_flag(pnl, score),
                     "verdict": "", "note": "; ".join(notes)})
    new = not GRADES_PATH.exists()
    with GRADES_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=GRADE_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"grade: {r['variant']} {r['mode']} {r['contract']} score={r['score']} {r['note']}")
    return rows


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now(ET).date().isoformat()
    grade_day(day)


if __name__ == "__main__":
    main()
