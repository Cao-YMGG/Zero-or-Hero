# Backtest — MU 0DTE, 2025-10-06 → 2026-10-02 (246 days)

Model: Black-Scholes at IV 68%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 58.9% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| open_drive_run | 122 | 32% | +112% | -97% | -30.0% | +426% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| open_drive_calm | 122 | 32% | +108% | -97% | -31.1% | +130% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| open_drive | 145 | 31% | +107% | -95% | -32.5% | +130% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| gap_with | 136 | 29% | +109% | -97% | -36.6% | +137% | 83 | 991 | 92% | — / — / — | — |
| open_drive_x4 | 122 | 15% | +320% | -99% | -37.0% | +368% | 9 | 500 | 98% | — / — / — | 2025-10-07 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive_x4 | 3.3% | 4.6% | 14.8% |
| open_drive_calm | 1.0% | 2.8% | 9.8% |
| open_drive | 0.8% | 2.2% | 8.5% |
| gap_with | 0.3% | 1.9% | 8.5% |
| open_drive_run | 2.9% | 4.3% | 7.5% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_x4 | 122 | -37.0% | 14.8% | 30 | -56.2% | 10.4% | fading |
| open_drive_run | 122 | -30.0% | 7.5% | 30 | -25.9% | 10.3% | holding up |
| open_drive_calm | 122 | -31.1% | 9.8% | 30 | -34.2% | 9.4% | holding up |
| open_drive | 145 | -32.5% | 8.5% | 37 | -34.6% | 8.5% | holding up |
| gap_with | 136 | -36.6% | 8.5% | 35 | -66.3% | 2.1% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| open_drive_run | 0 | +0.0% | 122 | -30.0% |
| open_drive_calm | 0 | +0.0% | 122 | -31.1% |
| open_drive | 23 | -39.8% | 122 | -31.1% |
| gap_with | 22 | -23.3% | 114 | -39.2% |
| open_drive_x4 | 0 | +0.0% | 122 | -37.0% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- open_drive_run: {'time': 87, 'trail': 35}
- open_drive_calm: {'time': 85, 'take_profit': 37}
- open_drive: {'time': 103, 'take_profit': 42}
- gap_with: {'take_profit': 39, 'time': 97}
- open_drive_x4: {'time': 104, 'take_profit': 18}
