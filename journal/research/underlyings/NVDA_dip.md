# Backtest — NVDA 0DTE, 2024-10-07 → 2026-10-02 (499 days)

Model: Black-Scholes at IV 39%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 33.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| move15_follow_d02 | 194 | 29% | +133% | -99% | -31.8% | +1443% | 24 | 797 | 97% | — / — / — | 2024-10-28 |
| move2_follow_d02 | 129 | 32% | +105% | -100% | -34.6% | +829% | 25 | 610 | 96% | — / — / — | 2024-10-29 |
| move1_follow_d02 | 251 | 26% | +146% | -98% | -35.0% | +1443% | 11 | 986 | 99% | — / — / — | 2024-10-29 |
| dip1_fade_d02 | 251 | 20% | +86% | -98% | -60.5% | +702% | 9 | 500 | 98% | — / — / — | 2024-10-24 |
| dip2_fade_d02 | 129 | 20% | +72% | -98% | -63.6% | +466% | 43 | 500 | 91% | — / — / — | 2024-11-07 |
| dip1_fade_d008 | 251 | 18% | +99% | -100% | -64.0% | +832% | 36 | 500 | 93% | — / — / — | 2024-10-15 |
| dip15_fade_d02 | 194 | 19% | +69% | -98% | -66.4% | +278% | 14 | 500 | 97% | — / — / — | 2024-10-29 |
| dip15_fade_d008 | 194 | 19% | +72% | -100% | -67.3% | +231% | 37 | 500 | 93% | — / — / — | 2024-10-28 |
| dip2_fade_d008 | 129 | 19% | +57% | -99% | -69.0% | +222% | 48 | 500 | 90% | — / — / — | 2024-10-28 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| move15_follow_d02 | 3.5% | 5.2% | 6.5% |
| move2_follow_d02 | 1.8% | 3.1% | 6.2% |
| move1_follow_d02 | 2.7% | 4.1% | 5.5% |
| dip1_fade_d02 | 0.3% | 0.9% | 2.2% |
| dip1_fade_d008 | 0.3% | 1.2% | 1.6% |
| dip2_fade_d02 | 0.1% | 0.2% | 1.2% |
| dip15_fade_d008 | 0.0% | 0.1% | 1.0% |
| dip15_fade_d02 | 0.0% | 0.1% | 0.9% |
| dip2_fade_d008 | 0.0% | 0.1% | 0.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| move15_follow_d02 | 194 | 29% | 0.20% | 0.00% | 15x, 9x, 6x, 4x, 4x |
| move2_follow_d02 | 129 | 32% | 0.07% | 0.00% | 9x, 4x, 4x, 3x, 3x |
| move1_follow_d02 | 251 | 26% | 0.05% | 0.00% | 15x, 9x, 7x, 7x, 5x |
| dip1_fade_d02 | 251 | 20% | 0.00% | 0.00% | 8x, 5x, 5x, 3x, 3x |
| dip2_fade_d02 | 129 | 20% | 0.00% | 0.00% | 6x, 3x, 2x, 2x, 2x |
| dip1_fade_d008 | 251 | 18% | 0.00% | 0.00% | 9x, 7x, 3x, 3x, 3x |
| dip15_fade_d02 | 194 | 19% | 0.00% | 0.00% | 4x, 4x, 3x, 2x, 2x |
| dip15_fade_d008 | 194 | 19% | 0.00% | 0.00% | 3x, 3x, 3x, 3x, 2x |
| dip2_fade_d008 | 129 | 19% | 0.00% | 0.00% | 3x, 3x, 2x, 2x, 2x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| move2_follow_d02 | 129 | -34.6% | 6.2% | 16 | -20.3% | 10.1% | holding up |
| move15_follow_d02 | 194 | -31.8% | 6.5% | 22 | -32.2% | 7.6% | holding up |
| dip2_fade_d02 | 129 | -63.6% | 1.2% | 16 | -47.9% | 6.7% | holding up |
| move1_follow_d02 | 251 | -35.0% | 5.5% | 29 | -35.2% | 5.9% | holding up |
| dip15_fade_d02 | 194 | -66.4% | 0.9% | 22 | -55.5% | 2.3% | holding up |
| dip2_fade_d008 | 129 | -69.0% | 0.7% | 16 | -63.8% | 0.8% | holding up |
| dip15_fade_d008 | 194 | -67.3% | 1.0% | 22 | -65.2% | 0.5% | fading |
| dip1_fade_d02 | 251 | -60.5% | 2.2% | 29 | -78.8% | 0.0% | broken |
| dip1_fade_d008 | 251 | -64.0% | 1.6% | 29 | -86.9% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| move15_follow_d02 | 12 | -76.6% | 182 | -28.8% |
| move2_follow_d02 | 5 | -74.8% | 124 | -33.0% |
| move1_follow_d02 | 17 | -79.9% | 234 | -31.7% |
| dip1_fade_d02 | 17 | -55.6% | 234 | -60.8% |
| dip2_fade_d02 | 5 | -48.6% | 124 | -64.2% |
| dip1_fade_d008 | 17 | -59.8% | 234 | -64.3% |
| dip15_fade_d02 | 12 | -38.2% | 182 | -68.2% |
| dip15_fade_d008 | 12 | -33.2% | 182 | -69.5% |
| dip2_fade_d008 | 5 | -48.2% | 124 | -69.8% |

Exit reasons:

- move15_follow_d02: {'trail': 57, 'time': 137}
- move2_follow_d02: {'trail': 41, 'time': 88}
- move1_follow_d02: {'trail': 63, 'time': 188}
- dip1_fade_d02: {'time': 201, 'trail': 50}
- dip2_fade_d02: {'time': 105, 'trail': 24}
- dip1_fade_d008: {'time': 205, 'trail': 46}
- dip15_fade_d02: {'time': 157, 'trail': 37}
- dip15_fade_d008: {'time': 158, 'trail': 36}
- dip2_fade_d008: {'time': 104, 'trail': 25}
