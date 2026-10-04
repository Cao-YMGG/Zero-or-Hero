# AMD dossier

Read before every pre-market call and sniper pick. Evidence: `PROFILE_AMD.md` (2026 minute
data), `underlyings/AMD.md` (1-year backtest), EVOLUTION.md v7–v10.

## Personality
- Very volatile: intraday vol ~50% (close-to-close 72% because of big overnight gaps).
  Median open→close 2.1%, range 4.4%; 62 days ≥3% and 23 days ≥5% in 2026.
- **Moves with the CPU / semis group, not NVDA**: open→close correlation SMH 0.78, QQQ 0.72,
  INTC 0.65, NVDA only 0.46. Its biggest days are Intel / CPU days (1/21, 3/09, 4/02, 5/08,
  6/16, 6/30: INTC moved 5–12% the same way). No usable 5-minute lead/lag.
- A fifth of the day's movement happens 09:30–10:00; after 11:00 it's quiet until a small
  pickup into the close.
- Wednesday is the most volatile day (median 2.5%, 14 days ≥3%); Friday the calmest.
  Same-day options exist Mon/Wed/Fri.

## What has (and hasn't) worked
- **Down gap ≥ 2% → it bounces**: gaps under −2% continued only 42% (median open→close
  +0.5%). `amd_gap_rebound` (buy calls 15 min after a ≥2% down gap, non-macro days):
  +24%/trade over 20 trades, +101% over the last 7. Small sample; shadow only.
- Up gap ≥ 2% → the stock continues (64%, gap filled 11%), but buying calls at 09:45 lost
  (`amd_gap_go` −40%/trade): too much already priced, options expensive.
- Early move from the open is not a reliable trend signal: small moves by 10:00 tend to
  reverse (only 30% kept going); bigger ones are ~57/43.
- Earnings: median run-up into the report +5.8% vs SPY, median reaction day −6.8%. Never
  hold into the print.

## Catalyst chain to watch
Intel news (foundry wins, CEO comments on CPU demand), CPU pricing (price hikes from AMD or
clouds), agentic-AI CPU demand stories (e.g. Meta Muse), TSMC monthly sales, NVDA/AVGO
earnings, hyperscaler capex, China export rules. Intraday-breaking Intel news is the best
setup (5/8: AMD +8.7% open→close); news already gapped pre-market is usually spent.
