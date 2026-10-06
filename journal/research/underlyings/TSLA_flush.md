# Backtest — TSLA 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 40%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 35.1% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flush15_both_d02 | 24 | 42% | +162% | -97% | +10.9% | +501% | 11 | 888 | 99% | — / — / — | 2026-05-21 |
| flush15_down_d02 | 9 | 22% | +260% | -100% | -19.9% | +497% | 11 | 500 | 98% | — / — / — | 2026-01-05 |
| flush15_both_d008 | 24 | 38% | +110% | -100% | -21.1% | +243% | 39 | 500 | 92% | — / — / — | 2026-02-03 |
| flush20_both_fade | 9 | 33% | +102% | -100% | -32.7% | +222% | 45 | 689 | 93% | — / — / — | 2026-09-15 |
| flush20_both_d02 | 9 | 22% | +64% | -100% | -63.5% | +116% | 28 | 500 | 94% | — / — / — | 2025-11-25 |
| flush20_both_d008 | 9 | 22% | +37% | -100% | -69.5% | +48% | 33 | 500 | 93% | — / — / — | 2026-09-03 |
| flush20_down_d02 | 4 | 0% | +0% | -100% | -99.8% | -99% | 47 | 500 | 91% | — / — / — | 2026-08-25 |
| flush30_both_d02 | 1 | 0% | +0% | -100% | -100.0% | -100% | 371 | 500 | 26% | — / — / — | — |
| flush30_down_d02 | 1 | 0% | +0% | -100% | -100.0% | -100% | 371 | 500 | 26% | — / — / — | — |
| flush30_both_d008 | 1 | 0% | +0% | -100% | -100.0% | -100% | 282 | 500 | 44% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| flush15_both_d02 | 27.6% | 21.6% | 17.3% |
| flush15_down_d02 | 8.5% | 7.0% | 12.6% |
| flush15_both_d008 | 3.9% | 6.5% | 9.0% |
| flush20_both_fade | 1.4% | 3.1% | 6.9% |
| flush20_both_d02 | 0.0% | 0.1% | 1.5% |
| flush20_both_d008 | 0.0% | 0.0% | 0.1% |
| flush20_down_d02 | 0.0% | 0.0% | 0.0% |
| flush30_both_d02 | 0.0% | 0.0% | 0.0% |
| flush30_down_d02 | 0.0% | 0.0% | 0.0% |
| flush30_both_d008 | 0.0% | 0.0% | 0.0% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| flush15_both_d02 | 24 | 42% | 0.78% | 0.18% | 6x, 6x, 3x, 2x, 2x |
| flush15_both_d008 | 24 | 38% | 0.15% | 0.03% | 3x, 3x, 2x, 2x, 2x |
| flush20_both_fade | 9 | 33% | 0.05% | 0.03% | 3x, 1x, 1x, 0x, 0x |
| flush15_down_d02 | 9 | 22% | 0.10% | 0.00% | 6x, 1x, 0x, 0x, 0x |
| flush20_both_d02 | 9 | 22% | 0.00% | 0.00% | 2x, 1x, 0x, 0x, 0x |
| flush20_both_d008 | 9 | 22% | 0.00% | 0.00% | 1x, 1x, 0x, 0x, 0x |
| flush20_down_d02 | 4 | 0% | 0.00% | 0.00% | 0x, 0x, 0x, 0x |
| flush30_both_d02 | 1 | 0% | 0.00% | 0.00% | 0x |
| flush30_down_d02 | 1 | 0% | 0.00% | 0.00% | 0x |
| flush30_both_d008 | 1 | 0% | 0.00% | 0.00% | 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| flush15_both_d008 | 24 | -21.1% | 9.0% | 8 | -7.8% | 11.2% | holding up |
| flush15_both_d02 | 24 | +10.9% | 17.3% | 8 | -24.2% | 10.1% | fading |
| flush20_both_fade | 9 | -32.7% | 6.9% | 3 | -52.3% | 1.4% | broken |
| flush15_down_d02 | 9 | -19.9% | 12.6% | 3 | -100.0% | 0.0% | broken |
| flush20_both_d02 | 9 | -63.5% | 1.5% | 3 | -100.0% | 0.0% | broken |
| flush20_both_d008 | 9 | -69.5% | 0.1% | 3 | -100.0% | 0.0% | broken |
| flush20_down_d02 | 4 | -99.8% | 0.0% | 2 | -100.0% | 0.0% | holding up |
| flush30_both_d02 | 1 | -100.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |
| flush30_down_d02 | 1 | -100.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |
| flush30_both_d008 | 1 | -100.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| flush15_both_d02 | 1 | +119.8% | 23 | +6.1% |
| flush15_down_d02 | 0 | +0.0% | 9 | -19.9% |
| flush15_both_d008 | 1 | +174.3% | 23 | -29.6% |
| flush20_both_fade | 0 | +0.0% | 9 | -32.7% |
| flush20_both_d02 | 0 | +0.0% | 9 | -63.5% |
| flush20_both_d008 | 0 | +0.0% | 9 | -69.5% |
| flush20_down_d02 | 0 | +0.0% | 4 | -99.8% |
| flush30_both_d02 | 0 | +0.0% | 1 | -100.0% |
| flush30_down_d02 | 0 | +0.0% | 1 | -100.0% |
| flush30_both_d008 | 0 | +0.0% | 1 | -100.0% |

Exit reasons:

- flush15_both_d02: {'time': 14, 'trail': 10}
- flush15_down_d02: {'time': 7, 'trail': 2}
- flush15_both_d008: {'time': 15, 'trail': 9}
- flush20_both_fade: {'time': 6, 'trail': 3}
- flush20_both_d02: {'time': 7, 'trail': 2}
- flush20_both_d008: {'time': 7, 'trail': 2}
- flush20_down_d02: {'time': 4}
- flush30_both_d02: {'time': 1}
- flush30_down_d02: {'time': 1}
- flush30_both_d008: {'time': 1}
