# Claude pre-market bias

A daily Claude session writes `YYYY-MM-DD.json` here (US/Eastern trading date) before the
open and pushes it to `main`. The live bot re-fetches `main` every 2 minutes until the file
appears; the `claude_bias` / `claude_confirm` variants trade it in shadow mode.

```json
{
  "date": "2026-10-05",
  "bias": "call",                 // "call", "put" or "none" (no trade)
  "confidence": 0.6,              // 0-1, how strongly the evidence points one way
  "summary": "one sentence",
  "reasons": ["...", "..."],
  "events": ["CPI 08:30"],        // scheduled releases / speakers today
  "inputs": {"es_futures_pct": 0.4, "vix": 16.2, "overnight": "..."},
  "generated_at": "2026-10-05T09:05:00-04:00"
}
```

Never edit a bias file after the open: it is the record the variant is scored on.
