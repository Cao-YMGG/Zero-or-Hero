# Week 46: where the week went (to 2026-11-13)

SPY +2.6% on the week (open to close +1.5%, +0.2%, +0.4%, +0.4%, -0.8%), SMH +4.9%. Real: 3 trades, 0 wins, -$285. Shadows: 26 closed, 5 wins. Option tables are real option minute bars, 10% costs each way; `a / b / c` = average / without the best trade / without the best two. See zoh/research/week46.py.

## 1. The picks at the stock: right at the open, late in the session (items 57, 59)

| group | picks | right open to close | avg open to close | entered | right from the entry | avg from the entry | 1% or more from the entry |
|---|---|---|---|---|---|---|---|
| pre-market sniper | 24 | 15 | +0.24% | 18 | 11 | +0.30% | 6 |
| intraday pick | 17 | 16 | +2.01% | 17 | 6 | -0.37% | 1 |
| sniper, rating change (upgrade or target) | 13 | 10 | +0.91% | 10 | 8 | +1.01% | 5 |
| sniper, company news | 10 | 5 | -0.46% | 7 | 3 | -0.47% | 1 |
| sniper, this week | 5 | 4 | +0.89% | 4 | 3 | +0.62% | 2 |

An intraday pick is right about the day and late for it: the stock had made its move before the pick. By how far it had already gone (its way from the open at the entry; d0.20, half at 3x, trail from 1.5x, sold day one):

| at the entry | picks | right from the entry | avg from the entry | option: n / win / a / b / c |
|---|---|---|---|---|
| under 2% its way | 5 | 3 | +0.10% | 5 | 60% | +13% / -27% / -36% |
| 2-3% | 7 | 3 | -0.07% | 7 | 0% | -48% / -56% / -65% |
| 3% or more | 5 | 0 | -1.26% | 5 | 0% | -42% / -49% / -58% |
| under one of its own average ranges | 4 | 1 | -0.35% | 4 | 25% | -74% / -100% / -100% |
| one average range or more | 13 | 5 | -0.38% | 13 | 15% | -15% / -30% / -33% |
| picked before 11:00 | 7 | 4 | +0.11% | 7 | 29% | +4% / -24% / -29% |
| picked 11:00-13:00 | 2 | 1 | -1.09% | 2 | 0% | -99% / -100% / - |
| picked after 13:00 | 8 | 1 | -0.62% | 8 | 12% | -40% / -46% / -52% |

## 2. The sniper by class, on real option prices (item 57)

Live entry (first minute 09:32-10:00 at or beyond the open). `carried` = held past day one to the expiry where the contract outlives the day, the trail still on.

| class | strike | exit | sold day one: n / win / a / b / c | carried: n / win / a / b / c |
|---|---|---|---|---|
| rating change | d0.10 | half3_arm1.5 | 10 | 50% | +24% / -3% / -24% | 10 | 50% | +21% / -7% / -28% |
| rating change | d0.10 | half2_arm1.5 | 10 | 50% | +17% / -7% / -26% | 10 | 50% | +19% / -5% / -23% |
| rating change | d0.10 | hold | 10 | 30% | -27% / -56% / -70% | 10 | 0% | -98% / -100% / -100% |
| rating change | d0.30 | half3_arm1.5 | 10 | 50% | +7% / -11% / -28% | 10 | 50% | +4% / -15% / -21% |
| rating change | d0.30 | half2_arm1.5 | 10 | 50% | +11% / -3% / -17% | 10 | 50% | +13% / -1% / -11% |
| rating change | d0.30 | hold | 10 | 40% | -12% / -32% / -51% | 10 | 10% | -75% / -86% / -92% |
| rating change | d0.45 | half3_arm1.5 | 10 | 60% | +17% / +1% / -9% | 10 | 60% | +19% / +3% / -3% |
| rating change | d0.45 | half2_arm1.5 | 10 | 60% | +17% / +7% / -4% | 10 | 60% | +22% / +12% / +6% |
| rating change | d0.45 | hold | 10 | 60% | +9% / -8% / -18% | 10 | 30% | -45% / -56% / -67% |
| company news | d0.10 | half3_arm1.5 | 7 | 14% | -61% / -82% / -98% | 7 | 14% | -62% / -83% / -99% |
| company news | d0.10 | half2_arm1.5 | 7 | 14% | -56% / -82% / -98% | 7 | 14% | -57% / -83% / -99% |
| company news | d0.10 | hold | 7 | 14% | -67% / -85% / -98% | 7 | 0% | -90% / -99% / -100% |
| company news | d0.30 | half3_arm1.5 | 7 | 0% | -69% / -80% / -95% | 7 | 29% | -42% / -61% / -79% |
| company news | d0.30 | half2_arm1.5 | 7 | 0% | -69% / -80% / -95% | 7 | 29% | -39% / -58% / -79% |
| company news | d0.30 | hold | 7 | 0% | -69% / -80% / -95% | 7 | 14% | -76% / -98% / -99% |
| company news | d0.45 | half3_arm1.5 | 7 | 14% | -63% / -74% / -87% | 7 | 14% | -55% / -66% / -78% |
| company news | d0.45 | half2_arm1.5 | 7 | 14% | -63% / -74% / -87% | 7 | 14% | -48% / -66% / -78% |
| company news | d0.45 | hold | 7 | 29% | -58% / -72% / -87% | 7 | 14% | -50% / -71% / -80% |
| every sniper | d0.10 | half3_arm1.5 | 18 | 33% | -16% / -32% / -45% | 18 | 33% | -18% / -35% / -48% |
| every sniper | d0.10 | half2_arm1.5 | 18 | 33% | -18% / -32% / -43% | 18 | 33% | -17% / -32% / -43% |
| every sniper | d0.10 | hold | 18 | 22% | -46% / -63% / -70% | 18 | 0% | -95% / -99% / -100% |
| every sniper | d0.30 | half3_arm1.5 | 18 | 28% | -28% / -40% / -50% | 18 | 39% | -19% / -31% / -38% |
| every sniper | d0.30 | half2_arm1.5 | 18 | 28% | -26% / -35% / -44% | 18 | 39% | -14% / -22% / -29% |
| every sniper | d0.30 | hold | 18 | 22% | -39% / -51% / -61% | 18 | 11% | -77% / -85% / -92% |
| every sniper | d0.45 | half3_arm1.5 | 18 | 39% | -20% / -31% / -37% | 18 | 39% | -16% / -27% / -32% |
| every sniper | d0.45 | half2_arm1.5 | 18 | 39% | -20% / -28% / -35% | 18 | 39% | -12% / -19% / -24% |
| every sniper | d0.45 | hold | 18 | 44% | -22% / -33% / -40% | 18 | 22% | -50% / -57% / -64% |

Each rating-change sniper (0.45 delta, half at 2x and a trail from 1.5x, sold day one):

| day | stock | class | open to close | entered | option |
|---|---|---|---|---|---|
| 2026-10-06 | AMD | target | +0.2% | no (against the pick until 10:00) | - |
| 2026-10-07 | MRVL | upgrade | +1.3% | 09:35 | +12% |
| 2026-10-08 | PLTR | upgrade | -0.2% | 09:31 | -73% |
| 2026-10-12 | CRM | upgrade | -1.2% | 09:31 | -63% |
| 2026-10-13 | META | target | +3.6% | 09:31 | +104% |
| 2026-10-14 | META | target | -2.9% | no (against the pick until 10:00) | - |
| 2026-10-19 | MSFT | target | +0.9% | 09:31 | -3% |
| 2026-10-22 | UNH | target | +1.6% | 09:31 | +89% |
| 2026-10-26 | TSLA | upgrade | +2.0% | 09:31 | +20% |
| 2026-10-30 | GEV | upgrade | +0.9% | 09:31 | -7% |
| 2026-11-09 | WMT | target | +0.7% | no (against the pick until 10:00) | - |
| 2026-11-11 | AAPL | upgrade | +1.8% | 09:31 | +28% |
| 2026-11-12 | AMD | upgrade | +2.9% | 09:36 | +59% |

The same question on every rating headline of two years, not only the ones I picked (95 events since 2024-02 on 25 large caps: a strict '<firm> upgrades / downgrades <stock>' headline before 09:30, bought at 09:32 when the stock is not against the rating, nearest expiry):

| events | strike | exit | sold day one: n / win / a / b / c | carried: n / win / a / b / c |
|---|---|---|---|---|
| all | d0.30 | half2_arm1.5 | 95 | 35% | -9% / -12% / -15% | 95 | 44% | +10% / +4% / -1% |
| all | d0.30 | half3_arm1.5 | 95 | 35% | -9% / -13% / -15% | 95 | 44% | +10% / +5% / -0% |
| all | d0.30 | hold | 95 | 24% | -23% / -29% / -33% | 95 | 22% | -7% / -20% / -27% |
| all | d0.45 | half2_arm1.5 | 95 | 34% | -14% / -18% / -20% | 95 | 45% | +2% / -3% / -8% |
| all | d0.45 | half3_arm1.5 | 95 | 33% | -14% / -18% / -20% | 95 | 42% | +0% / -5% / -9% |
| all | d0.45 | hold | 95 | 29% | -20% / -26% / -29% | 95 | 35% | -2% / -11% / -17% |
| last 3 months | d0.30 | half2_arm1.5 | 14 | 29% | -16% / -28% / -38% | 14 | 36% | +1% / -17% / -31% |
| last 3 months | d0.30 | half3_arm1.5 | 14 | 29% | -15% / -30% / -41% | 14 | 36% | +2% / -16% / -34% |
| last 3 months | d0.30 | hold | 14 | 21% | -42% / -57% / -64% | 14 | 14% | -59% / -78% / -86% |
| last 3 months | d0.45 | half2_arm1.5 | 14 | 43% | -13% / -23% / -29% | 14 | 50% | +3% / -12% / -22% |
| last 3 months | d0.45 | half3_arm1.5 | 14 | 36% | -14% / -28% / -32% | 14 | 43% | +3% / -13% / -27% |
| last 3 months | d0.45 | hold | 14 | 36% | -31% / -43% / -49% | 14 | 36% | -35% / -50% / -59% |
| calls (upgrades), all | d0.30 | half2_arm1.5 | 62 | 35% | -5% / -11% / -14% | 62 | 48% | +25% / +17% / +9% |
| calls (upgrades), all | d0.30 | half3_arm1.5 | 62 | 35% | -6% / -12% / -16% | 62 | 48% | +26% / +18% / +10% |
| calls (upgrades), all | d0.30 | hold | 62 | 24% | -16% / -25% / -31% | 62 | 23% | +9% / -11% / -22% |
| calls (upgrades), all | d0.45 | half2_arm1.5 | 62 | 35% | -9% / -14% / -17% | 62 | 52% | +19% / +12% / +5% |
| calls (upgrades), all | d0.45 | half3_arm1.5 | 62 | 34% | -7% / -14% / -17% | 62 | 48% | +17% / +10% / +3% |
| calls (upgrades), all | d0.45 | hold | 62 | 29% | -13% / -22% / -26% | 62 | 40% | +19% / +4% / -4% |
| calls (upgrades), last 3 months | d0.30 | half2_arm1.5 | 10 | 20% | -28% / -40% / -48% | 10 | 30% | -3% / -30% / -43% |
| calls (upgrades), last 3 months | d0.30 | half3_arm1.5 | 10 | 20% | -26% / -40% / -48% | 10 | 30% | -0% / -27% / -43% |
| calls (upgrades), last 3 months | d0.30 | hold | 10 | 10% | -59% / -68% / -74% | 10 | 10% | -71% / -82% / -88% |
| calls (upgrades), last 3 months | d0.45 | half2_arm1.5 | 10 | 40% | -16% / -23% / -29% | 10 | 50% | +12% / -9% / -17% |
| calls (upgrades), last 3 months | d0.45 | half3_arm1.5 | 10 | 30% | -22% / -27% / -33% | 10 | 40% | +6% / -15% / -24% |
| calls (upgrades), last 3 months | d0.45 | hold | 10 | 30% | -40% / -48% / -56% | 10 | 40% | -36% / -46% / -56% |
| puts (downgrades), all | d0.30 | half2_arm1.5 | 33 | 33% | -16% / -21% / -26% | 33 | 36% | -20% / -25% / -30% |
| puts (downgrades), all | d0.30 | half3_arm1.5 | 33 | 33% | -15% / -21% / -28% | 33 | 36% | -19% / -26% / -33% |
| puts (downgrades), all | d0.30 | hold | 33 | 24% | -37% / -43% / -50% | 33 | 21% | -36% / -49% / -60% |
| puts (downgrades), all | d0.45 | half2_arm1.5 | 33 | 30% | -25% / -30% / -34% | 33 | 33% | -31% / -38% / -44% |
| puts (downgrades), all | d0.45 | half3_arm1.5 | 33 | 30% | -26% / -32% / -37% | 33 | 30% | -32% / -40% / -48% |
| puts (downgrades), all | d0.45 | hold | 33 | 30% | -34% / -39% / -44% | 33 | 24% | -40% / -49% / -57% |

## 3. The gate of the open sniper, on the stock (item 64)

| gate | entered | avg its way from the open at the entry | right from the entry | avg from the entry |
|---|---|---|---|---|
| first minute at or beyond the open (live) | 18 of 24 | +0.38% | 11 | +0.30% |
| five closed minutes in a row beyond the open | 15 of 24 | +0.98% | 10 | +0.18% |
| a close beyond the first five minutes' extreme | 11 of 24 | +0.90% | 9 | +0.76% |

On the 15 days both gates entered: live +0.74% from the entry, five minutes +0.18%.

## 4. Exits of the open-drive ledgers on 0.35-delta contracts (item 60)

The ledgers' own days from opengate.json (NVDA / TSLA calls at +0.8%, SPY calls at +0.5%, SPY puts at -0.5%), exits to 15:30.

| family | period | trades (2x / 3x reached) | hold | all out at 3x | trail from 2x | half at 3x + trail |
|---|---|---|---|---|---|---|
| stock | all | 29 (17 / 12) | 45% / +69% / +39% / +12% | 45% / +16% / +8% / -0% | 52% / +31% / +8% / -5% | 45% / +36% / +18% / +2% |
| stock | last 3 months | 12 (5 / 3) | 33% / -31% / -46% / -60% | 33% / -13% / -36% / -60% | 42% / -20% / -43% / -56% | 33% / -18% / -41% / -60% |
| spy_call | all | 16 (11 / 9) | 56% / +69% / +37% / +11% | 62% / +64% / +51% / +38% | 62% / +63% / +30% / +4% | 62% / +69% / +48% / +29% |
| spy_call | last 3 months | 2 (1 / 1) | 50% / +106% / -86% / - | 50% / +83% / -86% / - | 50% / -32% / -86% / - | 50% / +95% / -86% / - |
| spy_put | all | 17 (11 / 5) | 41% / +39% / -5% / -28% | 41% / -3% / -17% / -32% | 47% / +21% / +1% / -18% | 41% / +5% / -12% / -30% |
| spy_put | last 3 months | 1 (1 / 1) | 100% / +748% / - / - | 100% / +217% / - / - | 100% / +291% / - / - | 100% / +254% / - / - |

## 5. The full-stake shadows: held to expiry against a trail on the same contract

| entered | variant | contract | stake | peak | held to expiry | with the small leg's trail (from the peak) | small leg that day |
|---|---|---|---|---|---|---|---|
| 2026-11-06 | catalyst_open_hero | LLY261106C01390000 | $236 | 1.64x | -100% | +0% | -100% (another strike) |
| 2026-11-06 | catalyst_intraday_hero | GE261106C00330000 | $456 | 1.00x | -98% | -98% | -98% |
| 2026-11-09 | catalyst_open_hero | WMT261113C00131000 | $442 | 1.00x | -100% | -100% | -100% |
| 2026-11-09 | catalyst_intraday_hero | LLY261113C01470000 | $423 | 1.25x | -100% | -100% | - |
| 2026-11-10 | catalyst_intraday_hero | AMZN261111C00277500 | $385 | 1.00x | -100% | -100% | -100% |
| 2026-11-10 | catalyst_open_hero | TSM261113C00415000 | $404 | 7.06x | -100% | +324% | +56% (another strike) |
| 2026-11-11 | catalyst_open_hero | AAPL261111C00357500 | $408 | 1.54x | -100% | +0% | -4% |
| 2026-11-11 | catalyst_intraday_hero | MSFT261111P00515000 | $372 | 1.84x | -100% | +10% | +10% |
| 2026-11-12 | catalyst_open_hero | AMD261113C00617500 | $330 | 2.53x | -100% | +52% | - |
| 2026-11-12 | catalyst_intraday_hero | AVGO261113C00377500 | $298 | 1.88x | -100% | +13% | +12% (another strike) |
| 2026-11-13 | catalyst_open_hero | TSLA261113C00415000 | $364 | 1.00x | -100% | -100% | -100% |

11 trades, 0 wins, $-4,110; 6 traded at 1.5x or better first. With the trail the same stakes come to about $-508 (an estimate from the recorded peak: a trail sells after the peak, at 60% of it or the entry, whichever is higher).

## 6. The SPY call (item 66)

30 mornings since 2026-10-05; 5 took a side (the last on 2026-10-22), right open to close on 4. Since the bar went to 0.60 / 0.40 on 2026-10-23: 16 mornings with a p_up, between 0.44 and 0.54, so none reached the bar, and none would have at 0.57 / 0.43. Brier 0.240 (0.250 for always 0.50). SPY closed above its open on 12 of the 16; the side I leaned to was right on 10 of 13; 'always up' on 9 of the same 13.

| p_up | mornings | closed above the open | avg open to close |
|---|---|---|---|
| 0.00-0.45 | 1 | 1 | +0.26% |
| 0.45-0.50 | 2 | 0 | -2.49% |
| 0.50-0.55 | 13 | 11 | +0.17% |

## 7. The opportunity log, split (12 sessions; item 67)

| group | ideas | paid (1% or more its way) | right | wrong | avg against SPY | without the best |
|---|---|---|---|---|---|---|
| all | 179 | 51 (28%) | 43 | 85 (47%) | +0.05% | +0.01% |
| listed by 10:00 | 101 | 37 (37%) | 21 | 43 (43%) | +0.25% | +0.18% |
| listed 10:01-12:00 | 62 | 13 (21%) | 16 | 33 (53%) | -0.18% | -0.25% |
| listed after 12:00 | 16 | 1 (6%) | 6 | 9 (56%) | -0.31% | -0.43% |
| call on a day SPY closed above its open | 69 | 27 (39%) | 19 | 23 (33%) | +0.31% | +0.21% |
| put on a day SPY closed above its open | 54 | 13 (24%) | 15 | 26 (48%) | -0.24% | -0.34% |
| call on a day SPY closed below its open | 34 | 1 (3%) | 6 | 27 (79%) | -0.24% | -0.35% |
| put on a day SPY closed below its open | 22 | 10 (45%) | 3 | 9 (41%) | +0.42% | +0.16% |
| after 10:00, under 1% its way from the open | 13 | 2 (15%) | 6 | 5 (38%) | -0.26% | -0.37% |
| after 10:00, 1-3% its way | 29 | 6 (21%) | 8 | 15 (52%) | +0.05% | -0.02% |
| after 10:00, 3% or more its way | 30 | 6 (20%) | 6 | 18 (60%) | -0.35% | -0.52% |
| this week | 92 | 27 (29%) | 26 | 39 (42%) | -0.10% | -0.18% |
| this week, calls | 54 | 22 (41%) | 15 | 17 (31%) | +0.34% | +0.21% |
| this week, puts | 38 | 5 (13%) | 11 | 22 (58%) | -0.72% | -0.81% |
| type: company_news | 46 | 16 (35%) | 9 | 21 (46%) | -0.04% | -0.20% |
| type: sector_move | 22 | 2 (9%) | 8 | 12 (55%) | -0.14% | -0.31% |
| type: relative_weakness | 14 | 2 (14%) | 4 | 8 (57%) | -0.44% | -0.59% |
| type: analyst | 13 | 7 (54%) | 5 | 1 (8%) | +1.42% | +1.04% |
| type: sector_intraday | 11 | 5 (45%) | 1 | 5 (45%) | +0.10% | -0.08% |
| type: rotation_laggard | 9 | 1 (11%) | 2 | 6 (67%) | -0.59% | -0.95% |
| type: gapdown_rebound | 9 | 1 (11%) | 3 | 5 (56%) | -0.23% | -0.41% |
| type: peer_readthrough | 9 | 4 (44%) | 0 | 5 (56%) | +0.93% | +0.44% |
| type: financing_fade | 8 | 3 (38%) | 2 | 3 (38%) | -0.13% | -0.38% |
| type: sympathy | 8 | 3 (38%) | 2 | 3 (38%) | +0.20% | -0.03% |

## 8. The rotation map as a same-day forecast (item 68)

My own lists, 30 mornings: the heating names beat the cooling names open to close on 12 (this week 0 of 5); against SPY the heating names averaged -0.07% and the cooling names -0.45% (below SPY on 20 mornings).

The theme model's state at a close against the basket's next open-to-close, less SPY's:

| period | state | theme-days | avg against SPY | beat SPY |
|---|---|---|---|---|
| last 3 months | heating | 84 | -0.073% | 50% |
| last 3 months | neutral | 457 | -0.021% | 49% |
| last 3 months | turning | 119 | -0.193% | 50% |
| two years | heating | 772 | -0.025% | 50% |
| two years | neutral | 3864 | -0.006% | 51% |
| two years | turning | 464 | +0.132% | 53% |

## 9. A release pop that fades before the bell (item 63)

26 release days in the calendar (CPI and jobs since 2025-10, plus the 2026-11-13 PPI); the first reaction is the larger of the 08:30-08:40 extremes against the 08:29 print, 25 days with 0.15% or more.

| at the 09:30 open | days | open to close with the first reaction: right | avg | open to close against it by 0.5% or more |
|---|---|---|---|---|
| half or more of the reaction gone | 16 | 8 | -0.19% | 3 |
| more than half still there | 9 | 4 | -0.34% | 2 |
