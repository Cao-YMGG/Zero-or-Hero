"""Fetch Alpaca historical option bars for the jobs in a request file; write raw bars and a run log.

    python exchange/claude-c/optbars/fetch.py exchange/claude-c/optbars/request.json exchange/claude-c/optbars/out

Branch c/optbars only (claude-c's own branch). Needs APCA_API_KEY_ID / APCA_API_SECRET_KEY in the environment
(this repo's Actions secrets, shared with the repo's own research jobs by the owner's permission). Never prints them.
Rate: at most one request per 0.6 s (<= 100/min, half the free tier's 200) so the shared key keeps headroom.
A failed request is written as ERR with its HTTP status -- an error is never recorded as "no bars".
Stdlib only.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

DATA = "https://data.alpaca.markets/v1beta1/options/bars"
MIN_GAP_S = 0.6
MAX_PAGES = 50
_last = [0.0]


def _get(params):
    req = urllib.request.Request(DATA + "?" + urllib.parse.urlencode(params), headers={
        "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"],
        "Accept": "application/json"})
    err = None
    for attempt in range(5):
        wait = MIN_GAP_S - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return 200, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")[:300]
            if e.code == 429 or e.code >= 500:
                time.sleep(15 * (attempt + 1))
                continue
            return e.code, {"error": err}
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            err = str(e)[:300]
            time.sleep(10 * (attempt + 1))
    return -1, {"error": "gave up after 5 attempts: %s" % err}


def run(job):
    bars, pages, token, body = {}, 0, None, {}
    while True:
        params = {"symbols": ",".join(job["symbols"]), "timeframe": job["timeframe"], "start": job["start"],
                  "end": job["end"], "limit": 10000, "sort": "asc"}
        if token:
            params["page_token"] = token
        code, body = _get(params)
        pages += 1
        if code != 200:
            return {"id": job["id"], "ev": "ERR", "http": code, "error": body.get("error"), "pages": pages}
        for sym, bs in (body.get("bars") or {}).items():
            bars.setdefault(sym, []).extend(bs)
        token = body.get("next_page_token")
        if not token or pages >= MAX_PAGES:
            break
    return {"id": job["id"], "ev": "OK", "pages": pages, "truncated": bool(token), "bars": bars,
            "missing": [s for s in job["symbols"] if not bars.get(s)],
            "otherFields": sorted(k for k in body if k not in ("bars", "next_page_token"))}


def main(request_path, out_dir):
    jobs = json.load(open(request_path, encoding="utf-8"))["jobs"]
    os.makedirs(out_dir, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    counts = {"OK": 0, "ERR": 0, "missingSymbols": 0, "truncated": 0}
    with open(os.path.join(out_dir, "bars.jsonl"), "w", encoding="utf-8") as fh:
        for job in jobs:
            row = run(job)
            counts[row["ev"]] += 1
            counts["missingSymbols"] += len(row.get("missing", []))
            counts["truncated"] += bool(row.get("truncated"))
            if row["ev"] == "ERR":
                print("ERR %s http=%s %s" % (row["id"], row["http"], row["error"]), file=sys.stderr)
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")
    summary = {"started": started, "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "jobs": len(jobs), **counts}
    json.dump(summary, open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
