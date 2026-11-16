# Opportunity scores

238 rows, 188 ideas after dropping later mentions of the same stock and direction on the same day, 2026-10-29 to 2026-11-16 (13 sessions). Moves are the stock from the listed time to the close, signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and `avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by `python -m zoh.research.opportunities`.

## All ideas

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| all ideas | 188 | 51% | 27% | -0.01% | -0.05% | +0.03% | 48% |

## By source

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| premarket | 94 | 53% | 33% | +0.22% | +0.14% | +0.20% | 54% |
| intraday | 78 | 45% | 18% | -0.32% | -0.38% | -0.24% | 38% |
| sniper | 10 | 70% | 50% | +0.25% | -0.11% | +0.64% | 70% |
| review | 6 | 67% | 17% | -0.15% | -0.40% | -0.21% | 50% |

## By direction

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| call | 110 | 49% | 25% | -0.11% | -0.18% | +0.09% | 47% |
| put | 78 | 54% | 29% | +0.13% | +0.03% | -0.07% | 50% |

## By action (picked or only listed)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| none | 172 | 51% | 27% | +0.00% | -0.04% | +0.01% | 47% |
| real | 10 | 50% | 30% | -0.33% | -0.64% | +0.16% | 60% |
| shadow | 5 | 60% | 40% | +0.13% | -0.71% | +0.30% | 60% |
| bot | 1 | 100% | 0% | +0.10% | - | +0.76% | 100% |

## By conviction (what I thought when I listed it; stated since 2026-11-13)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| not stated | 155 | 54% | 28% | +0.10% | +0.05% | +0.08% | 48% |
| yes | 15 | 53% | 33% | -0.18% | -0.44% | +0.21% | 60% |
| no | 14 | 29% | 14% | -0.93% | -1.23% | -0.70% | 36% |
| maybe | 4 | 25% | 0% | -0.58% | -0.95% | -0.09% | 50% |

## The 13:16 would-be picks (the comeback bar)

No pick at the 13:16 check-in since 2026-11-16 (CLAUDE.md); the file lists what it would have picked with conviction yes. The pick comes back when 10 of these hold 4 or more that went 1% further their way. So far 1 logged, 0 went 1% further. Every mention counts here, also one that repeats a morning idea.

| date | time | stock | way | move to the close | vs SPY |
|---|---|---|---|---|---|
| 2026-11-16 | 13:17 | MU | put | +0.53% | +0.26% |

## By type

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 50 | 52% | 32% | -0.24% | -0.39% | -0.06% | 54% |
| sector_move | 22 | 45% | 9% | -0.36% | -0.46% | -0.14% | 27% |
| analyst | 15 | 80% | 47% | +1.48% | +1.05% | +1.21% | 73% |
| relative_weakness | 15 | 40% | 13% | -0.51% | -0.63% | -0.48% | 40% |
| sector_intraday | 12 | 58% | 42% | +0.34% | +0.00% | +0.09% | 50% |
| gapdown_rebound | 10 | 40% | 10% | -0.73% | -0.94% | -0.35% | 30% |
| rotation_laggard | 9 | 33% | 11% | -1.38% | -1.83% | -0.59% | 33% |
| peer_readthrough | 9 | 44% | 44% | +1.35% | +0.59% | +0.93% | 56% |
| financing_fade | 8 | 62% | 38% | +0.53% | +0.22% | -0.13% | 50% |
| sympathy | 8 | 62% | 38% | +0.30% | +0.01% | +0.20% | 50% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| earnings_reaction | 5 | 80% | 40% | +1.88% | +0.92% | +1.42% | 80% |
| relative_strength | 4 | 75% | 25% | +0.50% | +0.09% | -0.29% | 25% |
| ma_acquirer | 3 | 67% | 33% | +2.47% | +0.29% | +2.17% | 67% |
| news_heating | 3 | 0% | 0% | -0.64% | -0.92% | +0.08% | 67% |
| other types (fewer than 3 ideas each) | 9 | 22% | 22% | -0.81% | -1.23% | -0.42% | 44% |

## By type, last 10 sessions

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 49 | 51% | 31% | -0.26% | -0.42% | -0.08% | 53% |
| sector_move | 21 | 48% | 10% | -0.31% | -0.41% | -0.09% | 29% |
| relative_weakness | 15 | 40% | 13% | -0.51% | -0.63% | -0.48% | 40% |
| analyst | 14 | 79% | 50% | +1.54% | +1.08% | +1.21% | 71% |
| sector_intraday | 10 | 60% | 40% | +0.41% | +0.00% | +0.08% | 50% |
| sympathy | 8 | 62% | 38% | +0.30% | +0.01% | +0.20% | 50% |
| peer_readthrough | 6 | 67% | 67% | +2.44% | +1.45% | +1.62% | 67% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| rotation_laggard | 6 | 33% | 17% | -1.40% | -2.13% | -0.46% | 33% |
| earnings_reaction | 5 | 80% | 40% | +1.88% | +0.92% | +1.42% | 80% |
| relative_strength | 4 | 75% | 25% | +0.50% | +0.09% | -0.29% | 25% |
| financing_fade | 3 | 67% | 33% | +0.45% | -0.03% | -0.40% | 33% |
| gapdown_rebound | 3 | 0% | 0% | -1.29% | -1.71% | -0.99% | 0% |
| other types (fewer than 3 ideas each) | 7 | 29% | 29% | -0.45% | -0.96% | -0.35% | 43% |

## Why the wrong ones were wrong

20 of 92 wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.

| cause | 中文 | wrong ideas | share | avg move | types it shows up in |
|---|---|---|---|---|---|
| chased | 追在延伸处 | 6 | 30% | -1.96% | relative_weakness 2, sector_intraday 2, company_news 2 |
| priced_in | 已经在价格里 | 3 | 15% | -1.94% | company_news 3 |
| noise | 没有可学的 | 3 | 15% | -0.22% | gapdown_rebound 1, sector_move 1, analyst 1 |
| no_catalyst | 没有自己的消息 | 2 | 10% | -1.53% | company_news 1, relative_weakness 1 |
| timing | 时间不对 | 2 | 10% | -1.16% | company_news 1, gapdown_rebound 1 |
| tide | 被大盘带走 | 2 | 10% | -1.27% | analyst 1, company_news 1 |
| reversal | 逆势 | 1 | 5% | -1.13% | gapdown_rebound 1 |
| misread_news | 消息读反了 | 1 | 5% | -2.22% | company_news 1 |
