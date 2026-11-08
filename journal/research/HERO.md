# Hero replay: our picks traded like the other Claude's rule ledgers

Every pre-market sniper (0.10 delta, the catalyst_open / catalyst_open_hero contract) and intraday pick (0.20 delta, catalyst_intraday / catalyst_intraday_hero) since 2026-10-01 on real option minute bars (journal/research/snipers.json, costs 10% each way), replayed as a $500 ledger that puts either 20% (today's real sizing) or 100% (the hero shadows, the other Claude's rounds) into whole contracts and compounds. Exits: `live` = half at 3x, trail armed at 1.5x with a 40% giveback, sold at 15:45; `hold` = nothing until 15:45; `_carry` = held to 15:45 of expiry when the contract outlives the day. A round ends as a hero at >= $5,000 or a zero at <= $50 and restarts at $500. See zoh/research/hero.py.

## Rounds

| ledger | size | exit | taken | skipped (no whole contract) | rounds closed | zeros | heroes | peak | open ledger | net P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| sniper 0.10 | 20% | live | 7 | 7 | 0 | 0 | 0 | $504 | $198 | $-302 |
| sniper 0.10 | 20% | hold | 7 | 7 | 0 | 0 | 0 | $504 | $198 | $-302 |
| sniper 0.10 | 20% | hold_carry | 7 | 7 | 0 | 0 | 0 | $500 | $167 | $-333 |
| sniper 0.10 | 100% | live | 11 | 3 | 3 | 3 | 0 | $1,798 | $105 | $-1,843 |
| sniper 0.10 | 100% | hold | 12 | 2 | 5 | 5 | 0 | $1,585 | $108 | $-2,786 |
| sniper 0.10 | 100% | hold_carry | 13 | 1 | 10 | 10 | 0 | $500 | $108 | $-5,195 |
| intraday 0.20 | 20% | live | 7 | 6 | 0 | 0 | 0 | $650 | $314 | $-186 |
| intraday 0.20 | 20% | hold | 7 | 6 | 0 | 0 | 0 | $636 | $310 | $-190 |
| intraday 0.20 | 20% | hold_carry | 7 | 6 | 0 | 0 | 0 | $761 | $458 | $-42 |
| intraday 0.20 | 100% | live | 12 | 1 | 3 | 3 | 0 | $1,311 | $216 | $-1,768 |
| intraday 0.20 | 100% | hold | 12 | 1 | 3 | 3 | 0 | $1,099 | $216 | $-1,756 |
| intraday 0.20 | 100% | hold_carry | 9 | 4 | 4 | 4 | 0 | $1,294 | $216 | $-2,239 |
| all picks | 20% | live | 12 | 15 | 0 | 0 | 0 | $504 | $194 | $-306 |
| all picks | 20% | hold | 12 | 15 | 0 | 0 | 0 | $504 | $160 | $-340 |
| all picks | 20% | hold_carry | 12 | 15 | 0 | 0 | 0 | $500 | $103 | $-397 |
| all picks | 100% | live | 26 | 1 | 8 | 8 | 0 | $3,333 | $74 | $-4,271 |
| all picks | 100% | hold | 25 | 2 | 8 | 8 | 0 | $2,044 | $74 | $-4,307 |
| all picks | 100% | hold_carry | 23 | 4 | 14 | 14 | 0 | $2,856 | $74 | $-7,173 |

## Per $1 of option cost

| ledger | exit | n | win% | avg | without the best | without the best two |
|---|---|---|---|---|---|---|
| sniper 0.10 | live, day one | 14 | 29% | -13% | -35% | -52% |
| sniper 0.10 | hold, day one | 14 | 21% | -48% | -69% | -79% |
| sniper 0.10 | live, carried | 14 | 29% | -16% | -39% | -56% |
| sniper 0.10 | hold, carried | 14 | 0% | -94% | -98% | -100% |
| intraday 0.20 | live, day one | 13 | 23% | -30% | -46% | -51% |
| intraday 0.20 | hold, day one | 13 | 31% | -31% | -46% | -51% |
| intraday 0.20 | live, carried | 13 | 31% | -4% | -21% | -38% |
| intraday 0.20 | hold, carried | 13 | 23% | -23% | -67% | -87% |
| all picks | live, day one | 27 | 26% | -21% | -33% | -41% |
| all picks | hold, day one | 27 | 26% | -39% | -50% | -58% |
| all picks | live, carried | 27 | 30% | -10% | -21% | -30% |
| all picks | hold, carried | 27 | 11% | -60% | -81% | -91% |

## Each pick (hero sizing, hold to 15:45 day one: the ledger after each trade)

| day | source | sym | dir | stock open->close | option entry | peak x | live | hold | hold carried | contracts | ledger after |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | intraday | AVGO | call | +2.5% | 1.21 | 1.5 | -6% | -14% | -100% | 4 | $430 |
| 2026-10-07 | sniper | MRVL | call | +1.3% | 0.85 | 1.4 | +5% | +5% | -100% | 5 | $452 |
| 2026-10-08 | sniper | PLTR | call | -0.2% | 0.61 | 1.1 | -93% | -93% | -100% | 7 | $53 |
| 2026-10-09 | sniper | LITE | call | -1.0% | 2.35 | 0.9 | -99% | -99% | -99% | 0 | $53 |
| 2026-10-12 | sniper | CRM | call | -1.2% | 0.53 | 2.1 | -73% | -73% | -100% | 1 | $15 |
| 2026-10-13 | sniper | META | call | +3.6% | 1.19 | 7.5 | +273% | +228% | -100% | 4 | $1,585 |
| 2026-10-15 | sniper | AAPL | call | -1.4% | 0.40 | 0.8 | -95% | -95% | -100% | 39 | $104 |
| 2026-10-16 | sniper | AAPL | call | -0.8% | 0.20 | 0.5 | -100% | -100% | -100% | 5 | $4 |
| 2026-10-19 | sniper | MSFT | call | +0.9% | 0.23 | 1.0 | -100% | -100% | -100% | 21 | $17 |
| 2026-10-19 | intraday | AMZN | call | +2.7% | 0.29 | 4.6 | +171% | +155% | +155% | 17 | $1,264 |
| 2026-10-21 | intraday | AMD | call | +1.2% | 1.30 | 1.1 | +3% | +3% | +3% | 9 | $1,294 |
| 2026-10-22 | sniper | UNH | call | +1.6% | 0.48 | 3.1 | +143% | +58% | -100% | 26 | $2,019 |
| 2026-10-22 | intraday | MSFT | put | -2.3% | 1.11 | 1.6 | +1% | +1% | -100% | 18 | $2,044 |
| 2026-10-23 | intraday | ORCL | call | +1.0% | 0.11 | 1.3 | -100% | -100% | -100% | 185 | $9 |
| 2026-10-26 | sniper | TSLA | call | +2.0% | 0.59 | 1.6 | -24% | -100% | -100% | 8 | $28 |
| 2026-10-26 | intraday | INTC | call | +2.9% | 1.49 | 1.3 | -28% | -28% | -100% | 3 | $375 |
| 2026-10-27 | sniper | AVGO | call | +0.9% | 0.64 | 1.9 | -1% | -24% | -32% | 5 | $299 |
| 2026-10-27 | intraday | ORCL | call | +2.9% | 1.38 | 4.7 | -18% | -18% | -100% | 2 | $249 |
| 2026-10-28 | intraday | AMAT | call | +3.2% | 1.69 | 1.6 | -7% | +6% | -100% | 1 | $259 |
| 2026-10-29 | sniper | V | call | +1.4% | 0.32 | 1.1 | -91% | -91% | -97% | 8 | $27 |
| 2026-10-29 | intraday | ORCL | put | -3.2% | 0.67 | 6.1 | -46% | -46% | +502% | 7 | $283 |
| 2026-10-30 | sniper | GEV | call | +0.9% | 1.16 | 3.8 | +166% | -84% | -84% | 2 | $87 |
| 2026-10-30 | intraday | AMZN | put | +3.4% | 0.18 | 1.3 | -100% | -100% | -100% | 4 | $15 |
| 2026-11-02 | intraday | AMZN | call | +1.2% | 0.55 | 0.9 | -100% | -100% | -100% | 9 | $5 |
| 2026-11-06 | sniper | LLY | call | +0.3% | 1.76 | 0.9 | -99% | -99% | -99% | 2 | $152 |
| 2026-11-06 | intraday | GE | call | +2.0% | 0.17 | 1.3 | -58% | -58% | -58% | 8 | $74 |
| 2026-11-06 | intraday | MU | put | -2.8% | 3.58 | 1.4 | -99% | -99% | -99% | 0 | $74 |

## The real fills (catalyst_open / catalyst_intraday, as traded at 20%)

`live` is the realised multiple per $1 (real fills, fees aside); `hold` the same contract sold at 15:45 of the entry day; `hold carried` at 15:45 of expiry. Rows the bot itself closed at 15:45 or let expire use the real exit; the rest use the 15:45 bar's bid at 10% costs.

| day | sym | contract | qty | entry | exit | real P&L | live | hold | hold carried |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-09 | LITE | LITE261009C01200000 | 1 | 0.40 | trail | $+45 | +112% | -100% | -100% |
| 2026-10-13 | META | META261014C00775000 | 1 | 0.93 | trail | $+322 | +346% | +156% | -100% |
| 2026-10-15 | AAPL | AAPL261016C00355000 | 4 | 0.36 | expired | $-144 | -100% | -94% | -100% |
| 2026-10-19 | MSFT | MSFT261019C00537500 | 3 | 0.34 | time | $-99 | -97% | -97% | -97% |
| 2026-10-21 | AMD | AMD261021C00562500 | 1 | 0.71 | time | $+23 | +32% | +32% | +32% |
| 2026-10-22 | MSFT | MSFT261023P00515000 | 1 | 1.02 | expired | $-102 | -100% | +20% | -100% |
| 2026-10-22 | UNH | UNH261023C00430000 | 2 | 0.52 | half+trail | $+168 | +162% | +48% | -100% |
| 2026-10-26 | TSLA | TSLA261026C00395000 | 1 | 0.88 | trail | $+18 | +20% | -89% | -89% |
| 2026-10-27 | AVGO | AVGO261028C00355000 | 2 | 0.48 | trail | $+44 | +46% | +0% | -4% |
| 2026-10-29 | ORCL | ORCL261030P00134000 | 2 | 0.64 | half+trail | $+369 | +288% | -44% | +531% |
| 2026-10-29 | V | V261030C00420000 | 2 | 0.70 | expired | $-140 | -100% | -87% | -100% |
| 2026-10-30 | AMZN | AMZN261030P00235000 | 11 | 0.18 | expired | $-198 | -100% | -100% | -100% |
| 2026-10-30 | GEV | GEV261030C00935000 | 1 | 2.15 | expired | $-215 | -100% | -100% | -100% |
| 2026-11-02 | AMZN | AMZN261102C00255000 | 2 | 0.43 | time | $-84 | -98% | -98% | -98% |

| ledger | exit | n | win% | avg | without the best | without the best two |
|---|---|---|---|---|---|---|
| real fills | live (as traded) | 14 | 50% | +22% | -3% | -27% |
| real fills | hold, day one | 14 | 29% | -39% | -55% | -63% |
| real fills | hold, carried | 14 | 14% | -37% | -81% | -91% |

| ledger | size | exit | taken | skipped (no whole contract) | rounds closed | zeros | heroes | peak | open ledger | net P&L |
|---|---|---|---|---|---|---|---|---|---|---|
| real fills | 20% | live | 13 | 1 | 0 | 0 | 0 | $1,120 | $604 | $+104 |
| real fills | 20% | hold | 7 | 7 | 0 | 0 | 0 | $500 | $215 | $-285 |
| real fills | 20% | hold_carry | 5 | 9 | 0 | 0 | 0 | $500 | $194 | $-306 |
| real fills | 100% | live | 14 | 0 | 7 | 6 | 1 | $8,463 | $500 | $+5,112 |
| real fills | 100% | hold | 14 | 0 | 5 | 5 | 0 | $1,225 | $500 | $-2,410 |
| real fills | 100% | hold_carry | 14 | 0 | 9 | 9 | 0 | $661 | $500 | $-4,226 |

## The hero shadows' own rounds (catalyst_open_hero / catalyst_intraday_hero, live since 2026-11-03)

2 trades, 0 rounds closed: 0 hero, 0 zero; open ledger $52, net $-448.

| day | variant | contract | qty | entry | result | P&L |
|---|---|---|---|---|---|---|
| 2026-11-06 | catalyst_intraday_hero | GE261106C00330000 | 8 | 0.57 | -98% | $-448 |
| 2026-11-06 | catalyst_open_hero | LLY261106C01390000 | 1 | 2.36 | -100% | $-236 |

## Reading

1. The hero recipe (whole ledger, no exits, hold to 15:45) on every pick named since 10-06: 25 trades, 8 zeros, 0 heroes, net $-4,307, best ledger $2,044. Removing the exits did not make a hero; with the live exits at the same full size: 8 zeros, 0 heroes, net $-4,271, best ledger $3,333.
2. On the 14 real fills, full size with the exits the bot actually used: 1 hero (best ledger $8,463) and 6 zeros, net $+5,112; the same fills held to 15:45: 0 hero, 5 zeros, net $-2,410. Where a hero appears it comes from full size on a streak the trailing exits kept alive, not from holding.
3. The ticket is the root: see the per-$1 tables. A full-size ledger on a negative ticket is a zero machine with an occasional hero, and a hero that rests on one trade is a candidate at most (EVOLUTION 2026-10-07). Nothing in the real ledgers changes on this; the hero shadows stay as the owner asked (pure hold) so their rounds can be compared with the other Claude's, and the 'real fills, 100%, live' row above is the second counter, rebuilt from trades.csv each run.
