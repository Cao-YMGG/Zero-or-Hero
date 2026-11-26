"""Day, week and month forecasts and their scores (owner, 2026-11-26: "judge the environment, notice where it is
moving, and say how the next trading day goes and why"; "by day, week and month").

A forecast file in journal/forecasts/ is written BEFORE its window opens and is not edited afterwards. A revision made
before the window opens is added beside the original with "revises", and both are scored. Each file carries `claims`,
one checkable statement each:

  {"id", "horizon": "day" | "week" | "month", "p": probability, "kind", ...the fields of its kind}
  close_above_open      date                 SPY closes above its open that day
  close_above           date, level          SPY's close that day is above `level`
  abs_open_close_under  date, pct            |close / open - 1| is under `pct` percent
  close_between         date, low, high      low <= close <= high (an 80% range has p 0.80)
  any_close_below       start, end, level    some close from start to end is under `level`
Optional: "symbol" (SPY when absent), "revises" (the id of the claim it revises), "written" (when).

Scoring reads unadjusted daily bars (levels are the prices people saw) and only sessions that have closed. A claim is
scored once its last date has a bar; any_close_below resolves early on the first close under its level. Each scored
claim is one row of journal/forecasts/scores.csv. The Brier score (p - outcome)^2 is set against 0.25, the score of
always saying 0.50; an 80% range should hold about eight times in ten.

    python -m zoh.research.forecasts --check journal/forecasts/2026-11-27.json
    python -m zoh.research.forecasts --score          # after the close; idempotent
    python -m zoh.research.forecasts --summary
"""
import argparse
import csv
import json
import re
from datetime import date, datetime, time, timedelta, timezone

from .. import journal
from ..strategy import ET

DIR = journal.JOURNAL_DIR / "forecasts"
SCORES = DIR / "scores.csv"
FIELDS = ["scored_on", "file", "claim", "horizon", "kind", "p", "outcome", "brier", "detail"]
HORIZONS = ("day", "week", "month")
KINDS = {"close_above_open": ("date",), "close_above": ("date", "level"), "abs_open_close_under": ("date", "pct"),
         "close_between": ("date", "low", "high"), "any_close_below": ("start", "end", "level")}
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(doc):
    """The problems with a forecast file's claims, in plain words; an empty list means it can be scored."""
    claims = doc.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["no claims"]
    problems, ids = [], set()
    for i, c in enumerate(claims):
        name = c.get("id") or f"claim {i}"
        if not c.get("id"):
            problems.append(f"{name}: no id")
        elif c["id"] in ids:
            problems.append(f"{name}: id used twice")
        ids.add(c.get("id"))
        if c.get("horizon") not in HORIZONS:
            problems.append(f"{name}: horizon must be one of {', '.join(HORIZONS)}")
        p = c.get("p")
        if not isinstance(p, (int, float)) or not 0 < p < 1:
            problems.append(f"{name}: p must be a number between 0 and 1")
        kind = c.get("kind")
        if kind not in KINDS:
            problems.append(f"{name}: unknown kind {kind!r}")
            continue
        for field in KINDS[kind]:
            v = c.get(field)
            if v is None:
                problems.append(f"{name}: {kind} needs {field}")
            elif field in ("date", "start", "end") and not (isinstance(v, str) and ISO.match(v)):
                problems.append(f"{name}: {field} must be YYYY-MM-DD")
            elif field not in ("date", "start", "end") and not isinstance(v, (int, float)):
                problems.append(f"{name}: {field} must be a number")
        if kind == "close_between" and isinstance(c.get("low"), (int, float)) and isinstance(c.get("high"), (int, float)) \
                and c["low"] >= c["high"]:
            problems.append(f"{name}: low must be under high")
        if kind == "any_close_below" and str(c.get("start")) > str(c.get("end")):
            problems.append(f"{name}: start must not be after end")
        if c.get("revises") and c["revises"] not in {x.get("id") for x in claims}:
            problems.append(f"{name}: revises an id that is not in the file")
    return problems


def outcome(claim, bars, through):
    """(1 or 0, detail) once the claim can be decided from `bars` ({date: (open, close)}, closed sessions only,
    up to `through`), else (None, why not yet)."""
    kind = claim["kind"]
    if kind == "any_close_below":
        window = sorted(d for d in bars if claim["start"] <= d <= claim["end"])
        for d in window:
            if bars[d][1] < claim["level"]:
                return 1, f"{d} close {bars[d][1]:.2f} under {claim['level']}"
        if through >= claim["end"]:
            low = min((bars[d][1] for d in window), default=None)
            return 0, ("lowest close " + (f"{low:.2f}" if low is not None else "none")) + f", level {claim['level']}"
        return None, "window still open"
    d = claim["date"]
    if d not in bars:
        return None, "no closed session on that date yet" if through < d else "no session on that date"
    o, c = bars[d]
    if kind == "close_above_open":
        return int(c > o), f"open {o:.2f} close {c:.2f}"
    if kind == "close_above":
        return int(c > claim["level"]), f"close {c:.2f} against {claim['level']}"
    if kind == "abs_open_close_under":
        move = (c / o - 1) * 100
        return int(abs(move) < claim["pct"]), f"open to close {move:+.2f}%"
    if kind == "close_between":
        return int(claim["low"] <= c <= claim["high"]), f"close {c:.2f} against {claim['low']}-{claim['high']}"
    raise ValueError(kind)


def score(docs, bars_by_symbol, done, today, through):
    """New score rows for the claims not yet in `done` ({(file, claim id)}) that can now be decided."""
    rows = []
    for name, doc in sorted(docs.items()):
        if validate(doc):
            continue
        for c in doc["claims"]:
            if (name, c["id"]) in done:
                continue
            got, detail = outcome(c, bars_by_symbol.get(c.get("symbol", "SPY"), {}), through)
            if got is None:
                continue
            rows.append({"scored_on": today, "file": name, "claim": c["id"], "horizon": c["horizon"],
                         "kind": c["kind"], "p": c["p"], "outcome": got,
                         "brier": round((c["p"] - got) ** 2, 4), "detail": detail})
    return rows


def summary(rows):
    """Plain lines per horizon: direction claims against 0.25, ranges against their stated rate."""
    out = []
    for h in HORIZONS:
        mine = [r for r in rows if r["horizon"] == h]
        if not mine:
            continue
        direct = [r for r in mine if r["kind"] != "close_between"]
        ranges = [r for r in mine if r["kind"] == "close_between"]
        line = f"{h}: {len(mine)} scored"
        if direct:
            b = sum(float(r["brier"]) for r in direct) / len(direct)
            line += f"; Brier {b:.3f} on {len(direct)} against 0.250 for always 0.50 ({'better' if b < 0.25 else 'not better'})"
        if ranges:
            hit = sum(int(r["outcome"]) for r in ranges)
            line += f"; ranges held {hit} of {len(ranges)} (stated about {float(ranges[0]['p']):.0%})"
        out.append(line)
    return out or ["nothing scored yet"]


def load_docs():
    return {p.name: json.loads(p.read_text()) for p in sorted(DIR.glob("*.json"))}


def load_scores():
    if not SCORES.exists():
        return []
    with SCORES.open() as f:
        return list(csv.DictReader(f))


def append_scores(rows):
    new = not SCORES.exists()
    with SCORES.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def closed_through(now):
    """The last date whose session has closed: today after 16:10 ET, else yesterday."""
    local = now.astimezone(ET)
    return local.date() if local.time() >= time(16, 10) else local.date() - timedelta(days=1)


def fetch(api, symbols, start, end, through):
    out = {}
    for s in symbols:
        bars = api.stock_bars(s, start, end, timeframe="1Day", feed="sip", adjustment="raw")
        out[s] = {b["t"][:10]: (b["o"], b["c"]) for b in bars if b["t"][:10] <= through}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", help="validate one forecast file")
    ap.add_argument("--score", action="store_true", help="score every claim that can now be decided")
    ap.add_argument("--summary", action="store_true", help="the scores so far, by horizon")
    args = ap.parse_args()
    if args.check:
        problems = validate(json.loads(open(args.check).read()))
        print("\n".join(problems) if problems else "ok")
        raise SystemExit(1 if problems else 0)
    if args.score:
        docs = load_docs()
        bad = {n: validate(d) for n, d in docs.items() if validate(d)}
        for n, problems in bad.items():
            print(f"skipped {n}: {'; '.join(problems)}")
        now = datetime.now(timezone.utc)
        through = closed_through(now).isoformat()
        dates = [c.get("date") or c.get("start") for d in docs.values() if not validate(d) for c in d["claims"]]
        if not dates:
            print("no claims")
            return
        start = datetime.combine(date.fromisoformat(min(dates)) - timedelta(days=7), time(), timezone.utc)
        symbols = sorted({c.get("symbol", "SPY") for d in docs.values() if not validate(d) for c in d["claims"]})
        from ..alpaca import Alpaca
        bars = fetch(Alpaca(), symbols, start, now - timedelta(minutes=20), through)
        done = {(r["file"], r["claim"]) for r in load_scores()}
        rows = score(docs, bars, done, closed_through(now).isoformat(), through)
        if rows:
            append_scores(rows)
        for r in rows:
            print(f"scored {r['file']} {r['claim']}: p {r['p']} outcome {r['outcome']} Brier {r['brier']} ({r['detail']})")
        print(f"{len(rows)} new; " + " | ".join(summary(load_scores())))
    if args.summary:
        print("\n".join(summary(load_scores())))


if __name__ == "__main__":
    main()
