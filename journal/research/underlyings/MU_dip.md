# Backtest — MU 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 57%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 49.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 208 | 24% | +136% | -98% | -42.9% | +768% | 24 | 500 | 95% | — / — / — | 2024-10-31 |
| dip2_fade_d008 | 208 | 23% | +121% | -98% | -47.1% | +2158% | 45 | 560 | 92% | — / — / — | 2024-10-24 |
| move15_follow_d02 | 250 | 24% | +116% | -98% | -47.6% | +768% | 34 | 500 | 93% | — / — / — | 2024-10-21 |
| move1_follow_d02 | 281 | 23% | +117% | -98% | -48.9% | +768% | 11 | 500 | 98% | — / — / — | 2024-10-21 |
| dip15_fade_d008 | 250 | 20% | +130% | -98% | -51.4% | +2153% | 33 | 500 | 93% | — / — / — | 2024-10-21 |
| dip1_fade_d008 | 281 | 21% | +113% | -98% | -54.5% | +1554% | 47 | 500 | 91% | — / — / — | 2024-10-17 |
| dip1_fade_d02 | 281 | 20% | +118% | -100% | -55.5% | +1000% | 17 | 596 | 97% | — / — / — | 2024-10-22 |
| dip2_fade_d02 | 208 | 22% | +94% | -99% | -56.0% | +1092% | 16 | 798 | 98% | — / — / — | 2024-11-05 |
| dip15_fade_d02 | 250 | 19% | +99% | -99% | -61.4% | +942% | 40 | 500 | 92% | — / — / — | 2024-10-21 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| move2_follow_d02 | 1.6% | 3.5% | 4.1% |
| move1_follow_d02 | 1.1% | 2.6% | 3.3% |
| move15_follow_d02 | 1.0% | 2.9% | 3.2% |
| dip2_fade_d02 | 1.1% | 1.5% | 3.0% |
| dip2_fade_d008 | 2.2% | 2.9% | 2.4% |
| dip15_fade_d008 | 2.3% | 2.9% | 2.6% |
| dip1_fade_d02 | 1.5% | 2.1% | 2.9% |
| dip1_fade_d008 | 1.3% | 1.8% | 2.6% |
| dip15_fade_d02 | 0.6% | 1.2% | 2.5% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| move15_follow_d02 | 250 | 24% | 0.03% | 0.03% | 9x, 8x, 8x, 8x, 4x |
| dip15_fade_d008 | 250 | 20% | 0.10% | 0.00% | 23x, 9x, 7x, 4x, 3x |
| move2_follow_d02 | 208 | 24% | 0.07% | 0.00% | 9x, 8x, 8x, 8x, 4x |
| dip2_fade_d008 | 208 | 23% | 0.07% | 0.00% | 23x, 9x, 7x, 3x, 2x |
| move1_follow_d02 | 281 | 23% | 0.05% | 0.00% | 9x, 8x, 8x, 8x, 4x |
| dip1_fade_d008 | 281 | 21% | 0.03% | 0.00% | 17x, 7x, 7x, 5x, 4x |
| dip1_fade_d02 | 281 | 20% | 0.03% | 0.00% | 11x, 11x, 10x, 5x, 4x |
| dip2_fade_d02 | 208 | 22% | 0.00% | 0.00% | 12x, 6x, 5x, 4x, 3x |
| dip15_fade_d02 | 250 | 19% | 0.00% | 0.00% | 10x, 6x, 5x, 3x, 3x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 208 | -42.9% | 4.1% | 31 | -36.6% | 5.9% | holding up |
| move1_follow_d02 | 281 | -48.9% | 3.3% | 35 | -37.7% | 5.4% | holding up |
| move15_follow_d02 | 250 | -47.6% | 3.2% | 33 | -39.4% | 5.0% | holding up |
| dip15_fade_d008 | 250 | -51.4% | 2.6% | 33 | -73.7% | 0.2% | broken |
| dip15_fade_d02 | 250 | -61.4% | 2.5% | 33 | -81.9% | 0.1% | broken |
| dip2_fade_d008 | 208 | -47.1% | 2.4% | 31 | -77.9% | 0.1% | broken |
| dip1_fade_d008 | 281 | -54.5% | 2.6% | 35 | -80.8% | 0.0% | broken |
| dip1_fade_d02 | 281 | -55.5% | 2.9% | 35 | -88.1% | 0.0% | broken |
| dip2_fade_d02 | 208 | -56.0% | 3.0% | 31 | -83.4% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| move2_follow_d02 | 18 | -58.4% | 190 | -41.4% |
| dip2_fade_d008 | 18 | -50.5% | 190 | -46.8% |
| move15_follow_d02 | 19 | -56.7% | 231 | -46.9% |
| move1_follow_d02 | 22 | -61.9% | 259 | -47.8% |
| dip15_fade_d008 | 19 | -50.4% | 231 | -51.5% |
| dip1_fade_d008 | 22 | -47.1% | 259 | -55.2% |
| dip1_fade_d02 | 22 | -33.4% | 259 | -57.4% |
| dip2_fade_d02 | 18 | -36.3% | 190 | -57.9% |
| dip15_fade_d02 | 19 | -42.1% | 231 | -63.0% |

Exit reasons:

- move2_follow_d02: {'time': 161, 'trail': 47}
- dip2_fade_d008: {'trail': 52, 'time': 156}
- move15_follow_d02: {'time': 194, 'trail': 56}
- move1_follow_d02: {'time': 219, 'trail': 62}
- dip15_fade_d008: {'time': 194, 'trail': 56}
- dip1_fade_d008: {'time': 218, 'trail': 63}
- dip1_fade_d02: {'trail': 55, 'time': 226}
- dip2_fade_d02: {'time': 165, 'trail': 43}
- dip15_fade_d02: {'time': 203, 'trail': 47}
