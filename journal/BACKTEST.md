# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gap_with | 125 | 42% | +106% | -91% | -9.0% | +151% | 4 | 500 | 99% | — / — / — | 2025-11-04 |
| oil_lead | 172 | 41% | +107% | -94% | -11.2% | +161% | 25 | 500 | 95% | — / — / — | 2025-10-07 |
| orb15_tp100 | 248 | 26% | +106% | -53% | -11.3% | +164% | 44 | 500 | 91% | — / — / — | 2025-10-21 |
| open_drive_calm | 177 | 38% | +110% | -92% | -15.4% | +251% | 73 | 500 | 85% | — / — / — | — |
| open_drive_run | 177 | 38% | +105% | -92% | -17.5% | +803% | 73 | 500 | 85% | — / — / — | — |
| open_drive | 200 | 36% | +111% | -92% | -18.0% | +251% | 73 | 500 | 85% | — / — / — | — |
| open_drive_x4 | 177 | 16% | +300% | -99% | -33.5% | +419% | 18 | 500 | 96% | — / — / — | 2025-10-07 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gap_with | 8.4% | 11.3% | 17.6% |
| oil_lead | 7.6% | 9.8% | 17.4% |
| open_drive_calm | 4.4% | 7.8% | 15.4% |
| open_drive_x4 | 4.0% | 5.2% | 15.3% |
| open_drive | 3.8% | 6.5% | 14.7% |
| orb15_tp100 | 2.4% | 5.4% | 10.2% |
| open_drive_run | 5.4% | 7.4% | 10.0% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_calm | 177 | -15.4% | 15.4% | 40 | -24.5% | 13.4% | holding up |
| open_drive_x4 | 177 | -33.5% | 15.3% | 40 | -48.2% | 12.8% | holding up |
| open_drive | 200 | -18.0% | 14.7% | 44 | -26.6% | 12.7% | holding up |
| gap_with | 125 | -9.0% | 17.6% | 31 | -26.3% | 12.2% | fading |
| open_drive_run | 177 | -17.5% | 10.0% | 40 | -12.4% | 11.1% | holding up |
| oil_lead | 172 | -11.2% | 17.4% | 47 | -27.1% | 10.9% | fading |
| orb15_tp100 | 248 | -11.3% | 10.2% | 63 | -14.7% | 9.5% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gap_with | 14 | -37.8% | 111 | -5.4% |
| oil_lead | 21 | -27.0% | 151 | -9.0% |
| orb15_tp100 | 30 | -27.3% | 218 | -9.1% |
| open_drive_calm | 0 | +0.0% | 177 | -15.4% |
| open_drive_run | 0 | +0.0% | 177 | -17.5% |
| open_drive | 23 | -37.7% | 177 | -15.4% |
| open_drive_x4 | 0 | +0.0% | 177 | -33.5% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- gap_with: {'time': 75, 'take_profit': 50}
- oil_lead: {'time': 103, 'take_profit': 69}
- orb15_tp100: {'stop_loss': 181, 'take_profit': 63, 'time': 4}
- open_drive_calm: {'time': 111, 'take_profit': 66}
- open_drive_run: {'time': 119, 'trail': 58}
- open_drive: {'time': 128, 'take_profit': 72}
- open_drive_x4: {'time': 151, 'take_profit': 26}
