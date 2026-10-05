# Backtest — TSLA 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 49%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 42.9% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| move15_follow_d02 | 239 | 32% | +139% | -99% | -22.0% | +1206% | 2 | 500 | 100% | — / — / — | 2024-10-28 |
| move2_follow_d02 | 195 | 32% | +134% | -99% | -24.0% | +766% | 6 | 500 | 99% | — / — / — | 2024-10-28 |
| move1_follow_d02 | 279 | 30% | +143% | -98% | -24.8% | +1206% | 13 | 500 | 97% | — / — / — | 2024-10-28 |
| dip2_fade_d008 | 195 | 23% | +141% | -100% | -45.4% | +753% | 17 | 500 | 97% | — / — / — | 2024-11-26 |
| dip15_fade_d02 | 239 | 23% | +128% | -99% | -46.9% | +1221% | 34 | 726 | 95% | — / — / — | 2024-11-29 |
| dip1_fade_d02 | 279 | 23% | +125% | -99% | -48.2% | +1111% | 1 | 500 | 100% | — / — / — | 2025-01-27 |
| dip2_fade_d02 | 195 | 22% | +110% | -98% | -52.4% | +474% | 1 | 824 | 100% | — / — / — | 2025-04-17 |
| dip1_fade_d008 | 279 | 22% | +110% | -99% | -52.7% | +988% | 21 | 500 | 96% | — / — / — | 2024-11-05 |
| dip15_fade_d008 | 239 | 22% | +110% | -99% | -53.8% | +695% | 31 | 500 | 94% | — / — / — | 2024-11-25 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| move15_follow_d02 | 5.9% | 7.8% | 8.3% |
| move1_follow_d02 | 5.3% | 6.4% | 8.2% |
| move2_follow_d02 | 4.8% | 7.2% | 7.9% |
| dip2_fade_d008 | 1.5% | 3.0% | 4.9% |
| dip15_fade_d02 | 1.4% | 1.9% | 4.8% |
| dip2_fade_d02 | 0.6% | 1.1% | 4.1% |
| dip1_fade_d02 | 1.6% | 2.4% | 3.4% |
| dip1_fade_d008 | 0.8% | 1.6% | 3.2% |
| dip15_fade_d008 | 0.5% | 1.1% | 3.2% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| move15_follow_d02 | 239 | 32% | 0.27% | 0.03% | 13x, 9x, 8x, 7x, 7x |
| move2_follow_d02 | 195 | 32% | 0.12% | 0.03% | 9x, 8x, 7x, 7x, 6x |
| move1_follow_d02 | 279 | 30% | 0.12% | 0.00% | 13x, 9x, 8x, 7x, 7x |
| dip1_fade_d02 | 279 | 23% | 0.12% | 0.00% | 12x, 10x, 5x, 4x, 4x |
| dip1_fade_d008 | 279 | 22% | 0.07% | 0.00% | 11x, 8x, 5x, 5x, 4x |
| dip2_fade_d02 | 195 | 22% | 0.05% | 0.00% | 6x, 6x, 5x, 5x, 4x |
| dip15_fade_d008 | 239 | 22% | 0.03% | 0.00% | 8x, 5x, 5x, 4x, 4x |
| dip2_fade_d008 | 195 | 23% | 0.00% | 0.00% | 9x, 8x, 7x, 6x, 5x |
| dip15_fade_d02 | 239 | 23% | 0.00% | 0.00% | 13x, 5x, 5x, 5x, 5x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| dip2_fade_d008 | 195 | -45.4% | 4.9% | 23 | -51.7% | 5.9% | holding up |
| dip15_fade_d008 | 239 | -53.8% | 3.2% | 28 | -64.9% | 3.9% | holding up |
| dip1_fade_d008 | 279 | -52.7% | 3.2% | 34 | -68.4% | 3.5% | holding up |
| dip2_fade_d02 | 195 | -52.4% | 4.1% | 23 | -66.0% | 1.6% | broken |
| dip15_fade_d02 | 239 | -46.9% | 4.8% | 28 | -75.0% | 0.4% | broken |
| dip1_fade_d02 | 279 | -48.2% | 3.4% | 34 | -82.0% | 0.2% | broken |
| move1_follow_d02 | 279 | -24.8% | 8.2% | 34 | -78.1% | 0.1% | broken |
| move15_follow_d02 | 239 | -22.0% | 8.3% | 28 | -81.3% | 0.0% | broken |
| move2_follow_d02 | 195 | -24.0% | 7.9% | 23 | -83.6% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| move15_follow_d02 | 14 | -48.3% | 225 | -20.4% |
| move2_follow_d02 | 12 | -50.4% | 183 | -22.2% |
| move1_follow_d02 | 19 | -60.7% | 260 | -22.2% |
| dip2_fade_d008 | 12 | -89.5% | 183 | -42.5% |
| dip15_fade_d02 | 14 | -91.0% | 225 | -44.2% |
| dip1_fade_d02 | 19 | -92.0% | 260 | -45.0% |
| dip2_fade_d02 | 12 | -86.6% | 183 | -50.2% |
| dip1_fade_d008 | 19 | -93.4% | 260 | -49.8% |
| dip15_fade_d008 | 14 | -91.0% | 225 | -51.5% |

Exit reasons:

- move15_follow_d02: {'time': 167, 'trail': 72}
- move2_follow_d02: {'time': 136, 'trail': 59}
- move1_follow_d02: {'time': 199, 'trail': 80}
- dip2_fade_d008: {'time': 150, 'trail': 45}
- dip15_fade_d02: {'time': 189, 'trail': 50}
- dip1_fade_d02: {'time': 221, 'trail': 58}
- dip2_fade_d02: {'time': 152, 'trail': 43}
- dip1_fade_d008: {'time': 216, 'trail': 63}
- dip15_fade_d008: {'time': 186, 'trail': 53}
