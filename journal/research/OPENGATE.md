# Chip breadth as a gate for the open-drive calls, and the put hand (SUNDAY_TESTS 62)

Signals of the live ledgers at 10:00 ET, real 1-minute option closes, 10% costs each way, 2024-02-01 to 2026-11-12: 168 signals priced (26 on macro days, left out below). `d35` is the contract nearest 0.35 delta at 10:00 (what the ledgers buy since 2026-11-09); `otm07` is the strike about 0.7% out of the money of OPENDRIVE.md. Exits to 15:30: hold, take3 (all out at 3x), trail (arms at 2x, out at 60% of the peak, never below the entry), half3_trail. `lit` = at least 75% of twelve chip names closed below their own 20-day average the evening before (DROPS.md). Rebuild: `python -m zoh.research.opengate`.

How to read it: sections 1 to 3 are the sample the light was found in, re-priced at the strike the ledgers buy; they can only show whether the split survives a strike change, not whether it is real. Sections 4 and 5 are the checks that could break it: how few stretches of the calendar carry the result, and the same 10:00 signals on the stock alone in 2020 to 2023, years the option data does not reach.

State at the last close (2026-11-12): chip breadth 75% (lit), SMH below its 20-day average and below its 100-day average.

## 1. NVDA / TSLA calls at +0.8% or more

95 trades. Median entry 1.26 at delta 0.34, 0.8% out of the money (d35); 1.29 for otm07.

Strike d35, lit against not lit, by exit:

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| lit | hold | 28 | 54% | 56% | 29% | 17% |
| lit | take3 | 28 | 54% | 45% | 38% | 30% |
| lit | trail | 28 | 64% | 41% | 29% | 17% |
| lit | half3_trail | 28 | 54% | 45% | 35% | 26% |
| not lit | hold | 67 | 25% | 8% | -9% | -23% |
| not lit | take3 | 67 | 30% | -15% | -19% | -22% |
| not lit | trail | 67 | 37% | 7% | -11% | -21% |
| not lit | half3_trail | 67 | 30% | -0% | -10% | -19% |

Strike otm07, lit against not lit, by exit:

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| lit | hold | 28 | 50% | 48% | 21% | 10% |
| lit | take3 | 28 | 50% | 40% | 33% | 25% |
| lit | trail | 28 | 64% | 37% | 24% | 14% |
| lit | half3_trail | 28 | 50% | 38% | 28% | 20% |
| not lit | hold | 67 | 25% | 12% | -5% | -19% |
| not lit | take3 | 67 | 28% | -15% | -19% | -23% |
| not lit | trail | 67 | 36% | 7% | -10% | -21% |
| not lit | half3_trail | 67 | 28% | 0% | -10% | -18% |

Strike d35, exit hold (what the ledger does with its one contract), by slice:

| slice | lit: trades | win% | avg | w/o best 2 | not lit: trades | win% | avg | w/o best 2 |
|---|---|---|---|---|---|---|---|---|
| since 2024-02 | 28 | 54% | 56% | 17% | 67 | 25% | 8% | -23% |
| last 3 months | 8 | 38% | -10% | -51% | 8 | 25% | -39% | -98% |
| last year | 21 | 57% | 70% | 19% | 35 | 34% | 59% | 1% |
| before the last year | 7 | 43% | 13% | -47% | 32 | 16% | -48% | -72% |
| 2024 | 4 | 50% | 32% | -98% | 17 | 12% | -56% | -85% |
| 2025 | 6 | 50% | 1% | -51% | 16 | 19% | -42% | -80% |
| 2026 | 18 | 56% | 80% | 20% | 34 | 35% | 64% | 4% |
| NVDA | 16 | 44% | 54% | -19% | 25 | 28% | -7% | -57% |
| TSLA | 12 | 67% | 60% | 23% | 42 | 24% | 17% | -33% |
| Fridays | 14 | 57% | 25% | -3% | 40 | 18% | -33% | -57% |
| Mondays and Wednesdays | 14 | 50% | 87% | 9% | 27 | 37% | 69% | -8% |
| new days (after 2026-10-15, not in DROPS.md) | 6 | 17% | -41% | -92% | 0 | - | - | - |

The ledger's own rule (Mondays and Wednesdays, the stronger of the two, no macro day, no monthly-expiry week), strike d35:

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| lit | hold | 9 | 67% | 141% | 61% | 27% |
| lit | take3 | 9 | 67% | 93% | 75% | 53% |
| lit | trail | 9 | 78% | 107% | 76% | 43% |
| lit | half3_trail | 9 | 67% | 98% | 73% | 48% |
| not lit | hold | 20 | 35% | 36% | -9% | -48% |
| not lit | take3 | 20 | 35% | -19% | -32% | -45% |
| not lit | trail | 20 | 40% | -3% | -39% | -50% |
| not lit | half3_trail | 20 | 35% | 9% | -20% | -47% |
| SMH below its 20-day average | hold | 15 | 67% | 189% | 138% | 89% |
| SMH below its 20-day average | take3 | 15 | 67% | 83% | 72% | 60% |
| SMH below its 20-day average | trail | 15 | 73% | 110% | 69% | 47% |
| SMH below its 20-day average | half3_trail | 15 | 67% | 125% | 94% | 66% |
| SMH above it | hold | 14 | 21% | -60% | -77% | -88% |
| SMH above it | take3 | 14 | 21% | -57% | -77% | -88% |
| SMH above it | trail | 14 | 29% | -53% | -70% | -79% |
| SMH above it | half3_trail | 14 | 21% | -58% | -77% | -88% |

Shuffle test (lit days reassigned at random, 20,000 times, d35 hold): the real gap in the average is 48 points and 17.6% of shuffles reach it; the gap in the win rate is 28 points and 0.9% of shuffles reach it. The cell was found among 48 (6 lights x 2 sides x 4 exits) on the otm07 strike, so read a single 5% as 1 in 20, not as proof. The same test for `SMH below its 20-day average`, picked from the 15 states of section 2 after reading them: 97 points, 1.6%; 30 points, 0.2%.

## 2. Is it about chip breadth? The same trades split by plainer states (d35, hold)

| state of the evening before | lit: trades | win% | avg | w/o best 2 | not lit: trades | win% | avg | w/o best 2 |
|---|---|---|---|---|---|---|---|---|
| chip breadth >= 75% (the light) | 28 | 54% | 56% | 17% | 67 | 25% | 8% | -23% |
| chip breadth >= 50% | 43 | 42% | 42% | 8% | 52 | 27% | 6% | -35% |
| chip breadth = 100% | 10 | 30% | 48% | -56% | 85 | 34% | 19% | -5% |
| SMH below its 20-day average | 44 | 50% | 74% | 38% | 51 | 20% | -23% | -56% |
| SMH above its 100-day average | 75 | 37% | 41% | 14% | 20 | 20% | -47% | -70% |
| SMH below its 20-day and above its 100-day average | 27 | 67% | 145% | 89% | 68 | 21% | -26% | -51% |
| SPY below its 20-day average | 33 | 42% | 25% | -15% | 62 | 29% | 20% | -11% |
| the name below its own 20-day average | 52 | 40% | 52% | 13% | 43 | 26% | -14% | -42% |
| the name down over 5 sessions | 54 | 39% | 20% | -10% | 41 | 27% | 25% | -23% |
| SMH down over 5 sessions | 51 | 43% | 50% | 18% | 44 | 23% | -10% | -48% |
| SPY 10-day volatility above its 1-year median | 46 | 30% | 39% | -6% | 49 | 37% | 6% | -17% |
| light: turning | 19 | 47% | 92% | 16% | 76 | 30% | 5% | -23% |
| light: rates | 9 | 11% | 9% | -97% | 86 | 36% | 24% | -0% |
| light: stretched | 3 | 33% | 196% | -100% | 92 | 34% | 17% | -6% |
| light: diverge | 29 | 38% | 47% | -4% | 66 | 32% | 11% | -20% |

Breadth light against the plain state, the four combinations:

| chip breadth | SMH against its 20-day average | trades | win% | avg | w/o best 2 |
|---|---|---|---|---|---|
| lit | below | 28 | 54% | 56% | 17% |
| lit | above | 0 | - | - | - |
| not lit | below | 16 | 44% | 106% | 8% |
| not lit | above | 51 | 20% | -23% | -56% |

## 3. By chip breadth share (d35, hold)

| chips below their 20-day average | trades | win% | avg | w/o best 2 |
|---|---|---|---|---|
| under 25% | 29 | 28% | 10% | -48% |
| 25% to 49% | 23 | 26% | 0% | -52% |
| 50% to 74% | 15 | 20% | 16% | -67% |
| 75% to 99% | 18 | 67% | 61% | 29% |
| all twelve | 10 | 30% | 48% | -56% |

## 4. How many stretches of the calendar carry it (NVDA / TSLA calls, d35, hold)

| quarter | trades | win% | avg | after a lit evening: trades | wins | after SMH below its 20-day average: trades | wins |
|---|---|---|---|---|---|---|---|
| 2024 Q1 | 3 | 33% | -9% | 0 | 0 | 0 | 0 |
| 2024 Q2 | 4 | 25% | -40% | 2 | 1 | 2 | 1 |
| 2024 Q3 | 7 | 0% | -89% | 0 | 0 | 1 | 0 |
| 2024 Q4 | 7 | 29% | -2% | 2 | 1 | 4 | 1 |
| 2025 Q1 | 6 | 17% | -6% | 1 | 0 | 6 | 1 |
| 2025 Q2 | 2 | 0% | -99% | 1 | 0 | 1 | 0 |
| 2025 Q3 | 8 | 25% | -45% | 1 | 1 | 1 | 1 |
| 2025 Q4 | 6 | 50% | -13% | 3 | 2 | 3 | 2 |
| 2026 Q1 | 12 | 33% | -36% | 4 | 2 | 7 | 4 |
| 2026 Q2 | 15 | 47% | 163% | 0 | 0 | 2 | 2 |
| 2026 Q3 | 18 | 50% | 102% | 8 | 7 | 11 | 9 |
| 2026 Q4 | 7 | 29% | -35% | 6 | 1 | 6 | 1 |

2 of 12 quarters averaged above zero. Without the best two (2026 Q2 and 2026 Q3): 62 trades, 26% win, -35% average, -47% without the best two. Lit against not lit in what is left: 20 | 40% | -4% | -25% against 42 | 19% | -50% | -68% (trades | win% | avg | w/o best 2); SMH below its 20-day average against above: 31 | 35% | -7% | -29% against 31 | 16% | -63% | -78%.

The three places the chip ETF can stand, same trades (a split found after reading section 2, kept here because section 5 breaks it):

| SMH the evening before | trades | win% | avg | w/o best 2 |
|---|---|---|---|---|
| dip in an uptrend | 27 | 67% | 145% | 89% |
| dip in a downtrend | 17 | 24% | -38% | -64% |
| above its 20-day average | 51 | 20% | -23% | -56% |

## 5. The same signals on the stock alone, back to 2020

Every session, expiry day or not: the stock at least 0.8% above its open at 10:00 (SPY 0.5% either way), and what it did from 10:00 to 15:30, signed the way of the trade. No option prices, so no costs and no fat tails; the question is only whether the evening state moves the odds of the follow-through a 0.35-delta call needs.
Against the real option results where both exist (95 trades): correlation 0.71; the call made money on 30 of 38 days when the stock added 1% or more after 10:00 and on 2 of 57 other days.

NVDA / TSLA at +0.8% or more:

| period | state of the evening before | signals | avg 10:00 to 15:30 | continued | +1% or more | -1% or worse |
|---|---|---|---|---|---|---|
| 2020-01 to 2024-01 (before the option data) | all | 573 | +0.28% | 57% | 38% | 26% |
| 2020-01 to 2024-01 (before the option data) | SMH below its 20-day average | 231 | +0.48% | 59% | 44% | 23% |
| 2020-01 to 2024-01 (before the option data) | SMH above its 20-day average | 342 | +0.14% | 55% | 35% | 28% |
| 2020-01 to 2024-01 (before the option data) | chip breadth lit | 154 | +0.27% | 56% | 42% | 27% |
| 2020-01 to 2024-01 (before the option data) | chip breadth not lit | 419 | +0.28% | 57% | 37% | 26% |
| 2020-01 to 2024-01 (before the option data) | dip in an uptrend | 100 | +0.61% | 62% | 43% | 17% |
| 2020-01 to 2024-01 (before the option data) | dip in a downtrend | 131 | +0.38% | 57% | 44% | 28% |
| 2024-02 on (the option sample's years) | all | 370 | +0.16% | 52% | 29% | 23% |
| 2024-02 on (the option sample's years) | SMH below its 20-day average | 157 | +0.38% | 55% | 33% | 20% |
| 2024-02 on (the option sample's years) | SMH above its 20-day average | 213 | -0.01% | 50% | 27% | 25% |
| 2024-02 on (the option sample's years) | chip breadth lit | 107 | +0.53% | 57% | 34% | 17% |
| 2024-02 on (the option sample's years) | chip breadth not lit | 263 | +0.01% | 51% | 28% | 25% |
| 2024-02 on (the option sample's years) | dip in an uptrend | 75 | +0.10% | 57% | 39% | 28% |
| 2024-02 on (the option sample's years) | dip in a downtrend | 82 | +0.62% | 54% | 28% | 12% |

By year (signals, average 10:00 to 15:30, share adding 1% or more):

| year | SMH below: signals | avg | +1% or more | SMH above: signals | avg | +1% or more | breadth lit: signals | avg | +1% or more | not lit: signals | avg | +1% or more |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020 | 46 | +0.38% | 46% | 99 | +0.26% | 37% | 28 | +0.01% | 43% | 117 | +0.37% | 39% |
| 2021 | 40 | +0.56% | 48% | 83 | +0.07% | 34% | 21 | +0.03% | 38% | 102 | +0.27% | 38% |
| 2022 | 88 | +0.43% | 42% | 63 | -0.19% | 35% | 80 | +0.30% | 41% | 71 | +0.03% | 37% |
| 2023 | 55 | +0.57% | 42% | 90 | +0.38% | 36% | 25 | +0.67% | 48% | 120 | +0.41% | 36% |
| 2024 | 48 | -0.01% | 27% | 97 | -0.22% | 28% | 36 | -0.04% | 28% | 109 | -0.18% | 28% |
| 2025 | 59 | +0.65% | 32% | 70 | +0.05% | 27% | 36 | +1.14% | 31% | 93 | +0.01% | 29% |
| 2026 | 52 | +0.46% | 40% | 53 | +0.21% | 21% | 35 | +0.49% | 43% | 70 | +0.25% | 24% |

SPY at +0.5% or more:

| period | state of the evening before | signals | avg 10:00 to 15:30 | continued | +1% or more | -1% or worse |
|---|---|---|---|---|---|---|
| 2020-01 to 2024-01 (before the option data) | all | 69 | +0.10% | 62% | 16% | 14% |
| 2020-01 to 2024-01 (before the option data) | SMH below its 20-day average | 48 | +0.04% | 58% | 17% | 15% |
| 2020-01 to 2024-01 (before the option data) | SMH above its 20-day average | 21 | +0.23% | 71% | 14% | 14% |
| 2020-01 to 2024-01 (before the option data) | chip breadth lit | 36 | -0.04% | 58% | 14% | 17% |
| 2020-01 to 2024-01 (before the option data) | chip breadth not lit | 33 | +0.25% | 67% | 18% | 12% |
| 2020-01 to 2024-01 (before the option data) | dip in an uptrend | 11 | -0.08% | 55% | 0% | 18% |
| 2020-01 to 2024-01 (before the option data) | dip in a downtrend | 37 | +0.07% | 59% | 22% | 14% |
| 2024-02 on (the option sample's years) | all | 22 | +0.72% | 77% | 23% | 5% |
| 2024-02 on (the option sample's years) | SMH below its 20-day average | 20 | +0.78% | 80% | 25% | 5% |
| 2024-02 on (the option sample's years) | SMH above its 20-day average | 2 | +0.09% | 50% | 0% | 0% |
| 2024-02 on (the option sample's years) | chip breadth lit | 16 | +0.90% | 81% | 25% | 6% |
| 2024-02 on (the option sample's years) | chip breadth not lit | 6 | +0.23% | 67% | 17% | 0% |
| 2024-02 on (the option sample's years) | dip in an uptrend | 4 | +0.21% | 75% | 0% | 0% |
| 2024-02 on (the option sample's years) | dip in a downtrend | 16 | +0.92% | 81% | 31% | 6% |

SPY at -0.5% or less, signed for a put (`continued` = fell further, `-1% or worse` = bounced 1% or more):

| period | state of the evening before | signals | avg 10:00 to 15:30 | continued | +1% or more | -1% or worse |
|---|---|---|---|---|---|---|
| 2020-01 to 2024-01 (before the option data) | all | 62 | -0.32% | 45% | 18% | 31% |
| 2020-01 to 2024-01 (before the option data) | SMH below its 20-day average | 34 | -0.65% | 35% | 15% | 38% |
| 2020-01 to 2024-01 (before the option data) | SMH above its 20-day average | 28 | +0.07% | 57% | 21% | 21% |
| 2020-01 to 2024-01 (before the option data) | chip breadth lit | 27 | -0.46% | 41% | 19% | 37% |
| 2020-01 to 2024-01 (before the option data) | chip breadth not lit | 35 | -0.22% | 49% | 17% | 26% |
| 2020-01 to 2024-01 (before the option data) | dip in an uptrend | 6 | -0.54% | 17% | 0% | 33% |
| 2020-01 to 2024-01 (before the option data) | dip in a downtrend | 28 | -0.67% | 39% | 18% | 39% |
| 2024-02 on (the option sample's years) | all | 30 | +0.09% | 40% | 17% | 10% |
| 2024-02 on (the option sample's years) | SMH below its 20-day average | 18 | +0.28% | 50% | 28% | 11% |
| 2024-02 on (the option sample's years) | SMH above its 20-day average | 12 | -0.20% | 25% | 0% | 8% |
| 2024-02 on (the option sample's years) | chip breadth lit | 12 | +0.27% | 50% | 25% | 17% |
| 2024-02 on (the option sample's years) | chip breadth not lit | 18 | -0.03% | 33% | 11% | 6% |
| 2024-02 on (the option sample's years) | dip in an uptrend | 5 | -0.06% | 40% | 0% | 0% |
| 2024-02 on (the option sample's years) | dip in a downtrend | 13 | +0.41% | 54% | 38% | 15% |

## 6. SPY calls at +0.5% or more

20 trades; the ledger takes 3x on its one contract (take3).

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| lit | hold | 14 | 50% | 82% | 46% | 16% |
| lit | take3 | 14 | 57% | 63% | 48% | 32% |
| lit | trail | 14 | 57% | 68% | 30% | -0% |
| lit | half3_trail | 14 | 57% | 73% | 48% | 27% |
| not lit | hold | 6 | 50% | -29% | -45% | -60% |
| not lit | take3 | 6 | 50% | 2% | -37% | -60% |
| not lit | trail | 6 | 50% | -12% | -30% | -53% |
| not lit | half3_trail | 6 | 50% | -7% | -37% | -60% |
| SMH below its 20-day average | hold | 18 | 50% | 60% | 30% | 8% |
| SMH below its 20-day average | take3 | 18 | 56% | 55% | 43% | 31% |
| SMH below its 20-day average | trail | 18 | 56% | 50% | 20% | -4% |
| SMH below its 20-day average | half3_trail | 18 | 56% | 60% | 40% | 24% |
| SMH above it | hold | 2 | 50% | -48% | -96% | - |
| SMH above it | take3 | 2 | 50% | -48% | -96% | - |
| SMH above it | trail | 2 | 50% | -10% | -96% | - |
| SMH above it | half3_trail | 2 | 50% | -48% | -96% | - |

## 7. SPY puts at -0.5% or less (the put hand)

27 trades; the ledger trails (arms at 2x, 40% giveback).

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| d35, since 2024-02 | hold | 27 | 33% | 4% | -25% | -40% |
| d35, since 2024-02 | take3 | 27 | 33% | -23% | -33% | -42% |
| d35, since 2024-02 | trail | 27 | 37% | -8% | -21% | -34% |
| d35, since 2024-02 | half3_trail | 27 | 33% | -18% | -30% | -41% |
| d35, last 3 months | hold | 1 | 100% | 748% | - | - |
| d35, last 3 months | take3 | 1 | 100% | 217% | - | - |
| d35, last 3 months | trail | 1 | 100% | 291% | - | - |
| d35, last 3 months | half3_trail | 1 | 100% | 254% | - | - |
| d35, last year | hold | 9 | 44% | 59% | -28% | -52% |
| d35, last year | take3 | 9 | 44% | -0% | -28% | -52% |
| d35, last year | trail | 9 | 56% | 24% | -9% | -31% |
| d35, last year | half3_trail | 9 | 44% | 4% | -28% | -52% |
| d35, before the last year | hold | 18 | 28% | -24% | -45% | -65% |
| d35, before the last year | take3 | 18 | 28% | -35% | -49% | -65% |
| d35, before the last year | trail | 18 | 28% | -24% | -45% | -65% |
| d35, before the last year | half3_trail | 18 | 28% | -29% | -47% | -65% |

Strike otm07 for comparison:

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| since 2024-02 | hold | 27 | 26% | 11% | -36% | -53% |
| since 2024-02 | take3 | 27 | 30% | -22% | -32% | -42% |
| since 2024-02 | trail | 27 | 33% | -9% | -30% | -47% |
| since 2024-02 | half3_trail | 27 | 30% | -17% | -32% | -45% |
| last 3 months | hold | 1 | 100% | 1228% | - | - |
| last 3 months | take3 | 1 | 100% | 201% | - | - |
| last 3 months | trail | 1 | 100% | 531% | - | - |
| last 3 months | half3_trail | 1 | 100% | 366% | - | - |
| last year | hold | 9 | 33% | 97% | -45% | -69% |
| last year | take3 | 9 | 44% | 16% | -8% | -37% |
| last year | trail | 9 | 44% | 37% | -24% | -45% |
| last year | half3_trail | 9 | 44% | 26% | -16% | -37% |

The ledger's own days (Monday to Thursday, no macro day, no monthly-expiry week), strike d35:

| group | exit | trades | win% | avg | w/o best | w/o best 2 |
|---|---|---|---|---|---|---|
| since 2024-02 | hold | 17 | 41% | 39% | -5% | -28% |
| since 2024-02 | take3 | 17 | 41% | -3% | -17% | -32% |
| since 2024-02 | trail | 17 | 47% | 21% | 1% | -18% |
| since 2024-02 | half3_trail | 17 | 41% | 5% | -12% | -30% |
| last 3 months | hold | 1 | 100% | 748% | - | - |
| last 3 months | take3 | 1 | 100% | 217% | - | - |
| last 3 months | trail | 1 | 100% | 291% | - | - |
| last 3 months | half3_trail | 1 | 100% | 254% | - | - |
| last year | hold | 4 | 50% | 160% | -36% | -96% |
| last year | take3 | 4 | 50% | 27% | -36% | -96% |
| last year | trail | 4 | 75% | 82% | 12% | -23% |
| last year | half3_trail | 4 | 50% | 36% | -36% | -96% |

Trade by trade on the ledger's own days (d35; entry, result under trail, result held to 15:30):

| day | entry | trail | hold | SMH against its 20-day average |
|---|---|---|---|---|
| 2024-05-23 | 0.79 | 275% | 275% | above |
| 2024-10-01 | 1.24 | -96% | -96% | above |
| 2024-11-06 | 0.97 | -100% | -100% | below |
| 2024-11-21 | 1.25 | -100% | -100% | below |
| 2025-02-24 | 0.93 | -96% | -96% | above |
| 2025-02-27 | 1.93 | 34% | 34% | below |
| 2025-03-03 | 1.51 | 341% | 341% | below |
| 2025-03-04 | 1.96 | -100% | -100% | below |
| 2025-03-13 | 1.67 | 11% | 11% | below |
| 2025-04-21 | 1.99 | 92% | 92% | below |
| 2025-04-30 | 1.53 | -99% | -99% | above |
| 2025-06-05 | 1.15 | -32% | -32% | above |
| 2025-08-20 | 0.80 | -99% | -99% | below |
| 2026-01-29 | 1.47 | 52% | -93% | above |
| 2026-03-30 | 1.39 | 83% | 83% | below |
| 2026-06-25 | 1.36 | -99% | -99% | above |
| 2026-11-05 | 1.75 | 291% | 748% | below |

Does any evening state make the puts pay? (d35, trail)

| state of the evening before | lit: trades | win% | avg | w/o best 2 | not lit: trades | win% | avg | w/o best 2 |
|---|---|---|---|---|---|---|---|---|
| chip breadth >= 75% (the light) | 11 | 55% | 34% | -29% | 16 | 25% | -37% | -72% |
| chip breadth >= 50% | 18 | 39% | -9% | -49% | 9 | 33% | -6% | -67% |
| chip breadth = 100% | 2 | 100% | 192% | - | 25 | 32% | -24% | -53% |
| SMH below its 20-day average | 16 | 50% | 16% | -27% | 11 | 18% | -42% | -88% |
| SMH above its 100-day average | 15 | 27% | -32% | -69% | 12 | 50% | 22% | -37% |
| SMH below its 20-day and above its 100-day average | 5 | 40% | -22% | -99% | 22 | 36% | -5% | -37% |
| SPY below its 20-day average | 18 | 44% | 3% | -36% | 9 | 22% | -30% | -86% |
| the name below its own 20-day average | 18 | 44% | 3% | -36% | 9 | 22% | -30% | -86% |
| the name down over 5 sessions | 15 | 47% | 9% | -39% | 12 | 25% | -29% | -76% |
| SMH down over 5 sessions | 15 | 47% | 9% | -39% | 12 | 25% | -29% | -76% |
| SPY 10-day volatility above its 1-year median | 21 | 43% | -1% | -34% | 6 | 17% | -32% | -99% |
| light: turning | 2 | 50% | 96% | - | 25 | 36% | -16% | -44% |
| light: rates | 2 | 0% | -98% | - | 25 | 40% | -1% | -28% |
| light: stretched | 4 | 50% | 47% | -98% | 23 | 35% | -18% | -49% |
| light: diverge | 4 | 25% | 4% | -100% | 23 | 39% | -10% | -40% |

## 8. The ledgers' own trades so far

| day | ledger | mode | contract | result | chip breadth the evening before | SMH against its 20-day average |
|---|---|---|---|---|---|---|
| 2026-10-19 | stock_open_drive | shadow | TSLA261019C00365000 | 230% | 100% (lit) | below |
| 2026-10-19 | stock_open_drive | real | TSLA261019C00365000 | 259% | 100% (lit) | below |
| 2026-10-26 | stock_open_drive | shadow | TSLA261026C00400000 | -100% | 100% (lit) | below |
| 2026-10-26 | stock_open_drive | real | TSLA261026C00400000 | -100% | 100% (lit) | below |
| 2026-11-04 | spy_open_drive | shadow | SPY261104C00773000 | -100% | 100% (lit) | below |
| 2026-11-04 | spy_open_drive | real | SPY261104C00773000 | -100% | 100% (lit) | below |
| 2026-11-04 | stock_open_drive | shadow | TSLA261104C00392500 | 58% | 100% (lit) | below |
| 2026-11-04 | stock_open_drive | real | TSLA261104C00392500 | -99% | 100% (lit) | below |
| 2026-11-09 | spy_open_drive | shadow | SPY261109C00753000 | 280% | 100% (lit) | below |
| 2026-11-09 | stock_open_drive | shadow | TSLA261109C00385000 | -91% | 100% (lit) | below |
| 2026-11-09 | stock_open_drive | real | TSLA261109C00385000 | -95% | 100% (lit) | below |
| 2026-11-11 | stock_open_drive | shadow | TSLA261111C00392500 | -96% | 92% (lit) | below |
| 2026-11-11 | stock_open_drive | real | TSLA261111C00392500 | -95% | 92% (lit) | below |

