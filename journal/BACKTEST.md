# Backtest — SPY 0DTE, 2025-10-06 → 2026-10-02 (248 days)

Model: Black-Scholes at IV 11%, slippage 1% + $0.01 each side, start $500, phase sizing from config. Option prices are modelled, not real quotes — use this to rank ideas.

Realised intraday vol over the period: 10.6% (if far from the IV above, recalibrate `backtest.iv` against live quotes from `python -m zoh.check`).

| variant | trades | win% | avg win | avg loss | expectancy/trade | best | final $ | peak $ | max DD | 2x / 5x / 10x | ruined |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orb15_tp100 | 248 | 26% | +106% | -53% | -11.3% | +164% | 48 | 571 | 92% | — / — / — | 2025-10-30 |
| orb30_fade | 245 | 23% | +111% | -53% | -15.0% | +176% | 40 | 661 | 94% | — / — / — | 2025-12-26 |
| open_drive | 200 | 36% | +111% | -92% | -18.0% | +251% | 68 | 500 | 86% | — / — / — | — |
| orb30_tp100 | 245 | 20% | +114% | -53% | -19.1% | +213% | 53 | 754 | 93% | — / — / — | — |
| orb60_tp100 | 222 | 20% | +110% | -53% | -20.5% | +213% | 41 | 891 | 95% | — / — / — | 2025-12-11 |
| orb30_hero | 245 | 20% | +92% | -53% | -23.8% | +551% | 56 | 644 | 91% | — / — / — | — |
| mom60_hero | 206 | 23% | +97% | -62% | -25.5% | +618% | 26 | 774 | 97% | — / — / — | 2025-12-10 |
| power_hour | 179 | 25% | +119% | -87% | -36.3% | +332% | 45 | 500 | 91% | — / — / — | 2025-10-24 |
| orb30_lotto | 241 | 12% | +343% | -99% | -45.8% | +673% | 47 | 500 | 91% | — / — / — | 2025-11-04 |

## Odds of $500 → $2,000 before ruin (bootstrap of each variant's trades, stake = % of equity per trade)

| variant | 30% stake | 50% stake | 100% stake |
|---|---|---|---|
| open_drive | 3.8% | 6.5% | 14.7% |
| orb30_lotto | 2.2% | 3.9% | 11.3% |
| orb15_tp100 | 2.4% | 5.4% | 10.2% |
| orb30_fade | 1.1% | 3.1% | 7.3% |
| orb30_tp100 | 0.4% | 2.0% | 5.6% |
| power_hour | 0.7% | 1.9% | 5.6% |
| orb60_tp100 | 0.5% | 1.6% | 5.0% |
| mom60_hero | 1.2% | 2.5% | 4.5% |
| orb30_hero | 0.8% | 1.7% | 3.6% |

Exit reasons:

- orb15_tp100: {'stop_loss': 181, 'take_profit': 63, 'time': 4}
- orb30_fade: {'stop_loss': 187, 'take_profit': 56, 'time': 2}
- open_drive: {'time': 128, 'take_profit': 72}
- orb30_tp100: {'stop_loss': 193, 'take_profit': 49, 'time': 3}
- orb60_tp100: {'stop_loss': 177, 'take_profit': 42, 'time': 3}
- orb30_hero: {'stop_loss': 193, 'trail': 44, 'time': 8}
- mom60_hero: {'trail': 43, 'stop_loss': 155, 'time': 8}
- power_hour: {'time': 144, 'take_profit': 35}
- orb30_lotto: {'time': 214, 'take_profit': 27}
