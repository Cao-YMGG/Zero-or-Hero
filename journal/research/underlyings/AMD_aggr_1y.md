# Backtest — AMD 0DTE, 2025-10-06 → 2026-10-02 (247 days)

Model: Black-Scholes at IV 56%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 49.0% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_d08_run | 18 | 67% | +211% | -100% | +107.1% | +750% | 26 | 766 | 97% | — / — / — | 2025-11-10 |
| rebound_d15_run | 18 | 61% | +169% | -100% | +64.2% | +526% | 49 | 733 | 93% | — / — / — | 2025-11-10 |
| rebound_d08_tp1 | 18 | 67% | +121% | -100% | +47.5% | +175% | 5 | 1,046 | 100% | 2025-11-05 / — / — | 2025-11-10 |
| rebound_d15_tp3 | 18 | 33% | +337% | -100% | +45.7% | +448% | 13 | 1,952 | 99% | 2025-11-05 / — / — | 2025-11-10 |
| rebound_d08_tp3 | 18 | 33% | +316% | -100% | +38.8% | +338% | 22 | 1,994 | 99% | 2025-11-05 / — / — | 2025-11-10 |
| rebound_d15_tp1 | 18 | 61% | +115% | -100% | +31.7% | +144% | 45 | 1,072 | 96% | 2025-11-05 / — / — | 2025-11-10 |
| gapw1_d08_run | 89 | 45% | +158% | -96% | +18.1% | +966% | 9 | 500 | 98% | — / — / — | 2025-10-14 |
| gapw1_d08_tp3 | 89 | 26% | +339% | -99% | +14.3% | +393% | 9 | 500 | 98% | — / — / — | 2025-10-14 |
| gapw_d08_run | 125 | 44% | +154% | -98% | +13.3% | +966% | 2 | 7,553 | 100% | 2025-10-08 / 2025-10-08 / 2025-10-15 | 2026-01-20 |
| gapw_d08_tp3 | 125 | 25% | +336% | -99% | +8.8% | +393% | 13,319 | 15,574 | 74% | 2025-10-08 / 2025-10-15 / 2025-10-15 | — |
| drive_d08_run | 123 | 38% | +176% | -100% | +5.4% | +1017% | 10,972 | 16,063 | 81% | 2025-10-06 / 2025-10-08 / 2025-10-10 | — |
| gapw1_d08_tp1 | 89 | 47% | +123% | -100% | +5.3% | +201% | 9 | 500 | 98% | — / — / — | 2025-10-14 |
| gapw_d08_tp1 | 125 | 46% | +124% | -100% | +2.1% | +201% | 24 | 1,005 | 98% | 2025-10-08 / — / — | 2025-10-14 |
| gapw_d15_run | 125 | 42% | +127% | -99% | -3.1% | +608% | 35 | 4,743 | 99% | 2025-10-08 / 2025-10-15 / — | 2026-01-05 |
| gapw1_d15_run | 89 | 43% | +122% | -98% | -4.0% | +608% | 1 | 500 | 100% | — / — / — | 2026-03-02 |
| gapw1_d15_tp1 | 89 | 44% | +118% | -100% | -4.5% | +160% | 1 | 500 | 100% | — / — / — | 2026-03-02 |
| gapw_d15_tp1 | 125 | 43% | +117% | -100% | -6.3% | +160% | 0 | 1,088 | 100% | 2025-10-08 / — / — | 2025-10-14 |
| gapw_d15_tp3 | 125 | 22% | +304% | -99% | -12.1% | +374% | 3 | 3,582 | 100% | 2025-10-08 / 2025-10-15 / — | 2025-11-13 |
| gapw1_d15_tp3 | 89 | 21% | +297% | -99% | -14.4% | +374% | 1 | 500 | 100% | — / — / — | 2026-03-02 |
| drive_d15_run | 123 | 35% | +142% | -99% | -14.6% | +683% | 47 | 4,980 | 99% | 2025-10-08 / 2025-10-10 / — | 2026-01-05 |
| drive_d08_tp1 | 123 | 38% | +114% | -100% | -18.1% | +176% | 1 | 5,565 | 100% | 2025-10-06 / 2025-10-27 / 2025-11-21 | 2026-04-16 |
| drive_d08_tp3 | 123 | 19% | +334% | -100% | -18.8% | +410% | 24 | 5,390 | 100% | 2025-10-06 / 2025-10-08 / 2025-11-14 | 2026-01-05 |
| drive1_d08_run | 103 | 32% | +148% | -100% | -20.7% | +969% | 23 | 500 | 95% | — / — / — | 2025-10-07 |
| drive_d15_tp1 | 123 | 36% | +116% | -100% | -22.7% | +227% | 43 | 4,520 | 99% | 2025-10-06 / 2025-10-08 / — | 2026-01-20 |
| drive_d15_tp3 | 123 | 17% | +318% | -98% | -27.2% | +364% | 17 | 8,023 | 100% | 2025-10-06 / 2025-10-08 / 2025-12-17 | 2026-03-03 |
| drive1_d15_run | 103 | 33% | +117% | -100% | -28.2% | +588% | 36 | 500 | 93% | — / — / — | 2025-10-07 |
| drive1_d15_tp1 | 103 | 33% | +115% | -100% | -29.0% | +169% | 36 | 500 | 93% | — / — / — | 2025-10-07 |
| drive1_d08_tp1 | 103 | 32% | +120% | -100% | -29.6% | +161% | 23 | 500 | 95% | — / — / — | 2025-10-07 |
| drive1_d08_tp3 | 103 | 14% | +343% | -100% | -39.4% | +425% | 23 | 500 | 95% | — / — / — | 2025-10-07 |
| drive1_d15_tp3 | 103 | 13% | +319% | -99% | -46.5% | +354% | 36 | 500 | 93% | — / — / — | 2025-10-07 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_d08_tp1 | 98.4% | 84.0% | 44.1% |
| rebound_d08_run | 98.4% | 85.8% | 41.5% |
| rebound_d15_run | 92.2% | 69.8% | 35.3% |
| rebound_d15_tp1 | 89.7% | 64.5% | 37.1% |
| rebound_d15_tp3 | 55.9% | 37.6% | 33.1% |
| rebound_d08_tp3 | 51.2% | 34.8% | 33.1% |
| gapw1_d08_run | 37.7% | 26.6% | 17.6% |
| gapw1_d08_tp1 | 30.5% | 24.3% | 22.5% |
| gapw_d08_run | 29.6% | 22.9% | 15.2% |
| gapw1_d08_tp3 | 28.3% | 20.4% | 25.6% |
| gapw_d08_tp1 | 23.3% | 20.6% | 19.5% |
| gapw_d08_tp3 | 22.4% | 16.9% | 22.6% |
| drive_d08_run | 19.7% | 17.3% | 11.7% |
| gapw1_d15_tp1 | 14.7% | 15.0% | 19.3% |
| gapw1_d15_tp3 | 10.3% | 10.1% | 18.7% |
| drive_d08_tp3 | 8.3% | 8.7% | 18.7% |
| gapw_d15_tp3 | 10.3% | 9.9% | 18.1% |
| gapw_d15_tp1 | 12.3% | 13.7% | 17.4% |
| drive_d15_tp3 | 5.2% | 6.5% | 17.2% |
| gapw1_d15_run | 15.2% | 15.2% | 14.2% |
| gapw_d15_run | 14.6% | 14.4% | 12.7% |
| drive_d08_tp1 | 4.0% | 7.5% | 14.3% |
| drive1_d08_tp3 | 3.2% | 4.1% | 14.0% |
| drive1_d15_tp3 | 1.8% | 3.0% | 13.2% |
| drive_d15_tp1 | 2.7% | 5.0% | 12.8% |
| drive1_d15_tp1 | 1.5% | 4.2% | 11.2% |
| drive1_d08_tp1 | 1.8% | 4.3% | 10.6% |
| drive_d15_run | 7.9% | 10.1% | 9.3% |
| drive1_d08_run | 6.4% | 7.8% | 8.6% |
| drive1_d15_run | 3.6% | 4.9% | 8.5% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_d08_run | 18 | +107.1% | 41.5% | 7 | +201.3% | 55.6% | holding up |
| rebound_d15_run | 18 | +64.2% | 35.3% | 7 | +139.0% | 54.3% | holding up |
| rebound_d08_tp1 | 18 | +47.5% | 44.1% | 7 | +64.2% | 50.6% | holding up |
| rebound_d15_tp1 | 18 | +31.7% | 37.1% | 7 | +50.6% | 50.6% | holding up |
| rebound_d15_tp3 | 18 | +45.7% | 33.1% | 7 | +95.9% | 42.9% | holding up |
| rebound_d08_tp3 | 18 | +38.8% | 33.1% | 7 | +80.3% | 42.9% | holding up |
| gapw1_d08_tp3 | 89 | +14.3% | 25.6% | 22 | +1.3% | 24.8% | holding up |
| gapw_d08_tp3 | 125 | +8.8% | 22.6% | 32 | +10.2% | 24.2% | holding up |
| gapw_d08_tp1 | 125 | +2.1% | 19.5% | 32 | +13.6% | 24.2% | holding up |
| gapw_d15_tp1 | 125 | -6.3% | 17.4% | 32 | +8.1% | 24.2% | holding up |
| drive_d08_tp3 | 123 | -18.8% | 18.7% | 30 | -3.1% | 23.7% | holding up |
| gapw_d08_run | 125 | +13.3% | 15.2% | 32 | +41.8% | 23.6% | holding up |
| drive_d08_run | 123 | +5.4% | 11.7% | 30 | +54.2% | 22.4% | holding up |
| gapw_d15_run | 125 | -3.1% | 12.7% | 32 | +23.3% | 21.8% | holding up |
| drive_d15_tp3 | 123 | -27.2% | 17.2% | 30 | -15.0% | 20.3% | holding up |
| drive_d15_run | 123 | -14.6% | 9.3% | 30 | +26.8% | 19.3% | holding up |
| drive_d08_tp1 | 123 | -18.1% | 14.3% | 30 | -8.5% | 19.3% | holding up |
| drive_d15_tp1 | 123 | -22.7% | 12.8% | 30 | -7.1% | 19.3% | holding up |
| gapw1_d08_run | 89 | +18.1% | 17.6% | 22 | +33.6% | 19.1% | holding up |
| gapw_d15_tp3 | 125 | -12.1% | 18.1% | 32 | -21.2% | 18.1% | holding up |
| gapw1_d15_run | 89 | -4.0% | 14.2% | 22 | +4.1% | 17.8% | holding up |
| gapw1_d08_tp1 | 89 | +5.3% | 22.5% | 22 | -5.8% | 17.6% | fading |
| gapw1_d15_tp1 | 89 | -4.5% | 19.3% | 22 | -9.6% | 17.6% | holding up |
| drive1_d08_tp3 | 103 | -39.4% | 14.0% | 26 | -32.6% | 15.8% | holding up |
| drive1_d15_tp3 | 103 | -46.5% | 13.2% | 26 | -34.9% | 15.8% | holding up |
| gapw1_d15_tp3 | 89 | -14.4% | 18.7% | 22 | -41.6% | 15.0% | holding up |
| drive1_d08_run | 103 | -20.7% | 8.6% | 26 | +2.2% | 13.4% | holding up |
| drive1_d08_tp1 | 103 | -29.6% | 10.6% | 26 | -23.0% | 12.4% | holding up |
| drive1_d15_run | 103 | -28.2% | 8.5% | 26 | -18.4% | 11.8% | holding up |
| drive1_d15_tp1 | 103 | -29.0% | 11.2% | 26 | -31.7% | 9.8% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_d08_run | 0 | +0.0% | 18 | +107.1% |
| rebound_d15_run | 0 | +0.0% | 18 | +64.2% |
| rebound_d08_tp1 | 0 | +0.0% | 18 | +47.5% |
| rebound_d15_tp3 | 0 | +0.0% | 18 | +45.7% |
| rebound_d08_tp3 | 0 | +0.0% | 18 | +38.8% |
| rebound_d15_tp1 | 0 | +0.0% | 18 | +31.7% |
| gapw1_d08_run | 14 | +13.2% | 75 | +19.0% |
| gapw1_d08_tp3 | 14 | +24.1% | 75 | +12.4% |
| gapw_d08_run | 21 | +7.6% | 104 | +14.5% |
| gapw_d08_tp3 | 21 | +25.3% | 104 | +5.4% |
| drive_d08_run | 0 | +0.0% | 123 | +5.4% |
| gapw1_d08_tp1 | 14 | +11.8% | 75 | +4.1% |
| gapw_d08_tp1 | 21 | +16.0% | 104 | -0.7% |
| gapw_d15_run | 21 | +14.8% | 104 | -6.7% |
| gapw1_d15_run | 14 | +5.3% | 75 | -5.7% |
| gapw1_d15_tp1 | 14 | +5.8% | 75 | -6.5% |
| gapw_d15_tp1 | 21 | +10.3% | 104 | -9.6% |
| gapw_d15_tp3 | 21 | +0.8% | 104 | -14.7% |
| gapw1_d15_tp3 | 14 | -7.7% | 75 | -15.7% |
| drive_d15_run | 0 | +0.0% | 123 | -14.6% |
| drive_d08_tp1 | 0 | +0.0% | 123 | -18.1% |
| drive_d08_tp3 | 0 | +0.0% | 123 | -18.8% |
| drive1_d08_run | 0 | +0.0% | 103 | -20.7% |
| drive_d15_tp1 | 0 | +0.0% | 123 | -22.7% |
| drive_d15_tp3 | 0 | +0.0% | 123 | -27.2% |
| drive1_d15_run | 0 | +0.0% | 103 | -28.2% |
| drive1_d15_tp1 | 0 | +0.0% | 103 | -29.0% |
| drive1_d08_tp1 | 0 | +0.0% | 103 | -29.6% |
| drive1_d08_tp3 | 0 | +0.0% | 103 | -39.4% |
| drive1_d15_tp3 | 0 | +0.0% | 103 | -46.5% |

Exit reasons:

- rebound_d08_run: {'trail': 12, 'time': 6}
- rebound_d15_run: {'trail': 11, 'time': 7}
- rebound_d08_tp1: {'take_profit': 12, 'time': 6}
- rebound_d15_tp3: {'take_profit': 6, 'time': 12}
- rebound_d08_tp3: {'take_profit': 6, 'time': 12}
- rebound_d15_tp1: {'take_profit': 11, 'time': 7}
- gapw1_d08_run: {'time': 47, 'trail': 42}
- gapw1_d08_tp3: {'time': 66, 'take_profit': 23}
- gapw_d08_run: {'trail': 57, 'time': 68}
- gapw_d08_tp3: {'take_profit': 31, 'time': 94}
- drive_d08_run: {'trail': 47, 'time': 76}
- gapw1_d08_tp1: {'time': 47, 'take_profit': 42}
- gapw_d08_tp1: {'take_profit': 57, 'time': 68}
- gapw_d15_run: {'trail': 54, 'time': 71}
- gapw1_d15_run: {'time': 50, 'trail': 39}
- gapw1_d15_tp1: {'time': 50, 'take_profit': 39}
- gapw_d15_tp1: {'take_profit': 54, 'time': 71}
- gapw_d15_tp3: {'take_profit': 24, 'time': 101}
- gapw1_d15_tp3: {'time': 73, 'take_profit': 16}
- drive_d15_run: {'trail': 44, 'time': 79}
- drive_d08_tp1: {'take_profit': 47, 'time': 76}
- drive_d08_tp3: {'take_profit': 23, 'time': 100}
- drive1_d08_run: {'time': 70, 'trail': 33}
- drive_d15_tp1: {'take_profit': 44, 'time': 79}
- drive_d15_tp3: {'take_profit': 21, 'time': 102}
- drive1_d15_run: {'time': 69, 'trail': 34}
- drive1_d15_tp1: {'time': 69, 'take_profit': 34}
- drive1_d08_tp1: {'time': 70, 'take_profit': 33}
- drive1_d08_tp3: {'time': 89, 'take_profit': 14}
- drive1_d15_tp3: {'time': 90, 'take_profit': 13}
