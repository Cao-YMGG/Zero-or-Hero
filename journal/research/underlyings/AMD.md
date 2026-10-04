# Backtest — AMD 0DTE, 2025-10-06 → 2026-10-02 (247 days)

Model: Black-Scholes at IV 56%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 49.0% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| amd_gap_rebound | 18 | 56% | +139% | -89% | +38.0% | +604% | 88 | 578 | 85% | — / — / — | — |
| gap_with | 125 | 36% | +113% | -96% | -20.6% | +140% | 54 | 957 | 94% | — / — / — | — |
| open_drive_calm | 123 | 33% | +113% | -95% | -25.6% | +155% | 69 | 4,354 | 98% | 2025-10-06 / 2025-10-27 / — | — |
| amd_open_calm | 123 | 33% | +113% | -95% | -25.6% | +155% | 69 | 4,354 | 98% | 2025-10-06 / 2025-10-27 / — | — |
| open_drive_run | 123 | 33% | +112% | -95% | -25.9% | +363% | 78 | 3,399 | 98% | 2025-10-06 / 2025-10-10 / — | — |
| open_drive_x4 | 123 | 17% | +318% | -98% | -27.2% | +364% | 17 | 8,023 | 100% | 2025-10-06 / 2025-10-08 / 2025-12-17 | 2026-03-03 |
| open_drive | 146 | 33% | +112% | -95% | -27.2% | +155% | 60 | 2,415 | 98% | 2025-10-06 / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| amd_gap_rebound | 76.2% | 52.5% | 25.8% |
| open_drive_x4 | 5.2% | 6.5% | 17.2% |
| gap_with | 3.1% | 5.3% | 12.3% |
| open_drive_calm | 1.8% | 4.2% | 11.6% |
| amd_open_calm | 1.8% | 4.2% | 11.6% |
| open_drive | 1.3% | 3.7% | 11.2% |
| open_drive_run | 2.6% | 5.3% | 8.8% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| amd_gap_rebound | 18 | +38.0% | 25.8% | 7 | +101.3% | 38.1% | holding up |
| open_drive_x4 | 123 | -27.2% | 17.2% | 30 | -15.0% | 20.3% | holding up |
| open_drive_calm | 123 | -25.6% | 11.6% | 30 | -14.1% | 16.6% | holding up |
| amd_open_calm | 123 | -25.6% | 11.6% | 30 | -14.1% | 16.6% | holding up |
| open_drive_run | 123 | -25.9% | 8.8% | 30 | -12.0% | 14.0% | holding up |
| open_drive | 146 | -27.2% | 11.2% | 37 | -18.8% | 13.6% | holding up |
| gap_with | 125 | -20.6% | 12.3% | 32 | -32.0% | 9.4% | fading |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| amd_gap_rebound | 0 | +0.0% | 18 | +38.0% |
| gap_with | 21 | -17.2% | 104 | -21.3% |
| open_drive_calm | 0 | +0.0% | 123 | -25.6% |
| amd_open_calm | 0 | +0.0% | 123 | -25.6% |
| open_drive_run | 0 | +0.0% | 123 | -25.9% |
| open_drive_x4 | 0 | +0.0% | 123 | -27.2% |
| open_drive | 23 | -35.8% | 123 | -25.6% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- amd_gap_rebound: {'trail': 9, 'time': 9}
- gap_with: {'take_profit': 45, 'time': 80}
- open_drive_calm: {'take_profit': 41, 'time': 82}
- amd_open_calm: {'take_profit': 41, 'time': 82}
- open_drive_run: {'trail': 37, 'time': 86}
- open_drive_x4: {'take_profit': 21, 'time': 102}
- open_drive: {'take_profit': 48, 'time': 98}
