# Backtest — TSLA 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 49%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 42.9% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rebound_trail_3_60 | 23 | 30% | +1157% | -100% | +282.6% | +2991% | 15,057 | 16,914 | 92% | 2024-12-20 / 2025-04-07 / 2025-04-07 | — |
| rebound_hold | 23 | 17% | +1785% | -100% | +227.9% | +2936% | 29 | 500 | 94% | — / — / — | 2025-01-14 |
| rebound_trail_1_65 | 23 | 35% | +330% | -51% | +81.4% | +1901% | 1,996 | 2,486 | 88% | 2024-12-20 / — / — | — |
| rebound_trail_1_40 | 23 | 65% | +170% | -90% | +79.3% | +1296% | 6,746 | 7,864 | 20% | 2024-12-20 / 2025-03-31 / 2025-04-07 | — |
| rebound_trail_2_50 | 23 | 35% | +307% | -100% | +41.6% | +1159% | 18 | 1,425 | 99% | 2024-12-20 / — / — | 2026-07-20 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| rebound_trail_1_40 | 95.0% | 75.9% | 35.0% |
| rebound_trail_1_65 | 76.9% | 53.3% | 22.9% |
| rebound_trail_3_60 | 73.6% | 50.3% | 18.9% |
| rebound_hold | 59.0% | 39.9% | 18.2% |
| rebound_trail_2_50 | 41.3% | 28.2% | 19.5% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| rebound_trail_1_40 | 23 | 65% | 8.10% | 2.67% | 14x, 5x, 3x, 2x, 2x |
| rebound_trail_1_65 | 23 | 35% | 4.50% | 1.45% | 20x, 3x, 3x, 3x, 2x |
| rebound_trail_3_60 | 23 | 30% | 4.55% | 1.38% | 31x, 30x, 14x, 4x, 4x |
| rebound_hold | 23 | 17% | 3.48% | 0.60% | 30x, 17x, 14x, 13x, 0x |
| rebound_trail_2_50 | 23 | 35% | 1.52% | 0.27% | 13x, 5x, 4x, 3x, 2x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| rebound_trail_1_40 | 23 | +79.3% | 35.0% | 1 | +22.2% | 100.0% | holding up |
| rebound_trail_3_60 | 23 | +282.6% | 18.9% | 1 | -100.0% | 0.0% | broken |
| rebound_hold | 23 | +227.9% | 18.2% | 1 | -100.0% | 0.0% | broken |
| rebound_trail_1_65 | 23 | +81.4% | 22.9% | 1 | -11.3% | 0.0% | broken |
| rebound_trail_2_50 | 23 | +41.6% | 19.5% | 1 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| rebound_trail_3_60 | 0 | +0.0% | 23 | +282.6% |
| rebound_hold | 0 | +0.0% | 23 | +227.9% |
| rebound_trail_1_65 | 0 | +0.0% | 23 | +81.4% |
| rebound_trail_1_40 | 0 | +0.0% | 23 | +79.3% |
| rebound_trail_2_50 | 0 | +0.0% | 23 | +41.6% |

Exit reasons:

- rebound_trail_3_60: {'time': 18, 'trail': 5}
- rebound_hold: {'time': 23}
- rebound_trail_1_65: {'trail': 16, 'time': 7}
- rebound_trail_1_40: {'trail': 16, 'time': 7}
- rebound_trail_2_50: {'time': 15, 'trail': 8}
