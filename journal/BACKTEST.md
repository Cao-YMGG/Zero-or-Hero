# Backtest — SPY 0DTE, 2025-10-30 → 2026-10-29 (251 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.3% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spy_open_drive | 7 | 29% | +392% | -95% | +44.3% | +732% | 462 | 642 | 38% | — / — / — | — |
| spy_open_drive_wide | 23 | 22% | +494% | -97% | +31.7% | +1033% | 441 | 640 | 85% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| spy_open_drive | 38.8% | 29.8% | 17.1% |
| spy_open_drive_wide | 28.9% | 24.4% | 15.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| spy_open_drive | 7 | 29% | 1.60% | 0.15% | 8x, 2x, 0x, 0x, 0x |
| spy_open_drive_wide | 23 | 22% | 0.80% | 0.15% | 11x, 8x, 7x, 2x, 1x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| spy_open_drive_wide | 23 | +31.7% | 15.7% | 4 | +189.9% | 27.7% | holding up |
| spy_open_drive | 7 | +44.3% | 17.1% | 1 | -73.6% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| spy_open_drive | 0 | +0.0% | 7 | +44.3% |
| spy_open_drive_wide | 0 | +0.0% | 23 | +31.7% |

Live-only variants (no history to backtest): claude_bias, catalyst_open, catalyst_intraday

Exit reasons:

- spy_open_drive: {'time': 7}
- spy_open_drive_wide: {'time': 23}
