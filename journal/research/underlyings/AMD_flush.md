# Backtest — AMD 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 55%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 47.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flush30_both_d008 | 7 | 43% | +219% | -100% | +36.6% | +503% | 315 | 507 | 68% | — / — / — | — |
| flush30_down_d02 | 4 | 50% | +154% | -100% | +26.9% | +269% | 503 | 866 | 42% | — / — / — | — |
| flush20_both_d008 | 34 | 38% | +163% | -95% | +3.3% | +825% | 26 | 500 | 95% | — / — / — | 2026-01-08 |
| flush15_both_d008 | 65 | 43% | +122% | -97% | -2.8% | +825% | 46 | 500 | 91% | — / — / — | 2025-12-09 |
| flush30_both_d02 | 7 | 43% | +113% | -100% | -8.8% | +269% | 122 | 500 | 76% | — / — / — | — |
| flush20_down_d02 | 13 | 38% | +111% | -100% | -18.8% | +269% | 90 | 500 | 82% | — / — / — | — |
| flush15_down_d02 | 28 | 39% | +99% | -100% | -21.8% | +269% | 6 | 500 | 99% | — / — / — | 2026-03-03 |
| flush20_both_d02 | 34 | 35% | +107% | -97% | -25.2% | +424% | 48 | 500 | 90% | — / — / — | 2026-01-05 |
| flush15_both_d02 | 65 | 37% | +99% | -99% | -25.5% | +424% | 1 | 500 | 100% | — / — / — | 2026-03-10 |
| flush20_both_fade | 34 | 26% | +90% | -100% | -49.5% | +192% | 15 | 1,993 | 99% | 2025-11-05 / — / — | 2026-02-17 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| flush30_down_d02 | 59.0% | 37.7% | 21.1% |
| flush30_both_d008 | 52.8% | 35.4% | 22.1% |
| flush20_both_d008 | 18.4% | 15.9% | 11.9% |
| flush15_both_d008 | 14.1% | 13.9% | 12.8% |
| flush30_both_d02 | 10.8% | 11.3% | 11.5% |
| flush20_down_d02 | 5.5% | 7.2% | 8.9% |
| flush15_both_d02 | 2.8% | 5.0% | 8.2% |
| flush20_both_d02 | 3.2% | 4.4% | 8.1% |
| flush15_down_d02 | 3.0% | 6.2% | 8.0% |
| flush20_both_fade | 0.1% | 0.7% | 3.4% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| flush30_both_d008 | 7 | 43% | 1.93% | 0.47% | 6x, 2x, 2x, 0x, 0x |
| flush30_down_d02 | 4 | 50% | 1.75% | 0.27% | 4x, 1x, 0x, 0x |
| flush30_both_d02 | 7 | 43% | 0.50% | 0.05% | 4x, 1x, 1x, 0x, 0x |
| flush15_both_d008 | 65 | 43% | 0.45% | 0.05% | 9x, 6x, 4x, 4x, 3x |
| flush20_both_d008 | 34 | 38% | 0.43% | 0.05% | 9x, 6x, 3x, 2x, 2x |
| flush20_down_d02 | 13 | 38% | 0.18% | 0.03% | 4x, 2x, 2x, 1x, 1x |
| flush20_both_d02 | 34 | 35% | 0.15% | 0.00% | 5x, 4x, 2x, 2x, 2x |
| flush15_down_d02 | 28 | 39% | 0.10% | 0.00% | 4x, 3x, 2x, 2x, 2x |
| flush15_both_d02 | 65 | 37% | 0.07% | 0.00% | 5x, 4x, 3x, 3x, 3x |
| flush20_both_fade | 34 | 26% | 0.00% | 0.00% | 3x, 3x, 2x, 2x, 2x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| flush30_both_d008 | 7 | +36.6% | 22.1% | 2 | +201.4% | 51.1% | holding up |
| flush30_down_d02 | 4 | +26.9% | 21.1% | 2 | +84.6% | 26.1% | holding up |
| flush30_both_d02 | 7 | -8.8% | 11.5% | 2 | +84.6% | 26.1% | holding up |
| flush20_down_d02 | 13 | -18.8% | 8.9% | 2 | +84.6% | 26.1% | holding up |
| flush20_both_d008 | 34 | +3.3% | 11.9% | 7 | +34.8% | 22.2% | holding up |
| flush15_both_d008 | 65 | -2.8% | 12.8% | 13 | +0.0% | 15.4% | holding up |
| flush20_both_d02 | 34 | -25.2% | 8.1% | 7 | -6.4% | 12.3% | holding up |
| flush15_both_d02 | 65 | -25.5% | 8.2% | 13 | -35.9% | 5.9% | fading |
| flush15_down_d02 | 28 | -21.8% | 8.0% | 8 | -31.5% | 5.5% | fading |
| flush20_both_fade | 34 | -49.5% | 3.4% | 7 | -78.1% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| flush30_both_d008 | 2 | -100.0% | 5 | +91.2% |
| flush30_down_d02 | 2 | -100.0% | 2 | +153.8% |
| flush20_both_d008 | 4 | -40.3% | 30 | +9.2% |
| flush15_both_d008 | 8 | -38.8% | 57 | +2.3% |
| flush30_both_d02 | 2 | -100.0% | 5 | +27.6% |
| flush20_down_d02 | 3 | -32.9% | 10 | -14.5% |
| flush15_down_d02 | 5 | -59.7% | 23 | -13.6% |
| flush20_both_d02 | 4 | -49.6% | 30 | -22.0% |
| flush15_both_d02 | 8 | -38.7% | 57 | -23.6% |
| flush20_both_fade | 4 | -60.8% | 30 | -48.0% |

Exit reasons:

- flush30_both_d008: {'time': 4, 'trail': 3}
- flush30_down_d02: {'time': 2, 'trail': 2}
- flush20_both_d008: {'time': 20, 'trail': 14}
- flush15_both_d008: {'time': 36, 'trail': 29}
- flush30_both_d02: {'time': 4, 'trail': 3}
- flush20_down_d02: {'time': 8, 'trail': 5}
- flush15_down_d02: {'time': 17, 'trail': 11}
- flush20_both_d02: {'time': 22, 'trail': 12}
- flush15_both_d02: {'time': 41, 'trail': 24}
- flush20_both_fade: {'trail': 9, 'time': 25}
