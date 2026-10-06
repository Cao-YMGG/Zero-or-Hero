# Backtest — MU 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 66%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 57.5% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flush20_both_fade | 49 | 35% | +140% | -98% | -15.1% | +784% | 46 | 500 | 91% | — / — / — | 2025-12-23 |
| flush15_down_d02 | 39 | 31% | +123% | -100% | -31.3% | +414% | 112 | 662 | 83% | — / — / — | — |
| flush15_both_d008 | 76 | 26% | +116% | -98% | -41.7% | +362% | 32 | 704 | 95% | — / — / — | 2025-12-09 |
| flush30_both_d02 | 18 | 33% | +73% | -99% | -41.9% | +188% | 229 | 906 | 80% | — / — / — | — |
| flush20_down_d02 | 24 | 25% | +129% | -100% | -42.5% | +414% | 84 | 558 | 85% | — / — / — | — |
| flush30_both_d008 | 18 | 33% | +71% | -100% | -43.2% | +148% | 54 | 606 | 91% | — / — / — | — |
| flush20_both_d008 | 49 | 22% | +143% | -97% | -43.3% | +687% | 10 | 500 | 98% | — / — / — | 2025-12-23 |
| flush15_both_d02 | 76 | 25% | +89% | -100% | -52.6% | +210% | 60 | 612 | 90% | — / — / — | — |
| flush20_both_d02 | 49 | 20% | +114% | -100% | -56.2% | +414% | 80 | 520 | 85% | — / — / — | — |
| flush30_down_d02 | 9 | 22% | +38% | -99% | -68.7% | +52% | 148 | 500 | 70% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| flush20_both_fade | 8.1% | 9.8% | 9.9% |
| flush15_down_d02 | 2.5% | 4.5% | 7.1% |
| flush15_both_d008 | 1.1% | 2.7% | 5.9% |
| flush20_down_d02 | 1.4% | 1.9% | 5.8% |
| flush20_both_d008 | 1.8% | 3.9% | 5.5% |
| flush30_both_d02 | 0.2% | 1.0% | 3.8% |
| flush20_both_d02 | 0.4% | 1.0% | 3.7% |
| flush30_both_d008 | 0.1% | 0.7% | 3.1% |
| flush15_both_d02 | 0.2% | 0.9% | 2.8% |
| flush30_down_d02 | 0.0% | 0.0% | 0.1% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| flush20_both_fade | 49 | 35% | 0.27% | 0.03% | 9x, 5x, 3x, 3x, 3x |
| flush15_down_d02 | 39 | 31% | 0.12% | 0.00% | 5x, 3x, 3x, 3x, 2x |
| flush15_both_d008 | 76 | 26% | 0.03% | 0.00% | 5x, 5x, 3x, 3x, 3x |
| flush20_both_d008 | 49 | 22% | 0.03% | 0.00% | 8x, 5x, 2x, 2x, 2x |
| flush20_both_d02 | 49 | 20% | 0.03% | 0.00% | 5x, 3x, 3x, 2x, 2x |
| flush30_both_d02 | 18 | 33% | 0.00% | 0.00% | 3x, 2x, 2x, 1x, 1x |
| flush20_down_d02 | 24 | 25% | 0.00% | 0.00% | 5x, 3x, 2x, 1x, 1x |
| flush30_both_d008 | 18 | 33% | 0.00% | 0.00% | 2x, 2x, 2x, 2x, 1x |
| flush15_both_d02 | 76 | 25% | 0.00% | 0.00% | 3x, 3x, 3x, 3x, 2x |
| flush30_down_d02 | 9 | 22% | 0.00% | 0.00% | 2x, 1x, 0x, 0x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| flush20_down_d02 | 24 | -42.5% | 5.8% | 6 | +62.2% | 32.4% | holding up |
| flush20_both_d008 | 49 | -43.3% | 5.5% | 9 | +56.1% | 26.1% | holding up |
| flush15_down_d02 | 39 | -31.3% | 7.1% | 8 | +21.7% | 21.6% | holding up |
| flush20_both_d02 | 49 | -56.2% | 3.7% | 9 | +8.2% | 18.5% | holding up |
| flush20_both_fade | 49 | -15.1% | 9.9% | 9 | -18.0% | 14.1% | holding up |
| flush15_both_d008 | 76 | -41.7% | 5.9% | 15 | -50.0% | 8.3% | holding up |
| flush15_both_d02 | 76 | -52.6% | 2.8% | 15 | -61.7% | 1.8% | fading |
| flush30_both_d02 | 18 | -41.9% | 3.8% | 1 | -100.0% | 0.0% | broken |
| flush30_both_d008 | 18 | -43.2% | 3.1% | 1 | -100.0% | 0.0% | broken |
| flush30_down_d02 | 9 | -68.7% | 0.1% | 0 | +0.0% | 0.0% | no recent trades |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| flush20_both_fade | 7 | -39.7% | 42 | -11.0% |
| flush15_down_d02 | 5 | -69.5% | 34 | -25.7% |
| flush15_both_d008 | 10 | -34.5% | 66 | -42.8% |
| flush30_both_d02 | 3 | +16.4% | 15 | -53.5% |
| flush20_down_d02 | 3 | -49.4% | 21 | -41.5% |
| flush30_both_d008 | 3 | +37.6% | 15 | -59.3% |
| flush20_both_d008 | 7 | -26.3% | 42 | -46.1% |
| flush15_both_d02 | 10 | -53.0% | 66 | -52.6% |
| flush20_both_d02 | 7 | -49.9% | 42 | -57.2% |
| flush30_down_d02 | 1 | +51.7% | 8 | -83.7% |

Exit reasons:

- flush20_both_fade: {'time': 32, 'trail': 17}
- flush15_down_d02: {'trail': 12, 'time': 27}
- flush15_both_d008: {'time': 55, 'trail': 21}
- flush30_both_d02: {'time': 13, 'trail': 5}
- flush20_down_d02: {'trail': 6, 'time': 18}
- flush30_both_d008: {'trail': 6, 'time': 12}
- flush20_both_d008: {'time': 37, 'trail': 12}
- flush15_both_d02: {'time': 58, 'trail': 18}
- flush20_both_d02: {'time': 40, 'trail': 9}
- flush30_down_d02: {'time': 7, 'trail': 2}
