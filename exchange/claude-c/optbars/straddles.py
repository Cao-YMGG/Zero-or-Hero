"""ATM straddle at the p close for each earnings event in request-v2c.json (claude-c, branch c/optbars only).

    python exchange/claude-c/optbars/straddles.py exchange/claude-c/optbars/request-v2c.json exchange/claude-c/optbars/out-v2c

Rules (frozen in claude-c's spec before this ran):
- spot = raw (unadjusted) daily close on p, Alpaca stock bars (adjustment=raw, feed=sip).
- expiry = earliest listed expiry in [t1, expiryTo] that has a call and a put at the same strike (standard root only);
  strike = listed strike nearest spot, ties -> lower.
- price = close of each leg's last 1-minute bar in [15:30, 16:00) America/New_York on p; a missing leg drops the event.
Read-only: market data plus the read-only options contract list. Never touches orders or account endpoints.
<= 100 requests/min (one per 0.6 s) on the shared key. Every failure is a row with its status -- never silently empty.
"""
import json
import os
import sys
import time
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


def paged(url, params, key):
    out, token = [], None
    for _ in range(50):
        p = dict(params)
        if token:
            p["page_token"] = token
        code, body = get(url, p)
        if code != 200:
            return code, body.get("error"), out
        out.extend(body.get(key) or [])
        token = body.get("next_page_token")
        if not token:
            return 200, None, out
    return 200, "TRUNCATED_AT_50_PAGES", out


def raw_closes(sym, start, end):
    """ET date -> raw close."""
    closes, token = {}, None
    for _ in range(20):
        params = {"symbols": sym, "timeframe": "1Day", "start": start, "end": end, "adjustment": "raw",
                  "feed": "sip", "limit": 10000}
        if token:
            params["page_token"] = token
        code, body = get(DATA + "/v2/stocks/bars", params)
        if code != 200:
            return code, body.get("error"), closes
        for b in (body.get("bars") or {}).get(sym, []):
            d = datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET).date().isoformat()
            closes[d] = b["c"]
        token = body.get("next_page_token")
        if not token:
            break
    return 200, None, closes


def choose(sym, contracts, spot):
    by = {}
    for c in contracts:
        if c.get("root_symbol", sym) != sym or c.get("underlying_symbol", sym) != sym:
            continue
        k = (c["expiration_date"], float(c["strike_price"]))
        by.setdefault(k, {})[c["type"]] = c["symbol"]
    pairs = {k: v for k, v in by.items() if "call" in v and "put" in v}
    if not pairs:
        return None
    expiry = min(k[0] for k in pairs)
    strikes = sorted(k[1] for k in pairs if k[0] == expiry)
    strike = min(strikes, key=lambda s: (abs(s - spot), s))
    v = pairs[(expiry, strike)]
    return {"expiry": expiry, "strike": strike, "call": v["call"], "put": v["put"]}


def main(req_path, out_dir):
    events = json.load(open(req_path, encoding="utf-8"))["events"]
    os.makedirs(out_dir, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today = date.today()
    syms = sorted({e["sym"] for e in events})
    lo = min(e["p"] for e in events)
    hi = max(e["p"] for e in events)
    spots, spot_err = {}, {}
    for s in syms:
        code, err, closes = raw_closes(s, lo, hi)
        if code != 200:
            spot_err[s] = "http=%s %s" % (code, err)
        spots[s] = closes
    rows, picks = {}, {}
    for e in events:
        sp = spots.get(e["sym"], {}).get(e["p"])
        if sp is None:
            rows[e["id"]] = dict(e, status="NO_SPOT", err=spot_err.get(e["sym"]))
            continue
        statuses = ["inactive"] if date.fromisoformat(e["expiryTo"]) < today - timedelta(days=1) else ["inactive", "active"]
        contracts, err = [], None
        for st in statuses:
            code, err, got = paged(TRADING + "/v2/options/contracts", {
                "underlying_symbols": e["sym"], "expiration_date_gte": e["t1"], "expiration_date_lte": e["expiryTo"],
                "strike_price_gte": "%.2f" % (0.7 * sp), "strike_price_lte": "%.2f" % (1.3 * sp), "status": st,
                "limit": 10000}, "option_contracts")
            if code != 200:
                break
            contracts += got
        if code != 200:
            rows[e["id"]] = dict(e, spot=sp, status="ERR_CONTRACTS", err="http=%s %s" % (code, err))
            continue
        pick = choose(e["sym"], contracts, sp)
        if pick is None:
            rows[e["id"]] = dict(e, spot=sp, status="NO_EXPIRY", nContracts=len(contracts))
            continue
        picks[e["id"]] = dict(e, spot=sp, **pick)
    by_p = {}
    for eid, pk in picks.items():
        by_p.setdefault(pk["p"], []).append(pk)
    for p, pks in sorted(by_p.items()):
        d = date.fromisoformat(p)
        start = datetime(d.year, d.month, d.day, 15, 30, tzinfo=ET).astimezone(timezone.utc)
        end = datetime(d.year, d.month, d.day, 16, 0, tzinfo=ET).astimezone(timezone.utc)
        for i in range(0, len(pks), 50):
            chunk = pks[i:i + 50]
            syms_c = [x for pk in chunk for x in (pk["call"], pk["put"])]
            bars, token, code, err = {}, None, 200, None
            for _ in range(20):
                params = {"symbols": ",".join(syms_c), "timeframe": "1Min", "limit": 10000, "sort": "asc",
                          "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "end": end.strftime("%Y-%m-%dT%H:%M:%SZ")}
                if token:
                    params["page_token"] = token
                code, body = get(DATA + "/v1beta1/options/bars", params)
                if code != 200:
                    err = body.get("error")
                    break
                for s, bs in (body.get("bars") or {}).items():
                    bars.setdefault(s, []).extend(bs)
                token = body.get("next_page_token")
                if not token:
                    break
            for pk in chunk:
                if code != 200:
                    rows[pk["id"]] = dict(pk, status="ERR_BARS", err="http=%s %s" % (code, err))
                    continue
                legs = {}
                for side in ("call", "put"):
                    bs = [b for b in bars.get(pk[side], []) if b["t"] < end.strftime("%Y-%m-%dT%H:%M:%SZ")]
                    if bs:
                        last = max(bs, key=lambda b: b["t"])
                        legs[side] = (last["c"], last["t"], last.get("v"))
                if len(legs) < 2:
                    rows[pk["id"]] = dict(pk, status="NO_BARS", legsFound=sorted(legs))
                    continue
                rows[pk["id"]] = dict(pk, status="OK", callPx=legs["call"][0], callT=legs["call"][1],
                                      callVol=legs["call"][2], putPx=legs["put"][0], putT=legs["put"][1],
                                      putVol=legs["put"][2])
    counts = {}
    with open(os.path.join(out_dir, "straddles.jsonl"), "w", encoding="utf-8") as fh:
        for e in events:
            r = rows.get(e["id"], dict(e, status="NOT_PROCESSED"))
            counts[r["status"]] = counts.get(r["status"], 0) + 1
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    summary = {"started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "events": len(events), "symbols": len(syms), "symbolsWithSpotErrors": len(spot_err),
               "byStatus": counts, **COUNTS}
    json.dump(summary, open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary))
    if spot_err:
        print("spot errors (first 10): %s" % list(spot_err.items())[:10], file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
