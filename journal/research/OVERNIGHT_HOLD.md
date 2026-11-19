# Where the return is: overnight against daytime (2026-11-18, owner: "we need methods that can really be used")

Daily bars, split- and dividend-adjusted, 2016-02 to 2026-11-18 (2,714 sessions). Overnight = yesterday's close to
today's open; daytime = open to close. Cost charged on the overnight leg: 0.02% a night (about a cent each way on a
liquid ETF). Annualised.

| | overnight | overnight after cost | daytime | buy and hold | overnight max drawdown |
|---|---|---|---|---|---|
| SPY | +9.5% | +4.1% | +5.0% | +15.0% | -33% |
| QQQ | +12.2% | +6.7% | +6.8% | +19.8% | -31% |
| IWM | +15.5% | +9.8% | -3.8% | +11.0% | -32% |
| SMH | +29.3% | +22.9% | +2.5% | +32.5% | -38% |
| XLE | +15.1% | +9.4% | -3.0% | +11.6% | -42% |
| XLF | +6.8% | +1.5% | +4.8% | +11.9% | -49% |
| XLV | +4.1% | -1.0% | +7.2% | +11.6% | -39% |
| XLP | +2.9% | -2.2% | +5.4% | +8.5% | -32% |
| NVDA | +50.2% | +42.9% | +9.8% | +65.0% | -59% |
| AMD | +53.2% | +45.7% | +9.3% | +67.4% | -42% |
| AVGO | +39.5% | +32.7% | -0.3% | +39.1% | -35% |
| AMZN | +28.3% | +22.0% | -3.4% | +23.9% | -39% |
| TSLA | +31.7% | +25.2% | +5.1% | +38.4% | -49% |
| AAPL | +1.3% | -3.6% | +27.9% | +29.6% | -65% |
| WMT | +3.1% | -2.0% | +16.2% | +19.7% | -40% |

By year, overnight after cost / daytime: SPY 2022 -18 / -6, 2024 +18 / +1, 2026 +6 / -2; SMH 2021 +42 / -5, 2022
-30 / -10, 2023 +9 / +51, 2024 +82 / -27, 2025 +27 / +11, 2026 +35 / -10. Overnight in falling months (the ETF's
one-month return negative), after cost, per night: SPY +0.002%, QQQ +0.010%, SMH +0.051%, NVDA +0.080%, AMD +0.165%,
AVGO +0.168%. Last 63 sessions: SMH -0.118% a night, QQQ -0.051%, SPY +0.016%. A 20-day-average switch does nothing for
SPY or QQQ (+0.019% above, +0.018% below).

## What it says
- For the chip and high-beta names this project trades (SMH, NVDA, AMD, AVGO, AMZN, TSLA), nearly all of ten years'
  return came overnight and the daytime leg was flat or negative. Every rule here buys after the open and sells before
  the close: the half of the day with no drift, on the names where that is most true. It is not universal: AAPL, WMT,
  COST, health care and staples made their return in the daytime.
- It is not a method by itself. Overnight-only does not beat holding the index (SPY +4.1% after cost against +15.0%),
  it loses in a bear year like any long position (2022: SPY -18%, SMH -30%), and its last three months on chips are
  negative. What it changes is where to look: holds across the night, not same-day options.
- To test (SUNDAY_TESTS 75): a call bought near the close and sold after the next open on SMH, NVDA, AMD, AVGO, on
  real option prices, against the same call held from 10:00 to 15:45.
