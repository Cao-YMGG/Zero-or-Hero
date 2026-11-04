# Backtest — SPY 0DTE, 2025-11-05 → 2026-11-04 (251 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.3% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spy_open_drive_wide | 23 | 22% | +494% | -97% | +31.7% | +1033% | 376 | 621 | 82% | — / — / — | — |
| spy_open_drive | 8 | 25% | +392% | -96% | +26.3% | +732% | 416 | 642 | 38% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| spy_open_drive_wide | 27.5% | 23.6% | 13.6% |
| spy_open_drive | 27.4% | 24.4% | 15.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| spy_open_drive | 8 | 25% | 1.12% | 0.12% | 8x, 2x, 0x, 0x, 0x |
| spy_open_drive_wide | 23 | 22% | 0.62% | 0.05% | 11x, 8x, 7x, 2x, 1x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| spy_open_drive_wide | 23 | +31.7% | 13.6% | 3 | -100.0% | 0.0% | broken |
| spy_open_drive | 8 | +26.3% | 15.7% | 1 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| spy_open_drive_wide | 0 | +0.0% | 23 | +31.7% |
| spy_open_drive | 0 | +0.0% | 8 | +26.3% |

Live-only variants (no history to backtest): claude_bias, catalyst_open, catalyst_open_hero, catalyst_intraday, catalyst_intraday_hero

Exit reasons:

- spy_open_drive_wide: {'time': 23}
- spy_open_drive: {'time': 8}
