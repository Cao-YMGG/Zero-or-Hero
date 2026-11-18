# claude-c: Alpaca option bars (branch `c/optbars` only)

The owner allowed claude-c (2026-11-18) to share this repo's Alpaca paper key for **market data only**.
Nothing here places orders or touches the trading endpoints. Nothing here runs on `main` or `claude/**`.

- `request.json` -- jobs: OCC option symbols, timeframe, start/end (UTC). Built by claude-c from its own ledgers.
- `fetch.py` -- stdlib fetcher for `GET data.alpaca.markets/v1beta1/options/bars`; <= 100 requests/min so this
  repo's own research jobs keep headroom on the shared key; every failed request is logged as ERR, never as "no bars".
- `out/bars.jsonl`, `out/summary.json` -- raw bars and the run summary, committed by the workflow
  `.github/workflows/c-optbars.yml` to this branch.

Stage 1 (this push) is a probe: bars for 16 recorded straddles (12 earnings, Oct-Nov 2026) are compared with
the mids claude-c recorded. Only if they agree (criterion frozen before the fetch) is a larger pull made.
