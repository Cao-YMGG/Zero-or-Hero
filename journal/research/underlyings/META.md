# Backtest — META 0DTE, 2025-10-06 → 2026-10-02 (238 days)

Model: Black-Scholes at IV 33%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 28.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gap_with | 107 | 39% | +109% | -98% | -16.6% | +154% | 6 | 500 | 99% | — / — / — | 2026-03-31 |
| open_drive_calm | 120 | 35% | +112% | -94% | -21.5% | +151% | 0 | 500 | 100% | — / — / — | 2026-08-24 |
| meta_open_calm | 120 | 35% | +112% | -94% | -21.5% | +151% | 0 | 500 | 100% | — / — / — | 2026-08-24 |
| open_drive_x4 | 120 | 18% | +313% | -97% | -22.1% | +409% | 68 | 500 | 86% | — / — / — | — |
| open_drive | 142 | 32% | +112% | -94% | -27.2% | +151% | 0 | 500 | 100% | — / — / — | 2026-08-24 |
| open_drive_run | 120 | 35% | +93% | -94% | -28.5% | +626% | 0 | 500 | 100% | — / — / — | 2026-08-24 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive_x4 | 6.3% | 7.1% | 17.7% |
| gap_with | 4.2% | 7.1% | 15.3% |
| open_drive_calm | 2.3% | 4.6% | 13.3% |
| meta_open_calm | 2.3% | 4.6% | 13.3% |
| open_drive | 1.1% | 3.5% | 11.0% |
| open_drive_run | 1.7% | 3.4% | 6.5% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_x4 | 120 | -22.1% | 17.7% | 30 | +1.5% | 23.1% | holding up |
| open_drive_calm | 120 | -21.5% | 13.3% | 30 | -8.9% | 18.1% | holding up |
| meta_open_calm | 120 | -21.5% | 13.3% | 30 | -8.9% | 18.1% | holding up |
| open_drive | 142 | -27.2% | 11.0% | 37 | -12.3% | 15.3% | holding up |
| gap_with | 107 | -16.6% | 15.3% | 25 | -20.9% | 13.6% | holding up |
| open_drive_run | 120 | -28.5% | 6.5% | 30 | -22.9% | 8.2% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gap_with | 17 | -49.1% | 90 | -10.5% |
| open_drive_calm | 0 | +0.0% | 120 | -21.5% |
| meta_open_calm | 0 | +0.0% | 120 | -21.5% |
| open_drive_x4 | 0 | +0.0% | 120 | -22.1% |
| open_drive | 22 | -57.9% | 120 | -21.5% |
| open_drive_run | 0 | +0.0% | 120 | -28.5% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- gap_with: {'time': 66, 'take_profit': 41}
- open_drive_calm: {'time': 78, 'take_profit': 42}
- meta_open_calm: {'time': 78, 'take_profit': 42}
- open_drive_x4: {'time': 99, 'take_profit': 21}
- open_drive: {'time': 96, 'take_profit': 46}
- open_drive_run: {'time': 82, 'trail': 38}
