# Backtest — AMD 0DTE, 2026-08-04 → 2026-10-02 (42 days)

Model: Black-Scholes at IV 47%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 41.0% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gapw_d08_run | 19 | 53% | +193% | -91% | +58.7% | +688% | 43 | 500 | 91% | — / — / — | 2026-08-11 |
| gapw1_d08_run | 11 | 45% | +227% | -86% | +56.4% | +688% | 43 | 500 | 91% | — / — / — | 2026-08-11 |
| gapw_d08_tp3 | 19 | 32% | +336% | -100% | +37.6% | +366% | 1 | 500 | 100% | — / — / — | 2026-08-11 |
| gapw_d15_run | 19 | 47% | +189% | -100% | +37.0% | +449% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| gapw_d08_tp1 | 19 | 58% | +120% | -100% | +27.5% | +154% | 46 | 500 | 91% | — / — / — | 2026-08-13 |
| gapw1_d08_tp1 | 11 | 55% | +119% | -100% | +19.6% | +132% | 46 | 500 | 91% | — / — / — | 2026-08-13 |
| gapw1_d08_tp3 | 11 | 27% | +329% | -100% | +17.0% | +351% | 1 | 500 | 100% | — / — / — | 2026-08-11 |
| rebound_d15_tp1 | 2 | 50% | +128% | -100% | +13.9% | +128% | 40 | 1,121 | 96% | 2026-08-05 / — / — | 2026-09-15 |
| rebound_d08_tp1 | 2 | 50% | +121% | -100% | +10.4% | +121% | 33 | 1,082 | 97% | 2026-08-05 / — / — | 2026-09-15 |
| gapw1_d15_run | 11 | 36% | +193% | -100% | +6.6% | +449% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| drive_d08_tp1 | 18 | 44% | +130% | -100% | +2.3% | +167% | 36 | 1,215 | 97% | 2026-08-05 / — / — | 2026-08-11 |
| drive_d08_tp3 | 18 | 22% | +354% | -100% | +1.0% | +407% | 7 | 500 | 99% | — / — / — | 2026-08-06 |
| gapw_d15_tp1 | 19 | 47% | +111% | -100% | -0.2% | +130% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| drive_d08_run | 18 | 44% | +123% | -100% | -1.1% | +436% | 32 | 762 | 96% | — / — / — | 2026-08-11 |
| gapw_d15_tp3 | 19 | 21% | +344% | -100% | -6.4% | +382% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| drive_d15_tp1 | 18 | 39% | +118% | -100% | -15.3% | +136% | 71 | 1,030 | 93% | 2026-08-05 / — / — | — |
| drive_d15_run | 18 | 39% | +104% | -100% | -20.5% | +293% | 106 | 706 | 85% | — / — / — | — |
| gapw1_d15_tp3 | 11 | 18% | +334% | -100% | -21.1% | +366% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| gapw1_d15_tp1 | 11 | 36% | +104% | -100% | -25.7% | +108% | 29 | 500 | 94% | — / — / — | 2026-08-06 |
| rebound_d08_run | 2 | 50% | +36% | -100% | -31.9% | +36% | 45 | 674 | 93% | — / — / — | 2026-09-15 |
| rebound_d15_run | 2 | 50% | +32% | -100% | -34.1% | +32% | 54 | 654 | 92% | — / — / — | — |
| drive1_d08_tp3 | 14 | 14% | +340% | -100% | -37.1% | +357% | 40 | 500 | 92% | — / — / — | 2026-08-06 |
| drive_d15_tp3 | 18 | 11% | +320% | -97% | -51.0% | +334% | 66 | 500 | 87% | — / — / — | — |
| drive1_d08_tp1 | 14 | 21% | +127% | -100% | -51.3% | +153% | 40 | 500 | 92% | — / — / — | 2026-08-06 |
| drive1_d15_tp1 | 14 | 21% | +114% | -100% | -54.1% | +126% | 26 | 500 | 95% | — / — / — | 2026-08-06 |
| drive1_d15_run | 14 | 21% | +96% | -100% | -58.0% | +146% | 26 | 500 | 95% | — / — / — | 2026-08-06 |
| drive1_d08_run | 14 | 21% | +95% | -100% | -58.2% | +200% | 40 | 500 | 92% | — / — / — | 2026-08-06 |
| drive1_d15_tp3 | 14 | 7% | +316% | -100% | -69.8% | +316% | 26 | 500 | 95% | — / — / — | 2026-08-06 |
| rebound_d15_tp3 | 2 | 0% | +0% | -100% | -100.0% | -100% | 14 | 500 | 97% | — / — / — | 2026-08-06 |
| rebound_d08_tp3 | 2 | 0% | +0% | -100% | -100.0% | -100% | 18 | 500 | 96% | — / — / — | 2026-08-06 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gapw_d08_tp1 | 82.7% | 55.6% | 33.0% |
| gapw_d08_run | 82.6% | 57.3% | 27.6% |
| gapw1_d08_run | 73.2% | 50.1% | 23.4% |
| gapw1_d08_tp1 | 64.7% | 43.8% | 28.6% |
| gapw_d15_run | 63.0% | 41.1% | 25.4% |
| gapw_d08_tp3 | 50.3% | 32.4% | 31.0% |
| rebound_d15_tp1 | 48.8% | 34.2% | 26.1% |
| rebound_d08_tp1 | 42.0% | 32.6% | 26.1% |
| gapw1_d08_tp3 | 29.9% | 21.3% | 26.5% |
| drive_d08_tp1 | 23.9% | 21.7% | 20.1% |
| gapw1_d15_run | 22.7% | 17.8% | 15.6% |
| drive_d08_tp3 | 18.2% | 16.0% | 22.4% |
| gapw_d15_tp1 | 19.3% | 18.3% | 21.5% |
| gapw_d15_tp3 | 14.3% | 12.4% | 21.1% |
| gapw1_d15_tp3 | 7.1% | 7.8% | 17.7% |
| drive_d08_run | 16.9% | 16.5% | 15.8% |
| drive_d15_tp1 | 5.8% | 9.0% | 15.2% |
| drive1_d08_tp3 | 4.2% | 4.3% | 14.1% |
| gapw1_d15_tp1 | 1.8% | 3.9% | 13.2% |
| drive_d15_tp3 | 1.0% | 2.6% | 11.5% |
| drive_d15_run | 3.6% | 6.5% | 8.8% |
| drive1_d15_tp3 | 0.2% | 0.9% | 6.9% |
| drive1_d08_tp1 | 0.1% | 1.1% | 4.7% |
| drive1_d15_tp1 | 0.1% | 0.5% | 4.7% |
| rebound_d08_run | 0.0% | 0.4% | 3.2% |
| drive1_d08_run | 0.1% | 0.3% | 2.6% |
| drive1_d15_run | 0.1% | 0.6% | 2.3% |
| rebound_d15_run | 0.0% | 0.1% | 1.7% |
| rebound_d15_tp3 | 0.0% | 0.0% | 0.0% |
| rebound_d08_tp3 | 0.0% | 0.0% | 0.0% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| gapw_d08_tp1 | 19 | +27.5% | 33.0% | 19 | +27.5% | 33.0% | holding up |
| gapw_d08_tp3 | 19 | +37.6% | 31.0% | 19 | +37.6% | 31.0% | holding up |
| gapw1_d08_tp1 | 11 | +19.6% | 28.6% | 11 | +19.6% | 28.6% | holding up |
| gapw_d08_run | 19 | +58.7% | 27.6% | 19 | +58.7% | 27.6% | holding up |
| gapw1_d08_tp3 | 11 | +17.0% | 26.5% | 11 | +17.0% | 26.5% | holding up |
| rebound_d15_tp1 | 2 | +13.9% | 26.1% | 2 | +13.9% | 26.1% | holding up |
| rebound_d08_tp1 | 2 | +10.4% | 26.1% | 2 | +10.4% | 26.1% | holding up |
| gapw_d15_run | 19 | +37.0% | 25.4% | 19 | +37.0% | 25.4% | holding up |
| gapw1_d08_run | 11 | +56.4% | 23.4% | 11 | +56.4% | 23.4% | holding up |
| drive_d08_tp3 | 18 | +1.0% | 22.4% | 18 | +1.0% | 22.4% | holding up |
| gapw_d15_tp1 | 19 | -0.2% | 21.5% | 19 | -0.2% | 21.5% | holding up |
| gapw_d15_tp3 | 19 | -6.4% | 21.1% | 19 | -6.4% | 21.1% | holding up |
| drive_d08_tp1 | 18 | +2.3% | 20.1% | 18 | +2.3% | 20.1% | holding up |
| gapw1_d15_tp3 | 11 | -21.1% | 17.7% | 11 | -21.1% | 17.7% | holding up |
| drive_d08_run | 18 | -1.1% | 15.8% | 18 | -1.1% | 15.8% | holding up |
| gapw1_d15_run | 11 | +6.6% | 15.6% | 11 | +6.6% | 15.6% | holding up |
| drive_d15_tp1 | 18 | -15.3% | 15.2% | 18 | -15.3% | 15.2% | holding up |
| drive1_d08_tp3 | 14 | -37.1% | 14.1% | 14 | -37.1% | 14.1% | holding up |
| gapw1_d15_tp1 | 11 | -25.7% | 13.2% | 11 | -25.7% | 13.2% | holding up |
| drive_d15_tp3 | 18 | -51.0% | 11.5% | 18 | -51.0% | 11.5% | holding up |
| drive_d15_run | 18 | -20.5% | 8.8% | 18 | -20.5% | 8.8% | holding up |
| drive1_d15_tp3 | 14 | -69.8% | 6.9% | 14 | -69.8% | 6.9% | holding up |
| drive1_d08_tp1 | 14 | -51.3% | 4.7% | 14 | -51.3% | 4.7% | holding up |
| drive1_d15_tp1 | 14 | -54.1% | 4.7% | 14 | -54.1% | 4.7% | holding up |
| rebound_d08_run | 2 | -31.9% | 3.2% | 2 | -31.9% | 3.2% | holding up |
| drive1_d08_run | 14 | -58.2% | 2.6% | 14 | -58.2% | 2.6% | holding up |
| drive1_d15_run | 14 | -58.0% | 2.3% | 14 | -58.0% | 2.3% | holding up |
| rebound_d15_run | 2 | -34.1% | 1.7% | 2 | -34.1% | 1.7% | holding up |
| rebound_d15_tp3 | 2 | -100.0% | 0.0% | 2 | -100.0% | 0.0% | holding up |
| rebound_d08_tp3 | 2 | -100.0% | 0.0% | 2 | -100.0% | 0.0% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gapw_d08_run | 6 | +6.5% | 13 | +82.9% |
| gapw1_d08_run | 5 | +0.4% | 6 | +103.1% |
| gapw_d08_tp3 | 6 | -31.3% | 13 | +69.4% |
| gapw_d15_run | 6 | -17.2% | 13 | +62.0% |
| gapw_d08_tp1 | 6 | +49.6% | 13 | +17.3% |
| gapw1_d08_tp1 | 5 | +32.0% | 6 | +9.3% |
| gapw1_d08_tp3 | 5 | -17.5% | 6 | +45.7% |
| rebound_d15_tp1 | 0 | +0.0% | 2 | +13.9% |
| rebound_d08_tp1 | 0 | +0.0% | 2 | +10.4% |
| gapw1_d15_run | 5 | -28.2% | 6 | +35.6% |
| drive_d08_tp1 | 0 | +0.0% | 18 | +2.3% |
| drive_d08_tp3 | 0 | +0.0% | 18 | +1.0% |
| gapw_d15_tp1 | 6 | +4.7% | 13 | -2.5% |
| drive_d08_run | 0 | +0.0% | 18 | -1.1% |
| gapw_d15_tp3 | 6 | -99.8% | 13 | +36.7% |
| drive_d15_tp1 | 0 | +0.0% | 18 | -15.3% |
| drive_d15_run | 0 | +0.0% | 18 | -20.5% |
| gapw1_d15_tp3 | 5 | -99.9% | 6 | +44.5% |
| gapw1_d15_tp1 | 5 | -18.2% | 6 | -31.9% |
| rebound_d08_run | 0 | +0.0% | 2 | -31.9% |
| rebound_d15_run | 0 | +0.0% | 2 | -34.1% |
| drive1_d08_tp3 | 0 | +0.0% | 14 | -37.1% |
| drive_d15_tp3 | 0 | +0.0% | 18 | -51.0% |
| drive1_d08_tp1 | 0 | +0.0% | 14 | -51.3% |
| drive1_d15_tp1 | 0 | +0.0% | 14 | -54.1% |
| drive1_d15_run | 0 | +0.0% | 14 | -58.0% |
| drive1_d08_run | 0 | +0.0% | 14 | -58.2% |
| drive1_d15_tp3 | 0 | +0.0% | 14 | -69.8% |
| rebound_d15_tp3 | 0 | +0.0% | 2 | -100.0% |
| rebound_d08_tp3 | 0 | +0.0% | 2 | -100.0% |

Exit reasons:

- gapw_d08_run: {'time': 8, 'trail': 11}
- gapw1_d08_run: {'time': 5, 'trail': 6}
- gapw_d08_tp3: {'time': 13, 'take_profit': 6}
- gapw_d15_run: {'time': 10, 'trail': 9}
- gapw_d08_tp1: {'time': 8, 'take_profit': 11}
- gapw1_d08_tp1: {'time': 5, 'take_profit': 6}
- gapw1_d08_tp3: {'time': 8, 'take_profit': 3}
- rebound_d15_tp1: {'take_profit': 1, 'time': 1}
- rebound_d08_tp1: {'take_profit': 1, 'time': 1}
- gapw1_d15_run: {'time': 7, 'trail': 4}
- drive_d08_tp1: {'take_profit': 8, 'time': 10}
- drive_d08_tp3: {'time': 14, 'take_profit': 4}
- gapw_d15_tp1: {'time': 10, 'take_profit': 9}
- drive_d08_run: {'trail': 8, 'time': 10}
- gapw_d15_tp3: {'time': 15, 'take_profit': 4}
- drive_d15_tp1: {'take_profit': 7, 'time': 11}
- drive_d15_run: {'trail': 7, 'time': 11}
- gapw1_d15_tp3: {'time': 9, 'take_profit': 2}
- gapw1_d15_tp1: {'time': 7, 'take_profit': 4}
- rebound_d08_run: {'trail': 1, 'time': 1}
- rebound_d15_run: {'trail': 1, 'time': 1}
- drive1_d08_tp3: {'time': 12, 'take_profit': 2}
- drive_d15_tp3: {'time': 16, 'take_profit': 2}
- drive1_d08_tp1: {'time': 11, 'take_profit': 3}
- drive1_d15_tp1: {'time': 11, 'take_profit': 3}
- drive1_d15_run: {'time': 11, 'trail': 3}
- drive1_d08_run: {'time': 11, 'trail': 3}
- drive1_d15_tp3: {'time': 13, 'take_profit': 1}
- rebound_d15_tp3: {'time': 2}
- rebound_d08_tp3: {'time': 2}
