# Opportunity scores

226 rows, 179 ideas after dropping later mentions of the same stock and direction on the same day, 2026-10-29 to 2026-11-13 (12 sessions). Moves are the stock from the listed time to the close, signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and `avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by `python -m zoh.research.opportunities`.

## All ideas

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| all ideas | 179 | 53% | 28% | +0.04% | -0.01% | +0.05% | 49% |

## By source

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| premarket | 89 | 55% | 35% | +0.28% | +0.20% | +0.21% | 54% |
| intraday | 75 | 45% | 19% | -0.30% | -0.37% | -0.21% | 40% |
| sniper | 9 | 78% | 56% | +0.50% | +0.13% | +0.81% | 78% |
| review | 6 | 67% | 17% | -0.15% | -0.40% | -0.21% | 50% |

## By direction

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| call | 103 | 51% | 27% | -0.04% | -0.11% | +0.13% | 48% |
| put | 76 | 54% | 30% | +0.13% | +0.03% | -0.05% | 51% |

## By action (picked or only listed)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| none | 164 | 52% | 28% | +0.04% | -0.00% | +0.03% | 48% |
| real | 10 | 50% | 30% | -0.33% | -0.64% | +0.16% | 60% |
| shadow | 4 | 75% | 50% | +0.66% | -0.29% | +0.61% | 75% |
| bot | 1 | 100% | 0% | +0.10% | - | +0.76% | 100% |

## By conviction (what I thought when I listed it; stated since 2026-11-13)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| not stated | 155 | 54% | 28% | +0.10% | +0.05% | +0.08% | 48% |
| yes | 14 | 57% | 36% | -0.05% | -0.32% | +0.29% | 64% |
| no | 10 | 30% | 20% | -0.88% | -1.30% | -0.72% | 40% |

## By type

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 46 | 54% | 35% | -0.16% | -0.33% | -0.04% | 54% |
| sector_move | 22 | 45% | 9% | -0.36% | -0.46% | -0.14% | 27% |
| relative_weakness | 14 | 43% | 14% | -0.52% | -0.65% | -0.44% | 43% |
| analyst | 13 | 92% | 54% | +1.87% | +1.40% | +1.42% | 77% |
| sector_intraday | 11 | 55% | 45% | +0.33% | -0.05% | +0.10% | 55% |
| rotation_laggard | 9 | 33% | 11% | -1.38% | -1.83% | -0.59% | 33% |
| gapdown_rebound | 9 | 44% | 11% | -0.56% | -0.77% | -0.23% | 33% |
| peer_readthrough | 9 | 44% | 44% | +1.35% | +0.60% | +0.93% | 56% |
| financing_fade | 8 | 62% | 38% | +0.53% | +0.22% | -0.13% | 50% |
| sympathy | 8 | 62% | 38% | +0.30% | +0.01% | +0.20% | 50% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| earnings_reaction | 5 | 80% | 40% | +1.88% | +0.92% | +1.42% | 80% |
| relative_strength | 4 | 75% | 25% | +0.50% | +0.09% | -0.30% | 25% |
| ma_acquirer | 3 | 67% | 33% | +2.47% | +0.29% | +2.17% | 67% |
| news_heating | 3 | 0% | 0% | -0.64% | -0.92% | +0.08% | 67% |
| other types (fewer than 3 ideas each) | 9 | 22% | 22% | -0.81% | -1.23% | -0.42% | 44% |

## By type, last 10 sessions

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 45 | 53% | 33% | -0.19% | -0.36% | -0.06% | 53% |
| sector_move | 21 | 48% | 10% | -0.31% | -0.41% | -0.09% | 29% |
| relative_weakness | 14 | 43% | 14% | -0.52% | -0.65% | -0.44% | 43% |
| analyst | 12 | 92% | 58% | +1.97% | +1.47% | +1.42% | 75% |
| sector_intraday | 11 | 55% | 45% | +0.33% | -0.05% | +0.10% | 55% |
| sympathy | 8 | 62% | 38% | +0.30% | +0.01% | +0.20% | 50% |
| peer_readthrough | 7 | 57% | 57% | +1.89% | +0.97% | +1.34% | 57% |
| rotation_laggard | 7 | 29% | 14% | -1.60% | -2.24% | -0.64% | 29% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| financing_fade | 5 | 80% | 40% | +1.00% | +0.56% | +0.09% | 60% |
| earnings_reaction | 5 | 80% | 40% | +1.88% | +0.92% | +1.42% | 80% |
| relative_strength | 4 | 75% | 25% | +0.50% | +0.09% | -0.30% | 25% |
| gapdown_rebound | 3 | 0% | 0% | -1.20% | -1.57% | -0.82% | 0% |
| other types (fewer than 3 ideas each) | 10 | 30% | 30% | +0.00% | -0.76% | +0.20% | 50% |

## Why the wrong ones were wrong

13 of 85 wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.

| cause | 中文 | wrong ideas | share | avg move | types it shows up in |
|---|---|---|---|---|---|
| chased | 追在延伸处 | 6 | 46% | -1.96% | relative_weakness 2, sector_intraday 2, company_news 2 |
| priced_in | 已经在价格里 | 2 | 15% | -1.81% | company_news 2 |
| noise | 没有可学的 | 2 | 15% | -0.27% | gapdown_rebound 1, sector_move 1 |
| no_catalyst | 没有自己的消息 | 1 | 8% | -2.61% | company_news 1 |
| reversal | 逆势 | 1 | 8% | -1.13% | gapdown_rebound 1 |
| timing | 时间不对 | 1 | 8% | -0.02% | company_news 1 |
