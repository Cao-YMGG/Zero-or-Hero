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
    python -m zoh.research.opportunities --review [date]  # the ideas that owe a post-mortem, as JSON
    python -m zoh.research.opportunities --add-reviews F  # append the written post-mortems
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
          "spy_pct", "vs_spy_pct", "grade", "repeat", "final", "conviction"]
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
# What I thought when I listed it (since 2026-11-16; first post-mortem, 2026-11-13: of 17 ideas the one I
# backed was wrong and two I had argued against, "a control, not a pick", were the day's best). yes = I
# would pick it if the bar allowed; maybe; no = a control, listed because it fits a type or to watch a
# line, expected to fail. A sniper or pick is yes by definition. If the no ideas pay as often as the
# yes ones, the pick bar is not adding anything.
CONVICTIONS = ("yes", "maybe", "no")

# The daily post-mortem (owner, 2026-11-13: "when you are wrong, work out why you read it wrong"). Every
# wrong idea and every pick gets one row in journal/opportunity_reviews.csv with one cause from this
# list, so the causes can be counted: a cause that keeps coming back is a habit to change.
REVIEWS_PATH = journal.JOURNAL_DIR / "opportunity_reviews.csv"
REVIEW_FIELDS = ["date", "time", "symbol", "direction", "type", "source", "grade", "entry_close_pct",
                 "vs_spy_pct", "cause", "thought", "happened", "lesson"]
CAUSES = {"chased": "追在延伸处：大部分行情已经走完才提",
          "no_catalyst": "没有自己的消息：只凭相对强弱或跟风",
          "missed_news": "漏看消息：当时已有的标题没读到或没当回事",
          "misread_news": "消息读反了：把利空当利好，或反过来",
          "priced_in": "已经在价格里：消息在缺口里就消化完了",
          "tide": "被大盘带走：比大盘强，但大盘的方向盖过了它",
          "reversal": "逆势：赌反弹或回落，当天的趋势没停",
          "timing": "时间不对：之前或之后是对的，从记录的时间算是错的",
          "luck": "对了但靠运气：理由没兑现，是大盘或别的事带着走",
          "sound": "判断成立：理由兑现了",
          "noise": "没有可学的：涨跌很小，哪边都说明不了什么",
          "other": "其他"}


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
                        "source": "sniper", "pick": True, "conviction": "yes"})
        out += [dict(o, source="premarket") for o in bias.get("opportunities") or []]
    intraday_path = root / "bias" / "intraday" / f"{day}.json"
    if intraday_path.exists():
        intraday = json.loads(intraday_path.read_text())
        for p in intraday.get("picks") or []:
            out.append({"type": p.get("catalyst_type") or "intraday", "symbol": p["symbol"],
                        "direction": p.get("direction", "call"), "time": p.get("time", "10:00"),
                        "why": p.get("catalyst", ""), "action": pick_action("intraday", config),
                        "source": "intraday", "pick": True, "conviction": "yes"})
        out += [dict(o, source="intraday") for o in intraday.get("opportunities") or []]
    extra_path = root / "opportunities" / f"{day}.json"
    if extra_path.exists():
        extra = json.loads(extra_path.read_text())
        out += [dict(o, source=o.get("source", "review")) for o in extra.get("opportunities") or []]
    for o in out:
        if o.get("conviction") not in CONVICTIONS:
            o["conviction"] = ""
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


# ---- the daily post-mortem ------------------------------------------------------------------

def load_reviews(path=None):
    return load_rows(path or REVIEWS_PATH)


def to_review(day, rows, reviews=()):
    """The day's ideas that owe a post-mortem and have none yet: every wrong one, and every pick
    (a pick that worked is checked for luck)."""
    done = {(r["date"], r["symbol"], r["direction"]) for r in reviews}
    return [r for r in ideas(rows) if r["date"] == day and (r["date"], r["symbol"], r["direction"]) not in done
            and (r.get("grade") == "wrong" or r.get("action") in ("real", "shadow") or r.get("source") == "sniper")]


def add_reviews(items, rows, reviews):
    """Validate the written post-mortems against the day's ideas and append them. Each item needs
    date, symbol, direction, a cause from CAUSES, and thought / happened / lesson in plain words."""
    by = {(r["date"], r["symbol"], r["direction"]): r for r in ideas(rows)}
    have = {(r["date"], r["symbol"], r["direction"]) for r in reviews}
    out = list(reviews)
    for it in items:
        key = (it["date"], it["symbol"], it["direction"])
        if it.get("cause") not in CAUSES:
            raise ValueError(f"{key}: cause must be one of {sorted(CAUSES)}")
        if key not in by:
            raise ValueError(f"{key}: no such idea in the scored log")
        if not all((it.get(k) or "").strip() for k in ("thought", "happened", "lesson")):
            raise ValueError(f"{key}: thought, happened and lesson must all be written")
        if key in have:
            continue
        idea = by[key]
        out.append({"date": key[0], "time": idea["time"], "symbol": key[1], "direction": key[2], "type": idea["type"],
                    "source": idea.get("source", ""), "grade": idea.get("grade", ""),
                    "entry_close_pct": idea.get("entry_close_pct", ""), "vs_spy_pct": idea.get("vs_spy_pct", ""),
                    "cause": it["cause"], "thought": it["thought"].strip(), "happened": it["happened"].strip(),
                    "lesson": it["lesson"].strip()})
        have.add(key)
    return out


def save_reviews(reviews, path=None):
    with Path(path or REVIEWS_PATH).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REVIEW_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(reviews)


def cause_counts(reviews, since=None):
    """[(cause, ideas)] for the wrong ideas, most common first."""
    count = {}
    for r in reviews:
        if r.get("grade") == "wrong" and (since is None or r["date"] >= since):
            count[r["cause"]] = count.get(r["cause"], 0) + 1
    return sorted(count.items(), key=lambda kv: -kv[1])


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
        stated = [r.get("conviction") for r in first if r.get("conviction") in CONVICTIONS]
        base["conviction"] = "yes" if acted or base["source"] == "sniper" else (stated[0] if stated else "")
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


def scoreboard(rows, small=3, reviews=()):
    """Markdown record by type, source, direction and action, rebuilt after every scoring run; with the
    post-mortems, also why the wrong ideas were wrong."""
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
    for title, key in (("By source", "source"), ("By direction", "direction"), ("By action (picked or only listed)", "action"),
                       ("By conviction (what I thought when I listed it; stated since 2026-11-13)", "conviction")):
        out += ["", f"## {title}", ""] + HEAD
        for k, s in sorted(board(rows, key).items(), key=lambda kv: -kv[1]["n"]):
            out.append(_line(k or ("not stated" if key == "conviction" else "-"), s))
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
    wrong = [r for r in reviews if r.get("grade") == "wrong"]
    if wrong:
        total = sum(1 for r in one if r.get("grade") == "wrong")
        out += ["", "## Why the wrong ones were wrong", "",
                f"{len(wrong)} of {total} wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each "
                "evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.", "",
                "| cause | 中文 | wrong ideas | share | avg move | types it shows up in |", "|---|---|---|---|---|---|"]
        for cause, n in cause_counts(reviews):
            part = [r for r in wrong if r["cause"] == cause]
            kinds = {}
            for r in part:
                kinds[r["type"]] = kinds.get(r["type"], 0) + 1
            top = ", ".join(f"{k} {v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])[:3])
            out.append(f"| {cause} | {CAUSES.get(cause, cause).split('：')[0]} | {n} | {_pct(n / len(wrong))} | "
                       f"{_pts(sum(float(r['entry_close_pct']) for r in part) / n)} | {top} |")
    return "\n".join(out) + "\n"


def summary_zh(rows, min_n=8, reviews=None):
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
    told = board(rows, "conviction")
    if told.get("yes") and told.get("no"):
        say = lambda k, word: f"{word}的 {told[k]['n']} 个：够赚钱 {_pct(told[k]['paid'])}、比大盘 {_pts(told[k]['vs_spy'])}"
        lines.append("我的判断：" + "；".join([say("yes", "看好")] + ([say("maybe", "拿不准")] if told.get("maybe") else [])
                                         + [say("no", "不看好（当对照）")]))
    causes = cause_counts(load_reviews() if reviews is None else reviews)
    if causes:
        lines.append("看错的原因（累计）：" + "、".join(f"{CAUSES.get(c, c).split('：')[0]} {n} 次" for c, n in causes[:3]))
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
                     "source": it.get("source", ""), **s, "why": (it.get("why") or "")[:200],
                     "conviction": it.get("conviction", "")})
        done.add(key)
        added += 1
    if not rows:
        return
    save_rows(rescore(api, rows))
    try:
        BOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
        BOARD_PATH.write_text(scoreboard(rows, reviews=load_reviews()))
    except Exception as e:  # the record by type must never cost the day's rows
        print(f"opportunities: scoreboard failed: {e}")
    print(f"opportunities: {added} scored for {day}, {len(rows)} rows in all")


def review_cli(argv):
    """--review [date]: print the ideas that owe a post-mortem as JSON to fill in.
    --add-reviews FILE: append the filled-in list ([{date, symbol, direction, cause, thought, happened,
    lesson}]) to journal/opportunity_reviews.csv and rebuild the record."""
    rows, reviews = load_rows(), load_reviews()
    if argv[0] == "--review":
        day = argv[1] if len(argv) > 1 else datetime.now(ET).date().isoformat()
        owed = to_review(day, rows, reviews)
        open_rows = sum(1 for r in rows if r["date"] == day and r.get("final") != "1")
        print(json.dumps({"date": day, "not_final_rows": open_rows, "causes": CAUSES, "owed": [
            {k: r.get(k, "") for k in ("date", "time", "symbol", "direction", "type", "source", "action", "conviction", "grade",
                                       "entry", "close", "entry_close_pct", "spy_pct", "vs_spy_pct",
                                       "best_after_entry_pct", "why")} for r in owed]}, ensure_ascii=False, indent=1))
        return
    items = json.loads(Path(argv[1]).read_text())
    out = add_reviews(items, rows, reviews)
    save_reviews(out)
    BOARD_PATH.write_text(scoreboard(rows, reviews=out))
    print(f"opportunities: {len(out) - len(reviews)} post-mortems added, {len(out)} in all")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--review", "--add-reviews"):
        review_cli(sys.argv[1:])
    else:
        args = [a for a in sys.argv[1:] if a != "--backfill"]
        main(datetime.fromisoformat(args[0]).date() if args else None, backfill_only="--backfill" in sys.argv)
