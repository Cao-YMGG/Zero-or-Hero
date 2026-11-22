# The selling side: SPY same-day credit spreads (SUNDAY_TESTS 82)

Every session 2024-02-01 to 2026-11-20 (705 days). At 10:00 sell the same-day SPY option nearest 0.30 delta and buy the one 5 points further out, on each side; out at 15:45 or when buying it back costs 2 times the credit. Real 1-minute option bars; dollars per spread (one contract a leg; the most a spread can lose is about $438). `python -m zoh.research.sellside`.

## What the cost assumption does

| cost each leg, each way | spreads | win | per spread | without best 5 | without worst 5 | stopped | last 3 months | rising months | falling months | months up |
|---|---|---|---|---|---|---|---|---|---|---|
| 10% | 1400 | 42% | -$15.4 | -$15.8 | -$14.9 | 57% | -$16.7 | -$12.7 | -$22.9 | 1 of 34 |
| 5% | 1400 | 49% | -$7.9 | -$8.4 | -$7.3 | 50% | -$8.2 | -$5.9 | -$13.3 | 4 of 34 |
| 2% | 1400 | 52% | -$4.0 | -$4.4 | -$3.4 | 46% | -$4.1 | -$3.1 | -$6.4 | 12 of 34 |
| a cent a leg | 1400 | 53% | -$2.3 | -$2.7 | -$1.7 | 45% | -$3.9 | -$1.1 | -$5.1 | 15 of 34 |
| none | 1400 | 56% | +$2.5 | +$2.1 | +$3.1 | 42% | -$0.8 | +$3.8 | -$0.7 | 23 of 34 |

The bar was written at 10% (5% as a bracket). A cent a leg is what a SPY same-day option's quote usually costs to cross; `none` is the trade price both ways, which nobody gets.

## Cost: 10%

| version | spreads | win | per spread | without best 5 | without worst 5 | worst month | average month |
|---|---|---|---|---|---|---|---|
| (a) both sides, every day | 1400 | 42% | -$15.4 | -$15.8 | -$14.9 | 2025-04 -$1,740 | -$635 |
| (b) only the side against the 10:00 move | 700 | 41% | -$16.3 | -$17.0 | -$15.3 | 2025-04 -$1,000 | -$335 |
| the side with the 10:00 move | 700 | 43% | -$14.6 | -$15.3 | -$13.7 | 2026-07 -$947 | -$300 |
| (c) days within 0.5% of the open at 10:00 | 1306 | 43% | -$14.1 | -$14.5 | -$13.5 | 2026-07 -$1,131 | -$541 |

By year, both sides: 2024 -$9.0 (454), 2025 -$17.4 (499), 2026 -$19.7 (447).
As a $5,000 account, one spread a side a day: ends at $994 (it could no longer cover a spread on 2024-12-24); SPY held over the same span +13.1% a year, worst fall -19%.

## Cost: 5%

| version | spreads | win | per spread | without best 5 | without worst 5 | worst month | average month |
|---|---|---|---|---|---|---|---|
| (a) both sides, every day | 1400 | 49% | -$7.9 | -$8.4 | -$7.3 | 2025-04 -$1,408 | -$327 |
| (b) only the side against the 10:00 move | 700 | 48% | -$8.3 | -$9.1 | -$7.0 | 2025-04 -$1,218 | -$171 |
| the side with the 10:00 move | 700 | 50% | -$7.6 | -$8.4 | -$6.7 | 2026-07 -$972 | -$156 |
| (c) days within 0.5% of the open at 10:00 | 1306 | 50% | -$7.1 | -$7.5 | -$6.6 | 2026-07 -$1,108 | -$273 |

By year, both sides: 2024 -$2.2 (454), 2025 -$10.1 (499), 2026 -$11.3 (447).
As a $5,000 account, one spread a side a day: ends at $982 (it could no longer cover a spread on 2025-06-02); SPY held over the same span +13.1% a year, worst fall -19%.

## Cost: a cent a leg

| version | spreads | win | per spread | without best 5 | without worst 5 | worst month | average month |
|---|---|---|---|---|---|---|---|
| (a) both sides, every day | 1400 | 53% | -$2.3 | -$2.7 | -$1.7 | 2025-04 -$986 | -$93 |
| (b) only the side against the 10:00 move | 700 | 53% | -$3.0 | -$3.8 | -$1.9 | 2025-04 -$1,150 | -$61 |
| the side with the 10:00 move | 700 | 54% | -$1.5 | -$2.4 | -$0.6 | 2026-07 -$657 | -$32 |
| (c) days within 0.5% of the open at 10:00 | 1306 | 54% | -$1.9 | -$2.3 | -$1.4 | 2026-07 -$745 | -$73 |

By year, both sides: 2024 +$1.3 (454), 2025 -$3.7 (499), 2026 -$4.2 (447).
As a $5,000 account, one spread a side a day: ends at $1,840, -30.0% a year, worst fall -71%; SPY held over the same span +13.1% a year, worst fall -19%.

## Cost: none

| version | spreads | win | per spread | without best 5 | without worst 5 | worst month | average month |
|---|---|---|---|---|---|---|---|
| (a) both sides, every day | 1400 | 56% | +$2.5 | +$2.1 | +$3.1 | 2025-04 -$846 | +$104 |
| (b) only the side against the 10:00 move | 700 | 55% | +$1.1 | +$0.2 | +$2.1 | 2025-04 -$1,189 | +$22 |
| the side with the 10:00 move | 700 | 58% | +$4.0 | +$3.2 | +$4.9 | 2026-07 -$387 | +$82 |
| (c) days within 0.5% of the open at 10:00 | 1306 | 57% | +$3.0 | +$2.5 | +$3.5 | 2026-06 -$544 | +$114 |

By year, both sides: 2024 +$5.6 (454), 2025 +$1.4 (499), 2026 +$0.6 (447).
As a $5,000 account, one spread a side a day: ends at $8,522, +21.0% a year, worst fall -17%; SPY held over the same span +13.1% a year, worst fall -19%.

## The bar

Written before the run: positive after costs over the whole span and over the last 3 months, in rising and in falling months, every calendar year above zero, and the worst month no worse than three average months of gain. Version (a):

| cost | whole span | last 3 months | rising | falling | every year | worst month | met |
|---|---|---|---|---|---|---|---|
| 10% | no | no | no | no | no | no | no |
| 5% | no | no | no | no | no | no | no |
| 2% | no | no | no | no | no | no | no |
| a cent a leg | no | no | no | no | no | no | no |
| none | yes | no | yes | no | yes | no | no |

## Without the stop

Held to 15:45 whatever happens, a cent a leg: 1400 spreads, 72% win, -$2.9 a spread, -$1.3 without the worst five, worst single spread -$462.0, worst month 2026-06 -$1,080. The stop changes how the losses arrive (many small ones instead of a few near the full width), not the sum.

