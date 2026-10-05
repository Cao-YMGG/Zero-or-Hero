# Backtest — AMD 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 49%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 42.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_trail_1_65 | 34 | 41% | +441% | -82% | +133.4% | +2246% | 39 | 500 | 92% | — / — / — | 2025-01-13 |
| rebound_trail_3_60 | 34 | 35% | +516% | -100% | +117.5% | +2246% | 39 | 500 | 92% | — / — / — | 2025-01-13 |
| rebound_trail_1_40 | 34 | 53% | +262% | -100% | +91.9% | +1189% | 39 | 500 | 92% | — / — / — | 2025-01-13 |
| rebound_trail_2_50 | 34 | 41% | +313% | -100% | +70.2% | +914% | 39 | 500 | 92% | — / — / — | 2025-01-13 |
| rebound_hold | 34 | 15% | +835% | -97% | +40.4% | +1984% | 39 | 500 | 92% | — / — / — | 2025-01-13 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_trail_1_40 | 88.4% | 64.1% | 28.9% |
| rebound_trail_1_65 | 74.9% | 51.4% | 22.5% |
| rebound_trail_2_50 | 69.3% | 46.9% | 23.8% |
| rebound_trail_3_60 | 62.2% | 42.0% | 18.6% |
| rebound_hold | 24.7% | 18.9% | 9.6% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| rebound_trail_1_40 | 34 | 53% | 5.40% | 1.52% | 13x, 9x, 7x, 5x, 4x |
| rebound_trail_1_65 | 34 | 41% | 4.05% | 1.23% | 23x, 21x, 10x, 4x, 3x |
| rebound_trail_2_50 | 34 | 41% | 3.05% | 0.68% | 10x, 8x, 8x, 6x, 5x |
| rebound_trail_3_60 | 34 | 35% | 2.40% | 0.55% | 23x, 16x, 10x, 5x, 4x |
| rebound_hold | 34 | 15% | 0.85% | 0.12% | 21x, 12x, 10x, 3x, 1x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_trail_1_40 | 34 | +91.9% | 28.9% | 7 | +217.3% | 52.6% | holding up |
| rebound_trail_1_65 | 34 | +133.4% | 22.5% | 7 | +406.6% | 51.3% | holding up |
| rebound_trail_2_50 | 34 | +70.2% | 23.8% | 7 | +219.7% | 42.9% | holding up |
| rebound_trail_3_60 | 34 | +117.5% | 18.6% | 7 | +317.8% | 34.1% | holding up |
| rebound_hold | 34 | +40.4% | 9.6% | 7 | +334.2% | 28.1% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_trail_1_65 | 0 | +0.0% | 34 | +133.4% |
| rebound_trail_3_60 | 0 | +0.0% | 34 | +117.5% |
| rebound_trail_1_40 | 0 | +0.0% | 34 | +91.9% |
| rebound_trail_2_50 | 0 | +0.0% | 34 | +70.2% |
| rebound_hold | 0 | +0.0% | 34 | +40.4% |

Exit reasons:

- rebound_trail_1_65: {'time': 18, 'trail': 16}
- rebound_trail_3_60: {'time': 23, 'trail': 11}
- rebound_trail_1_40: {'time': 16, 'trail': 18}
- rebound_trail_2_50: {'time': 20, 'trail': 14}
- rebound_hold: {'time': 34}
