# Backtest — META 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 33%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 28.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_hold | 12 | 25% | +2075% | -100% | +443.9% | +4034% | 16,594 | 19,736 | 19% | 2025-01-27 / 2025-01-27 / 2025-04-07 | — |
| rebound_trail_1_40 | 12 | 50% | +986% | -100% | +443.1% | +5286% | 15,952 | 17,219 | 49% | 2025-03-31 / 2025-04-07 / 2025-04-07 | — |
| rebound_trail_2_50 | 12 | 33% | +1426% | -100% | +408.6% | +4186% | 12,777 | 14,345 | 18% | 2025-01-27 / 2025-01-27 / 2025-04-07 | — |
| rebound_trail_1_65 | 12 | 33% | +898% | -80% | +246.3% | +2657% | 4,918 | 7,251 | 33% | 2025-01-27 / 2025-04-07 / 2025-04-07 | — |
| rebound_trail_3_60 | 12 | 33% | +938% | -100% | +245.9% | +2657% | 4,737 | 7,389 | 39% | 2025-01-27 / 2025-01-27 / 2025-04-07 | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_trail_1_40 | 87.8% | 65.9% | 25.4% |
| rebound_trail_1_65 | 81.0% | 59.8% | 26.1% |
| rebound_hold | 79.9% | 57.9% | 25.4% |
| rebound_trail_2_50 | 79.5% | 56.8% | 22.8% |
| rebound_trail_3_60 | 73.1% | 50.9% | 21.4% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| rebound_trail_1_40 | 12 | 50% | 9.38% | 3.48% | 54x, 3x, 3x, 2x, 2x |
| rebound_trail_2_50 | 12 | 33% | 6.10% | 2.50% | 43x, 14x, 3x, 2x, 0x |
| rebound_trail_1_65 | 12 | 33% | 6.08% | 2.23% | 28x, 9x, 2x, 1x, 1x |
| rebound_hold | 12 | 25% | 6.10% | 2.20% | 41x, 14x, 10x, 0x, 0x |
| rebound_trail_3_60 | 12 | 33% | 4.75% | 1.45% | 28x, 10x, 2x, 2x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_trail_1_40 | 12 | +443.1% | 25.4% | 1 | +128.6% | 100.0% | holding up |
| rebound_trail_2_50 | 12 | +408.6% | 22.8% | 1 | +103.3% | 100.0% | holding up |
| rebound_trail_1_65 | 12 | +246.3% | 26.1% | 1 | +18.9% | 100.0% | holding up |
| rebound_trail_3_60 | 12 | +245.9% | 21.4% | 1 | +63.9% | 100.0% | holding up |
| rebound_hold | 12 | +443.9% | 25.4% | 1 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_hold | 0 | +0.0% | 12 | +443.9% |
| rebound_trail_1_40 | 0 | +0.0% | 12 | +443.1% |
| rebound_trail_2_50 | 0 | +0.0% | 12 | +408.6% |
| rebound_trail_1_65 | 0 | +0.0% | 12 | +246.3% |
| rebound_trail_3_60 | 0 | +0.0% | 12 | +245.9% |

Exit reasons:

- rebound_hold: {'time': 12}
- rebound_trail_1_40: {'trail': 6, 'time': 6}
- rebound_trail_2_50: {'trail': 4, 'time': 8}
- rebound_trail_1_65: {'trail': 6, 'time': 6}
- rebound_trail_3_60: {'trail': 4, 'time': 8}
