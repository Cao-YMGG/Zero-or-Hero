# Backtest — MU 0DTE, 2025-10-06 → 2026-10-02 (246 days)

Model: Black-Scholes at IV 68%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 58.9% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orb15_tp100 | 134 | 25% | +106% | -52% | -13.2% | +143% | 120 | 500 | 76% | — / — / — | — |
| open_drive_run | 122 | 32% | +110% | -96% | -30.2% | +426% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| open_drive_calm | 122 | 32% | +109% | -96% | -30.7% | +130% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| open_drive | 145 | 31% | +108% | -95% | -32.1% | +130% | 1 | 500 | 100% | — / — / — | 2025-10-07 |
| gap_with | 136 | 29% | +109% | -96% | -36.1% | +137% | 83 | 991 | 92% | — / — / — | — |
| open_drive_x4 | 122 | 15% | +287% | -97% | -40.0% | +368% | 9 | 500 | 98% | — / — / — | 2025-10-07 |
| oil_lead | 101 | 21% | +110% | -94% | -51.3% | +127% | 76 | 1,969 | 96% | 2025-10-06 / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive_x4 | 2.6% | 4.5% | 13.4% |
| open_drive_calm | 1.0% | 2.8% | 9.9% |
| orb15_tp100 | 1.7% | 4.1% | 9.8% |
| gap_with | 0.6% | 1.8% | 8.6% |
| open_drive | 0.8% | 2.2% | 8.5% |
| open_drive_run | 2.5% | 4.6% | 7.5% |
| oil_lead | 0.1% | 0.5% | 4.5% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_x4 | 122 | -40.0% | 13.4% | 30 | -47.1% | 10.5% | fading |
| open_drive_run | 122 | -30.2% | 7.5% | 30 | -25.5% | 10.3% | holding up |
| orb15_tp100 | 134 | -13.2% | 9.8% | 33 | -10.3% | 9.8% | holding up |
| open_drive_calm | 122 | -30.7% | 9.9% | 30 | -32.9% | 9.6% | holding up |
| open_drive | 145 | -32.1% | 8.5% | 37 | -33.0% | 8.4% | holding up |
| gap_with | 136 | -36.1% | 8.6% | 35 | -65.5% | 2.1% | broken |
| oil_lead | 101 | -51.3% | 4.5% | 28 | -69.3% | 1.0% | broken |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| orb15_tp100 | 21 | -20.4% | 113 | -11.8% |
| open_drive_run | 0 | +0.0% | 122 | -30.2% |
| open_drive_calm | 0 | +0.0% | 122 | -30.7% |
| open_drive | 23 | -39.2% | 122 | -30.7% |
| gap_with | 22 | -22.5% | 114 | -38.7% |
| open_drive_x4 | 0 | +0.0% | 122 | -40.0% |
| oil_lead | 17 | -42.7% | 84 | -53.0% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- orb15_tp100: {'stop_loss': 99, 'take_profit': 31, 'time': 4}
- open_drive_run: {'time': 87, 'trail': 35}
- open_drive_calm: {'time': 85, 'take_profit': 37}
- open_drive: {'time': 103, 'take_profit': 42}
- gap_with: {'take_profit': 39, 'time': 97}
- open_drive_x4: {'time': 106, 'take_profit': 16}
- oil_lead: {'take_profit': 21, 'time': 80}
