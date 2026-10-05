# Backtest — META 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 33%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 28.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 89 | 36% | +198% | -99% | +7.7% | +1635% | 41 | 500 | 92% | — / — / — | 2024-12-09 |
| move15_follow_d02 | 149 | 29% | +163% | -98% | -22.9% | +1635% | 13 | 500 | 97% | — / — / — | 2024-11-21 |
| move1_follow_d02 | 237 | 24% | +215% | -99% | -24.6% | +4980% | 58 | 559 | 90% | — / — / — | — |
| dip15_fade_d008 | 149 | 24% | +203% | -100% | -26.7% | +2130% | 22 | 500 | 96% | — / — / — | 2024-12-02 |
| dip2_fade_d008 | 89 | 26% | +154% | -100% | -34.3% | +1032% | 7 | 500 | 99% | — / — / — | 2024-12-10 |
| dip1_fade_d008 | 237 | 27% | +138% | -99% | -36.4% | +1735% | 19 | 500 | 96% | — / — / — | 2024-10-24 |
| dip2_fade_d02 | 89 | 25% | +146% | -98% | -37.3% | +1147% | 11 | 500 | 98% | — / — / — | 2025-04-10 |
| dip15_fade_d02 | 149 | 24% | +114% | -98% | -46.7% | +872% | 2 | 500 | 100% | — / — / — | 2025-01-16 |
| dip1_fade_d02 | 237 | 26% | +90% | -99% | -49.5% | +781% | 52 | 500 | 90% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| move2_follow_d02 | 18.1% | 15.6% | 9.8% |
| move15_follow_d02 | 7.3% | 7.2% | 4.9% |
| dip15_fade_d008 | 6.6% | 6.8% | 4.8% |
| dip2_fade_d008 | 4.2% | 5.3% | 6.0% |
| move1_follow_d02 | 5.0% | 5.6% | 3.9% |
| dip1_fade_d008 | 3.6% | 3.7% | 5.2% |
| dip2_fade_d02 | 4.0% | 4.2% | 4.9% |
| dip15_fade_d02 | 1.4% | 3.2% | 4.1% |
| dip1_fade_d02 | 0.6% | 1.1% | 3.3% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| dip15_fade_d008 | 149 | 24% | 0.25% | 0.05% | 22x, 14x, 9x, 4x, 4x |
| move2_follow_d02 | 89 | 36% | 0.68% | 0.03% | 17x, 15x, 10x, 9x, 5x |
| move1_follow_d02 | 237 | 24% | 0.27% | 0.00% | 51x, 15x, 9x, 9x, 6x |
| dip2_fade_d008 | 89 | 26% | 0.07% | 0.00% | 11x, 7x, 4x, 3x, 3x |
| move15_follow_d02 | 149 | 29% | 0.05% | 0.00% | 17x, 15x, 9x, 9x, 3x |
| dip1_fade_d008 | 237 | 27% | 0.05% | 0.00% | 18x, 14x, 7x, 5x, 4x |
| dip15_fade_d02 | 149 | 24% | 0.05% | 0.00% | 10x, 6x, 5x, 3x, 3x |
| dip2_fade_d02 | 89 | 25% | 0.03% | 0.00% | 12x, 7x, 5x, 3x, 2x |
| dip1_fade_d02 | 237 | 26% | 0.00% | 0.00% | 9x, 6x, 4x, 3x, 3x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| dip1_fade_d008 | 237 | -36.4% | 5.2% | 32 | +2.5% | 17.4% | holding up |
| dip15_fade_d008 | 149 | -26.7% | 4.8% | 23 | -6.8% | 14.2% | holding up |
| dip2_fade_d008 | 89 | -34.3% | 6.0% | 19 | -29.8% | 10.3% | holding up |
| dip1_fade_d02 | 237 | -49.5% | 3.3% | 32 | -16.3% | 10.2% | holding up |
| move2_follow_d02 | 89 | +7.7% | 9.8% | 19 | +32.6% | 9.9% | holding up |
| move15_follow_d02 | 149 | -22.9% | 4.9% | 23 | +18.1% | 8.3% | holding up |
| dip15_fade_d02 | 149 | -46.7% | 4.1% | 23 | -26.0% | 8.1% | holding up |
| move1_follow_d02 | 237 | -24.6% | 3.9% | 32 | -9.2% | 5.3% | holding up |
| dip2_fade_d02 | 89 | -37.3% | 4.9% | 19 | -45.1% | 2.8% | fading |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| move2_follow_d02 | 5 | +137.5% | 84 | -0.0% |
| move15_follow_d02 | 5 | +123.5% | 144 | -28.0% |
| move1_follow_d02 | 13 | -13.4% | 224 | -25.3% |
| dip15_fade_d008 | 5 | -58.8% | 144 | -25.6% |
| dip2_fade_d008 | 5 | -55.6% | 84 | -33.0% |
| dip1_fade_d008 | 13 | -53.8% | 224 | -35.4% |
| dip2_fade_d02 | 5 | -59.0% | 84 | -36.1% |
| dip15_fade_d02 | 5 | -62.4% | 144 | -46.2% |
| dip1_fade_d02 | 13 | -49.0% | 224 | -49.5% |

Exit reasons:

- move2_follow_d02: {'time': 59, 'trail': 30}
- move15_follow_d02: {'time': 107, 'trail': 42}
- move1_follow_d02: {'trail': 52, 'time': 185}
- dip15_fade_d008: {'time': 113, 'trail': 36}
- dip2_fade_d008: {'time': 66, 'trail': 23}
- dip1_fade_d008: {'time': 173, 'trail': 64}
- dip2_fade_d02: {'time': 67, 'trail': 22}
- dip15_fade_d02: {'time': 113, 'trail': 36}
- dip1_fade_d02: {'time': 176, 'trail': 61}
