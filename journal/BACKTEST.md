# Backtest — SPY 0DTE, 2026-09-04 → 2026-10-02 (20 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 7.7% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orb15_tp100 | 19 | 21% | +106% | -52% | -19.0% | +113% | 86 | 500 | 83% | — / — / — | — |
| oil_lead | 14 | 36% | +111% | -100% | -24.6% | +125% | 4 | 500 | 99% | — / — / — | 2026-09-14 |
| open_drive_calm | 13 | 31% | +104% | -96% | -34.7% | +107% | 4 | 500 | 99% | — / — / — | 2026-09-11 |
| open_drive | 15 | 27% | +104% | -97% | -43.4% | +107% | 4 | 500 | 99% | — / — / — | 2026-09-11 |
| gap_fade | 8 | 25% | +108% | -100% | -48.1% | +114% | 44 | 500 | 91% | — / — / — | 2026-09-11 |
| gap_with | 8 | 25% | +104% | -100% | -48.9% | +105% | 13 | 500 | 97% | — / — / — | 2026-09-11 |
| rates_lead | 17 | 18% | +120% | -100% | -61.2% | +149% | 8 | 500 | 98% | — / — / — | 2026-09-08 |
| open_drive_macro | 2 | 0% | +0% | -100% | -100.0% | -100% | 76 | 500 | 85% | — / — / — | — |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| oil_lead | 2.5% | 4.2% | 12.6% |
| open_drive_calm | 0.4% | 2.4% | 9.2% |
| open_drive | 0.1% | 0.9% | 6.9% |
| orb15_tp100 | 0.3% | 1.3% | 6.3% |
| gap_fade | 0.1% | 0.8% | 6.2% |
| gap_with | 0.1% | 0.7% | 6.0% |
| rates_lead | 0.0% | 0.5% | 2.8% |
| open_drive_macro | 0.0% | 0.0% | 0.0% |

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
| orb15_tp100 | 3 | -54.9% | 16 | -12.3% |
| oil_lead | 3 | -24.9% | 11 | -24.6% |
| open_drive_calm | 0 | +0.0% | 13 | -34.7% |
| open_drive | 2 | -100.0% | 13 | -34.7% |
| gap_fade | 2 | -100.0% | 6 | -30.8% |
| gap_with | 2 | -99.9% | 6 | -31.9% |
| rates_lead | 4 | -100.0% | 13 | -49.2% |
| open_drive_macro | 2 | -100.0% | 0 | +0.0% |

Live-only variants (no history to backtest): claude_bias, claude_confirm

Exit reasons:

- orb15_tp100: {'stop_loss': 15, 'take_profit': 4}
- oil_lead: {'time': 9, 'take_profit': 5}
- open_drive_calm: {'time': 9, 'take_profit': 4}
- open_drive: {'time': 11, 'take_profit': 4}
- gap_fade: {'time': 6, 'take_profit': 2}
- gap_with: {'time': 6, 'take_profit': 2}
- rates_lead: {'time': 14, 'take_profit': 3}
- open_drive_macro: {'time': 2}
