# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gap_fade | 125 | 43% | +112% | -99% | -7.8% | +143% | 50 | 500 | 90% | — / — / — | 2025-10-14 |
| gap_with | 125 | 42% | +106% | -91% | -9.0% | +151% | 4 | 500 | 99% | — / — / — | 2025-11-04 |
| orb15_tp100 | 248 | 26% | +106% | -53% | -11.3% | +164% | 44 | 500 | 91% | — / — / — | 2025-10-21 |
| orb30_fade | 245 | 23% | +111% | -53% | -15.0% | +176% | 57 | 500 | 89% | — / — / — | — |
| open_drive_calm | 177 | 38% | +110% | -92% | -15.4% | +251% | 73 | 500 | 85% | — / — / — | — |
| open_drive | 200 | 36% | +111% | -92% | -18.0% | +251% | 73 | 500 | 85% | — / — / — | — |
| open_drive_macro | 23 | 26% | +119% | -93% | -37.7% | +150% | 59 | 500 | 88% | — / — / — | — |
| orb30_lotto | 241 | 12% | +343% | -99% | -45.8% | +673% | 17 | 500 | 97% | — / — / — | 2025-10-07 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gap_fade | 11.4% | 12.6% | 18.0% |
| gap_with | 8.4% | 11.3% | 17.6% |
| open_drive_calm | 4.4% | 7.8% | 15.4% |
| open_drive | 3.8% | 6.5% | 14.7% |
| orb30_lotto | 2.2% | 3.9% | 11.3% |
| orb15_tp100 | 2.4% | 5.4% | 10.2% |
| orb30_fade | 1.1% | 3.1% | 7.3% |
| open_drive_macro | 0.6% | 1.8% | 6.7% |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gap_fade | 14 | -36.8% | 111 | -4.1% |
| gap_with | 14 | -37.8% | 111 | -5.4% |
| orb15_tp100 | 30 | -27.3% | 218 | -9.1% |
| orb30_fade | 30 | -6.8% | 215 | -16.1% |
| open_drive_calm | 0 | +0.0% | 177 | -15.4% |
| open_drive | 23 | -37.7% | 177 | -15.4% |
| open_drive_macro | 23 | -37.7% | 0 | +0.0% |
| orb30_lotto | 30 | -45.3% | 211 | -45.8% |

Live-only variants (no history to backtest): claude_bias, claude_confirm

Exit reasons:

- gap_fade: {'time': 72, 'take_profit': 53}
- gap_with: {'time': 75, 'take_profit': 50}
- orb15_tp100: {'stop_loss': 181, 'take_profit': 63, 'time': 4}
- orb30_fade: {'stop_loss': 187, 'take_profit': 56, 'time': 2}
- open_drive_calm: {'time': 111, 'take_profit': 66}
- open_drive: {'time': 128, 'take_profit': 72}
- open_drive_macro: {'time': 17, 'take_profit': 6}
- orb30_lotto: {'time': 214, 'take_profit': 27}
