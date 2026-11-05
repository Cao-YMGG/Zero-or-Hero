# The lock gate: was 2026-11-05 knowable at 10:00?

Gate (registered before the replay, SUNDAY_TESTS 45): at 10:00 ET SPY >= 0.1% below its open, VIXY >= 3% above its own open, and >= 8 of 10 mega caps (AAPL MSFT NVDA AMZN META GOOGL TSLA AVGO AMD MU) below their opens. 30-minute bars (Alpaca SIP) from 2024-02; the 09:30 bar's close is the 10:00 price. Data through 2026-11-05. 694 sessions, 11 lock days.

## Index from 10:00 to the close, by day class

| class | period | days | SPY closed below 10:00 | SPY 10:00->close avg | median | QQQ avg | SMH avg | SMH down% | macro days |
|---|---|---|---|---|---|---|---|---|---|
| lock | since 2024-02 | 11 | 36% | +0.1% | +0.3% | +0.3% | +0.3% | 36% | 0 |
| lock | last year | 3 | 33% | -0.7% | +0.3% | -0.3% | -0.3% | 33% | 0 |
| lock | last 3 months | 1 | 100% | -2.8% | -2.8% | -2.9% | -5.2% | 100% | 0 |
| vix_only | since 2024-02 | 1 | 0% | +0.8% | +0.8% | +1.1% | +1.5% | 0% | 0 |
| breadth_only | since 2024-02 | 92 | 62% | -0.1% | -0.1% | -0.2% | -0.2% | 57% | 6 |
| breadth_only | last year | 36 | 61% | -0.2% | -0.2% | -0.3% | -0.4% | 64% | 6 |
| breadth_only | last 3 months | 6 | 100% | -0.4% | -0.4% | -0.6% | -0.8% | 100% | 2 |
| below_open | since 2024-02 | 112 | 38% | +0.1% | +0.1% | +0.1% | +0.2% | 35% | 5 |
| below_open | last year | 39 | 41% | +0.1% | +0.1% | +0.2% | +0.4% | 38% | 5 |
| below_open | last 3 months | 13 | 15% | +0.2% | +0.2% | +0.4% | +0.7% | 23% | 1 |
| above_open | since 2024-02 | 478 | 46% | +0.0% | +0.1% | +0.0% | -0.0% | 44% | 21 |
| above_open | last year | 174 | 47% | -0.0% | +0.0% | -0.0% | -0.0% | 49% | 19 |
| above_open | last 3 months | 45 | 62% | -0.1% | -0.1% | -0.1% | -0.2% | 64% | 5 |

## One flag at a time (days with SPY below its open at 10:00)

| flag (SPY below open and ...) | period | days | SPY closed below 10:00 | SPY 10:00->close avg | SMH avg |
|---|---|---|---|---|---|
| VIXY >= +3% | since 2024-02 | 12 | 33% | +0.2% | +0.4% |
| VIXY >= +3% | last year | 3 | 33% | -0.7% | -0.3% |
| VIXY >= +3% | last 3 months | 1 | 100% | -2.8% | -5.2% |
| VIXY >= +5% | since 2024-02 | 1 | 100% | -2.8% | -5.2% |
| VIXY >= +5% | last year | 1 | 100% | -2.8% | -5.2% |
| VIXY >= +5% | last 3 months | 1 | 100% | -2.8% | -5.2% |
| breadth >= 8/10 | since 2024-02 | 103 | 59% | -0.1% | -0.1% |
| breadth >= 8/10 | last year | 39 | 59% | -0.2% | -0.4% |
| breadth >= 8/10 | last 3 months | 7 | 100% | -0.7% | -1.4% |
| breadth 10/10 | since 2024-02 | 16 | 62% | -0.2% | -0.2% |
| breadth 10/10 | last year | 7 | 57% | -0.4% | -0.6% |
| breadth 10/10 | last 3 months | 2 | 100% | -1.9% | -3.4% |
| VIXY < 0 (fading) | since 2024-02 | 31 | 35% | +0.0% | +0.0% |
| VIXY < 0 (fading) | last year | 11 | 45% | +0.1% | -0.0% |
| VIXY < 0 (fading) | last 3 months | 7 | 43% | +0.0% | -0.1% |
| SPY <= -1% at 10:00 | since 2024-02 | 3 | 33% | -0.0% | +0.6% |
| SPY <= -1% at 10:00 | last year | 2 | 50% | -1.2% | -0.8% |
| SPY <= -1% at 10:00 | last 3 months | 1 | 100% | -2.8% | -5.2% |
| lock and SPY <= -1% | since 2024-02 | 3 | 33% | -0.0% | +0.6% |
| lock and SPY <= -1% | last year | 2 | 50% | -1.2% | -0.8% |
| lock and SPY <= -1% | last 3 months | 1 | 100% | -2.8% | -5.2% |
| lock, not a macro day | since 2024-02 | 11 | 36% | +0.1% | +0.3% |
| lock, not a macro day | last year | 3 | 33% | -0.7% | -0.3% |
| lock, not a macro day | last 3 months | 1 | 100% | -2.8% | -5.2% |

## Real 0DTE puts bought at 10:00 (OPENDRIVE rows, 0.7% OTM; data through 2026-10-15)

take3 = sell at 3x else 15:30; hold = 15:30; trail = OPENDRIVE's trail. 'w/o best' drops the best trade.

| class | underlying | period | trades | win% (take3) | take3 avg | w/o best | w/o best 2 | hold avg | trail avg | median hold |
|---|---|---|---|---|---|---|---|---|---|---|
| lock | SPY | since 2024-02 | 10 | 20% | -57.7% | -86.5% | -97.9% | -87.5% | -49.0% | -98.8% |
| lock | QQQ | since 2024-02 | 10 | 10% | -82.6% | -95.4% | -98.2% | -82.6% | -22.5% | -98.7% |
| breadth_only | SPY | since 2024-02 | 91 | 22% | -25.6% | -28.9% | -32.1% | -29.2% | -28.5% | -95.6% |
| breadth_only | SPY | last year | 35 | 23% | -24.4% | -33.1% | -41.6% | +8.0% | -15.6% | -95.8% |
| breadth_only | SPY | last 3 months | 5 | 20% | -23.2% | -91.0% | -96.3% | -56.0% | -12.6% | -88.9% |
| breadth_only | QQQ | since 2024-02 | 90 | 22% | -29.7% | -32.7% | -35.7% | -37.4% | -34.7% | -95.3% |
| breadth_only | QQQ | last year | 34 | 24% | -22.0% | -29.6% | -37.5% | -16.8% | -27.0% | -88.0% |
| breadth_only | QQQ | last 3 months | 4 | 25% | -11.8% | -92.0% | -97.9% | -0.5% | -37.5% | -88.9% |
| breadth_only | NVDA+TSLA | since 2024-02 | 47 | 34% | +4.0% | -1.1% | -6.1% | +23.1% | +14.1% | -68.3% |
| breadth_only | NVDA+TSLA | last year | 27 | 41% | +20.4% | +12.6% | +4.4% | +46.8% | +34.0% | -40.8% |
| breadth_only | NVDA+TSLA | last 3 months | 4 | 25% | -18.7% | -98.7% | -99.7% | -26.7% | -21.2% | -98.0% |
| below_open | SPY | since 2024-02 | 110 | 18% | -33.6% | -38.9% | -41.7% | +13.5% | -24.0% | -98.3% |
| below_open | SPY | last year | 37 | 14% | -51.6% | -59.8% | -68.0% | -76.7% | -47.1% | -98.0% |
| below_open | SPY | last 3 months | 11 | 9% | -71.6% | -98.8% | -99.4% | -95.9% | -80.7% | -100.0% |
| below_open | QQQ | since 2024-02 | 82 | 22% | -26.6% | -30.0% | -33.3% | +11.4% | +3.6% | -96.4% |
| below_open | QQQ | last year | 29 | 17% | -34.2% | -44.0% | -53.5% | -72.9% | -31.4% | -96.4% |
| below_open | QQQ | last 3 months | 7 | 14% | -54.7% | -99.3% | -99.8% | -98.2% | -48.9% | -100.0% |
| below_open | NVDA+TSLA | since 2024-02 | 35 | 23% | -25.9% | -34.8% | -43.0% | -36.6% | -31.1% | -96.7% |
| below_open | NVDA+TSLA | last year | 22 | 14% | -47.8% | -63.3% | -76.8% | -60.4% | -46.4% | -95.9% |
| below_open | NVDA+TSLA | last 3 months | 6 | 17% | -12.7% | -70.5% | -78.3% | -56.3% | -2.3% | -57.5% |

## Lock days, most recent first

| day | macro | SPY 10:00 | VIXY 10:00 | breadth | SPY 10:00->close | SPY 11:00->close | QQQ | SMH |
|---|---|---|---|---|---|---|---|---|
| 2026-11-05 |  | -1.5% | +9.3% | 10/10 | -2.8% | -1.2% | -2.9% | -5.2% |
| 2026-06-25 |  | -1.2% | +3.7% | 9/10 | +0.5% | -0.3% | +1.5% | +3.6% |
| 2026-01-29 |  | -0.7% | +4.1% | 10/10 | +0.3% | +1.2% | +0.5% | +0.6% |
| 2025-04-30 |  | -1.0% | +4.3% | 8/10 | +2.3% | +1.3% | +2.7% | +3.4% |
| 2025-04-14 |  | -0.7% | +3.2% | 9/10 | -0.3% | -0.6% | -0.6% | -0.6% |
| 2025-03-18 |  | -0.7% | +3.4% | 9/10 | +0.0% | +0.0% | +0.1% | +0.4% |
| 2025-02-27 |  | -0.7% | +3.4% | 9/10 | -1.2% | -1.4% | -1.9% | -3.9% |
| 2024-11-21 |  | -0.6% | +3.2% | 9/10 | +0.6% | +0.3% | +0.7% | +1.2% |
| 2024-11-20 |  | -0.5% | +3.4% | 10/10 | +0.5% | +0.5% | +0.7% | +0.8% |
| 2024-10-01 |  | -0.7% | +4.8% | 9/10 | -0.2% | +0.1% | -0.3% | -1.3% |
| 2024-09-11 |  | -0.7% | +3.1% | 9/10 | +1.8% | +2.4% | +2.5% | +4.6% |

## The last sessions, classed

| day | class | SPY 10:00 | VIXY 10:00 | breadth | SPY 10:00->close | SMH |
|---|---|---|---|---|---|---|
| 2026-10-28 | below_open | -0.1% | -0.9% | 7/10 | +0.2% | +0.5% |
| 2026-10-29 | above_open | -0.0% | -0.3% | 7/10 | +0.1% | +0.5% |
| 2026-10-30 | above_open | -0.0% | +0.2% | 4/10 | -0.7% | -2.0% |
| 2026-11-02 | above_open | +0.1% | -1.3% | 4/10 | -1.1% | -3.3% |
| 2026-11-03 | above_open | +0.1% | -0.7% | 4/10 | +0.1% | -0.2% |
| 2026-11-04 | above_open | +0.6% | -2.4% | 1/10 | -0.1% | -2.3% |
| 2026-11-05 | lock | -1.5% | +9.3% | 10/10 | -2.8% | -5.2% |
