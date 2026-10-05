# Backtest — NVDA 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 39%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 33.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_trail_1_40 | 23 | 43% | +729% | -100% | +260.4% | +6296% | 44 | 500 | 91% | — / — / — | 2025-04-07 |
| rebound_hold | 23 | 9% | +3912% | -100% | +249.1% | +7440% | 43 | 500 | 91% | — / — / — | 2025-02-04 |
| rebound_trail_2_50 | 23 | 26% | +982% | -100% | +182.3% | +4959% | 46 | 500 | 91% | — / — / — | 2025-03-11 |
| rebound_trail_1_65 | 23 | 22% | +812% | -74% | +118.6% | +3614% | 50 | 500 | 90% | — / — / — | 2025-04-03 |
| rebound_trail_3_60 | 23 | 22% | +885% | -100% | +114.1% | +3614% | 33 | 500 | 93% | — / — / — | 2025-03-11 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_trail_1_40 | 55.3% | 36.4% | 15.5% |
| rebound_trail_2_50 | 39.2% | 25.3% | 11.8% |
| rebound_trail_1_65 | 38.1% | 25.7% | 9.1% |
| rebound_trail_3_60 | 32.1% | 21.6% | 10.8% |
| rebound_hold | 27.0% | 17.5% | 8.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| rebound_trail_1_40 | 23 | 43% | 2.88% | 0.75% | 64x, 6x, 3x, 2x, 2x |
| rebound_trail_2_50 | 23 | 26% | 1.68% | 0.47% | 51x, 5x, 3x, 3x, 2x |
| rebound_trail_1_65 | 23 | 22% | 1.32% | 0.43% | 37x, 3x, 2x, 2x, 1x |
| rebound_trail_3_60 | 23 | 22% | 1.45% | 0.40% | 37x, 4x, 3x, 2x, 2x |
| rebound_hold | 23 | 9% | 0.80% | 0.25% | 75x, 5x, 0x, 0x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_trail_1_40 | 23 | +260.4% | 15.5% | 2 | +205.9% | 51.1% | holding up |
| rebound_trail_2_50 | 23 | +182.3% | 11.8% | 2 | +139.2% | 51.1% | holding up |
| rebound_trail_3_60 | 23 | +114.1% | 10.8% | 2 | +108.6% | 51.1% | holding up |
| rebound_trail_1_65 | 23 | +118.6% | 9.1% | 2 | +72.4% | 26.1% | holding up |
| rebound_hold | 23 | +249.1% | 8.7% | 2 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_trail_1_40 | 0 | +0.0% | 23 | +260.4% |
| rebound_hold | 0 | +0.0% | 23 | +249.1% |
| rebound_trail_2_50 | 0 | +0.0% | 23 | +182.3% |
| rebound_trail_1_65 | 0 | +0.0% | 23 | +118.6% |
| rebound_trail_3_60 | 0 | +0.0% | 23 | +114.1% |

Exit reasons:

- rebound_trail_1_40: {'time': 13, 'trail': 10}
- rebound_hold: {'time': 23}
- rebound_trail_2_50: {'time': 17, 'trail': 6}
- rebound_trail_1_65: {'time': 13, 'trail': 10}
- rebound_trail_3_60: {'time': 18, 'trail': 5}
