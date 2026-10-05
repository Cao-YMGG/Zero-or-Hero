# Backtest — AMD 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 49%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 42.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 179 | 28% | +115% | -98% | -37.6% | +644% | 48 | 500 | 90% | — / — / — | 2024-11-21 |
| move15_follow_d02 | 234 | 24% | +117% | -99% | -47.9% | +644% | 8 | 500 | 98% | — / — / — | 2024-10-31 |
| dip2_fade_d008 | 179 | 22% | +123% | -99% | -49.1% | +1089% | 46 | 500 | 91% | — / — / — | 2024-10-31 |
| dip15_fade_d008 | 234 | 24% | +105% | -99% | -49.3% | +1085% | 47 | 500 | 91% | — / — / — | 2024-10-24 |
| dip1_fade_d008 | 281 | 25% | +97% | -99% | -49.6% | +807% | 41 | 500 | 92% | — / — / — | 2024-10-22 |
| dip15_fade_d02 | 234 | 24% | +97% | -98% | -50.3% | +976% | 10 | 500 | 98% | — / — / — | 2024-10-28 |
| dip1_fade_d02 | 281 | 26% | +89% | -98% | -50.3% | +919% | 6 | 500 | 99% | — / — / — | 2024-10-29 |
| move1_follow_d02 | 281 | 23% | +111% | -99% | -50.5% | +644% | 5 | 500 | 99% | — / — / — | 2024-10-31 |
| dip2_fade_d02 | 179 | 23% | +96% | -98% | -52.8% | +640% | 50 | 500 | 90% | — / — / — | 2024-11-21 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| move2_follow_d02 | 1.5% | 3.4% | 5.7% |
| move15_follow_d02 | 0.9% | 2.5% | 4.6% |
| move1_follow_d02 | 0.7% | 1.9% | 3.8% |
| dip15_fade_d008 | 1.1% | 1.9% | 3.6% |
| dip1_fade_d008 | 0.7% | 1.8% | 3.5% |
| dip1_fade_d02 | 0.7% | 1.7% | 3.5% |
| dip2_fade_d008 | 1.6% | 2.5% | 3.4% |
| dip2_fade_d02 | 0.5% | 1.4% | 3.0% |
| dip15_fade_d02 | 1.0% | 1.7% | 2.8% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| move15_follow_d02 | 234 | 24% | 0.05% | 0.00% | 7x, 7x, 6x, 6x, 5x |
| dip2_fade_d008 | 179 | 22% | 0.05% | 0.00% | 12x, 9x, 6x, 5x, 3x |
| move1_follow_d02 | 281 | 23% | 0.05% | 0.00% | 7x, 7x, 6x, 6x, 5x |
| dip1_fade_d008 | 281 | 25% | 0.03% | 0.00% | 9x, 8x, 4x, 4x, 3x |
| move2_follow_d02 | 179 | 28% | 0.00% | 0.00% | 7x, 6x, 6x, 5x, 5x |
| dip15_fade_d008 | 234 | 24% | 0.00% | 0.00% | 12x, 9x, 4x, 4x, 4x |
| dip15_fade_d02 | 234 | 24% | 0.00% | 0.00% | 11x, 7x, 5x, 5x, 3x |
| dip1_fade_d02 | 281 | 26% | 0.00% | 0.00% | 10x, 5x, 5x, 5x, 4x |
| dip2_fade_d02 | 179 | 23% | 0.00% | 0.00% | 7x, 7x, 5x, 4x, 4x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 179 | -37.6% | 5.7% | 23 | +4.4% | 17.2% | holding up |
| move15_follow_d02 | 234 | -47.9% | 4.6% | 28 | -17.5% | 12.0% | holding up |
| move1_follow_d02 | 281 | -50.5% | 3.8% | 36 | -34.8% | 8.2% | holding up |
| dip1_fade_d008 | 281 | -49.6% | 3.5% | 36 | -45.4% | 3.0% | holding up |
| dip15_fade_d008 | 234 | -49.3% | 3.6% | 28 | -46.5% | 2.3% | fading |
| dip15_fade_d02 | 234 | -50.3% | 2.8% | 28 | -43.6% | 1.8% | fading |
| dip1_fade_d02 | 281 | -50.3% | 3.5% | 36 | -52.0% | 1.1% | broken |
| dip2_fade_d02 | 179 | -52.8% | 3.0% | 23 | -70.2% | 0.1% | broken |
| dip2_fade_d008 | 179 | -49.1% | 3.4% | 23 | -67.5% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| move2_follow_d02 | 15 | -42.3% | 164 | -37.2% |
| move15_follow_d02 | 17 | -53.6% | 217 | -47.5% |
| dip2_fade_d008 | 15 | -20.5% | 164 | -51.7% |
| dip15_fade_d008 | 17 | -16.1% | 217 | -51.9% |
| dip1_fade_d008 | 22 | -31.7% | 259 | -51.1% |
| dip15_fade_d02 | 17 | +3.0% | 217 | -54.4% |
| dip1_fade_d02 | 22 | -19.0% | 259 | -52.9% |
| move1_follow_d02 | 22 | -56.9% | 259 | -50.0% |
| dip2_fade_d02 | 15 | -19.9% | 164 | -55.8% |

Exit reasons:

- move2_follow_d02: {'time': 128, 'trail': 51}
- move15_follow_d02: {'time': 180, 'trail': 54}
- dip2_fade_d008: {'time': 137, 'trail': 42}
- dip15_fade_d008: {'time': 175, 'trail': 59}
- dip1_fade_d008: {'time': 209, 'trail': 72}
- dip15_fade_d02: {'time': 177, 'trail': 57}
- dip1_fade_d02: {'time': 211, 'trail': 70}
- move1_follow_d02: {'time': 217, 'trail': 64}
- dip2_fade_d02: {'time': 138, 'trail': 41}
