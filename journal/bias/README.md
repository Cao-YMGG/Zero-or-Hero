# Claude pre-market bias

A daily Claude session writes `YYYY-MM-DD.json` here (US/Eastern trading date) before the
open and pushes it to `main`. The live bot re-fetches `main` every 2 minutes until the file
appears; the `claude_bias` / `claude_confirm` variants trade it in shadow mode.

```json
{
  "date": "2026-10-05",
  "bias": "call",                 // "call", "put" or "none" (no trade)
  "confidence": 0.6,              // 0-1, how strongly the evidence points one way (legacy)
  "p_up": 0.55,                   // since 2026-10-23: probability SPY closes above its OPEN today;
                                  // a call only at >= 0.60, a put only at <= 0.40, else "none"
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
  "opportunities": [              // since 2026-10-29: every opportunity spotted, traded or not
    {"type": "rotation_laggard", "symbol": "META", "direction": "call", "time": "10:00",
     "why": "-12% in a week after its offering, green pre-market while GOOGL -11%",
     "why_zh": "发债后一周跌 12%，谷歌跌 11% 时它盘前反而是红的",   // plain Chinese for Discord
     "conviction": "maybe",       // since 2026-11-16: "yes" (I would pick it if the bar allowed), "maybe",
                                  // or "no" (a control: it fits a type or is past a line, I expect it to fail)
     "action": "none"}            // "real" (sniper / pick), "shadow" or "none"
  ],
  "zh": {                         // since 2026-11-02: plain Chinese for the Discord posts (the owner
                                  // reads Chinese; no jargon, no tickers without a word of context)
    "summary": "一两句话：今天大盘怎么判断、为什么",
    "sniper": "选了谁、看涨还是看跌、因为什么消息；或者为什么今天不选",
    "heating": "医疗、必需消费、银行",
    "cooling": "CPU、存储、光模块、互联网"
  },
  "generated_at": "2026-10-05T09:05:00-04:00"
}
```

`opportunities` (owner, 2026-10-29: "list every kind of opportunity"): one entry per idea, with a
`type` key from journal/research/OPPORTUNITIES.md. The sniper and intraday picks are added
automatically. The intraday file may carry its own `opportunities` list, and
`journal/opportunities/<date>.json` (`{"date", "opportunities": [...]}`) holds ideas added later in
the day or at the review. `zoh/research/opportunities.py` scores all of them after the close
(stock move from `time`, default 10:00, to the close, signed by direction; open to close; best move
after entry) into journal/opportunities.csv, and the Notify workflow posts them to Discord. No
orders: a type that keeps scoring well becomes a variant.

The `catalyst_sniper` variant buys a ~0.2-delta nearest-expiry option on `sniper.symbol` only
if the stock has moved >= 1% from its open in the stated direction after 09:45 (price
confirmation). Pick only mega caps with same-day options (META, NVDA, TSLA, AAPL, AMZN, MSFT,
GOOGL, AVGO, AMD, MU...) and only for a fresh, non-earnings catalyst whose effect is not
already in a big pre-market gap (> 4%): product traction, legal rulings, regulatory news,
major contracts, sector-moving news. Research (journal/research/SNIPER.md) shows a purely
mechanical "biggest mover" rule fires most days and loses; the edge has to come from the
catalyst judgment. Since v17 (paper account, the owner asked for boldness) name a pick on
most days that have a fresh catalyst with a small gap, an upgrade being the most common one
(journal/research/ANALYST.md: upgrades carry, downgrades do not). `catalyst_open` buys a
~0.1-delta option at the open (from 09:31, as long as the stock is not against the pick) and
trails; `catalyst_sniper` keeps the 1% confirmation. Null only when nothing qualifies.
On a `put` day with aligned macro evidence the sniper may be a put (`"direction": "put"`): a
mega cap without good news of its own that is exposed to the day's driver (rates, a cooling
theme, a peer's miss), gap under ~4%. Both catalyst variants trade puts the same way
(catalyst_open buys at the open as long as the stock is not above it).
What matters is whether the move is already in the price, not source vs echo. Pick the
name in the catalyst chain with the most catalyst left relative to its gap: on 2026-09-21
Meta (source, gap +2.3%) ran +10% while the CPU echoes had gapped 4-7%; on 2026-06-11
Intel (source) gapped +6% and added 3%, while AMD (echo, gap +2%) ran +5.8%. News that
breaks during market hours is the best case (2026-05-08 WSJ Apple-Intel report: both INTC
and AMD gapped ~2% and ran +9-12%); news already gapped pre-market (2026-06-18 Intel-Apple
post, INTC +8.8% gap) is usually spent.

Two more patterns from 2026-10-05: (1) a same-morning analyst upgrade with a small gap (Melius upgraded MSFT to Buy, gap +0.9%, then +1.5% from the open in 15 minutes); (2) the day after a sharp non-earnings selloff on a supply/competition headline, when the sell side pushes back pre-market (WDC -10% on 10/2 on Toshiba doubling HDD capacity; Bernstein, Citi and Morgan Stanley said supply stays tight through 2028; WDC gapped +3.5% and was +6.6% by 09:55, STX +5.4%). A theme marked "cooling" after a one-day headline drop is a rebound candidate, not a fade. WDC/STX only have Friday expiries, so on other days the sniper uses the nearest expiry.

Third pattern from 2026-10-05, the other side of the same headline: Musk said TSMC is in talks to help run Terafab. INTC fell -3.7% pre-market (the loser was priced), while TSLA (the beneficiary, plus a Q3 delivery beat) was -0.4% pre-market, dipped to -1% in the first 15 minutes and then climbed to +3.2% from the open by 15:20. When news moves one name pre-market, check who is on the other side of it and whether that name has moved yet.

Never edit a bias file after the open: it is the record the variant is scored on.

## Intraday picks (since v19)

Weekday check-ins at about 10:30 and 13:00 ET may add a pick to
`journal/bias/intraday/YYYY-MM-DD.json` (the pre-market file above stays untouched):

```json
{"date": "2026-10-06",
 "picks": [{"time": "10:32", "symbol": "AMD", "direction": "call", "confidence": 0.6,
            "catalyst": "news that broke after the open and is not yet in the price",
            "catalyst_zh": "开盘后才出的消息，股价还没反映（Discord 用的中文）"}]}
```
Opportunities in this file also carry `why_zh` (plain Chinese for Discord), as in the pre-market file.

Append, never rewrite earlier picks. The bot re-reads main every 2 minutes and
`catalyst_intraday` books a ~0.2-delta same-day/nearest option on the latest pick right away
(until 14:30), then trails; shadow-only since 2026-11-09 (the hero shadow takes the full ledger),
real money returns when the live rule is positive over 20 more picks. Bar: news that broke during the session (the best case in the
research, e.g. 2026-05-08 WSJ Apple-Intel), or a big move with a clear cause that is still
unfolding. Most check-ins should add nothing.
