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
  "inputs": {"es_futures_pct": 0.4, "vix": 16.2, "wti_pct": -1.2, "us10y": 4.12,
             "us10y_change_bp": -3, "us2y_change_bp": -2, "dxy_pct": 0.1, "overnight": "..."},
  "rotation": {                   // theme baskets, 1-week / 1-month returns
    "heating": ["optical (LITE +15% 1w)", "GPU (NVDA +4% 1w)"],
    "cooling": ["CPU (INTC -3% 1w after +33% 1m)", "storage (WDC -9% 1w)"],
    "note": "money rotating from CPU into optical; SPY flat while themes diverge"
  },
  "sniper": {                     // optional: at most ONE single stock with a fresh catalyst
    "symbol": "META", "direction": "call",
    "catalyst": "Muse hit #1 on the US App Store over the weekend; Wells Fargo PT raise",
    "confidence": 0.6
  },                              // or null when nothing qualifies (most days)
  "generated_at": "2026-10-05T09:05:00-04:00"
}
```

The `catalyst_sniper` variant buys a ~0.2-delta nearest-expiry option on `sniper.symbol` only
if the stock has moved >= 1% from its open in the stated direction after 09:45 (price
confirmation). Pick only mega caps with same-day options (META, NVDA, TSLA, AAPL, AMZN, MSFT,
GOOGL, AVGO, AMD, MU...) and only for a fresh, non-earnings catalyst whose effect is not
already in a big pre-market gap (> 4%): product traction, legal rulings, regulatory news,
major contracts, sector-moving news. Research (journal/research/SNIPER.md) shows a purely
mechanical "biggest mover" rule fires most days and loses; the edge has to come from the
catalyst judgment. Leave it null unless the case is clear.
What matters is whether the move is already in the price, not source vs echo. Pick the
name in the catalyst chain with the most catalyst left relative to its gap: on 2026-09-21
Meta (source, gap +2.3%) ran +10% while the CPU echoes had gapped 4-7%; on 2026-06-11
Intel (source) gapped +6% and added 3%, while AMD (echo, gap +2%) ran +5.8%. News that
breaks during market hours is the best case (2026-05-08 WSJ Apple-Intel report: both INTC
and AMD gapped ~2% and ran +9-12%); news already gapped pre-market (2026-06-18 Intel-Apple
post, INTC +8.8% gap) is usually spent.

Two more patterns from 2026-10-05: (1) a same-morning analyst upgrade with a small gap (Melius upgraded MSFT to Buy, gap +0.9%, then +1.5% from the open in 15 minutes); (2) the day after a sharp non-earnings selloff on a supply/competition headline, when the sell side pushes back pre-market (WDC -10% on 10/2 on Toshiba doubling HDD capacity; Bernstein, Citi and Morgan Stanley said supply stays tight through 2028; WDC gapped +3.5% and was +6.6% by 09:55, STX +5.4%). A theme marked "cooling" after a one-day headline drop is a rebound candidate, not a fade. WDC/STX only have Friday expiries, so on other days the sniper uses the nearest expiry.

Never edit a bias file after the open: it is the record the variant is scored on.
