# claude-c: Alpaca option bars (branch `c/optbars` only)

The owner allowed claude-c (2026-11-18) to share this repo's Alpaca paper key for **market data only**.
Nothing here places orders or reads the account. The only call to the trading host is the read-only
`GET /v2/options/contracts` (contract list, used by `straddles.py`). Nothing here runs on `main` or `claude/**`.

- `request.json` -- jobs: OCC option symbols, timeframe, start/end (UTC). Built by claude-c from its own ledgers.
- `fetch.py` -- stdlib fetcher for `GET data.alpaca.markets/v1beta1/options/bars`; <= 100 requests/min so this
  repo's own research jobs keep headroom on the shared key; every failed request is logged as ERR, never as "no bars".
- `out/bars.jsonl`, `out/summary.json` -- raw bars and the run summary, committed by the workflow
  `.github/workflows/c-optbars.yml` to this branch.

Stage 1 (this push) is a probe: bars for 16 recorded straddles (12 earnings, Oct-Nov 2026) are compared with
the mids claude-c recorded. Only if they agree (criterion frozen before the fetch) is a larger pull made.

Stage 1 result: PASS -- 16/16 rows had both legs; median |Alpaca - recorded mid| = 0.26%, max 2.1%.
Stage 2: `straddles.py` + `request-v2c.json` -> `out-v2c/` -- ATM straddle (earliest expiry within 14 days after the
reaction session, strike nearest the raw close) from each leg's last 1-minute bar in 15:30-16:00 ET on the last
pre-earnings close, for 4,455 earnings events since 2024-02.
Stage 3: `replay/fetch.py` + `replay/request.json` -> `replay/out/` -- raw data for a replay of two rule-based
paper books (buy a call debit spread after a two-sigma down day, a put debit spread after a two-sigma up day; SPY,
QQQ and seven large caps, signal days since 2024-02): the first 5-minute tick across the line on raw 1-minute stock
bars, the monthly contracts nearest 90 days, each leg's entry price within 30 minutes and its daily closes to the
time exit. Same read-only calls and the same 100-requests/minute ceiling as stages 1-2. Outcomes are scored elsewhere.
