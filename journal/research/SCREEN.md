# Stock screen for aggressive 0DTE — last 2 years

25 stocks × 10 rules. Same-day expiries: Mon/Wed/Fri for the largest names, Fridays only for the rest. Black-Scholes at each stock's intraday vol ×1.15, 3% slippage + $0.01; deep OTM prices are flattered by the flat-IV model. Odds are all-in bootstraps from $500 unless noted. Only rules with >= 10 trades are ranked.

## Ultra: best rule per stock by P($500 → $500k)

| stock | days | IV | rule | trades | win% | exp/trade | P(→$50k) | P(→$500k) | top multiples |
|---|---|---|---|---|---|---|---|---|---|
| AAPL | M/W/F | 26% | big3_d08_run | 11 | 82% | +234% | 35.7% | 22.90% | 15x, 7x, 4x, 2x |
| META | M/W/F | 35% | rebound_d08_run | 10 | 60% | +588% | 17.4% | 9.38% | 48x, 13x, 3x, 2x |
| TSLA | M/W/F | 50% | rebound_d02_x10 | 23 | 30% | +201% | 7.4% | 2.08% | 13x, 12x, 12x, 10x |
| AMZN | M/W/F | 28% | rebound_d08_run | 14 | 57% | +88% | 5.8% | 1.62% | 9x, 5x, 5x, 2x |
| RKLB | Fri | 90% | rebound_d08_run | 14 | 50% | +77% | 5.2% | 1.35% | 6x, 5x, 4x, 3x |
| CRDO | Fri | 110% | rebound_d08_run | 12 | 58% | +53% | 3.8% | 1.03% | 7x, 3x, 3x, 2x |
| AMD | M/W/F | 50% | gap2_d02_x10 | 65 | 22% | +133% | 4.8% | 0.95% | 12x, 12x, 12x, 11x |
| COIN | Fri | 77% | gap2_d08_run | 33 | 52% | +49% | 3.6% | 0.92% | 9x, 4x, 4x, 4x |
| NVDA | M/W/F | 39% | rebound_d08_run | 23 | 43% | +380% | 4.5% | 0.88% | 91x, 6x, 3x, 2x |
| APP | Fri | 73% | gap1_d08_run | 51 | 43% | +188% | 2.9% | 0.78% | 58x, 49x, 6x, 6x |
| GOOGL | M/W/F | 29% | gap2_d08_run | 26 | 42% | +65% | 3.4% | 0.73% | 13x, 6x, 4x, 4x |
| HOOD | Fri | 65% | rebound_d08_run | 18 | 50% | +96% | 2.7% | 0.68% | 21x, 4x, 4x, 1x |
| SMCI | Fri | 80% | gap2_d08_run | 34 | 50% | +50% | 3.1% | 0.62% | 10x, 5x, 5x, 4x |
| NFLX | Fri | 32% | gap1_d08_run | 11 | 55% | +34% | 2.6% | 0.57% | 4x, 3x, 3x, 2x |
| AVGO | M/W/F | 43% | gap2_d02_x10 | 69 | 16% | +73% | 2.5% | 0.45% | 12x, 12x, 11x, 11x |
| PLTR | Fri | 57% | gap2_d08_run | 18 | 50% | +39% | 2.1% | 0.43% | 6x, 5x, 4x, 2x |
| MSTR | Fri | 84% | gap1_d08_run | 56 | 54% | +53% | 2.2% | 0.40% | 19x, 15x, 3x, 3x |
| MU | M/W/F | 58% | rebound_d02_x10 | 26 | 15% | +74% | 2.1% | 0.38% | 12x, 11x, 11x, 10x |
| SNDK | Fri | 105% | gap1_d08_run | 37 | 38% | +36% | 1.6% | 0.30% | 10x, 10x, 9x, 4x |
| ARM | Fri | 60% | rebound_d02_x10 | 15 | 13% | +63% | 1.9% | 0.25% | 14x, 10x, 0x, 0x |
| ORCL | Fri | 45% | big3_d02_x10 | 15 | 13% | +37% | 1.5% | 0.25% | 10x, 10x, 0x, 0x |
| INTC | Fri | 56% | rebound_d08_run | 12 | 42% | +48% | 1.5% | 0.22% | 9x, 3x, 2x, 2x |
| MSFT | M/W/F | 24% | gap1_d08_run | 60 | 48% | +5% | 0.7% | 0.15% | 5x, 4x, 4x, 3x |
| LITE | Fri | 102% | rebound_d02_x10 | 10 | 10% | +3% | 0.9% | 0.07% | 10x, 0x, 0x, 0x |
| IONQ | Fri | 105% | gap2_d08_run | 29 | 38% | -32% | 0.1% | 0.00% | 3x, 2x, 2x, 2x |

## Positive expectancy: best rule per stock by P($500 → $2k) at a 30% stake

| stock | rule | trades | win% | exp/trade | P(→$2k) 30% | P(→$2k) all-in | last 3 months: n / avg / odds |
|---|---|---|---|---|---|---|---|
| AAPL | big3_d08_run | 11 | 82% | +234% | 100% | 64% | 2 / -43% / 0% |
| META | rebound_d08_run | 10 | 60% | +588% | 98% | 40% | 1 / +100% / 100% |
| TSLA | rebound_d08_run | 23 | 61% | +82% | 91% | 31% | 2 / -100% / 0% |
| RKLB | rebound_d08_run | 14 | 50% | +77% | 90% | 32% | 1 / +223% / 100% |
| AMZN | rebound_d08_run | 14 | 57% | +88% | 90% | 34% | 1 / +59% / 100% |
| CRDO | rebound_d08_run | 12 | 58% | +53% | 83% | 29% | 3 / +263% / 100% |
| COIN | gap2_d08_run | 33 | 52% | +49% | 81% | 28% | 11 / +77% / 30% |
| SMCI | gap2_d08_run | 34 | 50% | +50% | 75% | 26% | 2 / +34% / 24% |
| AMD | rebound_d08_run | 36 | 50% | +68% | 75% | 23% | 7 / +140% / 42% |
| NFLX | gap1_d08_run | 11 | 55% | +34% | 74% | 28% | 3 / +1% / 20% |
| GOOGL | gap2_d08_run | 26 | 42% | +65% | 67% | 26% | 5 / +148% / 46% |
| PLTR | gap2_d08_run | 18 | 50% | +39% | 63% | 22% | 2 / +166% / 49% |
| HOOD | rebound_d08_run | 18 | 50% | +96% | 62% | 19% | 2 / +136% / 100% |
| MSTR | gap1_d08_run | 56 | 54% | +53% | 58% | 19% | 11 / +124% / 24% |
| NVDA | rebound_d08_run | 23 | 43% | +380% | 56% | 16% | 2 / +206% / 51% |
| INTC | rebound_d08_run | 12 | 42% | +48% | 53% | 18% | 2 / +364% / 49% |
| APP | gap1_d08_run | 51 | 43% | +188% | 50% | 15% | 7 / +5% / 19% |
| SNDK | gap2_d08_run | 31 | 39% | +45% | 44% | 17% | 7 / -36% / 4% |
| AVGO | gap2_d08_run | 69 | 46% | +23% | 40% | 18% | 5 / +56% / 28% |
| MU | rebound_d02_x10 | 26 | 15% | +74% | 38% | 15% | 10 / +117% / 20% |
| ARM | rebound_d02_x10 | 15 | 13% | +63% | 32% | 13% | 1 / +1321% / 100% |
| ORCL | gap1_d02_x10 | 46 | 13% | +56% | 30% | 14% | 3 / -100% / 0% |
| MSFT | gap1_d08_run | 60 | 48% | +5% | 25% | 16% | 8 / +62% / 37% |
| LITE | rebound_d08_run | 11 | 27% | -3% | 14% | 11% | 3 / +141% / 33% |
| IONQ | drive_d08_run | 86 | 29% | -33% | 3% | 8% | 9 / -86% / 0% |

## Rules that work across many stocks (count of stocks with positive expectancy)

| rule | stocks > 0 | median exp/trade | best stock |
|---|---|---|---|
| big3_d02_x10 | 5/17 | -58% | META (+93%, 20 trades) |
| big3_d08_run | 10/24 | -14% | AAPL (+234%, 11 trades) |
| drive_d02_x10 | 2/21 | -33% | APP (+23%, 87 trades) |
| drive_d08_run | 3/25 | -25% | GOOGL (+57%, 269 trades) |
| gap1_d02_x10 | 11/21 | +5% | AMD (+57%, 116 trades) |
| gap1_d08_run | 13/25 | +5% | APP (+188%, 51 trades) |
| gap2_d02_x10 | 11/19 | +10% | AMD (+133%, 65 trades) |
| gap2_d08_run | 13/24 | +6% | GOOGL (+65%, 26 trades) |
| rebound_d02_x10 | 8/13 | +9% | META (+220%, 10 trades) |
| rebound_d08_run | 15/22 | +48% | META (+588%, 10 trades) |
