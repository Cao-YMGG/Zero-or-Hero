# Were the drops traceable?

How to read it: a light earns its name only if drops are clearly more frequent after it than on an average evening (lift well above 1), if the same is not true of rallies (otherwise it marks big days, not down days), and if our own trades differ on lit days. Recall alone (it was lit before the drop) proves nothing when the light is on a fifth of the time.

Alpaca daily bars 2020-01-02 to 2026-11-12. Lights are read at the close; a drop is SPY <= -1.5% (SMH <= -4%) close to close in the sessions after. Lift = rate on lit evenings / rate on all evenings. Episodes = runs of lit evenings (a run ends after 10 unlit sessions), counted from the first lit evening. See zoh/research/drops.py.

Lit at the last close (2026-11-12): breadth, rates.

## Hit rate and false alarms

### Last two years (2024-11-12 on)

502 evenings. Unconditional: SPY <= -1.5% within 1 / 3 / 5 sessions 6% / 16% / 23%; SMH <= -4% 5% / 14% / 21%; 5-day forward return SPY 0.28%, SMH 0.83%.

| light | lit evenings | share | SPY drop 1d | 3d | 5d (lift) | SMH drop 5d (lift) | fwd 5d SPY | fwd 5d SMH | episodes | episodes with an SPY drop in 5 / 10 sessions |
|---|---|---|---|---|---|---|---|---|---|---|
| turning | 71 | 14% | 7% | 21% | 29% (1.3x) | 41% (1.9x) | 0.02% | 0.13% | 12 | 17% of 12 / 33% of 12 |
| diverge | 104 | 21% | 4% | 6% | 10% (0.4x) | 20% (1.0x) | 0.24% | 0.60% | 11 | 9% of 11 / 27% of 11 |
| stretched | 22 | 4% | 18% | 38% | 55% (2.4x) | 70% (3.3x) | 0.05% | -0.29% | 4 | 25% of 4 / 75% of 4 |
| breadth | 129 | 26% | 10% | 28% | 37% (1.6x) | 38% (1.8x) | 0.18% | 0.86% | 12 | 17% of 12 / 42% of 12 |
| rates | 45 | 9% | 11% | 27% | 36% (1.6x) | 20% (1.0x) | 0.20% | 1.35% | 12 | 36% of 11 / 45% of 11 |
| two or more | 107 | 21% | 8% | 22% | 29% (1.3x) | 35% (1.7x) | 0.13% | 0.47% | 11 | 9% of 11 / 27% of 11 |
| three or more | 50 | 10% | 8% | 18% | 27% (1.2x) | 42% (2.0x) | -0.07% | -0.26% | 9 | 11% of 9 / 33% of 9 |
| turning + rates | 4 | 1% | 0% | 0% | 25% (1.1x) | 50% (2.4x) | 0.49% | 1.65% | 3 | 33% of 3 / 33% of 3 |

### 2026 only

218 evenings. Unconditional: SPY <= -1.5% within 1 / 3 / 5 sessions 5% / 13% / 20%; SMH <= -4% 6% / 17% / 28%; 5-day forward return SPY 0.24%, SMH 0.76%.

| light | lit evenings | share | SPY drop 1d | 3d | 5d (lift) | SMH drop 5d (lift) | fwd 5d SPY | fwd 5d SMH | episodes | episodes with an SPY drop in 5 / 10 sessions |
|---|---|---|---|---|---|---|---|---|---|---|
| turning | 50 | 23% | 6% | 16% | 28% (1.4x) | 45% (1.6x) | 0.09% | -0.38% | 4 | 0% of 4 / 50% of 4 |
| diverge | 61 | 28% | 5% | 8% | 13% (0.7x) | 33% (1.2x) | -0.13% | -0.58% | 5 | 0% of 5 / 40% of 5 |
| stretched | 17 | 8% | 12% | 25% | 47% (2.3x) | 73% (2.6x) | -0.01% | -0.28% | 2 | 0% of 2 / 50% of 2 |
| breadth | 64 | 29% | 6% | 18% | 28% (1.4x) | 37% (1.3x) | 0.15% | 0.51% | 5 | 0% of 5 / 40% of 5 |
| rates | 16 | 7% | 7% | 7% | 13% (0.7x) | 13% (0.5x) | 0.19% | 3.06% | 5 | 25% of 4 / 25% of 4 |
| two or more | 64 | 29% | 5% | 15% | 25% (1.2x) | 38% (1.4x) | -0.04% | -0.33% | 5 | 0% of 5 / 40% of 5 |
| three or more | 38 | 17% | 8% | 16% | 28% (1.4x) | 47% (1.7x) | -0.05% | -0.36% | 5 | 0% of 5 / 40% of 5 |
| turning + rates | 3 | 1% | 0% | 0% | 33% (1.7x) | 67% (2.4x) | 0.10% | 1.55% | 2 | 50% of 2 / 50% of 2 |

### Everything before the known episode (2020-01-02 to mid-October 2026)

1707 evenings. Unconditional: SPY <= -1.5% within 1 / 3 / 5 sessions 7% / 18% / 27%; SMH <= -4% 4% / 12% / 18%; 5-day forward return SPY 0.31%, SMH 0.72%.

| light | lit evenings | share | SPY drop 1d | 3d | 5d (lift) | SMH drop 5d (lift) | fwd 5d SPY | fwd 5d SMH | episodes | episodes with an SPY drop in 5 / 10 sessions |
|---|---|---|---|---|---|---|---|---|---|---|
| turning | 146 | 9% | 8% | 23% | 34% (1.3x) | 35% (1.9x) | 0.34% | 0.82% | 36 | 33% of 36 / 50% of 36 |
| diverge | 212 | 12% | 5% | 8% | 17% (0.6x) | 17% (0.9x) | 0.36% | 0.83% | 32 | 25% of 32 / 34% of 32 |
| stretched | 54 | 3% | 20% | 48% | 61% (2.3x) | 48% (2.6x) | -0.02% | -0.26% | 14 | 64% of 14 / 71% of 14 |
| breadth | 410 | 24% | 13% | 30% | 41% (1.6x) | 33% (1.8x) | 0.26% | 0.96% | 39 | 36% of 39 / 54% of 39 |
| rates | 287 | 17% | 10% | 25% | 34% (1.3x) | 24% (1.3x) | 0.04% | 0.73% | 48 | 23% of 48 / 38% of 48 |
| two or more | 292 | 17% | 10% | 24% | 35% (1.3x) | 31% (1.7x) | 0.21% | 0.70% | 35 | 29% of 35 / 40% of 35 |
| three or more | 100 | 6% | 7% | 23% | 32% (1.2x) | 33% (1.8x) | 0.40% | 1.18% | 30 | 30% of 30 / 47% of 30 |
| turning + rates | 34 | 2% | 3% | 24% | 41% (1.6x) | 32% (1.8x) | 0.58% | 1.52% | 15 | 40% of 15 / 53% of 15 |

### Full sample (2020-01-02 on)

1726 evenings. Unconditional: SPY <= -1.5% within 1 / 3 / 5 sessions 7% / 19% / 27%; SMH <= -4% 4% / 12% / 19%; 5-day forward return SPY 0.31%, SMH 0.69%.

| light | lit evenings | share | SPY drop 1d | 3d | 5d (lift) | SMH drop 5d (lift) | fwd 5d SPY | fwd 5d SMH | episodes | episodes with an SPY drop in 5 / 10 sessions |
|---|---|---|---|---|---|---|---|---|---|---|
| turning | 163 | 9% | 8% | 24% | 37% (1.4x) | 39% (2.1x) | 0.24% | 0.47% | 36 | 33% of 36 / 50% of 36 |
| diverge | 222 | 13% | 5% | 10% | 18% (0.7x) | 20% (1.1x) | 0.30% | 0.65% | 32 | 25% of 32 / 34% of 32 |
| stretched | 64 | 4% | 19% | 43% | 60% (2.2x) | 53% (2.8x) | -0.10% | -0.35% | 15 | 60% of 15 / 73% of 15 |
| breadth | 428 | 25% | 13% | 30% | 42% (1.6x) | 35% (1.9x) | 0.23% | 0.82% | 39 | 36% of 39 / 54% of 39 |
| rates | 288 | 17% | 10% | 25% | 34% (1.3x) | 24% (1.3x) | 0.04% | 0.73% | 49 | 23% of 48 / 38% of 48 |
| two or more | 310 | 18% | 10% | 25% | 36% (1.3x) | 34% (1.8x) | 0.17% | 0.52% | 35 | 29% of 35 / 40% of 35 |
| three or more | 113 | 7% | 8% | 24% | 35% (1.3x) | 39% (2.1x) | 0.25% | 0.64% | 30 | 30% of 30 / 47% of 30 |
| turning + rates | 34 | 2% | 3% | 24% | 41% (1.5x) | 32% (1.7x) | 0.58% | 1.52% | 15 | 40% of 15 / 53% of 15 |

## Direction or just volatility?

### Last two years (2024-11-12 on)

Unconditional: a -1.5% SPY day within 5 sessions 23%, a +1.5% day 22%; next session 0.06% close to close, 0.02% open to close, average size 0.69%.

| light | lit | -1.5% day in 5 (lift) | +1.5% day in 5 (lift) | next session close-close | open->close | down days | average size | fwd 5d SPY median |
|---|---|---|---|---|---|---|---|---|
| turning | 71 | 29% (1.3x) | 29% (1.3x) | -0.03% | 0.11% | 44% | 0.93% | -0.22% |
| diverge | 104 | 10% (0.4x) | 13% (0.6x) | -0.11% | -0.04% | 52% | 0.68% | 0.32% |
| stretched | 22 | 55% (2.4x) | 45% (2.0x) | -0.35% | -0.35% | 50% | 0.98% | -0.27% |
| breadth | 129 | 37% (1.6x) | 34% (1.5x) | 0.11% | 0.08% | 42% | 1.02% | 0.11% |
| rates | 45 | 36% (1.6x) | 25% (1.1x) | 0.20% | 0.25% | 43% | 1.03% | 0.32% |
| two or more | 107 | 29% (1.3x) | 26% (1.2x) | 0.07% | 0.16% | 43% | 0.97% | -0.10% |
| three or more | 50 | 27% (1.2x) | 29% (1.3x) | -0.08% | -0.01% | 46% | 0.88% | -0.27% |
| turning + rates | 4 | 25% (1.1x) | 0% (0.0x) | 0.46% | 0.75% | 25% | 0.61% | 0.91% |

### Everything before the known episode

Unconditional: a -1.5% SPY day within 5 sessions 27%, a +1.5% day 28%; next session 0.06% close to close, 0.03% open to close, average size 0.83%.

| light | lit | -1.5% day in 5 (lift) | +1.5% day in 5 (lift) | next session close-close | open->close | down days | average size | fwd 5d SPY median |
|---|---|---|---|---|---|---|---|---|
| turning | 146 | 34% (1.3x) | 38% (1.3x) | 0.12% | 0.15% | 45% | 0.96% | 0.35% |
| diverge | 212 | 17% (0.6x) | 20% (0.7x) | 0.05% | 0.05% | 46% | 0.72% | 0.53% |
| stretched | 54 | 61% (2.3x) | 61% (2.2x) | -0.01% | 0.09% | 48% | 1.48% | -0.41% |
| breadth | 410 | 41% (1.6x) | 47% (1.6x) | -0.01% | 0.02% | 49% | 1.20% | 0.51% |
| rates | 287 | 34% (1.3x) | 34% (1.2x) | 0.03% | 0.08% | 47% | 0.99% | 0.10% |
| two or more | 292 | 35% (1.3x) | 37% (1.3x) | -0.02% | 0.06% | 48% | 1.06% | 0.41% |
| three or more | 100 | 32% (1.2x) | 44% (1.5x) | 0.17% | 0.13% | 45% | 0.98% | 0.42% |
| turning + rates | 34 | 41% (1.6x) | 56% (2.0x) | 0.59% | 0.43% | 38% | 1.02% | 0.58% |

### Full sample

Unconditional: a -1.5% SPY day within 5 sessions 27%, a +1.5% day 29%; next session 0.06% close to close, 0.03% open to close, average size 0.83%.

| light | lit | -1.5% day in 5 (lift) | +1.5% day in 5 (lift) | next session close-close | open->close | down days | average size | fwd 5d SPY median |
|---|---|---|---|---|---|---|---|---|
| turning | 163 | 37% (1.4x) | 39% (1.4x) | 0.10% | 0.12% | 45% | 0.97% | 0.07% |
| diverge | 222 | 18% (0.7x) | 20% (0.7x) | 0.01% | 0.03% | 46% | 0.74% | 0.47% |
| stretched | 64 | 60% (2.2x) | 56% (2.0x) | -0.06% | 0.02% | 48% | 1.41% | -0.41% |
| breadth | 428 | 42% (1.6x) | 47% (1.6x) | -0.01% | 0.02% | 48% | 1.20% | 0.46% |
| rates | 288 | 34% (1.3x) | 34% (1.2x) | 0.03% | 0.08% | 47% | 0.99% | 0.10% |
| two or more | 310 | 36% (1.3x) | 38% (1.3x) | -0.02% | 0.05% | 48% | 1.06% | 0.24% |
| three or more | 113 | 35% (1.3x) | 43% (1.5x) | 0.10% | 0.08% | 46% | 0.98% | -0.06% |
| turning + rates | 34 | 41% (1.5x) | 56% (2.0x) | 0.59% | 0.43% | 38% | 1.02% | 0.58% |

## Every 'stretched' episode

SMH >= 12% below its 20-day closing high while SPY is down < 1.5% over five sessions; one row per run.

| first lit evening | lit evenings in the run | SMH vs its 20-day high | worst SPY day in the next 5 | in the next 10 | SPY 5 sessions later | 10 later | SMH 10 later |
|---|---|---|---|---|---|---|---|
| 2020-03-06 | 1 | -13.4% | -7.1% | -10.8% | -9.2% | -22.4% | -23.4% |
| 2020-03-25 | 6 | -17.3% | -4.4% | -4.4% | -0.3% | 11.0% | 10.5% |
| 2021-03-04 | 2 | -13.4% | -0.5% | -1.4% | 4.5% | 3.9% | 4.2% |
| 2022-01-28 | 2 | -17.1% | -2.4% | -2.4% | 1.5% | -0.3% | 1.4% |
| 2022-03-14 | 1 | -14.6% | -0.0% | -1.3% | 6.9% | 9.7% | 16.2% |
| 2022-04-08 | 5 | -13.0% | -1.7% | -2.7% | -2.1% | -4.3% | -3.3% |
| 2022-06-21 | 10 | -15.1% | -2.0% | -2.0% | 1.5% | 2.2% | -6.2% |
| 2022-09-07 | 5 | -15.3% | -4.3% | -4.3% | -0.8% | -4.7% | -3.9% |
| 2022-10-07 | 4 | -13.2% | -2.3% | -2.3% | -1.4% | 3.2% | -1.2% |
| 2022-12-28 | 1 | -12.4% | -1.1% | -1.1% | 0.7% | 5.4% | 14.0% |
| 2024-07-26 | 5 | -14.6% | -1.9% | -2.9% | -2.1% | -2.1% | -6.4% |
| 2025-03-18 | 1 | -12.6% | -0.3% | -2.0% | 2.9% | 0.3% | -5.7% |
| 2025-04-11 | 4 | -12.7% | -2.4% | -2.4% | -3.8% | 3.2% | 4.6% |
| 2026-07-07 | 7 | -13.1% | -0.8% | -1.0% | 0.6% | 0.1% | 0.5% |
| 2026-10-19 | 10 | -13.5% | -1.2% | -1.8% | -0.1% | -1.9% | -7.3% |

## Our open-drive rule on lit and unlit days

135 live-like trades, 2024-02-09 to 2026-10-05 (SPY calls and puts, NVDA/TSLA calls). Exits: hold = to 15:30, take3 = all out at 3x, half3_trail = half at 3x and a trail on the rest, trail = trail only (zoh/research/opendrive.py).

| lights the evening before | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| any light | hold | 69 | 36% | 23% | 12% | 2% |
| any light | take3 | 69 | 38% | 6% | 1% | -3% |
| any light | half3_trail | 69 | 38% | 11% | 5% | -2% |
| any light | trail | 69 | 43% | 7% | -3% | -9% |
| no light | hold | 66 | 29% | 5% | -12% | -27% |
| no light | take3 | 66 | 36% | 4% | -3% | -7% |
| no light | half3_trail | 66 | 36% | 13% | 3% | -6% |
| no light | trail | 66 | 44% | 14% | -4% | -11% |
| stretched | hold | 4 | 50% | 167% | -38% | -98% |
| stretched | take3 | 4 | 50% | 30% | -38% | -98% |
| stretched | half3_trail | 4 | 50% | 46% | -38% | -98% |
| stretched | trail | 4 | 50% | 56% | -46% | -98% |
| breadth | hold | 45 | 49% | 54% | 37% | 22% |
| breadth | take3 | 45 | 51% | 37% | 29% | 24% |
| breadth | half3_trail | 45 | 51% | 41% | 32% | 25% |
| breadth | trail | 45 | 58% | 33% | 25% | 16% |
| turning | hold | 18 | 44% | 116% | 77% | 39% |
| turning | take3 | 18 | 50% | 44% | 33% | 20% |
| turning | half3_trail | 18 | 50% | 72% | 49% | 23% |
| turning | trail | 18 | 56% | 67% | 31% | 10% |
| rates | hold | 13 | 23% | 24% | -39% | -80% |
| rates | take3 | 13 | 23% | -32% | -54% | -80% |
| rates | half3_trail | 13 | 23% | -20% | -49% | -80% |
| rates | trail | 13 | 38% | 5% | -28% | -64% |

By side, exit take3:

| lights the evening before | side | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| any light | call | 56 | 41% | 17% | 10% | 6% |
| any light | put | 13 | 23% | -38% | -59% | -72% |
| no light | call | 52 | 38% | 12% | 4% | -0% |
| no light | put | 14 | 29% | -27% | -49% | -70% |
| stretched | call | 1 | 100% | 231% | - | - |
| stretched | put | 3 | 33% | -38% | -98% | -98% |
| breadth | call | 34 | 59% | 57% | 47% | 42% |
| breadth | put | 11 | 27% | -27% | -51% | -66% |

Calls after a `breadth` evening against calls after any other evening (exit take3 / hold):

| slice | breadth lit: trades | win% | avg take3 | w/o best 2 | avg hold | not lit: trades | win% | avg take3 | w/o best 2 | avg hold |
|---|---|---|---|---|---|---|---|---|---|---|
| all | 34 | 59% | 57% | 42% | 75% | 74 | 31% | -5% | -15% | 6% |
| last 3 months of the data | 9 | 78% | 126% | 95% | 233% | 11 | 18% | -35% | -93% | 11% |
| last year of the data | 18 | 67% | 92% | 65% | 133% | 39 | 41% | 18% | 1% | 52% |
| before that | 16 | 50% | 18% | -12% | 9% | 35 | 20% | -32% | -47% | -46% |
| SPY | 12 | 58% | 56% | 6% | 80% | 7 | 57% | 87% | -6% | -56% |
| NVDA / TSLA | 22 | 59% | 58% | 41% | 71% | 67 | 28% | -15% | -23% | 12% |

## Recall: were the lights on before the drops?

### Last two years

29 SPY drops of 1.5% or more. For each light: on how many of them it was lit the evening before (recall) against how often it is lit at all (prevalence). Recall near prevalence = no information.

| light | lit before a drop | recall | prevalence | ratio |
|---|---|---|---|---|
| turning | 5 of 29 | 17% | 14% | 1.2x |
| diverge | 4 of 29 | 14% | 21% | 0.7x |
| stretched | 4 of 29 | 14% | 4% | 3.1x |
| breadth | 13 of 29 | 45% | 26% | 1.7x |
| rates | 5 of 29 | 17% | 9% | 1.9x |
| two or more | 8 of 29 | 28% | 21% | 1.3x |
| three or more | 4 of 29 | 14% | 10% | 1.4x |
| turning + rates | 0 of 29 | 0% | 1% | 0.0x |

Drops with no light at all the evening before: 12 of 29.

### Full sample

125 SPY drops of 1.5% or more. For each light: on how many of them it was lit the evening before (recall) against how often it is lit at all (prevalence). Recall near prevalence = no information.

| light | lit before a drop | recall | prevalence | ratio |
|---|---|---|---|---|
| turning | 13 of 125 | 10% | 9% | 1.1x |
| diverge | 12 of 125 | 10% | 13% | 0.7x |
| stretched | 12 of 125 | 10% | 4% | 2.6x |
| breadth | 54 of 125 | 43% | 25% | 1.7x |
| rates | 28 of 125 | 22% | 17% | 1.3x |
| two or more | 30 of 125 | 24% | 18% | 1.3x |
| three or more | 9 of 125 | 7% | 7% | 1.1x |
| turning + rates | 1 of 125 | 1% | 2% | 0.4x |

Drops with no light at all the evening before: 48 of 125.

## After the open: could a gap be traded?

Gap = open vs the prior close; then the same day's open to close. Mega caps: NVDA, AMD, AVGO, MU, INTC, TSM, TSLA, META, AAPL, MSFT, GOOGL, AMZN, NFLX, ORCL, PLTR, COIN (earnings gaps included).

### Last two years

| group | events | mean gap | open->close mean | median | closed above the open |
|---|---|---|---|---|---|
| mega cap gap <= -5% | 131 | -7.5% | 0.31% | 0.12% | 52% |
| mega cap gap -5% to -3% | 250 | -3.8% | 0.07% | 0.02% | 50% |
| mega cap gap >= +5% | 160 | 8.0% | -0.64% | -0.63% | 42% |
| mega cap, every session | 8032 | 0.1% | 0.03% | 0.01% | 50% |
| NVDA gap <= -3% | 16 | -5.7% | 1.73% | 1.67% | 56% |
| SMH gap <= -2% | 48 | -3.3% | 0.07% | 0.26% | 52% |
| SPY gap <= -0.7% | 46 | -1.2% | 0.11% | 0.11% | 54% |
| SPY, every session | 502 | 0.0% | 0.02% | 0.05% | 52% |

### Full sample

| group | events | mean gap | open->close mean | median | closed above the open |
|---|---|---|---|---|---|
| mega cap gap <= -5% | 338 | -8.1% | 0.55% | 0.05% | 50% |
| mega cap gap -5% to -3% | 622 | -3.8% | 0.14% | 0.05% | 50% |
| mega cap gap >= +5% | 414 | 8.1% | -0.15% | -0.18% | 48% |
| mega cap, every session | 27104 | 0.1% | 0.05% | 0.03% | 51% |
| NVDA gap <= -3% | 61 | -5.1% | 0.70% | -0.13% | 48% |
| SMH gap <= -2% | 105 | -3.3% | -0.03% | -0.39% | 46% |
| SPY gap <= -0.7% | 177 | -1.4% | 0.04% | 0.10% | 55% |
| SPY, every session | 1726 | 0.0% | 0.03% | 0.07% | 54% |

## The recent days

Every session since 2026-10-01 with SPY <= -1%, SMH <= -3%, NVDA <= -4% or an NVDA gap <= -5%.

| day | SPY | SMH | NVDA close-close | NVDA gap | NVDA open->close | lights the evening before |
|---|---|---|---|---|---|---|
| 2026-10-14 | -1.08% | -3.98% | -3.2% | -1.3% | -1.9% | turning, diverge, breadth |
| 2026-10-16 | -1.11% | -3.41% | -1.4% | -0.3% | -1.1% | turning, diverge, breadth |
| 2026-10-22 | -1.18% | -5.99% | -4.4% | -2.2% | -2.3% | turning, diverge, stretched, breadth |
| 2026-10-30 | -1.77% | -6.98% | -4.2% | -2.2% | -2.1% | turning, diverge, breadth |
| 2026-11-05 | -4.41% | -11.21% | -9.3% | -2.0% | -7.4% | turning, diverge, stretched, breadth |
| 2026-11-09 | 2.37% | 5.05% | -4.3% | -7.3% | 3.2% | turning, breadth |
| 2026-11-10 | -0.37% | -0.78% | -5.5% | -2.6% | -2.9% | turning, stretched, breadth |
| 2026-11-12 | -0.35% | -1.03% | -4.3% | -13.1% | 10.1% | diverge |

