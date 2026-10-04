# Backtest — TSLA 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 41%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 35.4% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orb15_tp100 | 142 | 30% | +108% | -52% | -5.0% | +126% | 77 | 500 | 85% | — / — / — | — |
| gap_with | 118 | 45% | +103% | -97% | -7.2% | +144% | 5 | 500 | 99% | — / — / — | 2025-11-24 |
| open_drive_run | 124 | 35% | +136% | -95% | -15.0% | +1114% | 1 | 500 | 100% | — / — / — | 2025-11-20 |
| oil_lead | 101 | 41% | +101% | -96% | -15.7% | +135% | 90 | 500 | 82% | — / — / — | — |
| open_drive | 147 | 35% | +106% | -94% | -23.5% | +120% | 24 | 601 | 96% | — / — / — | 2025-11-20 |
| open_drive_calm | 124 | 35% | +107% | -95% | -25.2% | +120% | 24 | 601 | 96% | — / — / — | 2025-11-20 |
| open_drive_x4 | 124 | 15% | +305% | -96% | -34.8% | +336% | 56 | 500 | 89% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gap_with | 11.3% | 12.7% | 19.2% |
| oil_lead | 4.5% | 7.7% | 15.8% |
| open_drive_x4 | 2.8% | 5.5% | 15.8% |
| orb15_tp100 | 8.9% | 11.8% | 15.5% |
| open_drive | 2.1% | 4.4% | 13.1% |
| open_drive_calm | 1.8% | 3.9% | 13.1% |
| open_drive_run | 8.6% | 8.5% | 10.2% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive | 147 | -23.5% | 13.1% | 37 | -10.8% | 18.2% | holding up |
| open_drive_x4 | 124 | -34.8% | 15.8% | 30 | -28.7% | 17.8% | holding up |
| open_drive_calm | 124 | -25.2% | 13.1% | 30 | -25.4% | 12.3% | holding up |
| orb15_tp100 | 142 | -5.0% | 15.5% | 35 | -10.2% | 11.4% | fading |
| oil_lead | 101 | -15.7% | 15.8% | 28 | -28.7% | 10.0% | fading |
| gap_with | 118 | -7.2% | 19.2% | 28 | -32.6% | 9.8% | fading |
| open_drive_run | 124 | -15.0% | 10.2% | 30 | -27.8% | 8.6% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| orb15_tp100 | 22 | -16.2% | 120 | -3.0% |
| gap_with | 14 | +16.7% | 104 | -10.4% |
| open_drive_run | 0 | +0.0% | 124 | -15.0% |
| oil_lead | 17 | -49.4% | 84 | -8.9% |
| open_drive | 23 | -14.0% | 124 | -25.2% |
| open_drive_calm | 0 | +0.0% | 124 | -25.2% |
| open_drive_x4 | 0 | +0.0% | 124 | -34.8% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- orb15_tp100: {'stop_loss': 99, 'take_profit': 42, 'time': 1}
- gap_with: {'time': 68, 'take_profit': 50}
- open_drive_run: {'time': 89, 'trail': 35}
- oil_lead: {'time': 64, 'take_profit': 37}
- open_drive: {'time': 96, 'take_profit': 51}
- open_drive_calm: {'time': 82, 'take_profit': 42}
- open_drive_x4: {'time': 106, 'take_profit': 18}
