# Stock screen for aggressive 0DTE — last 2 years

21 stocks × 10 rules. Same-day expiries: Mon/Wed/Fri for the largest names, Fridays only for the rest. Black-Scholes at each stock's intraday vol ×1.15, 3% slippage + $0.01; deep OTM prices are flattered by the flat-IV model. Odds are all-in bootstraps from $500 unless noted.

## Ultra: best rule per stock by P($500 → $500k)

| stock | days | IV | rule | trades | win% | exp/trade | P(→$50k) | P(→$500k) | top multiples |
|---|---|---|---|---|---|---|---|---|---|
| MSFT | M/W/F | 24% | rebound_d08_run | 6 | 100% | +200% | 100.0% | 100.00% | 6x, 5x, 2x, 2x |
| NFLX | Fri | 32% | gap2_d02_x10 | 1 | 100% | +929% | 100.0% | 100.00% | 10x |
| AAPL | M/W/F | 26% | big3_d08_run | 10 | 70% | +237% | 23.5% | 11.92% | 16x, 7x, 4x, 2x |
| META | M/W/F | 35% | rebound_d08_run | 10 | 60% | +588% | 17.4% | 9.38% | 48x, 13x, 3x, 2x |
| GOOGL | M/W/F | 29% | rebound_d08_run | 9 | 56% | +364% | 9.4% | 4.32% | 34x, 2x, 2x, 2x |
| TSLA | M/W/F | 50% | rebound_d02_x10 | 23 | 30% | +201% | 7.4% | 2.08% | 13x, 12x, 12x, 10x |
| AMZN | M/W/F | 29% | rebound_d08_run | 14 | 57% | +92% | 6.5% | 1.98% | 9x, 5x, 4x, 2x |
| CRDO | Fri | 110% | rebound_d08_run | 12 | 58% | +53% | 3.8% | 1.03% | 7x, 3x, 3x, 2x |
| HOOD | Fri | 66% | rebound_d08_run | 18 | 50% | +106% | 2.9% | 0.97% | 22x, 4x, 4x, 2x |
| AMD | M/W/F | 50% | gap2_d02_x10 | 65 | 22% | +133% | 4.8% | 0.95% | 12x, 12x, 12x, 11x |
| COIN | Fri | 77% | gap2_d08_run | 33 | 52% | +49% | 3.6% | 0.92% | 9x, 4x, 4x, 4x |
| PLTR | Fri | 57% | rebound_d08_run | 7 | 57% | +40% | 4.1% | 0.83% | 3x, 3x, 2x, 1x |
| APP | Fri | 82% | rebound_d08_run | 10 | 40% | +67% | 3.4% | 0.83% | 8x, 5x, 2x, 1x |
| NVDA | M/W/F | 39% | rebound_d08_run | 23 | 43% | +147% | 2.1% | 0.57% | 38x, 6x, 3x, 2x |
| AVGO | M/W/F | 43% | gap2_d02_x10 | 69 | 16% | +73% | 2.5% | 0.45% | 12x, 12x, 11x, 11x |
| MSTR | Fri | 84% | gap1_d08_run | 56 | 54% | +53% | 2.2% | 0.40% | 19x, 15x, 3x, 3x |
| MU | M/W/F | 58% | rebound_d02_x10 | 26 | 15% | +74% | 2.1% | 0.38% | 12x, 11x, 11x, 10x |
| SNDK | Fri | 105% | gap1_d08_run | 37 | 38% | +36% | 1.6% | 0.30% | 10x, 10x, 9x, 4x |
| ORCL | Fri | 47% | rebound_d02_x10 | 8 | 12% | +32% | 1.5% | 0.30% | 11x, 0x, 0x, 0x |
| ARM | Fri | 81% | rebound_d08_run | 10 | 50% | +35% | 1.6% | 0.20% | 8x, 1x, 1x, 1x |
| LITE | Fri | 102% | rebound_d02_x10 | 10 | 10% | +3% | 0.9% | 0.07% | 10x, 0x, 0x, 0x |

## Positive expectancy: best rule per stock by P($500 → $2k) at a 30% stake

| stock | rule | trades | win% | exp/trade | P(→$2k) 30% | P(→$2k) all-in | last 3 months: n / avg / odds |
|---|---|---|---|---|---|---|---|
| MSFT | rebound_d08_run | 6 | 100% | +200% | 100% | 100% | 1 / +71% / 100% |
| NFLX | gap2_d02_x10 | 1 | 100% | +929% | 100% | 100% | 0 / +0% / 0% |
| AAPL | big3_d08_run | 10 | 70% | +237% | 100% | 53% | 2 / -100% / 0% |
| META | rebound_d08_run | 10 | 60% | +588% | 98% | 40% | 1 / +100% / 100% |
| GOOGL | rebound_d08_run | 9 | 56% | +364% | 93% | 31% | 2 / +17% / 26% |
| AMZN | rebound_d08_run | 14 | 57% | +92% | 93% | 36% | 1 / +62% / 100% |
| TSLA | rebound_d08_run | 23 | 61% | +82% | 91% | 31% | 2 / -100% / 0% |
| PLTR | rebound_d08_run | 7 | 57% | +40% | 87% | 28% | 0 / +0% / 0% |
| CRDO | rebound_d08_run | 12 | 58% | +53% | 83% | 29% | 3 / +263% / 100% |
| COIN | gap2_d08_run | 33 | 52% | +49% | 81% | 28% | 11 / +77% / 30% |
| AMD | rebound_d08_run | 36 | 50% | +68% | 75% | 23% | 7 / +140% / 42% |
| HOOD | gap2_d08_run | 35 | 60% | +44% | 73% | 24% | 7 / +220% / 50% |
| APP | rebound_d08_run | 10 | 40% | +67% | 72% | 30% | 2 / -39% / 1% |
| MSTR | gap1_d08_run | 56 | 54% | +53% | 58% | 19% | 11 / +124% / 24% |
| NVDA | rebound_d08_run | 23 | 43% | +147% | 52% | 16% | 2 / +203% / 51% |
| ARM | rebound_d08_run | 10 | 50% | +35% | 49% | 18% | 5 / +103% / 32% |
| SNDK | gap2_d08_run | 31 | 39% | +45% | 44% | 17% | 7 / -36% / 4% |
| AVGO | gap2_d08_run | 69 | 46% | +23% | 40% | 18% | 5 / +56% / 28% |
| MU | rebound_d02_x10 | 26 | 15% | +74% | 38% | 15% | 10 / +117% / 20% |
| ORCL | rebound_d02_x10 | 8 | 12% | +32% | 23% | 13% | 0 / +0% / 0% |
| LITE | rebound_d08_run | 11 | 27% | -3% | 14% | 11% | 3 / +141% / 33% |

## Rules that work across many stocks (count of stocks with positive expectancy)

| rule | stocks > 0 | median exp/trade | best stock |
|---|---|---|---|
| big3_d02_x10 | 4/17 | -41% | META (+93%, 20 trades) |
| big3_d08_run | 9/20 | -2% | AAPL (+237%, 10 trades) |
| drive_d02_x10 | 1/20 | -42% | MU (+5%, 156 trades) |
| drive_d08_run | 3/21 | -23% | GOOGL (+57%, 269 trades) |
| gap1_d02_x10 | 7/20 | -2% | AMD (+57%, 116 trades) |
| gap1_d08_run | 12/21 | +9% | APP (+116%, 35 trades) |
| gap2_d02_x10 | 11/19 | +8% | AMD (+133%, 65 trades) |
| gap2_d08_run | 11/20 | +18% | GOOGL (+65%, 26 trades) |
| rebound_d02_x10 | 9/13 | +9% | META (+220%, 10 trades) |
| rebound_d08_run | 12/18 | +67% | META (+588%, 10 trades) |
