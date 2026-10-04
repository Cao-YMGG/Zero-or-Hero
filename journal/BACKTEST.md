# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gap_fade | 125 | 43% | +112% | -99% | -7.8% | +143% | 50 | 500 | 90% | — / — / — | 2025-10-14 |
| gap_with | 125 | 42% | +106% | -91% | -9.0% | +151% | 4 | 500 | 99% | — / — / — | 2025-11-04 |
| oil_lead | 172 | 41% | +107% | -94% | -11.2% | +161% | 25 | 500 | 95% | — / — / — | 2025-10-07 |
| orb15_tp100 | 248 | 26% | +106% | -53% | -11.3% | +164% | 44 | 500 | 91% | — / — / — | 2025-10-21 |
| open_drive_calm | 177 | 38% | +110% | -92% | -15.4% | +251% | 73 | 500 | 85% | — / — / — | — |
| open_drive | 200 | 36% | +111% | -92% | -18.0% | +251% | 73 | 500 | 85% | — / — / — | — |
| rates_lead | 185 | 33% | +111% | -97% | -28.3% | +161% | 30 | 500 | 94% | — / — / — | 2025-10-07 |
| open_drive_macro | 23 | 26% | +119% | -93% | -37.7% | +150% | 59 | 500 | 88% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gap_fade | 11.4% | 12.6% | 18.0% |
| gap_with | 8.4% | 11.3% | 17.6% |
| oil_lead | 7.6% | 9.8% | 17.4% |
| open_drive_calm | 4.4% | 7.8% | 15.4% |
| open_drive | 3.8% | 6.5% | 14.7% |
| rates_lead | 1.5% | 4.0% | 10.8% |
| orb15_tp100 | 2.4% | 5.4% | 10.2% |
| open_drive_macro | 0.6% | 1.8% | 6.7% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_calm | 177 | -15.4% | 15.4% | 40 | -24.5% | 13.4% | holding up |
| open_drive | 200 | -18.0% | 14.7% | 44 | -26.6% | 12.7% | holding up |
| gap_with | 125 | -9.0% | 17.6% | 31 | -26.3% | 12.2% | fading |
| oil_lead | 172 | -11.2% | 17.4% | 47 | -27.1% | 10.9% | fading |
| orb15_tp100 | 248 | -11.3% | 10.2% | 63 | -14.7% | 9.5% | holding up |
| gap_fade | 125 | -7.8% | 18.0% | 31 | -46.4% | 6.8% | broken |
| open_drive_macro | 23 | -37.7% | 6.7% | 4 | -47.6% | 6.7% | holding up |
| rates_lead | 185 | -28.3% | 10.8% | 46 | -52.1% | 5.2% | fading |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gap_fade | 14 | -36.8% | 111 | -4.1% |
| gap_with | 14 | -37.8% | 111 | -5.4% |
| oil_lead | 21 | -27.0% | 151 | -9.0% |
| orb15_tp100 | 30 | -27.3% | 218 | -9.1% |
| open_drive_calm | 0 | +0.0% | 177 | -15.4% |
| open_drive | 23 | -37.7% | 177 | -15.4% |
| rates_lead | 26 | -42.6% | 159 | -26.0% |
| open_drive_macro | 23 | -37.7% | 0 | +0.0% |

Live-only variants (no history to backtest): claude_bias, claude_confirm

Exit reasons:

- gap_fade: {'time': 72, 'take_profit': 53}
- gap_with: {'time': 75, 'take_profit': 50}
- oil_lead: {'time': 103, 'take_profit': 69}
- orb15_tp100: {'stop_loss': 181, 'take_profit': 63, 'time': 4}
- open_drive_calm: {'time': 111, 'take_profit': 66}
- open_drive: {'time': 128, 'take_profit': 72}
- rates_lead: {'time': 126, 'take_profit': 59}
- open_drive_macro: {'time': 17, 'take_profit': 6}
