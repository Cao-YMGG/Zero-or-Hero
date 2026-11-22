# Week 47 (2026-11-16 to 2026-11-20): the owed tests on real option prices

Written 2026-11-22. Each test had its bar written before the run (journal/research/SUNDAY_TESTS.md). Numbers are
average / without the best trade / without the best two unless said otherwise; costs are 10% of the option's price
each way unless said otherwise; the last 3 months start 2026-08-21. Data: `week47.json`, `sellside.json`,
`fills.json`.

## The week

SPY closed below its open on all five sessions (-1.3%, -0.8%, -0.4%, -2.9%, -3.2%) and lost about 8% on the week;
chips led it down (SMH -8.7% open to close on Friday, NVDA -12.5%). No real order filled: the one that was sent
(nvda_gapdown_put, Friday) was cancelled at its limit. Five shadow trades closed, three of them winners, the
largest a carried TSM put that the two crash days turned into +720%. The morning SPY estimate stayed between 0.48
and 0.56 on five down days (Brier 0.253 against 0.250 for a flat 0.50). The Trade workflow ran clean all week.

## 82. The selling side (SELLSIDE.md)

SPY same-day credit spreads, both sides, every session since 2024-02 (1400 spreads): at the 10% a side the
bar was written at, -15.4 dollars a spread and 1 month of 34 above zero; at a cent a leg,
-2.3; at the trade price both ways, which nobody gets, +2.5 on about $438 at risk. No version (both
sides, only against the 10:00 move, only on flat days) is better. The bar is not met at any cost. My guess before
the run ("positive on average, with the worst two weeks taking most of it back") was wrong: there is nothing to
take back. SPY's same-day options are priced about right at 10:00; what the buyer and the seller both lose is
the cost of crossing the quote.

## 70. rating_open's own rule on upgrades it was not found on

260 of 278 upgrades on 105 large caps outside our 25 could be priced (nearest expiry, bought at 09:32).

| contract, exit | sold on day one | carried to expiry | carried, last 3 months |
|---|---|---|---|
| 0.45 delta, half out at 2x, trail from 1.5x (the rule) | -18% / -20% / -20% (260) | -17% / -19% / -20% (260) | -9% / -25% / -40% (16) |
| 0.45 delta, held | -18% / -21% / -22% (260) | -20% / -23% / -25% (260) | +6% / -17% / -42% (16) |
| 0.30 delta, the rule's exit | -18% / -19% / -20% (260) | -21% / -23% / -25% (260) | -25% / -48% / -57% (16) |
| the rule at 5% costs | -8% / -9% / -10% (260) | -6% / -7% / -9% (260) | +8% / -10% / -25% (16) |

By year, the rule carried: 2024 -32% / -36% / -40% (93), 2025 -27% / -32% / -37% (77), 2026 +6% / +2% / -2% (90).
Bar (written 2026-11-16): negative without the best two over two years retires it. **Retired.** It had been added
on ten of our own picks (+17%, -4% without the best two).

## 74. The 10:16 put mirror on option prices

Days since 2024-11 with the theme's ETF down over the last month and below its open at 10:15; a put on the theme's
weakest mega cap, nearest expiry, sold the same day at 15:45.

| what is bought | trades | win | 0.20 delta, held | last 3 months | 0.20 delta, live exit | 0.35 delta, held |
|---|---|---|---|---|---|---|
| chips, weakest name, 10:16 | 96 | 26% | +4% / -15% / -22% | -36% / -45% / -52% (23) | -1% / -12% / -14% | -10% / -15% / -19% |
| chips days, SMH itself | 96 | 23% | +9% / -7% / -19% | -6% / -19% / -29% (23) | -9% / -12% / -15% | -3% / -11% / -18% |
| the same mornings, QQQ same-day put | 173 | 17% | -10% / -21% / -28% | -12% / -60% / -76% (26) | -22% / -25% / -28% | -8% / -14% / -19% |
| software, weakest name, 10:16 | 103 | 28% | -16% / -21% / -25% | -20% / -36% / -48% (11) | -3% / -5% / -7% | -13% / -17% / -20% |
| chips, weakest name, 11:21 | 96 | 27% | -14% / -18% / -21% | -34% / -41% / -50% (19) | -18% / -20% / -23% | -14% / -17% / -19% |

Bar: the 10:16 entry positive without its best two over the last 3 months, and better than 11:21. Not met: nothing
in the table is positive without its best two, over two years or over three months, on the name, the ETF or the
index, at either strike or exit. On stock moves the pattern was there in falling months (+0.67%, 99 days); it does
not pay for an option. The mirror leaves the trial shelf and is no longer listed as an idea.

## 75. A call held across the night: first cut, last 3 months only

63 nights (2026-08-20 to 2026-11-17), SMH, NVDA, AMD, AVGO: the call nearest 0.50 delta on the nearest expiry at least
two days out, bought at 15:50 and sold at 09:35, against one bought at 10:00 and sold at 15:45.

| | stock, night | stock, 10:00-15:45 | night call, no cost | night call, 2% a side | night call, 10% | day call, no cost |
|---|---|---|---|---|---|---|
| SMH | -0.22% | -0.20% | -18% / -21% / -23% (49) | -21% / -24% / -26% (49) | -33% / -35% / -37% (49) | -6% / -10% / -12% (32) |
| NVDA | -0.11% | -0.56% | -2% / -8% / -11% (60) | -6% / -12% / -14% (60) | -20% / -25% / -27% (60) | -15% / -17% / -18% (60) |
| AMD | -0.05% | -0.16% | -5% / -11% / -15% (60) | -9% / -14% / -18% (60) | -23% / -27% / -30% (60) | -7% / -10% / -12% (55) |
| AVGO | +0.11% | -0.20% | +2% / -2% / -5% (59) | -2% / -5% / -9% (59) | -17% / -19% / -22% (59) | -10% / -11% / -13% (57) |
| all | -0.07% | -0.28% | -5% / -7% / -8% (228) | -9% / -11% / -12% (228) | -23% / -24% / -25% (228) | -10% / -11% / -11% (204) |

By the month SMH was in: rising, 28 nights, -16% / -19% / -21% (105) before costs; falling, 35 nights, +4% / +1% / -1% (123).
The night call beats its daytime twin and still loses before any cost over the last three months, so the two-year
run is not owed: a rule negative on its last three months is a reject. Half-way through the run (31 nights) the
same table read +7.8% a night before costs; the other 32 nights took it to -5%. The ten-year night effect on the
stock (OVERNIGHT_HOLD.md) stands as an observation about stocks, not something an option holds.

## 80. The day after an open-to-close of -2% or worse

Daily bars, the day after each name's own -2% day, closing above its open; IWM and DIA are the names not looked at
when the base rate was first read.

| | 2004-2016 | SPY month rising | SPY month falling | 2016-2026 | rising | falling |
|---|---|---|---|---|---|---|
| SPY | 61%, +0.36% (77) | 40%, -0.17% (10) | 64%, +0.44% (67) | 57%, +0.45% (51) | 17%, -0.81% (6) | 61%, +0.60% (44) |
| QQQ | 52%, +0.24% (109) | 38%, -0.32% (24) | 57%, +0.40% (84) | 60%, +0.41% (114) | 57%, -0.05% (35) | 60%, +0.60% (78) |
| IWM | 57%, +0.40% (182) | 54%, +0.07% (48) | 59%, +0.53% (133) | 63%, +0.34% (113) | 61%, +0.07% (33) | 63%, +0.43% (78) |
| DIA | 56%, +0.36% (55) | 38%, -0.70% (8) | 60%, +0.54% (47) | 65%, +0.63% (43) | 57%, -0.22% (7) | 66%, +0.79% (35) |
| IWM and DIA together | 57%, +0.39% (237) | 52%, -0.04% (56) | 59%, +0.54% (180) | 64%, +0.42% (156) | 60%, +0.02% (40) | 64%, +0.54% (113) |

Bar: at least 58% up and +0.25% on IWM and DIA together in both halves. The first half is 57%: **not met**, by a
point. The split written with the bar says where it lives: after a -2% day in a falling month both halves are 59%
and 64% up, +0.54% each; in a rising month there is nothing. It stays a base rate quoted in the morning file and
does not move `p_up` by itself (it was quoted on 11-20 and SPY fell 3.2% from its open). SUNDAY_TESTS 84 puts the
falling-month case on option prices with its bar.

## 81 and 83. Fills (FILLS.md)

51 real fills since 10-13: 43 inside the prints around them, 8 outside, all on thin single-stock contracts; one
(GEV, 10-30) was bought at 2.15 while the contract printed 0.07 to 0.72 and cost a third of all real losses. The
bot now refuses an ask more than double a recent print. Six shadow rows whose real order was cancelled unfilled
average +36% against -1% for the filled ones: they are flagged (journal/unfilled.csv) and left out of the
leaderboard and the promotion rule.

## S5. The open-drive ledgers and the week of monthly expiry

The stored open-drive trades (opengate.json: 0.35 delta, half at 3x, the rest held), split by expiry week:

| | expiry week | other weeks |
|---|---|---|
| SPY, NVDA and TSLA | -34% / -59% / -70% (30) | +8% / +4% / +0% (138) |
| SPY | -59% / -79% / -94% (11) | +26% / +14% / +5% (41) |
| NVDA and TSLA | -20% / -58% / -77% (19) | +0% / -5% / -11% (97) |
| 2024 | -94% / -98% / -99% (5) | -33% / -42% / -52% (29) |
| 2025 | -69% / -79% / -86% (13) | -10% / -20% / -28% (42) |
| 2026 | +28% / -31% / -59% (12) | +37% / +29% / +22% (67) |

The skip holds on real prices in each of the three years. The other weeks' last 3 months: -13% / -36% / -51% (23).

## What it adds up to

Five more ways of holding an option were put to real prices this week (selling the spread, buying the upgrade
near the money, the mirror put, the overnight call, and the same-day call it was compared with). None is above
zero without its best two trades; the two that looked good in a short record (rating_open on ten picks, the
overnight call on its first 31 nights) lost on the longer one. On SPY the option's price is fair and the cost is
the quote; on thin single-stock contracts the quote costs 3% to 20% a side and, once, far more. Nothing tested so
far beats holding the index.
