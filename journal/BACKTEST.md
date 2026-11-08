# Backtest — SPY 0DTE, 2025-11-10 → 2026-11-06 (250 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spy_open_drive_put | 8 | 75% | +245% | -100% | +159.0% | +463% | 3,440 | 3,440 | 17% | 2026-02-03 / 2026-11-05 / — | — |
| spy_open_drive | 8 | 25% | +392% | -96% | +26.3% | +732% | 416 | 642 | 38% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| spy_open_drive_put | 100.0% | 98.1% | 61.7% |
| spy_open_drive | 27.4% | 24.4% | 15.7% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| spy_open_drive_put | 8 | 75% | 27.30% | 15.57% | 6x, 5x, 3x, 3x, 2x |
| spy_open_drive | 8 | 25% | 1.12% | 0.12% | 8x, 2x, 0x, 0x, 0x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| spy_open_drive_put | 8 | +159.0% | 61.7% | 2 | +164.6% | 48.9% | fading |
| spy_open_drive | 8 | +26.3% | 15.7% | 1 | -100.0% | 0.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| spy_open_drive_put | 0 | +0.0% | 8 | +159.0% |
| spy_open_drive | 0 | +0.0% | 8 | +26.3% |

Live-only variants (no history to backtest): claude_bias, catalyst_open, catalyst_open_hero, catalyst_intraday, catalyst_intraday_hero

Exit reasons:

- spy_open_drive_put: {'trail': 6, 'time': 2}
- spy_open_drive: {'time': 8}
