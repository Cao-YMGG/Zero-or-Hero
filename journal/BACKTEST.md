# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-02 (250 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.5% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gap_with | 127 | 43% | +108% | -92% | -5.7% | +162% | 2 | 1,293 | 100% | 2025-10-20 / — / — | 2025-11-17 |
| open_drive_calm | 177 | 38% | +109% | -92% | -15.5% | +253% | 4 | 500 | 99% | — / — / — | 2025-10-16 |
| open_drive | 200 | 36% | +110% | -92% | -18.2% | +253% | 4 | 500 | 99% | — / — / — | 2025-10-16 |
| open_drive_run | 177 | 38% | +98% | -92% | -19.7% | +805% | 4 | 500 | 99% | — / — / — | 2025-10-16 |
| open_drive_x4 | 177 | 18% | +311% | -99% | -27.3% | +513% | 25 | 500 | 95% | — / — / — | 2025-10-15 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| gap_with | 12.7% | 13.7% | 19.8% |
| open_drive_x4 | 5.8% | 7.1% | 16.2% |
| open_drive_calm | 4.8% | 7.8% | 15.2% |
| open_drive | 3.4% | 6.4% | 14.4% |
| open_drive_run | 4.4% | 6.2% | 9.1% |

## Ultra-aggressive: all-in odds of $500 → $50k / $500k, and the best multiples

| variant | trades | win% | P(→$50k) | P(→$500k) | top 5 multiples |
|---|---|---|---|---|---|
| gap_with | 127 | 43% | 0.50% | 0.03% | 3x, 2x, 2x, 2x, 2x |
| open_drive_calm | 177 | 38% | 0.22% | 0.03% | 4x, 2x, 2x, 2x, 2x |
| open_drive_x4 | 177 | 18% | 0.20% | 0.03% | 6x, 5x, 5x, 5x, 5x |
| open_drive_run | 177 | 38% | 0.20% | 0.00% | 9x, 8x, 5x, 4x, 4x |
| open_drive | 200 | 36% | 0.12% | 0.00% | 4x, 3x, 2x, 2x, 2x |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_x4 | 177 | -27.3% | 16.2% | 40 | -48.1% | 13.2% | holding up |
| gap_with | 127 | -5.7% | 19.8% | 32 | -22.3% | 12.4% | fading |
| open_drive_calm | 177 | -15.5% | 15.2% | 40 | -28.3% | 11.8% | fading |
| open_drive_run | 177 | -19.7% | 9.1% | 40 | -15.4% | 10.7% | holding up |
| open_drive | 200 | -18.2% | 14.4% | 44 | -30.0% | 10.5% | fading |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| gap_with | 14 | -38.3% | 113 | -1.6% |
| open_drive_calm | 0 | +0.0% | 177 | -15.5% |
| open_drive | 23 | -39.0% | 177 | -15.5% |
| open_drive_run | 0 | +0.0% | 177 | -19.7% |
| open_drive_x4 | 0 | +0.0% | 177 | -27.3% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper, catalyst_open

Exit reasons:

- gap_with: {'time': 73, 'take_profit': 54}
- open_drive_calm: {'time': 111, 'take_profit': 66}
- open_drive: {'time': 128, 'take_profit': 72}
- open_drive_run: {'time': 118, 'trail': 59}
- open_drive_x4: {'time': 149, 'take_profit': 28}
