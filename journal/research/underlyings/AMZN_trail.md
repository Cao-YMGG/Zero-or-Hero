# Backtest — AMZN 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 28%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 24.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_trail_3_60 | 14 | 43% | +784% | -100% | +278.8% | +2746% | 27,821 | 29,555 | 75% | 2025-04-04 / 2025-04-07 / 2025-04-07 | — |
| rebound_hold | 14 | 36% | +761% | -93% | +212.2% | +2767% | 6,678 | 9,981 | 87% | 2025-04-07 / 2025-04-07 / 2025-04-07 | — |
| rebound_trail_1_65 | 14 | 36% | +655% | -68% | +190.0% | +2746% | 5,153 | 7,339 | 76% | 2025-04-07 / 2025-04-07 / 2025-04-07 | — |
| rebound_trail_2_50 | 14 | 50% | +349% | -100% | +124.7% | +926% | 3,857 | 5,013 | 73% | 2025-04-02 / 2025-04-04 / 2025-04-07 | — |
| rebound_trail_1_40 | 14 | 57% | +228% | -100% | +87.6% | +845% | 5,900 | 7,808 | 74% | 2025-01-27 / 2025-04-07 / 2025-04-07 | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_trail_2_50 | 92.1% | 70.7% | 29.8% |
| rebound_trail_3_60 | 91.0% | 71.5% | 34.0% |
| rebound_trail_1_40 | 89.6% | 66.0% | 34.1% |
| rebound_trail_1_65 | 80.2% | 55.8% | 24.7% |
| rebound_hold | 78.4% | 54.5% | 23.8% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| rebound_trail_3_60 | 14 | 43% | 7.80% | 2.83% | 28x, 9x, 7x, 4x, 3x |
| rebound_trail_2_50 | 14 | 50% | 6.60% | 2.23% | 10x, 8x, 4x, 3x, 2x |
| rebound_trail_1_65 | 14 | 36% | 5.53% | 1.88% | 28x, 4x, 3x, 1x, 1x |
| rebound_trail_1_40 | 14 | 57% | 5.80% | 1.62% | 9x, 5x, 5x, 2x, 2x |
| rebound_hold | 14 | 36% | 4.75% | 1.52% | 29x, 7x, 3x, 2x, 2x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_trail_1_65 | 14 | +190.0% | 24.7% | 1 | +34.5% | 100.0% | holding up |
| rebound_trail_2_50 | 14 | +124.7% | 29.8% | 1 | +75.4% | 100.0% | holding up |
| rebound_trail_1_40 | 14 | +87.6% | 34.1% | 1 | +59.3% | 100.0% | holding up |
| rebound_trail_3_60 | 14 | +278.8% | 34.0% | 1 | -100.0% | 0.0% | broken |
| rebound_hold | 14 | +212.2% | 23.8% | 1 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_trail_3_60 | 0 | +0.0% | 14 | +278.8% |
| rebound_hold | 0 | +0.0% | 14 | +212.2% |
| rebound_trail_1_65 | 0 | +0.0% | 14 | +190.0% |
| rebound_trail_2_50 | 0 | +0.0% | 14 | +124.7% |
| rebound_trail_1_40 | 0 | +0.0% | 14 | +87.6% |

Exit reasons:

- rebound_trail_3_60: {'time': 8, 'trail': 6}
- rebound_hold: {'time': 14}
- rebound_trail_1_65: {'trail': 8, 'time': 6}
- rebound_trail_2_50: {'time': 7, 'trail': 7}
- rebound_trail_1_40: {'trail': 8, 'time': 6}
