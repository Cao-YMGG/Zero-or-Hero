# The oversold-ETF rule and two other dip-buying rules, as trades and as an account (2026-11-19)

Owner, 2026-11-18: "we need methods that can really be used." Three textbook dip-buying rules, parameters as
published and not tuned, on 14 ETFs (SPY, QQQ, IWM, DIA, SMH, XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLU, IGV), adjusted
daily bars 2016-11 to 2026-11, signals from 2017, 0.05% a round trip. Scripts: scratchpad t78_swing.py,
t78b_port.py, t78c_trend.py (not in the repo; a Sunday item rebuilds them if the rule goes further).

## Per trade

| rule | trades | win | avg | w/o best 5 | falling month | rising month | last 12 months | last 3 months | worst |
|---|---|---|---|---|---|---|---|---|---|
| A. RSI(2) < 10 at the close, close above the 200-day average; out at the first close above the 5-day average (10 sessions at most) | 1,145 | 70% | +0.37% | +0.35% | +0.42% (511) | +0.33% (634) | +0.71% (142) | **-0.40% (39, 51% win)** | -11.4% |
| A0. the same without the 200-day condition | 1,637 | 70% | +0.38% | +0.36% | +0.40% | +0.37% | +0.70% | -0.24% (58) | -39.2% |
| B. daytime fall of 1% or more, hold the night | 4,760 | 51% | -0.01% | -0.02% | 0.00% | -0.03% | +0.16% | -0.07% | -17.6% |
| C. three lower closes, hold one day | 3,196 | 54% | +0.15% | +0.13% | +0.20% | +0.08% | +0.21% | -0.04% | -6.9% |

For scale: any day, close to next close, the 14 ETFs: +0.064%. Rule A holds 3.6 days a trade, so about +0.10% a day
held.

Rule A by year: 2017 +0.46%, 2018 **-0.89%**, 2019 +0.39%, 2020 -0.13%, 2021 +0.82%, 2022 -0.29%, 2023 +0.30%,
2024 +0.62%, 2025 +0.72%, 2026 +0.67%. By ETF (A0): SMH +0.99%, XLK +0.86%, QQQ +0.61%, XLF +0.53%, XLY +0.49%,
IGV +0.48%, SPY +0.39%; XLE -0.12%, XLU +0.05%.

The 1,145 trades are not 1,145 bets: the ETFs fall together. They sit on 547 entry days (up to ten entries on one
day); by entry day 69% positive, +0.29% (+0.25% without the best five). Last 3 months: 20 entry days, -0.64%
(SMH 10-08 -8.4%, IGV 10-29 -6.1%, XLK 10-30 -4.9%, XLF 09-16 -4.2%).

## As an account (2017-01 to 2026-11, cash earns nothing)

| what | a year | worst fall | days with money in | Sharpe |
|---|---|---|---|---|
| hold SPY | +14.4% | -33.8% | 100% | 0.84 |
| hold QQQ | +19.7% | -35.0% | 100% | 0.90 |
| hold SMH | +30.7% | -45.3% | 100% | 0.95 |
| SPY only while above its 200-day average | +10.7% | -20.7% | 84% | 0.90 |
| QQQ only while above its 200-day average | +15.7% | -22.9% | 83% | 0.94 |
| rule A, 14 ETFs, five equal slots, bought at the close | +5.3% | -17.1% | 49% | 0.66 |
| the same bought at the next open | +3.9% | -14.5% | 42% | 0.51 |
| rule A, SPY QQQ SMH XLK, two slots, at the close | +7.5% | -14.4% | 20% | 0.86 |
| the same at the next open | +3.5% | -15.9% | 16% | 0.44 |
| rule A, SPY only, at the close | +4.0% | -15.0% | 12% | 0.65 |
| the same at the next open | +2.5% | -13.5% | 9% | 0.44 |
| rule A, 14 ETFs, five slots, with a 3% / 5% stop | +4.8% / +4.1% | -17.1% / -19.7% | 48% | 0.60 / 0.52 |

Rule A, 14 ETFs, five slots, by year: 2017 +6%, 2018 -9%, 2019 +5%, 2020 -2%, 2021 +12%, 2022 -2%, 2023 +7%,
2024 +11%, 2025 +11%, 2026 +17%. SPY held: +21%, -5%, +31%, +18%, +29%, -18%, +26%, +25%, +18%, +8%.

## What it says

1. Rule A is real per trade: positive in rising and in falling months, in eight of ten years, not carried by a few
   trades. It is the first thing tested here that clears the two-sided bar on ten years.
2. It is not a way to make more than holding. Run as an account it makes 4-7% a year against 14% for SPY held,
   because the money is out of the market most days. What it buys is a smaller worst fall (-15% against -34%).
3. Half of it is gone by the next morning: bought at the next open instead of the signal's close, +0.24% a trade
   and 2.5-4% a year. The bounce starts overnight, which fits OVERNIGHT_HOLD.md. A person has to place the order
   in the last ten minutes of the day the signal appears.
4. The last three months are negative, and 2018, 2020 and 2022 lost: it loses exactly when a fall keeps going, and a
   stop makes it worse, not better.
5. Rule B (hold the night after a red day) is nothing, as in DIPBUY.md (Sunday test 47: the 16 days SPY fell 1.5% or
   more, bought at the close, -0.08% to the next open); rule C is small and lives in tech ETFs.
6. Every "method" from here on is measured as an account against SPY held over the same years, not only per trade.
   Per-trade averages made rule A look better than it is.

Shelf: observation with a test owed (SUNDAY_TESTS 77). Not executed; nothing in config changes.
