# Backtest — META 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 32%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 28.0% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flush30_both_d008 | 1 | 100% | +174% | +0% | +174.5% | +174% | 884 | 884 | 0% | — / — / — | — |
| flush30_both_d02 | 1 | 100% | +164% | +0% | +164.2% | +164% | 713 | 713 | 0% | — / — / — | — |
| flush30_down_d02 | 1 | 100% | +164% | +0% | +164.2% | +164% | 713 | 713 | 0% | — / — / — | — |
| flush20_down_d02 | 5 | 40% | +175% | -100% | +10.1% | +186% | 434 | 1,045 | 58% | 2026-08-26 / — / — | — |
| flush20_both_d008 | 9 | 44% | +123% | -100% | -0.8% | +286% | 99 | 524 | 81% | — / — / — | — |
| flush20_both_d02 | 9 | 44% | +117% | -100% | -3.6% | +186% | 240 | 1,103 | 78% | 2026-08-26 / — / — | — |
| flush15_both_d008 | 18 | 50% | +89% | -100% | -5.5% | +286% | 28 | 637 | 96% | — / — / — | 2026-09-28 |
| flush15_down_d02 | 10 | 50% | +89% | -100% | -5.7% | +186% | 102 | 500 | 80% | — / — / — | — |
| flush15_both_d02 | 18 | 50% | +76% | -100% | -11.9% | +186% | 28 | 562 | 95% | — / — / — | 2026-06-09 |
| flush20_both_fade | 9 | 44% | +75% | -100% | -22.1% | +130% | 25 | 500 | 95% | — / — / — | 2026-08-03 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| flush30_both_d008 | 100.0% | 100.0% | 100.0% |
| flush30_both_d02 | 100.0% | 100.0% | 100.0% |
| flush30_down_d02 | 100.0% | 100.0% | 100.0% |
| flush20_down_d02 | 32.2% | 24.2% | 16.5% |
| flush20_both_d008 | 18.7% | 16.9% | 13.6% |
| flush20_both_d02 | 15.6% | 15.8% | 14.9% |
| flush15_both_d008 | 11.8% | 13.9% | 13.9% |
| flush15_down_d02 | 11.5% | 13.1% | 13.3% |
| flush15_both_d02 | 5.7% | 9.1% | 12.7% |
| flush20_both_fade | 1.6% | 3.9% | 8.6% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| flush30_both_d008 | 1 | 100% | 100.00% | 100.00% | 3x |
| flush30_both_d02 | 1 | 100% | 100.00% | 100.00% | 3x |
| flush30_down_d02 | 1 | 100% | 100.00% | 100.00% | 3x |
| flush20_down_d02 | 5 | 40% | 0.95% | 0.20% | 3x, 3x, 0x, 0x, 0x |
| flush20_both_d008 | 9 | 44% | 0.60% | 0.07% | 4x, 3x, 1x, 1x, 0x |
| flush20_both_d02 | 9 | 44% | 0.55% | 0.07% | 3x, 3x, 2x, 1x, 0x |
| flush15_both_d008 | 18 | 50% | 0.43% | 0.07% | 4x, 3x, 2x, 2x, 1x |
| flush15_both_d02 | 18 | 50% | 0.27% | 0.05% | 3x, 3x, 2x, 2x, 1x |
| flush15_down_d02 | 10 | 50% | 0.47% | 0.03% | 3x, 3x, 1x, 1x, 1x |
| flush20_both_fade | 9 | 44% | 0.07% | 0.00% | 2x, 2x, 2x, 1x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| flush30_both_d008 | 1 | +174.5% | 100.0% | 1 | +174.5% | 100.0% | holding up |
| flush30_both_d02 | 1 | +164.2% | 100.0% | 1 | +164.2% | 100.0% | holding up |
| flush30_down_d02 | 1 | +164.2% | 100.0% | 1 | +164.2% | 100.0% | holding up |
| flush20_both_fade | 9 | -22.1% | 8.6% | 7 | +0.1% | 19.0% | holding up |
| flush15_down_d02 | 10 | -5.7% | 13.3% | 4 | -1.3% | 15.2% | holding up |
| flush20_down_d02 | 5 | +10.1% | 16.5% | 3 | -11.9% | 11.5% | fading |
| flush20_both_d02 | 9 | -3.6% | 14.9% | 7 | -17.0% | 10.9% | fading |
| flush15_both_d02 | 18 | -11.9% | 12.7% | 9 | -20.9% | 9.4% | fading |
| flush15_both_d008 | 18 | -5.5% | 13.9% | 9 | -27.2% | 7.3% | fading |
| flush20_both_d008 | 9 | -0.8% | 13.6% | 7 | -27.6% | 5.3% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| flush30_both_d008 | 0 | +0.0% | 1 | +174.5% |
| flush30_both_d02 | 0 | +0.0% | 1 | +164.2% |
| flush30_down_d02 | 0 | +0.0% | 1 | +164.2% |
| flush20_down_d02 | 0 | +0.0% | 5 | +10.1% |
| flush20_both_d008 | 0 | +0.0% | 9 | -0.8% |
| flush20_both_d02 | 0 | +0.0% | 9 | -3.6% |
| flush15_both_d008 | 4 | -8.2% | 14 | -4.8% |
| flush15_down_d02 | 2 | -39.5% | 8 | +2.8% |
| flush15_both_d02 | 4 | -24.2% | 14 | -8.4% |
| flush20_both_fade | 0 | +0.0% | 9 | -22.1% |

Exit reasons:

- flush30_both_d008: {'trail': 1}
- flush30_both_d02: {'trail': 1}
- flush30_down_d02: {'trail': 1}
- flush20_down_d02: {'time': 3, 'trail': 2}
- flush20_both_d008: {'time': 5, 'trail': 4}
- flush20_both_d02: {'time': 5, 'trail': 4}
- flush15_both_d008: {'trail': 9, 'time': 9}
- flush15_down_d02: {'time': 5, 'trail': 5}
- flush15_both_d02: {'trail': 9, 'time': 9}
- flush20_both_fade: {'time': 5, 'trail': 4}
