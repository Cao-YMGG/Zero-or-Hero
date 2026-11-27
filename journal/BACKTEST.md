# Backtest — SPY 0DTE, 2025-11-28 → 2026-11-27 (251 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spy_open_drive_put | 8 | 75% | +233% | -100% | +149.5% | +630% | 2,607 | 2,607 | 25% | 2026-02-04 / 2026-11-05 / — | — |
| spy_open_drive | 10 | 50% | +203% | -90% | +56.3% | +420% | 1,058 | 1,318 | 33% | 2026-04-02 / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| spy_open_drive_put | 100.0% | 97.9% | 58.4% |
| spy_open_drive | 87.5% | 62.6% | 31.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| spy_open_drive_put | 8 | 75% | 25.75% | 14.50% | 7x, 3x, 3x, 2x, 2x |
| spy_open_drive | 10 | 50% | 4.72% | 1.32% | 5x, 4x, 3x, 2x, 1x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| spy_open_drive_put | 8 | +149.5% | 58.4% | 2 | +264.8% | 48.9% | holding up |
| spy_open_drive | 10 | +56.3% | 31.7% | 3 | +22.7% | 10.9% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| spy_open_drive_put | 0 | +0.0% | 8 | +149.5% |
| spy_open_drive | 0 | +0.0% | 10 | +56.3% |

Live-only variants (no history to backtest): claude_bias, catalyst_open, catalyst_open_hero, catalyst_intraday, catalyst_intraday_hero

Exit reasons:

- spy_open_drive_put: {'trail': 5, 'time': 3}
- spy_open_drive: {'time': 10}
