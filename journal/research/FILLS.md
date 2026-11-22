# Were our real fills at real prices, and what did the unfilled orders' shadows make? (SUNDAY_TESTS 81 and 83)

Run 2026-11-22 from the paper broker's order list (every order since 2026-10-13) and the option minute bars of
each contract on its day. A fill is "inside" when its price lies within the lowest and highest print of the minute
before, the minute of and the minute after the fill.

## 81. The fills

51 real fills (30 buys, 21 sells): 43 inside, 8 outside. Every fill on a SPY, TSLA or NVDA same-day contract, which
is all the four ledger rules trade, is inside. The 8 are on thin single-stock contracts, all bought by the sniper,
the intraday pick or leader_follow (shadow-only since 2026-11-09, or retired):

| date | contract | side | our fill | prints around it | paid against the nearest print |
|---|---|---|---|---|---|
| 10-22 | UNH 430C (10-23) | buy | 0.52 | 0.32 - 0.44 | +18% |
| 10-29 | V 420C (10-30) | buy | 0.70 | 0.27 - 0.63 | +11% |
| 10-29 | COIN 185C (10-30) | buy | 0.70 | 0.60 | +17% |
| 10-29 | COIN 185C (10-30) | sell | 0.29 | 0.32 | -9% |
| 10-29 | ORCL 134P (10-30) | buy | 0.64 | 0.61 - 0.62 | +3% |
| 10-30 | GEV 935C (same day) | buy | 2.15 | 0.72 at 09:30, 0.07 at 09:36, 0.30 at 09:41 | 3 to 30 times |
| 10-30 | AMZN 235P (same day) | buy | 0.18 | 0.15 - 0.17 | +6% |
| 11-09 | WMT 131C (11-13) | buy | 0.24 | 0.18 - 0.20 | +20% |

Seven of them are the price of crossing a thin quote: 3% to 20% above the last print, about what the 10% cost in
our studies assumes. One is not: the GEV call was bought at 2.15 at 09:38 while its three prints of the first eleven
minutes were 0.72, 0.07 and 0.30. It expired at zero and cost $215, a third of the $650 the real orders have lost
since 10-13. That quote was not a price anyone was trading at.

**Fix (in the bot from 2026-11-23):** an ask more than double a print of the last 15 minutes is treated like a wide
quote: no real order, and the shadow books the middle of the quote (`MAX_OVER_LAST`, next to the spread gate of
2026-11-08, which stops a quote whose bid is under half its ask). The ledger rules trade contracts that print every
few seconds, so the check should not bind for them; it is there for whatever trades a thin contract next.

Note for anyone repeating this: the option *snapshot* endpoint, read from the research container, is 15 minutes
behind with current time stamps. Minute bars older than 15 minutes are the record.

## 83. Real orders that were cancelled unfilled

Seven entry orders on six contracts were cancelled unfilled. In every case the shadow booked the first ask as if it
had been bought:

| date | rule | contract | our limit | prints in the next minutes | the shadow's result |
|---|---|---|---|---|---|
| 10-23 | catalyst_intraday | ORCL 128C | 0.24 | 0.27, 0.30, 0.32 - 0.34 | +29% |
| 10-28 | catalyst_intraday | AMAT 445C (10-30) | 1.32 | none | -100% |
| 11-06 | catalyst_open | LLY 1430C | 0.91 | 0.44 - 0.50, 0.20, 0.30 - 0.61 | -100% |
| 11-06 | catalyst_intraday | GE 330C (two orders) | 0.54 | none | -98% |
| 11-09 | spy_open_drive | SPY 753C | 0.37 | 0.36 - 0.44, 0.40 - 0.49 | +280% |
| 11-20 | nvda_gapdown_put | NVDA 141P | 1.28 | 1.20 - 1.46, 1.28 - 1.53 | +208% |

The six shadows average +36%; the 32 real rows of the same weeks average -1% (median -96%). The two that mattered
are the two that ran away from the limit: an order at the first ask fills when the price is about to come back and
misses when it is leaving. A shadow that books the first ask therefore keeps the winners real money misses.

**Bar (a), written before the run: met.** The shadows of unfilled real entries average above the filled ones, so
they are flagged and left out. The bot now writes each miss to `journal/unfilled.csv` (the six above are filled in
from the broker's list), and the review's leaderboard, the promotion rule and the dashboard skip the matching
shadow rows. With them out: spy_open_drive's shadow record is 1 trade at -100% (it was 2 at +90%),
nvda_gapdown_put 2 trades at +125% (3 at +153%), catalyst_intraday 10 at +11% (13 at -4%), catalyst_open 16 at
-5% (17 at -11%).

**Bar (b): not met.** What a second quote 30% above the first ask would have bought, single stocks only: ORCL at
about 0.31 (sold at 0.31: 0%), NVDA at about 1.51 (sold at 3.94: +161%), and LLY, GE and AMAT at a higher price
than the one that already lost everything. Five re-quotes, -28% on average and -100% without the best two. The
single-stock cap stays at 10%; SPY and QQQ keep the 50% they got on 11-09.
