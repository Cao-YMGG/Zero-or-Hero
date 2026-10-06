# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-05 (251 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.5% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| open_drive_run | 177 | 38% | +98% | -92% | -18.7% | +805% | 9 | 500 | 98% | — / — / — | 2025-12-10 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive_run | 4.5% | 7.0% | 8.5% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| open_drive_run | 177 | 38% | 0.30% | 0.03% | 9x, 8x, 5x, 4x, 4x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_run | 177 | -18.7% | 8.5% | 40 | -14.7% | 9.7% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| open_drive_run | 0 | +0.0% | 177 | -18.7% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper, catalyst_open, catalyst_intraday

Exit reasons:

- open_drive_run: {'time': 118, 'trail': 59}
