# Opportunity tests on daily bars — 2026-10-29

57 large caps in 9 sector groups plus their sector ETFs, Alpaca SIP daily bars 2024-09 to
2026-10-28 (`python -m zoh.research.rotation fetch|analyze`). Stock moves only, no option prices
yet. "3 mo" = since 2026-07-29 (leads, per CLAUDE.md); w/o best = average without the best trade.

## Sell the news: gap up, follow from the open, by theme state

Theme state = the stock's sector ETF 21-day return minus SPY's, as of the prior close.

| gap | theme | 2y n | 2y avg | 2y up | 3 mo n | 3 mo avg | 3 mo up | 3 mo w/o 2 |
|---|---|---|---|---|---|---|---|---|
| >= 2% | heating (> +2%) | 619 | +0.00% | 49% | 67 | +0.62% | 54% | +0.31% |
| >= 2% | neutral | 471 | -0.37% | 46% | 52 | +0.13% | 58% | -0.13% |
| >= 2% | cooling (< -2%) | 510 | -0.34% | 45% | 113 | **-0.72%** | **37%** | -0.92% |
| >= 3% | heating | 300 | +0.21% | 50% | 28 | **+1.67%** | 64% | +0.96% |
| >= 3% | cooling | 237 | -0.64% | 41% | 59 | **-0.84%** | 37% | -1.23% |

Next day after the gap: no continuation (cooling +0.18% over 3 months). The split is a
current-regime effect (two-year gap small): a candidate, and the strongest of today's ideas.

By the 10 days before the gap (2 years): after a > 5% fall -0.90% open to close (40% up), flat
-0.18%, after a > 5% run-up +0.32%. Good news after a fall fades most; "it already ran up, so it
gets sold" is not what the data shows.

## Rotation laggard

Shock = a stock in internet / software / chips gaps down <= -5% while SPY's gap is > -1%. The
laggard (worst 21-day return in that group, green at the open), open to close: 32 events +0.40%
avg, 59% up, w/o 2 +0.09%; 3 months 8 events +0.32%, w/o best -0.41%. Other green members that day
-0.16%. Baseline (group laggard green at the open on any day) -0.09% (2y), +0.51% (3 mo). No edge.

Chip-selloff day (chip basket gap <= -1.5%, SPY gap > -0.7%) -> internet laggard green at the open:
21 events +0.32% (w/o 2 -0.02%); 3 months 8 events **+1.29%, 75% up**, w/o 2 +0.54% (META 08-03
+5.0%, 08-24 +1.6%; NFLX six times). Candidate on a small, recent sample.

## Not yet tested
Financing fade (needs event dates from news), the options version of each, pre-earnings drift
with longer-dated calls (SUNDAY_TESTS 29-33).
