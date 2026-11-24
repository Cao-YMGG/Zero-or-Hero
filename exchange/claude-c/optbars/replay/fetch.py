"""Raw data for claude-c's replay of two rule-based paper books (branch c/optbars only).

    python exchange/claude-c/optbars/replay/fetch.py exchange/claude-c/optbars/replay/request.json exchange/claude-c/optbars/replay/out

For each candidate (book, symbol, day) in request.json -- a day whose low / high crossed
prev close x (1 -/+ move) on adjusted daily bars -- this records, with raw (unadjusted) prices:
  - the first 5-minute tick (09:36, 09:41, ... 15:46 ET) whose 1-minute close is at or past the raw line;
  - the monthly expiry nearest 90 days (60..130) and the two strikes (long nearest the price, short nearest 2.5% further);
  - each leg's 1-minute close nearest the tick within +-60 minutes (ties -> the later bar);
  - control rows (fixedTick) skip the line and enter at that tick;
  - each leg's daily closes from the signal day to 10 days past (expiry - 21 days).
Scoring (exits, limits, statistics) is done elsewhere from these rows; nothing here decides a trade's outcome.
Read-only: market data plus the read-only options contract list. Never touches orders or account endpoints.
<= 100 requests/min (one per 0.6 s) on the shared key. Every failure is a row with its status -- never silently empty.
"""
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

DATA = "https://data.alpaca.markets"
TRADING = "https://paper-api.alpaca.markets"     # used ONLY for GET /v2/options/contracts (read-only reference data)
ET = ZoneInfo("America/New_York")
MIN_GAP_S = 0.6
_last = [0.0]
COUNTS = {"requests": 0, "httpErrors": 0}
TICKS = ["%02d:%02d" % divmod(m, 60) for m in range(9 * 60 + 36, 15 * 60 + 47, 5)]   # 09:36 .. 15:46
TARGET_DTE, DTE_MIN, DTE_MAX = 90, 60, 130
WIDTH_PCT = 0.025
TIME_EXIT_DAYS = 21
ENTRY_WINDOW_MIN = 60   # +- minutes around the tick (spec amendment 15:05 ET; was 30 after only)


def get(url, params):
    req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers={
        "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"], "Accept": "application/json"})
    err = None
    for attempt in range(5):
        wait = MIN_GAP_S - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        COUNTS["requests"] += 1
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return 200, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(15 * (attempt + 1))
                continue
            COUNTS["httpErrors"] += 1
            return e.code, {"error": err}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = str(e)[:300]
            time.sleep(10 * (attempt + 1))
    COUNTS["httpErrors"] += 1
    return -1, {"error": "gave up after 5 attempts: %s" % err}


def bars_paged(url, params):
    """Multi-symbol bars endpoint -> (code, err, {symbol: [bar]})."""
    out, token = {}, None
    for _ in range(50):
        p = dict(params)
        if token:
            p["page_token"] = token
        code, body = get(url, p)
        if code != 200:
            return code, body.get("error"), out
        for s, bs in (body.get("bars") or {}).items():
            out.setdefault(s, []).extend(bs)
        token = body.get("next_page_token")
        if not token:
            return 200, None, out
    return 200, "TRUNCATED_AT_50_PAGES", out


def contracts_paged(params):
    out, token = [], None
    for _ in range(50):
        p = dict(params)
        if token:
            p["page_token"] = token
        code, body = get(TRADING + "/v2/options/contracts", p)
        if code != 200:
            return code, body.get("error"), out
        out.extend(body.get("option_contracts") or [])
        token = body.get("next_page_token")
        if not token:
            return 200, None, out
    return 200, "TRUNCATED_AT_50_PAGES", out


def et(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ET)


def z(t):
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def et_dt(day, hhmm):
    d = date.fromisoformat(day)
    h, m = map(int, hhmm.split(":"))
    return datetime(d.year, d.month, d.day, h, m, tzinfo=ET)


def first_cross(minutes, line, book):
    """minutes: sorted [(HH:MM, close)]. The first tick whose last close at or before it is at/past the line."""
    i, last = 0, None
    for tick in TICKS:
        while i < len(minutes) and minutes[i][0] <= tick:
            last = minutes[i][1]
            i += 1
        if last is None:
            continue
        if (book == "paper-dip-v1" and last <= line) or (book == "paper-rip-v1" and last >= line):
            return tick, last
    return None, None


def monthly_expiries(dates):
    """Third-Friday monthly expiries; the same week's Thursday when that Friday is not listed (holiday)."""
    by_month = {}
    for d in dates:
        dd = date.fromisoformat(d)
        if 15 <= dd.day <= 21 and dd.weekday() in (3, 4):
            by_month.setdefault((dd.year, dd.month), {})[dd.weekday()] = d
    return {v.get(4) or v.get(3) for v in by_month.values()}


def choose_expiry(dates, day):
    d0 = date.fromisoformat(day)
    ok = [(abs((date.fromisoformat(e) - d0).days - TARGET_DTE), e) for e in monthly_expiries(dates)
          if DTE_MIN <= (date.fromisoformat(e) - d0).days <= DTE_MAX]
    return min(ok)[1] if ok else None


def choose_strikes(chain, price, option_type):
    """Same as moomoo_paper.choose_strikes. chain: [(strike, code)]."""
    rows = sorted({(float(k), c) for k, c in chain})
    if len(rows) < 2:
        return None
    if option_type == "call":
        long_ = min(rows, key=lambda r: (abs(r[0] - price), r[0]))
        beyond = [r for r in rows if r[0] > long_[0]]
        target = price * (1 + WIDTH_PCT)
    else:
        long_ = min(rows, key=lambda r: (abs(r[0] - price), -r[0]))
        beyond = [r for r in rows if r[0] < long_[0]]
        target = price * (1 - WIDTH_PCT)
    if not beyond:
        return None
    short = min(beyond, key=lambda r: abs(r[0] - target))
    return long_, short


def main(req_path, out_dir):
    req = json.load(open(req_path, encoding="utf-8"))
    cands = req["candidates"][: req.get("limit") or None]
    os.makedirs(out_dir, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = date.today()
    rows = {c["id"]: dict(c, status="NOT_PROCESSED") for c in cands}

    # 1. raw daily closes per symbol
    syms = sorted({c["sym"] for c in cands})
    lo = (date.fromisoformat(min(c["prevDay"] for c in cands)) - timedelta(days=7)).isoformat()
    hi = max(c["day"] for c in cands)
    code, err, daily = bars_paged(DATA + "/v2/stocks/bars", {"symbols": ",".join(syms), "timeframe": "1Day",
                                                          "start": lo, "end": hi, "adjustment": "raw", "feed": "sip",
                                                          "limit": 10000})
    raw = {s: {et(b["t"]).date().isoformat(): b["c"] for b in daily.get(s, [])} for s in syms}
    if code != 200:
        print("raw daily error http=%s %s" % (code, err), file=sys.stderr)

    # 2. stock minute bars per day, first tick across the raw line
    by_day = {}
    for c in cands:
        by_day.setdefault(c["day"], []).append(c)
    for day, cs in sorted(by_day.items()):
        try:
            code, err, mb = bars_paged(DATA + "/v2/stocks/bars", {
                "symbols": ",".join(sorted({c["sym"] for c in cs})), "timeframe": "1Min",
                "start": z(et_dt(day, "09:30")), "end": z(et_dt(day, "16:00")), "adjustment": "raw", "feed": "sip",
                "limit": 10000, "sort": "asc"})
            for c in cs:
                r = rows[c["id"]]
                prev = raw.get(c["sym"], {}).get(c["prevDay"])
                if prev is None:
                    r["status"] = "NO_RAW_PREV"
                    continue
                line = round(prev * (1 - c["move"]) if c["book"] == "paper-dip-v1" else prev * (1 + c["move"]), 2)
                r.update(prevRaw=prev, line=line)
                if code != 200:
                    r.update(status="ERR_STOCK_MIN", err="http=%s %s" % (code, err))
                    continue
                mins = sorted((et(b["t"]).strftime("%H:%M"), b["c"]) for b in mb.get(c["sym"], []))
                if not mins:
                    r["status"] = "NO_STOCK_MIN"
                    continue
                if c.get("fixedTick"):   # control row: no line, enter at the fixed tick
                    before = [p for m, p in mins if m <= c["fixedTick"]]
                    if not before:
                        r["status"] = "NO_TICK_CROSS"
                        continue
                    r.update(tick=c["fixedTick"], px=before[-1], pastLine=None, status="CROSSED")
                    continue
                tick, px = first_cross(mins, line, c["book"])
                if tick is None:
                    r["status"] = "NO_TICK_CROSS"
                    continue
                past = (line - px) / line if c["book"] == "paper-dip-v1" else (px - line) / line
                r.update(tick=tick, px=px, pastLine=round(past, 6), status="CROSSED")
        except Exception as e:  # noqa: BLE001 -- one bad day must not end the run
            for c in cs:
                rows[c["id"]].update(status="ERR_EXCEPTION", err="%s: %s" % (type(e).__name__, str(e)[:200]))
            traceback.print_exc()

    # 3. contracts and strikes per crossed candidate
    for cid, r in rows.items():
        if r["status"] != "CROSSED":
            continue
        try:
            typ = "call" if r["book"] == "paper-dip-v1" else "put"
            d0 = date.fromisoformat(r["day"])
            e_lo, e_hi = d0 + timedelta(days=DTE_MIN), d0 + timedelta(days=DTE_MAX)
            statuses = ["inactive"] if e_hi < today - timedelta(days=1) else ["inactive", "active"]
            got, code, err = [], 200, None
            for st in statuses:
                code, err, part = contracts_paged({
                    "underlying_symbols": r["sym"], "type": typ, "status": st,
                    "expiration_date_gte": e_lo.isoformat(), "expiration_date_lte": e_hi.isoformat(),
                    "strike_price_gte": "%.2f" % (0.8 * r["px"]), "strike_price_lte": "%.2f" % (1.2 * r["px"]),
                    "limit": 10000})
                if code != 200:
                    break
                got += part
            if code != 200:
                r.update(status="ERR_CONTRACTS", err="http=%s %s" % (code, err))
                continue
            got = [x for x in got if x.get("root_symbol", r["sym"]) == r["sym"]
                   and x.get("underlying_symbol", r["sym"]) == r["sym"] and x.get("type") == typ]
            expiry = choose_expiry(sorted({x["expiration_date"] for x in got}), r["day"])
            if expiry is None:
                r.update(status="NO_EXPIRY", nContracts=len(got))
                continue
            pick = choose_strikes([(x["strike_price"], x["symbol"]) for x in got if x["expiration_date"] == expiry],
                                  r["px"], typ)
            if pick is None:
                r.update(status="NO_STRIKES", expiry=expiry)
                continue
            (lk, lcode), (sk, scode) = pick
            r.update(expiry=expiry, longK=lk, shortK=sk, long=lcode, short=scode, status="PICKED",
                     timeExit=(date.fromisoformat(expiry) - timedelta(days=TIME_EXIT_DAYS)).isoformat())
        except Exception as e:  # noqa: BLE001
            r.update(status="ERR_EXCEPTION", err="%s: %s" % (type(e).__name__, str(e)[:200]))
            traceback.print_exc()

    # 4. entry prices: each leg's 1-minute close nearest the tick, within +-60 minutes, ties -> the later bar
    #    (spec amendment 15:05 ET: the first smoke run found 13/24 legs with no trade in the 30 minutes after the tick)
    picked_by_day = {}
    for r in rows.values():
        if r["status"] == "PICKED":
            picked_by_day.setdefault(r["day"], []).append(r)
    for day, rs in sorted(picked_by_day.items()):
        try:
            code, err, ob = bars_paged(DATA + "/v1beta1/options/bars", {
                "symbols": ",".join(sorted({x for r in rs for x in (r["long"], r["short"])})), "timeframe": "1Min",
                "start": z(et_dt(day, "09:30")), "end": z(et_dt(day, "16:00")), "limit": 10000, "sort": "asc"})
            for r in rs:
                if code != 200:
                    r.update(status="ENTRY_PRICED", minuteEntry=False, minuteErr="http=%s %s" % (code, err))
                    continue
                t = et_dt(day, r["tick"])
                legs = {}
                for side in ("long", "short"):
                    near = []
                    for x in ob.get(r[side], []):
                        gap = (et(x["t"]) - t).total_seconds() / 60.0
                        if abs(gap) <= ENTRY_WINDOW_MIN:
                            near.append((abs(gap), -gap, x, gap))
                    if near:
                        _, _, x, gap = min(near, key=lambda n: (n[0], n[1]))
                        legs[side] = (x["c"], et(x["t"]).strftime("%H:%M"), x.get("v"), round(gap, 1))
                if len(legs) < 2:
                    # spec amendment 15:15 ET: the main result enters at the signal day's close, so the daily
                    # closes are still fetched; the minute entry is only the side comparison.
                    r.update(status="ENTRY_PRICED", minuteEntry=False, legsFound=sorted(legs))
                    continue
                r.update(longEntry=legs["long"][0], longEntryT=legs["long"][1], longEntryV=legs["long"][2],
                         longGapMin=legs["long"][3], shortEntry=legs["short"][0], shortEntryT=legs["short"][1],
                         shortEntryV=legs["short"][2], shortGapMin=legs["short"][3], minuteEntry=True,
                         status="ENTRY_PRICED")
        except Exception as e:  # noqa: BLE001
            for r in rs:
                r.update(status="ERR_EXCEPTION", err="%s: %s" % (type(e).__name__, str(e)[:200]))
            traceback.print_exc()

    # 5. daily closes of both legs from the signal day to 10 days past the time exit (or yesterday)
    for r in rows.values():
        if r["status"] != "ENTRY_PRICED":
            continue
        try:
            end = min(date.fromisoformat(r["timeExit"]) + timedelta(days=10), today - timedelta(days=1))
            code, err, db = bars_paged(DATA + "/v1beta1/options/bars", {
                "symbols": "%s,%s" % (r["long"], r["short"]), "timeframe": "1Day",
                "start": r["day"], "end": end.isoformat(), "limit": 10000, "sort": "asc"})
            if code != 200:
                r.update(status="ERR_OPT_DAY", err="http=%s %s" % (code, err))
                continue
            r["daily"] = {side: [[et(x["t"]).date().isoformat(), x["c"], x.get("v")] for x in db.get(r[side], [])]
                          for side in ("long", "short")}
            r["dailyEnd"] = end.isoformat()
            r["status"] = "OK"
        except Exception as e:  # noqa: BLE001
            r.update(status="ERR_EXCEPTION", err="%s: %s" % (type(e).__name__, str(e)[:200]))
            traceback.print_exc()

    counts = {}
    with open(os.path.join(out_dir, "rows.jsonl"), "w", encoding="utf-8") as fh:
        for c in cands:
            r = rows[c["id"]]
            counts[r["status"]] = counts.get(r["status"], 0) + 1
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    summary = {"started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "candidates": len(cands), "symbols": syms, "byStatus": counts, **COUNTS}
    json.dump(summary, open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
