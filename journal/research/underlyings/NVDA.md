# Backtest — NVDA 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 34%, slippage 3% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 29.8% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orb15_tp100 | 137 | 23% | +111% | -53% | -15.8% | +148% | 35 | 500 | 93% | — / — / — | 2025-10-16 |
| open_drive_calm | 124 | 37% | +110% | -95% | -18.9% | +137% | 0 | 500 | 100% | — / — / — | 2025-10-09 |
| open_drive_run | 124 | 36% | +108% | -94% | -20.9% | +656% | 0 | 500 | 100% | — / — / — | 2025-10-09 |
| oil_lead | 101 | 36% | +107% | -96% | -23.5% | +131% | 15 | 500 | 97% | — / — / — | 2025-10-07 |
| open_drive_x4 | 124 | 18% | +322% | -99% | -24.1% | +360% | 26 | 500 | 95% | — / — / — | 2025-10-07 |
| open_drive | 147 | 33% | +111% | -96% | -26.8% | +137% | 0 | 500 | 100% | — / — / — | 2025-10-09 |
| gap_with | 115 | 33% | +110% | -96% | -28.3% | +142% | 42 | 500 | 92% | — / — / — | 2025-10-09 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive_x4 | 5.8% | 6.0% | 18.4% |
| open_drive_calm | 3.6% | 5.8% | 14.2% |
| oil_lead | 1.9% | 4.6% | 12.8% |
| open_drive | 1.7% | 4.2% | 11.2% |
| gap_with | 1.0% | 3.1% | 10.8% |
| open_drive_run | 3.7% | 5.8% | 8.8% |
| orb15_tp100 | 1.0% | 2.5% | 8.3% |

## Regime check: last 63 trading days vs full period

If a variant only works in the old part of the sample, the market has moved on.

| variant | full: trades | full: avg | full: odds (100%) | recent: trades | recent: avg | recent: odds (100%) | verdict |
|---|---|---|---|---|---|---|---|
| open_drive_x4 | 124 | -24.1% | 18.4% | 30 | +13.8% | 27.0% | holding up |
| open_drive_run | 124 | -20.9% | 8.8% | 30 | +29.4% | 21.6% | holding up |
| oil_lead | 101 | -23.5% | 12.8% | 28 | -1.6% | 20.9% | holding up |
| open_drive_calm | 124 | -18.9% | 14.2% | 30 | -5.8% | 20.1% | holding up |
| gap_with | 115 | -28.3% | 10.8% | 30 | -22.6% | 14.2% | holding up |
| open_drive | 147 | -26.8% | 11.2% | 37 | -23.4% | 12.4% | holding up |
| orb15_tp100 | 137 | -15.8% | 8.3% | 37 | -11.0% | 10.8% | holding up |

## Macro days (CPI / NFP / FOMC) vs other days — expectancy per trade

| variant | macro-day trades | macro-day avg | other trades | other avg |
|---|---|---|---|---|
| orb15_tp100 | 20 | -19.3% | 117 | -15.2% |
| open_drive_calm | 0 | +0.0% | 124 | -18.9% |
| open_drive_run | 0 | +0.0% | 124 | -20.9% |
| oil_lead | 17 | -45.8% | 84 | -19.0% |
| open_drive_x4 | 0 | +0.0% | 124 | -24.1% |
| open_drive | 23 | -69.3% | 124 | -18.9% |
| gap_with | 18 | +8.2% | 97 | -35.1% |

Live-only variants (no history to backtest): claude_bias, claude_confirm, catalyst_sniper

Exit reasons:

- orb15_tp100: {'stop_loss': 106, 'take_profit': 31}
- open_drive_calm: {'time': 78, 'take_profit': 46}
- open_drive_run: {'time': 84, 'trail': 40}
- oil_lead: {'time': 66, 'take_profit': 35}
- open_drive_x4: {'time': 102, 'take_profit': 22}
- open_drive: {'time': 98, 'take_profit': 49}
- gap_with: {'time': 77, 'take_profit': 38}
