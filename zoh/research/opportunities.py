"""Score the day's opportunity list (no orders).

Sources, all for one US/Eastern date:
- journal/bias/<date>.json: the sniper and an optional "opportunities" list (pre-market),
- journal/bias/intraday/<date>.json: the picks and an optional "opportunities" list,
- journal/opportunities/<date>.json: entries added later in the day or at the review.

Each entry: {"type", "symbol", "direction": "call"|"put", "time": "HH:MM" (default 10:00),
"why", "action": "real"|"shadow"|"none"}. The sniper's and the picks' action follows the config:
"real" while catalyst_open / catalyst_intraday carry a real_risk, "shadow" once it is 0 (since
2026-11-09 both are shadow-only). The score is the stock move from the entry time to the
close, signed by direction, plus open->close and the best move after entry, from IEX minute
bars. Written to journal/opportunities.csv so each type builds a record (owner, 2026-10-29:
"list every kind of opportunity").

Since 2026-11-13 each row also carries what SPY did over the same minutes and the move against
it, a three-way grade (paid / right / wrong), a repeat flag and a final flag (the workflow scores
before the bell; a later run scores the row again to the real close), and every run rebuilds the
record by type in journal/research/OPPORTUNITY_SCORES.md.

    python -m zoh.research.opportunities [YYYY-MM-DD]     # score a day and rebuild the record
    python -m zoh.research.opportunities --backfill       # only score the open rows again and rebuild
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
BOARD_PATH = journal.JOURNAL_DIR / "research" / "OPPORTUNITY_SCORES.md"
FIELDS = ["date", "time", "type", "symbol", "direction", "action", "source", "open", "entry",
          "close", "open_close_pct", "entry_close_pct", "best_after_entry_pct", "why",
          "spy_pct", "vs_spy_pct", "grade", "repeat", "final"]
# Since 2026-11-13 (owner: "the scoring could be better"). Before, a row was right when the stock
# closed a cent the idea's way: 56% of 205 rows were "right" and only 29% moved the 1% a same-day
# option needs; every put looked right on a down day; 43 rows were the same idea listed again at a
# later check; 31 type keys, 14 of them used once; and nobody had added the rows up by type.
# The workflow scores at about 15:48, twelve minutes before the bell, so `close` was never the close:
# a row stays final=0 until a later run finds bars to 15:55 or beyond and scores it again.
FINAL_FROM = time(15, 55)
PAID = 1.0  # % the idea's way from entry to close: about what a 0.35-delta same-day option needs
            # (OPENGATE.md: the call made money on 30 of 38 days with it and on 2 of 57 without)
ALIASES = {"analyst_upgrade": "analyst", "upgrade": "analyst", "analyst_downgrade": "analyst",
           "mirror": "put_mirror", "mirror_conditional": "put_mirror", "headline": "company_news",
           "other_side": "peer_readthrough", "post_earnings_reversal": "earnings_reaction",
           "rotation_reversal": "rotation_laggard", "rotation_unwind": "rotation_laggard"}
GENERIC = {"sniper", "intraday"}  # a pick logged without its catalyst kind


PICK_VARIANTS = {"sniper": "catalyst_open", "intraday": "catalyst_intraday"}


def canonical(kind):
    return ALIASES.get(kind or "", kind or "")


def grade_of(pct):
    """paid: moved at least PAID the idea's way; right: the right way but not enough for an option."""
    return "paid" if pct >= PAID else "right" if pct > 0 else "wrong"


def pick_action(source, config=None):
    """'real' when the variant behind a sniper or intraday pick risks real money, else 'shadow'."""
    config = journal.load_config() if config is None else config
    for v in config.get("variants", []):
        if v.get("id") == PICK_VARIANTS.get(source):
            return "real" if v.get("real_risk", v.get("risk", 0)) else "shadow"
    return "shadow"


def merge_picks(items):
    """The sniper or a pick that the same file also lists by hand under its catalyst kind is one idea:
    the pick row takes that kind as its type and the hand-written twin is dropped."""
    drop = set()
    for it in items:
        if not it.get("pick"):
            continue
        listed = "premarket" if it["source"] == "sniper" else "intraday"
        for j, other in enumerate(items):
            if (j not in drop and not other.get("pick") and other.get("source") == listed
                    and other.get("symbol") == it["symbol"] and other.get("direction", "call") == it["direction"]
                    and other.get("time", "10:00") == it["time"]):
                if it["type"] in GENERIC and other.get("type"):
                    it["type"] = other["type"]
                drop.add(j)
                break
    return [{k: v for k, v in it.items() if k != "pick"} for j, it in enumerate(items) if j not in drop]


def collect(day, root=None, config=None):
    root = Path(root or journal.JOURNAL_DIR)
    out = []
    bias_path = root / "bias" / f"{day}.json"
    if bias_path.exists():
        bias = json.loads(bias_path.read_text())
        sniper = bias.get("sniper")
        if sniper and sniper.get("symbol"):
            out.append({"type": sniper.get("catalyst_type") or "sniper", "symbol": sniper["symbol"],
                        "direction": sniper.get("direction", "call"), "time": "09:31",
                        "why": sniper.get("catalyst", ""), "action": pick_action("sniper", config),
                        "source": "sniper", "pick": True})
        out += [dict(o, source="premarket") for o in bias.get("opportunities") or []]
    intraday_path = root / "bias" / "intraday" / f"{day}.json"
    if intraday_path.exists():
        intraday = json.loads(intraday_path.read_text())
        for p in intraday.get("picks") or []:
            out.append({"type": p.get("catalyst_type") or "intraday", "symbol": p["symbol"],
                        "direction": p.get("direction", "call"), "time": p.get("time", "10:00"),
                        "why": p.get("catalyst", ""), "action": pick_action("intraday", config),
                        "source": "intraday", "pick": True})
        out += [dict(o, source="intraday") for o in intraday.get("opportunities") or []]
    extra_path = root / "opportunities" / f"{day}.json"
    if extra_path.exists():
        extra = json.loads(extra_path.read_text())
        out += [dict(o, source=o.get("source", "review")) for o in extra.get("opportunities") or []]
    return merge_picks(out)


def _after(bars, entry_hhmm):
    h, m = (int(x) for x in entry_hhmm.split(":"))
    return [b for b in bars if datetime.fromisoformat(b["t"].replace("Z", "+00:00"))
            .astimezone(ET).time() >= time(h, m)]


def window_pct(bars, entry_hhmm):
    """Plain move, in %, from the first bar at or after the entry time to the last close."""
    after = _after(bars or [], entry_hhmm)
    return round((bars[-1]["c"] / after[0]["o"] - 1) * 100, 2) if after else None


def session_over(day, now=None):
    """True once the regular session of `day` has ended (a minute after the bell)."""
    now = now or datetime.now(ET)
    return day < now.date() or (day == now.date() and now.time() >= time(16, 1))


def score(bars, entry_hhmm, direction, spy_bars=None, closed=True):
    """bars: [{"t": iso, "o", "h", "l", "c"}] for the regular session, oldest first. With SPY's bars
    the row also says what the index did over the same window and how far the idea beat it. `closed`
    is whether the session has ended: a row scored before the bell is never final."""
    if not bars:
        return None
    sign = 1 if direction == "call" else -1
    after = _after(bars, entry_hhmm)
    if not after:
        return None
    open_, close, entry = bars[0]["o"], bars[-1]["c"], after[0]["o"]
    best = max(b["h"] for b in after) if sign > 0 else min(b["l"] for b in after)
    out = {"open": round(open_, 2), "entry": round(entry, 2), "close": round(close, 2),
           "open_close_pct": round(sign * (close / open_ - 1) * 100, 2),
           "entry_close_pct": round(sign * (close / entry - 1) * 100, 2),
           "best_after_entry_pct": round(sign * (best / entry - 1) * 100, 2)}
    out["grade"] = grade_of(out["entry_close_pct"])
    last = datetime.fromisoformat(bars[-1]["t"].replace("Z", "+00:00")).astimezone(ET).time()
    out["final"] = "1" if closed and last >= FINAL_FROM else "0"
    spy = window_pct(spy_bars, entry_hhmm) if spy_bars else None
    if spy is not None:
        out["spy_pct"] = spy
        out["vs_spy_pct"] = round(out["entry_close_pct"] - sign * spy, 2)
    return out


def session_bars(api, symbol, day, feed="iex"):
    start = datetime.combine(day, time(9, 30), ET)
    end = datetime.combine(day, time(16, 0), ET)
    return [b for b in api.stock_bars(symbol, start, end, feed=feed)
            if datetime.fromisoformat(b["t"].replace("Z", "+00:00")) < end]


def day_bars(api, symbol, day, today=None):
    """The consolidated tape for a finished day (free once it is 15 minutes old), IEX for today."""
    today = today or datetime.now(ET).date()
    if day < today:
        try:
            return session_bars(api, symbol, day, feed="sip")
        except AlpacaError:
            pass
    return session_bars(api, symbol, day)


def load_rows(path=None):
    path = Path(path or CSV_PATH)
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def save_rows(rows, path=None):
    with Path(path or CSV_PATH).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows({k: r.get(k, "") if r.get(k) is not None else "" for k in FIELDS} for r in rows)


def mark_repeats(rows):
    """repeat = 1 on every later mention of the same stock and direction on the same day."""
    seen = set()
    for i in sorted(range(len(rows)), key=lambda i: (rows[i]["date"], rows[i]["time"], i)):
        key = (rows[i]["date"], rows[i]["symbol"], rows[i]["direction"])
        rows[i]["repeat"] = "1" if key in seen else "0"
        seen.add(key)
    return rows


def rescore(api, rows, today=None, now=None):
    """Score again every row that is not final: rows written before the bell get the real close, and rows
    from before 2026-11-13 get the SPY window, the grade and the repeat flag. A row whose bars cannot be
    read keeps what it has."""
    cache = {}

    def bars(symbol, day):
        if (symbol, day) not in cache:
            try:
                cache[(symbol, day)] = day_bars(api, symbol, datetime.fromisoformat(day).date(), today)
            except AlpacaError:
                cache[(symbol, day)] = []
        return cache[(symbol, day)]
    for r in rows:
        if r.get("final") == "1":
            continue
        new = score(bars(r["symbol"], r["date"]), r["time"], r["direction"], bars("SPY", r["date"]),
                    closed=session_over(datetime.fromisoformat(r["date"]).date(), now))
        if new:
            r.update(new)
        elif r.get("grade") in (None, ""):
            r["grade"] = grade_of(float(r["entry_close_pct"]))
    return mark_repeats(rows)


# ---- the record by type ---------------------------------------------------------------------

def ideas(rows):
    """One row per idea: the first mention of a stock and direction on a day. A pick logged as plain
    "sniper" / "intraday" next to a hand-written twin of the same minute takes the twin's type and
    keeps its own action; type aliases are merged."""
    groups = {}
    for r in rows:
        groups.setdefault((r["date"], r["symbol"], r["direction"]), []).append(r)
    out = []
    for g in groups.values():
        g.sort(key=lambda r: r["time"])
        first = [r for r in g if r["time"] == g[0]["time"]]
        base = dict(first[0])
        named = [r["type"] for r in first if r["type"] not in GENERIC]
        base["type"] = canonical(named[0] if named else base["type"])
        acted = [r["action"] for r in first if r.get("action") in ("real", "shadow")]
        base["action"] = acted[0] if acted else base.get("action") or "none"
        if any(r.get("source") == "sniper" for r in first):
            base["source"] = "sniper"
        out.append(base)
    return sorted(out, key=lambda r: (r["date"], r["time"]))


def _num(r, key):
    return float(r[key]) if r.get(key) not in (None, "") else None


def stats(rs):
    """ideas, share right, share paid, average move, average against SPY, average without the best."""
    moves = sorted(_num(r, "entry_close_pct") for r in rs)
    if not moves:
        return None
    rel = [x for x in (_num(r, "vs_spy_pct") for r in rs) if x is not None]
    return {"n": len(moves), "right": sum(x > 0 for x in moves) / len(moves),
            "paid": sum(x >= PAID for x in moves) / len(moves), "avg": sum(moves) / len(moves),
            "vs_spy": sum(rel) / len(rel) if rel else None,
            "beat": sum(x > 0 for x in rel) / len(rel) if rel else None,
            "wo_best": sum(moves[:-1]) / (len(moves) - 1) if len(moves) > 1 else None}


def board(rows, key="type"):
    out = {}
    for r in ideas(rows):
        out.setdefault(r.get(key) or "", []).append(r)
    return {k: stats(v) for k, v in out.items()}


def _pct(x, digits=0):
    return "-" if x is None else f"{x * 100:.{digits}f}%"


def _pts(x):
    return "-" if x is None else f"{x:+.2f}%"


def _line(label, s):
    return (f"| {label} | {s['n']} | {_pct(s['right'])} | {_pct(s['paid'])} | {_pts(s['avg'])} | {_pts(s['wo_best'])} | "
            f"{_pts(s['vs_spy'])} | {_pct(s['beat'])} |")


HEAD = ["| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |",
        "|---|---|---|---|---|---|---|---|"]


def scoreboard(rows, small=3):
    """Markdown record by type, source, direction and action, rebuilt after every scoring run."""
    one = ideas(rows)
    if not one:
        return "# Opportunity scores\n\nNo rows yet.\n"
    days = sorted({r["date"] for r in one})
    recent = set(days[-10:])
    out = ["# Opportunity scores", "",
           f"{len(rows)} rows, {len(one)} ideas after dropping later mentions of the same stock and direction on the same "
           f"day, {days[0]} to {days[-1]} ({len(days)} sessions). Moves are the stock from the listed time to the close, "
           "signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's "
           "way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY "
           "did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the "
           "tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and "
           "`avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by "
           "`python -m zoh.research.opportunities`.", "", "## All ideas", ""] + HEAD + [_line("all ideas", stats(one))]
    for title, key in (("By source", "source"), ("By direction", "direction"), ("By action (picked or only listed)", "action")):
        out += ["", f"## {title}", ""] + HEAD
        for k, s in sorted(board(rows, key).items(), key=lambda kv: -kv[1]["n"]):
            out.append(_line(k or "-", s))
    for title, part in (("By type", one), (f"By type, last {len(recent)} sessions", [r for r in one if r["date"] in recent])):
        by = {}
        for r in part:
            by.setdefault(r["type"], []).append(r)
        out += ["", f"## {title}", ""] + HEAD
        rest = []
        for k, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
            if len(rs) < small:
                rest += rs
            else:
                out.append(_line(k, stats(rs)))
        if rest:
            out.append(_line(f"other types (fewer than {small} ideas each)", stats(rest)))
    return "\n".join(out) + "\n"


def summary_zh(rows, min_n=8):
    """Two or three plain Chinese lines for the Discord post: the running record and its best and worst types."""
    one = ideas(rows)
    if not one:
        return []
    s = stats(one)
    lines = [f"累计 {s['n']} 个想法（同一天同一只股票重复提的只算一次）：方向对 {_pct(s['right'])}，"
             f"够期权赚钱（顺方向 1% 以上）{_pct(s['paid'])}，平均比大盘多 {_pts(s['vs_spy'])}"]
    by = [(k, v) for k, v in board(rows).items() if v["n"] >= min_n]
    if len(by) >= 2:
        from ..notify import TYPES
        name = lambda k: TYPES.get(k, k)
        by.sort(key=lambda kv: kv[1]["paid"], reverse=True)
        show = lambda kv: f"{name(kv[0])}（{kv[1]['n']} 个，够赚钱 {_pct(kv[1]['paid'])}，比大盘 {_pts(kv[1]['vs_spy'])}）"
        lines.append("最好的类型：" + "、".join(show(x) for x in by[:2]))
        lines.append("最差的类型：" + "、".join(show(x) for x in by[-2:][::-1]))
    return lines


def main(day=None, backfill_only=False):
    day = day or datetime.now(ET).date()
    rows, api = load_rows(), Alpaca()
    items = [] if backfill_only else collect(day.isoformat())
    if not items and not backfill_only:
        print(f"opportunities: none listed for {day}")
    done = {(r["date"], r["time"], r["type"], r["symbol"]) for r in rows}
    spy_bars, added = None, 0
    for it in items:
        key = (day.isoformat(), it.get("time", "10:00"), canonical(it.get("type", "")), it["symbol"])
        if key in done or (key[0], key[1], it.get("type", ""), key[3]) in done:
            continue
        try:
            if spy_bars is None:
                spy_bars = day_bars(api, "SPY", day)
            s = score(day_bars(api, it["symbol"], day), key[1], it.get("direction", "call"), spy_bars,
                      closed=session_over(day))
        except AlpacaError as e:
            print(f"opportunities: {it['symbol']} bars failed: {e}")
            continue
        if not s:
            continue
        rows.append({"date": key[0], "time": key[1], "type": key[2], "symbol": key[3],
                     "direction": it.get("direction", "call"), "action": it.get("action", "none"),
                     "source": it.get("source", ""), **s, "why": (it.get("why") or "")[:200]})
        done.add(key)
        added += 1
    if not rows:
        return
    save_rows(rescore(api, rows))
    try:
        BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        BOARD_PATH.write_text(scoreboard(rows))
    except Exception as e:  # the record by type must never cost the day's rows
        print(f"opportunities: scoreboard failed: {e}")
    print(f"opportunities: {added} scored for {day}, {len(rows)} rows in all")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--backfill"]
    main(datetime.fromisoformat(args[0]).date() if args else None, backfill_only="--backfill" in sys.argv)
