# Backtest — NVDA 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 34%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 29.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| flush20_both_d008 | 5 | 40% | +241% | -100% | +36.4% | +390% | 292 | 715 | 73% | — / — / — | — |
| flush20_down_d02 | 4 | 50% | +111% | -100% | +5.5% | +203% | 275 | 545 | 68% | — / — / — | — |
| flush30_both_d02 | 0 | 0% | +0% | +0% | +0.0% | +0% | 500 | 500 | 0% | — / — / — | — |
| flush30_down_d02 | 0 | 0% | +0% | +0% | +0.0% | +0% | 500 | 500 | 0% | — / — / — | — |
| flush30_both_d008 | 0 | 0% | +0% | +0% | +0.0% | +0% | 500 | 500 | 0% | — / — / — | — |
| flush20_both_fade | 5 | 60% | +52% | -100% | -8.6% | +75% | 270 | 836 | 72% | — / — / — | — |
| flush15_down_d02 | 6 | 50% | +76% | -100% | -11.8% | +203% | 233 | 563 | 77% | — / — / — | — |
| flush20_both_d02 | 5 | 40% | +111% | -100% | -15.6% | +203% | 176 | 545 | 68% | — / — / — | — |
| flush15_both_d008 | 14 | 21% | +178% | -100% | -40.4% | +390% | 49 | 623 | 92% | — / — / — | 2026-02-17 |
| flush15_both_d02 | 14 | 29% | +87% | -100% | -46.6% | +203% | 19 | 869 | 98% | — / — / — | 2026-04-27 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| flush20_both_d008 | 54.1% | 36.9% | 25.3% |
| flush20_down_d02 | 26.6% | 24.2% | 14.1% |
| flush20_both_fade | 5.9% | 9.7% | 14.4% |
| flush15_down_d02 | 7.2% | 11.3% | 9.5% |
| flush20_both_d02 | 6.4% | 10.5% | 8.4% |
| flush15_both_d008 | 2.2% | 3.9% | 8.2% |
| flush15_both_d02 | 0.4% | 1.4% | 3.4% |
| flush30_both_d02 | 0.0% | 0.0% | 0.0% |
| flush30_down_d02 | 0.0% | 0.0% | 0.0% |
| flush30_both_d008 | 0.0% | 0.0% | 0.0% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| flush20_both_d008 | 5 | 40% | 1.85% | 0.33% | 5x, 2x, 0x, 0x, 0x |
| flush20_down_d02 | 4 | 50% | 1.05% | 0.15% | 3x, 1x, 0x, 0x |
| flush15_down_d02 | 6 | 50% | 0.35% | 0.05% | 3x, 1x, 1x, 0x, 0x |
| flush20_both_d02 | 5 | 40% | 0.30% | 0.03% | 3x, 1x, 0x, 0x, 0x |
| flush20_both_fade | 5 | 60% | 0.40% | 0.00% | 2x, 1x, 1x, 0x, 0x |
| flush15_both_d008 | 14 | 21% | 0.10% | 0.00% | 5x, 2x, 2x, 0x, 0x |
| flush30_both_d02 | 0 | 0% | 0.00% | 0.00% |  |
| flush30_down_d02 | 0 | 0% | 0.00% | 0.00% |  |
| flush30_both_d008 | 0 | 0% | 0.00% | 0.00% |  |
| flush15_both_d02 | 14 | 29% | 0.00% | 0.00% | 3x, 2x, 1x, 1x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| flush20_down_d02 | 4 | +5.5% | 14.1% | 1 | +203.1% | 100.0% | holding up |
| flush15_down_d02 | 6 | -11.8% | 9.5% | 1 | +203.1% | 100.0% | holding up |
| flush20_both_d008 | 5 | +36.4% | 25.3% | 2 | +144.9% | 51.1% | holding up |
| flush15_both_d008 | 14 | -40.4% | 8.2% | 3 | +63.2% | 33.0% | holding up |
| flush20_both_d02 | 5 | -15.6% | 8.4% | 2 | +51.6% | 26.1% | holding up |
| flush15_both_d02 | 14 | -46.6% | 3.4% | 3 | +1.0% | 10.9% | holding up |
| flush20_both_fade | 5 | -8.6% | 14.4% | 2 | -33.9% | 2.8% | broken |
| flush30_both_d02 | 0 | +0.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |
| flush30_down_d02 | 0 | +0.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |
| flush30_both_d008 | 0 | +0.0% | 0.0% | 0 | +0.0% | 0.0% | no recent trades |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| flush20_both_d008 | 1 | -100.0% | 4 | +70.5% |
| flush20_down_d02 | 1 | -100.0% | 3 | +40.7% |
| flush30_both_d02 | 0 | +0.0% | 0 | +0.0% |
| flush30_down_d02 | 0 | +0.0% | 0 | +0.0% |
| flush30_both_d008 | 0 | +0.0% | 0 | +0.0% |
| flush20_both_fade | 1 | +75.2% | 4 | -29.6% |
| flush15_down_d02 | 1 | -100.0% | 5 | +5.9% |
| flush20_both_d02 | 1 | -100.0% | 4 | +5.5% |
| flush15_both_d008 | 3 | -49.3% | 11 | -38.0% |
| flush15_both_d02 | 3 | -27.2% | 11 | -51.9% |

Exit reasons:

- flush20_both_d008: {'trail': 2, 'time': 3}
- flush20_down_d02: {'trail': 2, 'time': 2}
- flush30_both_d02: {}
- flush30_down_d02: {}
- flush30_both_d008: {}
- flush20_both_fade: {'trail': 3, 'time': 2}
- flush15_down_d02: {'time': 4, 'trail': 2}
- flush20_both_d02: {'trail': 2, 'time': 3}
- flush15_both_d008: {'trail': 3, 'time': 11}
- flush15_both_d02: {'trail': 3, 'time': 11}
