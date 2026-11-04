# Theme turn flags on daily bars

10 themes, 2 years of Alpaca daily bars to 2026-11-03. Theme = equal-weight basket of its members; five turn flags and five heat flags per day (see zoh/research/themes.py); state 'turning' / 'heating' with >= 3, used from the next session. Stock moves only, no option prices and no costs: these are forecast tests. Columns: n | mean | median | % positive.

## State at the last close

| theme | state | turn flags | heat flags |
|---|---|---|---|
| chips | turning | REL_WEAK, BREADTH, PERIPH | - |
| internet | neutral | BREADTH, PERIPH | - |
| software | turning | REL_WEAK, BREADTH, RATIO_LOW | - |
| banks | neutral | - | BREADTH_UP |
| health | neutral | PERIPH | REL_STRONG |
| energy | neutral | - | - |
| consumer | neutral | - | REL_STRONG, BREADTH_UP |
| industrials | heating | - | REL_STRONG, AT_HIGH, BREADTH_UP, RATIO_HIGH, PERIPH_UP |
| power | neutral | BREADTH | REL_STRONG |
| optical | neutral | REL_WEAK, BREADTH | - |

## Forward theme return minus SPY, by state (last 3 months)

| theme | state | days | 5d | 10d | 20d |
|---|---|---|---|---|---|
| chips | turning | 25 | -0.10% (50%) | -0.20% (33%) | +6.62% (78%) |
| chips | neutral | 33 | -0.49% (42%) | -0.45% (42%) | +0.27% (55%) |
| chips | heating | 8 | -2.83% (50%) | -7.93% (25%) | -15.08% (0%) |
| internet | turning | 7 | -3.03% (0%) | - | - |
| internet | neutral | 52 | -0.00% (54%) | +0.14% (59%) | +0.86% (73%) |
| internet | heating | 7 | -0.73% (29%) | -2.50% (29%) | -0.19% (60%) |
| software | turning | 12 | -0.14% (64%) | -0.41% (36%) | +3.58% (64%) |
| software | neutral | 36 | +0.79% (66%) | +1.82% (63%) | +0.01% (59%) |
| software | heating | 18 | +1.08% (72%) | +2.40% (67%) | +4.01% (69%) |
| banks | turning | 13 | -1.84% (8%) | -3.15% (8%) | -2.68% (33%) |
| banks | neutral | 52 | -0.52% (48%) | -1.57% (40%) | -5.44% (18%) |
| banks | heating | 1 | - | - | - |
| health | neutral | 53 | +1.24% (66%) | +2.24% (63%) | +3.07% (75%) |
| health | heating | 13 | +0.28% (45%) | +0.82% (50%) | -2.16% (17%) |
| energy | turning | 2 | +0.76% (100%) | +1.14% (100%) | +10.19% (100%) |
| energy | neutral | 49 | +1.79% (73%) | +3.21% (71%) | +4.49% (61%) |
| energy | heating | 15 | +0.40% (64%) | +1.29% (67%) | -0.54% (50%) |
| consumer | turning | 7 | +0.07% (43%) | +1.73% (43%) | +7.04% (71%) |
| consumer | neutral | 51 | -0.33% (25%) | -1.23% (23%) | -2.90% (26%) |
| consumer | heating | 8 | +1.67% (67%) | +4.98% (100%) | - |
| industrials | turning | 3 | -0.85% (0%) | -0.98% (0%) | -4.00% (0%) |
| industrials | neutral | 58 | -0.57% (32%) | -1.36% (22%) | -3.21% (5%) |
| industrials | heating | 5 | -1.98% (0%) | -2.98% (0%) | -5.27% (0%) |
| power | turning | 14 | +1.00% (54%) | +1.75% (67%) | +1.90% (57%) |
| power | neutral | 48 | -0.73% (41%) | -1.84% (33%) | -2.58% (22%) |
| power | heating | 4 | -5.19% (0%) | -9.33% (0%) | -8.54% (0%) |
| optical | turning | 23 | -1.59% (45%) | -2.29% (31%) | +6.30% (78%) |
| optical | neutral | 36 | +0.32% (56%) | -0.79% (55%) | -2.67% (43%) |
| optical | heating | 7 | -5.33% (29%) | -10.65% (14%) | -16.67% (0%) |
| **all** | turning | 106 | -0.63% (42%) | -0.76% (34%) | +3.24% (60%) |
| **all** | neutral | 468 | +0.13% (50%) | -0.03% (46%) | -0.79% (43%) |
| **all** | heating | 86 | -0.67% (51%) | -1.63% (47%) | -4.61% (33%) |

## Forward theme return minus SPY, by state (1 year)

| theme | state | days | 5d | 10d | 20d |
|---|---|---|---|---|---|
| chips | turning | 47 | +0.38% (57%) | +0.16% (41%) | +1.32% (58%) |
| chips | neutral | 143 | +1.65% (62%) | +2.94% (64%) | +6.62% (73%) |
| chips | heating | 62 | +0.30% (63%) | +2.18% (66%) | +5.41% (71%) |
| internet | turning | 20 | -0.77% (41%) | +2.18% (69%) | +3.17% (85%) |
| internet | neutral | 215 | -0.16% (44%) | -0.48% (42%) | -0.92% (43%) |
| internet | heating | 17 | -0.79% (35%) | -1.87% (29%) | -1.63% (33%) |
| software | turning | 72 | -0.33% (46%) | -1.81% (41%) | -2.00% (44%) |
| software | neutral | 150 | -0.96% (41%) | -1.23% (40%) | -2.91% (39%) |
| software | heating | 30 | +0.08% (60%) | +0.80% (56%) | +0.60% (52%) |
| banks | turning | 19 | -1.15% (21%) | -1.99% (26%) | -0.73% (44%) |
| banks | neutral | 203 | +0.03% (51%) | +0.07% (47%) | -0.12% (44%) |
| banks | heating | 30 | +0.42% (62%) | +0.33% (59%) | +0.05% (48%) |
| health | turning | 1 | +2.31% (100%) | +5.28% (100%) | +8.31% (100%) |
| health | neutral | 207 | +0.84% (59%) | +1.21% (60%) | +1.70% (68%) |
| health | heating | 44 | -0.92% (33%) | -0.33% (41%) | -0.01% (57%) |
| energy | turning | 19 | +0.93% (68%) | +2.03% (68%) | +3.69% (63%) |
| energy | neutral | 173 | +0.40% (62%) | +1.14% (58%) | +2.74% (64%) |
| energy | heating | 60 | +1.74% (71%) | +2.38% (72%) | +2.76% (66%) |
| consumer | turning | 15 | +0.36% (53%) | +0.28% (27%) | +2.30% (67%) |
| consumer | neutral | 216 | -0.42% (39%) | -0.94% (34%) | -2.33% (34%) |
| consumer | heating | 21 | -0.10% (47%) | +0.31% (50%) | -0.89% (46%) |
| industrials | turning | 7 | +0.01% (43%) | -0.14% (29%) | -2.26% (0%) |
| industrials | neutral | 202 | +0.11% (48%) | +0.19% (47%) | +0.37% (46%) |
| industrials | heating | 43 | +0.54% (57%) | +1.02% (60%) | +2.11% (62%) |
| power | turning | 34 | +1.61% (64%) | +1.90% (72%) | +0.66% (48%) |
| power | neutral | 191 | -0.26% (47%) | -0.49% (42%) | -0.56% (41%) |
| power | heating | 27 | -2.15% (30%) | -3.03% (26%) | -3.66% (27%) |
| optical | turning | 63 | +4.34% (73%) | +5.90% (70%) | +10.92% (84%) |
| optical | neutral | 136 | +1.40% (61%) | +2.58% (61%) | +5.43% (62%) |
| optical | heating | 53 | -1.27% (47%) | +0.57% (55%) | +5.11% (60%) |
| **all** | turning | 297 | +1.05% (56%) | +1.13% (52%) | +2.30% (58%) |
| **all** | neutral | 1836 | +0.21% (51%) | +0.38% (49%) | +0.75% (50%) |
| **all** | heating | 387 | -0.06% (53%) | +0.68% (55%) | +2.04% (57%) |

## Forward theme return minus SPY, by state (all)

| theme | state | days | 5d | 10d | 20d |
|---|---|---|---|---|---|
| chips | turning | 70 | +0.89% (62%) | +1.07% (55%) | +1.62% (56%) |
| chips | neutral | 321 | +1.08% (58%) | +1.77% (60%) | +4.21% (61%) |
| chips | heating | 120 | +0.58% (63%) | +2.70% (68%) | +5.52% (71%) |
| internet | turning | 22 | -0.72% (37%) | +1.92% (67%) | +2.59% (73%) |
| internet | neutral | 428 | +0.05% (49%) | +0.04% (49%) | +0.14% (54%) |
| internet | heating | 61 | +0.05% (48%) | -0.26% (36%) | -0.01% (53%) |
| software | turning | 92 | -0.12% (48%) | -1.20% (44%) | -0.59% (55%) |
| software | neutral | 356 | -0.28% (47%) | -0.21% (46%) | -1.16% (40%) |
| software | heating | 63 | +0.42% (60%) | +0.60% (63%) | +0.97% (60%) |
| banks | turning | 23 | -0.91% (26%) | -0.92% (39%) | -0.52% (41%) |
| banks | neutral | 425 | +0.28% (57%) | +0.56% (57%) | +0.95% (53%) |
| banks | heating | 63 | +0.33% (58%) | +0.28% (56%) | +0.14% (52%) |
| health | turning | 27 | -1.41% (48%) | -1.00% (48%) | -3.99% (33%) |
| health | neutral | 411 | +0.28% (52%) | +0.31% (50%) | +0.57% (56%) |
| health | heating | 73 | -0.53% (35%) | -0.41% (41%) | +0.11% (58%) |
| energy | turning | 41 | +0.41% (56%) | +1.77% (59%) | +1.99% (59%) |
| energy | neutral | 380 | +0.07% (54%) | +0.26% (51%) | +0.44% (53%) |
| energy | heating | 90 | +0.37% (60%) | -0.12% (49%) | -0.38% (46%) |
| consumer | turning | 19 | +0.64% (53%) | +0.75% (42%) | +1.89% (58%) |
| consumer | neutral | 457 | -0.34% (42%) | -0.74% (37%) | -1.53% (38%) |
| consumer | heating | 35 | -0.27% (36%) | +0.27% (53%) | -1.14% (41%) |
| industrials | turning | 7 | +0.01% (43%) | -0.14% (29%) | -2.26% (0%) |
| industrials | neutral | 438 | +0.16% (52%) | +0.34% (53%) | +0.73% (56%) |
| industrials | heating | 66 | +0.27% (48%) | +0.50% (54%) | +0.95% (52%) |
| power | turning | 64 | +1.18% (59%) | +1.41% (58%) | +0.73% (54%) |
| power | neutral | 363 | +0.23% (53%) | +0.58% (52%) | +1.63% (55%) |
| power | heating | 84 | -0.25% (50%) | -0.54% (37%) | -1.01% (41%) |
| optical | turning | 88 | +3.19% (66%) | +3.61% (63%) | +6.45% (65%) |
| optical | neutral | 313 | +1.85% (65%) | +3.29% (66%) | +6.71% (70%) |
| optical | heating | 110 | -0.71% (51%) | +1.78% (61%) | +5.50% (73%) |
| **all** | turning | 453 | +0.79% (54%) | +0.94% (53%) | +1.41% (55%) |
| **all** | neutral | 3892 | +0.29% (52%) | +0.52% (52%) | +1.07% (53%) |
| **all** | heating | 765 | +0.03% (53%) | +0.69% (53%) | +1.71% (57%) |

## Turning episodes (first day with >= 3 flags after 10 quiet sessions)

Result within 20 sessions: 'continued' = basket fell another 5% first, 'recovered' = reclaimed the fire-day 20-day high first.

| theme | fired | flags | result | 20d vs SPY |
|---|---|---|---|---|
| chips | 2024-10-21 | REL_WEAK, DIVERGE, PERIPH | continued | -6.0% |
| chips | 2024-12-20 | REL_WEAK, BREADTH, PERIPH | recovered | +10.3% |
| chips | 2025-01-27 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | +1.9% |
| chips | 2025-02-27 | REL_WEAK, BREADTH, RATIO_LOW | continued | -2.6% |
| chips | 2025-03-31 | REL_WEAK, BREADTH, RATIO_LOW | continued | +0.1% |
| chips | 2025-08-06 | REL_WEAK, DIVERGE, RATIO_LOW, PERIPH | recovered | -1.0% |
| chips | 2025-08-21 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +12.4% |
| chips | 2025-11-20 | REL_WEAK, BREADTH, RATIO_LOW | recovered | +3.9% |
| chips | 2026-02-04 | REL_WEAK, DIVERGE, BREADTH | recovered | +6.7% |
| chips | 2026-03-03 | REL_WEAK, DIVERGE, BREADTH | neither | +7.3% |
| chips | 2026-07-02 | REL_WEAK, DIVERGE, BREADTH | continued | -13.2% |
| chips | 2026-10-13 | REL_WEAK, DIVERGE, BREADTH | continued | open |
| internet | 2025-03-07 | BREADTH, RATIO_LOW, PERIPH | continued | -1.9% |
| internet | 2026-01-21 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -4.5% |
| internet | 2026-02-06 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | +3.4% |
| internet | 2026-06-03 | REL_WEAK, RATIO_LOW, PERIPH | continued | -2.6% |
| internet | 2026-07-23 | REL_WEAK, BREADTH, PERIPH | recovered | +4.8% |
| internet | 2026-10-22 | REL_WEAK, DIVERGE, RATIO_LOW, PERIPH | continued | open |
| software | 2025-01-07 | REL_WEAK, BREADTH, RATIO_LOW | neither | +6.8% |
| software | 2025-02-24 | REL_WEAK, BREADTH, RATIO_LOW | continued | +0.2% |
| software | 2025-03-31 | REL_WEAK, BREADTH, RATIO_LOW | continued | +9.6% |
| software | 2025-07-11 | REL_WEAK, RATIO_LOW, PERIPH | recovered | +0.6% |
| software | 2025-08-11 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | -1.8% |
| software | 2025-10-03 | REL_WEAK, DIVERGE, PERIPH | neither | +0.4% |
| software | 2025-11-11 | REL_WEAK, DIVERGE, RATIO_LOW | continued | +0.2% |
| software | 2026-01-02 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | continued | -18.5% |
| software | 2026-04-07 | REL_WEAK, BREADTH, RATIO_LOW | continued | -7.1% |
| software | 2026-09-08 | REL_WEAK, DIVERGE, PERIPH | continued | -5.6% |
| software | 2026-11-03 | REL_WEAK, BREADTH, RATIO_LOW | neither | open |
| banks | 2025-03-06 | REL_WEAK, BREADTH, RATIO_LOW | continued | -3.4% |
| banks | 2025-04-04 | REL_WEAK, BREADTH, RATIO_LOW | neither | +8.9% |
| banks | 2026-01-14 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -1.0% |
| banks | 2026-02-24 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | continued | +2.0% |
| banks | 2026-05-14 | REL_WEAK, RATIO_LOW, PERIPH | recovered | +11.9% |
| banks | 2026-09-17 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -8.7% |
| health | 2024-11-06 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -5.1% |
| health | 2024-12-12 | REL_WEAK, DIVERGE, RATIO_LOW | neither | +4.1% |
| health | 2025-04-09 | BREADTH, RATIO_LOW, PERIPH | continued | -8.1% |
| health | 2025-07-31 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +5.9% |
| health | 2026-05-08 | REL_WEAK, RATIO_LOW, PERIPH | recovered | +8.3% |
| energy | 2024-10-29 | DIVERGE, BREADTH, RATIO_LOW | neither | +2.5% |
| energy | 2024-12-06 | REL_WEAK, DIVERGE, RATIO_LOW | continued | +2.0% |
| energy | 2025-04-04 | REL_WEAK, BREADTH, RATIO_LOW | continued | -13.6% |
| energy | 2025-04-29 | REL_WEAK, DIVERGE, BREADTH | neither | -8.5% |
| energy | 2025-05-22 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +3.8% |
| energy | 2025-07-18 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -0.7% |
| energy | 2025-10-02 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -2.9% |
| energy | 2026-04-10 | REL_WEAK, DIVERGE, BREADTH | neither | -12.8% |
| energy | 2026-05-07 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +3.3% |
| energy | 2026-06-15 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -1.3% |
| energy | 2026-09-21 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +9.7% |
| consumer | 2025-03-14 | REL_WEAK, BREADTH, RATIO_LOW | neither | +5.5% |
| consumer | 2025-06-17 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | -1.4% |
| consumer | 2025-10-08 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -1.6% |
| consumer | 2026-04-02 | REL_WEAK, RATIO_LOW, PERIPH | neither | -10.2% |
| consumer | 2026-05-04 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -9.5% |
| consumer | 2026-06-02 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +2.8% |
| consumer | 2026-08-26 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -7.0% |
| consumer | 2026-09-21 | REL_WEAK, DIVERGE, RATIO_LOW, PERIPH | neither | +6.9% |
| industrials | 2026-04-22 | REL_WEAK, DIVERGE, RATIO_LOW | neither | -1.5% |
| industrials | 2026-09-02 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | -2.6% |
| power | 2024-12-10 | REL_WEAK, DIVERGE, RATIO_LOW | recovered | +13.4% |
| power | 2025-01-27 | REL_WEAK, DIVERGE, BREADTH | neither | -2.1% |
| power | 2025-02-24 | REL_WEAK, BREADTH, RATIO_LOW | continued | +3.6% |
| power | 2025-08-06 | REL_WEAK, DIVERGE, PERIPH | continued | -7.5% |
| power | 2025-10-22 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | +2.8% |
| power | 2025-12-17 | REL_WEAK, BREADTH, RATIO_LOW | neither | +1.7% |
| power | 2026-01-07 | DIVERGE, BREADTH, RATIO_LOW | neither | +0.1% |
| power | 2026-05-08 | REL_WEAK, DIVERGE, RATIO_LOW | continued | -7.2% |
| power | 2026-07-02 | REL_WEAK, DIVERGE, PERIPH | continued | -0.2% |
| power | 2026-08-21 | REL_WEAK, DIVERGE, BREADTH | neither | -2.1% |
| power | 2026-10-19 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | continued | open |
| optical | 2024-11-15 | REL_WEAK, BREADTH, PERIPH | recovered | +18.5% |
| optical | 2024-12-23 | REL_WEAK, DIVERGE, BREADTH, PERIPH | recovered | +8.1% |
| optical | 2025-01-27 | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | neither | -2.9% |
| optical | 2025-04-03 | REL_WEAK, BREADTH, RATIO_LOW | continued | +21.6% |
| optical | 2025-05-30 | REL_WEAK, DIVERGE, PERIPH | recovered | +12.2% |
| optical | 2025-08-20 | REL_WEAK, DIVERGE, BREADTH | recovered | +31.5% |
| optical | 2025-11-13 | REL_WEAK, BREADTH, PERIPH | recovered | +17.7% |
| optical | 2025-12-12 | DIVERGE, BREADTH, PERIPH | recovered | +7.2% |
| optical | 2026-01-08 | REL_WEAK, DIVERGE, BREADTH, PERIPH | recovered | +30.2% |
| optical | 2026-03-03 | DIVERGE, BREADTH, PERIPH | continued | +4.7% |
| optical | 2026-03-26 | REL_WEAK, BREADTH, PERIPH | continued | +26.0% |
| optical | 2026-04-28 | REL_WEAK, DIVERGE, BREADTH | recovered | +8.9% |
| optical | 2026-07-01 | REL_WEAK, DIVERGE, BREADTH | continued | -15.6% |
| optical | 2026-08-19 | REL_WEAK, DIVERGE, BREADTH | continued | +2.0% |
| optical | 2026-09-28 | REL_WEAK, DIVERGE, BREADTH | recovered | -12.0% |

Tally: continued 34, neither 28, recovered 25.

## Basket gap days, open -> close by prior-close state (last 3 months)

Gap up = basket opens >= +0.7% vs the prior close (the bounce / good-news day); gap down <= -0.7%. Members = each member's own open->close on those days.

| gap | state | basket n | mean | median | % up | members n | mean | median | % up |
|---|---|---|---|---|---|---|---|---|---|
| up | turning | 34 | +0.22% | +0.21% | 56% | 257 | +0.07% | +0.29% | 53% |
| up | neutral | 123 | -0.01% | -0.21% | 47% | 805 | -0.11% | -0.25% | 45% |
| up | heating | 20 | -0.31% | -0.14% | 45% | 132 | -0.26% | -0.06% | 48% |
| down | turning | 37 | -0.33% | +0.11% | 51% | 263 | -0.18% | -0.02% | 49% |
| down | neutral | 74 | -0.16% | -0.05% | 46% | 495 | -0.12% | -0.08% | 48% |
| down | heating | 20 | -0.27% | -0.27% | 45% | 125 | -0.10% | -0.13% | 50% |

## Basket gap days, open -> close by prior-close state (1 year)

Gap up = basket opens >= +0.7% vs the prior close (the bounce / good-news day); gap down <= -0.7%. Members = each member's own open->close on those days.

| gap | state | basket n | mean | median | % up | members n | mean | median | % up |
|---|---|---|---|---|---|---|---|---|---|
| up | turning | 98 | +0.36% | +0.37% | 61% | 658 | +0.21% | +0.31% | 55% |
| up | neutral | 421 | -0.03% | +0.07% | 52% | 2784 | -0.03% | -0.02% | 49% |
| up | heating | 84 | -0.10% | -0.09% | 49% | 612 | +0.01% | -0.07% | 48% |
| down | turning | 87 | +0.03% | +0.11% | 53% | 597 | +0.09% | +0.07% | 52% |
| down | neutral | 305 | +0.05% | -0.01% | 49% | 2034 | +0.08% | +0.05% | 51% |
| down | heating | 78 | -0.23% | -0.27% | 41% | 533 | -0.41% | -0.41% | 44% |

## Basket gap days, open -> close by prior-close state (all)

Gap up = basket opens >= +0.7% vs the prior close (the bounce / good-news day); gap down <= -0.7%. Members = each member's own open->close on those days.

| gap | state | basket n | mean | median | % up | members n | mean | median | % up |
|---|---|---|---|---|---|---|---|---|---|
| up | turning | 132 | +0.22% | +0.22% | 60% | 896 | +0.11% | +0.12% | 52% |
| up | neutral | 798 | -0.01% | +0.13% | 54% | 5313 | +0.01% | +0.05% | 51% |
| up | heating | 169 | -0.02% | +0.08% | 51% | 1188 | -0.01% | -0.05% | 49% |
| down | turning | 121 | +0.29% | +0.27% | 55% | 811 | +0.27% | +0.14% | 53% |
| down | neutral | 621 | +0.15% | +0.09% | 52% | 4100 | +0.14% | +0.12% | 52% |
| down | heating | 129 | -0.09% | -0.05% | 47% | 891 | -0.17% | -0.05% | 49% |

## Chips: the flags this autumn

| day | state | turn flags | basket vs 20d high |
|---|---|---|---|
| 2026-09-04 | neutral | DIVERGE | -6.1% |
| 2026-09-11 | neutral | DIVERGE | -5.1% |
| 2026-09-14 | turning | REL_WEAK, DIVERGE, BREADTH | -10.9% |
| 2026-09-15 | neutral | REL_WEAK, BREADTH | -7.8% |
| 2026-09-16 | neutral | REL_WEAK | -7.0% |
| 2026-09-21 | heating | - | +0.0% |
| 2026-09-22 | heating | - | +0.0% |
| 2026-09-29 | heating | - | -0.3% |
| 2026-09-30 | heating | - | -0.2% |
| 2026-10-01 | heating | - | +0.0% |
| 2026-10-02 | heating | - | +0.0% |
| 2026-10-05 | heating | - | +0.0% |
| 2026-10-08 | neutral | REL_WEAK | -4.4% |
| 2026-10-09 | neutral | REL_WEAK, DIVERGE | -5.2% |
| 2026-10-12 | neutral | REL_WEAK, DIVERGE | -7.7% |
| 2026-10-13 | turning | REL_WEAK, DIVERGE, BREADTH | -8.6% |
| 2026-10-14 | turning | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | -12.8% |
| 2026-10-15 | turning | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW | -13.8% |
| 2026-10-16 | turning | REL_WEAK, BREADTH, RATIO_LOW | -17.7% |
| 2026-10-19 | turning | REL_WEAK, DIVERGE, BREADTH | -16.2% |
| 2026-10-20 | turning | REL_WEAK, DIVERGE, BREADTH | -17.0% |
| 2026-10-21 | turning | REL_WEAK, DIVERGE, BREADTH, PERIPH | -15.7% |
| 2026-10-22 | turning | REL_WEAK, DIVERGE, BREADTH, RATIO_LOW, PERIPH | -21.8% |
| 2026-10-23 | turning | REL_WEAK, BREADTH, PERIPH | -21.3% |
| 2026-10-26 | turning | REL_WEAK, DIVERGE, BREADTH, PERIPH | -19.1% |
| 2026-10-27 | turning | DIVERGE, BREADTH, PERIPH | -16.7% |
| 2026-10-28 | turning | DIVERGE, BREADTH, PERIPH | -14.2% |
| 2026-10-29 | turning | DIVERGE, BREADTH, PERIPH | -15.9% |
| 2026-10-30 | turning | BREADTH, RATIO_LOW, PERIPH | -23.3% |
| 2026-11-02 | turning | REL_WEAK, BREADTH, RATIO_LOW, PERIPH | -26.7% |
| 2026-11-03 | turning | REL_WEAK, BREADTH, PERIPH | -24.8% |

## Our trades on theme members (journal/trades.csv), by the theme's state at entry

pnl % per trade on the contract; $ = summed real-paper P&L of the real fills among them.

| direction | state | n (real) | mean pnl % | median | % positive | real $ |
|---|---|---|---|---|---|---|
| call | heating | 7 (1) | +69% | +2% | 57% | +322 |
| call | neutral | 38 (10) | -20% | -90% | 34% | -439 |
| call | turning | 28 (8) | -68% | -99% | 21% | -442 |
| put | heating | 1 (0) | +114% | +114% | 100% | +0 |
| put | neutral | 6 (2) | +157% | +222% | 67% | +369 |
| put | turning | 7 (3) | +8% | -99% | 43% | -109 |

## Longer horizons (added 2026-11-04 14:10 ET)

Same flags, forward windows out to 120 sessions (themes.py constants FWD; the "3-month flags" row uses LOOK 60 /
MONTH 63 / WEEK 21). Theme return minus SPY, mean (% positive, n).

| flags | window | state | 20d | 40d | 60d | 120d |
|---|---|---|---|---|---|---|
| 20-day | all, 2 years | turning | +1.4% (55%, 407) | +1.9% (49%, 372) | +4.0% (49%, 350) | +9.3% (54%, 267) |
| 20-day | all, 2 years | neutral | +1.1% (53%) | +2.3% (55%) | +4.0% (56%) | +9.8% (59%) |
| 20-day | all, 2 years | heating | +1.7% (57%, 731) | +4.0% (60%) | +5.5% (57%) | **+17.8% (62%, 608)** |
| 20-day | all, last 6 months | turning | +2.1% (56%, 153) | +0.7% (42%) | +4.1% (57%, 96) | +1.5% (46%, 13) |
| 20-day | all, last 6 months | heating | -1.1% (48%, 133) | -1.5% (51%) | **-3.0% (43%, 92)** | -12.5% (30%, 10) |
| 20-day | chips, 2 years | turning | +1.6% (56%, 54) | +5.4% (51%) | +9.8% (69%) | +28.5% (82%, 28) |
| 20-day | chips, 2 years | heating | +5.5% (71%, 120) | +9.7% (76%) | +13.7% (82%) | +45.5% (98%, 96) |
| 20-day | chips, last 6 months | turning | +0.2% (50%, 26) | -0.5% (32%) | -2.0% (45%, 20) | - |
| 20-day | chips, last 6 months | heating | +1.2% (46%, 28) | -2.3% (43%) | -6.3% (30%, 20) | - |
| 3-month | all, 2 years | turning | +0.3% (52%, 788) | +0.3% (46%) | +1.2% (49%) | +4.4% (55%, 493) |
| 3-month | all, 2 years | heating | +2.0% (56%, 598) | +4.4% (57%) | +6.2% (54%) | +19.9% (61%, 519) |
| 3-month | all, last 6 months | heating | -1.5% (39%, 93) | -2.4% (46%) | -6.0% (33%, 61) | -14.4% (14%, 14) |

From the fire day of a 20-day-flag episode (n 86 -> 66 as the window lengthens): 20d +1.7% (median +0.4%),
60d +7.3% (median +2.6%), 120d +16.7% (median +7.8%), 54-56% positive at every horizon. With 3-month flags:
73 episodes, 37 continued / 28 recovered / 8 neither; 60d median 0.0%.

Reading: pulling the horizon out does not turn the turn flag into a short signal at any horizon; after a turn
fires, the theme is back ahead of SPY four to six months later more often than not. The long-horizon pattern in
the two-year data is momentum on the heat side (heating themes +18% vs SPY over six months, 62% positive), and
that is exactly what reversed in the last six months (heating -3% at 60 days, -12.5% at 120 days on a small n),
which is the regime change: chasing the hot theme stopped paying around May 2026. Chips underperformed SPY over
40-60 days in every state in the last six months. By the house rule (positive over two years, negative recently
-> reject for now) theme momentum is not a trade; mean reversion into turning themes (positive recently, flat over
two years) is a candidate at most.
