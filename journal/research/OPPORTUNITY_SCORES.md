# Opportunity scores

273 rows, 221 ideas after dropping later mentions of the same stock and direction on the same day, 2026-10-29 to 2026-11-27 (19 sessions). Moves are the stock from the listed time to the close, signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and `avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by `python -m zoh.research.opportunities`.

## All ideas

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| all ideas | 221 | 51% | 25% | -0.03% | -0.06% | +0.04% | 49% |

## By source

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| premarket | 104 | 52% | 30% | +0.04% | -0.03% | +0.13% | 53% |
| intraday | 97 | 47% | 20% | -0.11% | -0.19% | -0.07% | 42% |
| sniper | 14 | 57% | 36% | +0.07% | -0.20% | +0.26% | 64% |
| review | 6 | 67% | 17% | -0.15% | -0.40% | -0.21% | 50% |

## By direction

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| call | 128 | 47% | 23% | -0.27% | -0.33% | +0.05% | 48% |
| put | 93 | 56% | 28% | +0.31% | +0.22% | +0.04% | 49% |

## By action (picked or only listed)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| none | 195 | 50% | 26% | -0.01% | -0.05% | +0.04% | 47% |
| real | 13 | 54% | 23% | -0.22% | -0.44% | +0.12% | 62% |
| shadow | 12 | 50% | 17% | -0.13% | -0.46% | -0.09% | 58% |
| bot | 1 | 100% | 0% | +0.10% | - | +0.76% | 100% |

## By conviction (what I thought when I listed it; stated since 2026-11-13)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| not stated | 150 | 52% | 26% | +0.04% | -0.01% | +0.04% | 47% |
| no | 27 | 52% | 30% | -0.07% | -0.31% | +0.03% | 52% |
| yes | 25 | 52% | 20% | -0.18% | -0.33% | +0.02% | 60% |
| maybe | 19 | 37% | 21% | -0.33% | -0.80% | +0.13% | 47% |

## By distance from the day's best price when listed (since 2026-11-17)

How far the stock was from its session high (a call) or low (a put) before the listed time: an idea listed at the extreme is one the day's move has already been made for (the post-mortems' top cause is `chased`).

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| at the day's extreme (under 0.25%) | 55 | 44% | 13% | -0.45% | -0.54% | -0.52% | 38% |
| 0.25% to 1% from it | 90 | 59% | 34% | +0.50% | +0.41% | +0.49% | 57% |
| 1% or more from it | 76 | 46% | 24% | -0.35% | -0.45% | -0.08% | 47% |

## After the market (since 2026-11-18, all rows)

The move with beta times SPY's move over the same minutes taken out (60-day beta; these names carry about twice SPY). An idea is mostly a bet on the market that day; this is what is left for the stock itself. A group earns attention when it is positive here, not when the tape happened to go its way.

| group | ideas | positive after the market | avg after the market | w/o best | avg raw move |
|---|---|---|---|---|---|
| all ideas | 221 | 48% | -0.01% | -0.04% | -0.03% |
| picked (sniper or intraday pick) | 25 | 68% | +0.48% | +0.35% | -0.18% |
| listed, not picked | 196 | 46% | -0.07% | -0.10% | -0.01% |
| call | 128 | 49% | +0.22% | +0.17% | -0.27% |
| put | 93 | 47% | -0.32% | -0.39% | +0.31% |
| conviction no | 27 | 52% | +0.55% | +0.34% | -0.07% |
| conviction yes | 25 | 68% | +0.48% | +0.35% | -0.18% |
| conviction maybe | 19 | 26% | -0.12% | -0.40% | -0.33% |
| company_news | 57 | 54% | +0.17% | +0.06% | -0.42% |
| sector_move | 23 | 26% | -0.45% | -0.58% | -0.51% |
| analyst | 21 | 62% | +0.59% | +0.48% | +0.86% |
| sector_intraday | 21 | 38% | -0.44% | -0.55% | +0.72% |
| relative_weakness | 17 | 53% | +0.11% | -0.26% | -0.14% |
| peer_readthrough | 11 | 64% | +0.63% | +0.21% | +1.36% |
| gapdown_rebound | 10 | 60% | +0.59% | +0.33% | -0.73% |
| rotation_laggard | 9 | 33% | -0.77% | -1.16% | -1.38% |
| sympathy | 9 | 33% | +0.15% | -0.31% | -0.51% |
| financing_fade | 8 | 25% | -0.92% | -1.21% | +0.53% |
| sell_the_news | 6 | 50% | -1.38% | -1.88% | -1.64% |
| earnings_reaction | 6 | 67% | +0.23% | -0.17% | +1.72% |
| relative_strength | 6 | 50% | +0.31% | -0.14% | +0.80% |
| ma_acquirer | 3 | 100% | +1.34% | +0.60% | +2.47% |
| news_heating | 3 | 0% | -0.96% | -1.42% | -0.64% |

## The 13:16 would-be picks (the comeback bar)

No pick at the 13:16 check-in since 2026-11-16 (CLAUDE.md); the file lists what it would have picked with conviction yes. The pick comes back when 10 of these hold 4 or more that went 1% further their way. So far 1 logged, 0 went 1% further. Every mention counts here, also one that repeats a morning idea.

| date | time | stock | way | move to the close | vs SPY |
|---|---|---|---|---|---|
| 2026-11-16 | 13:17 | MU | put | +0.53% | +0.26% |

## By type

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 57 | 53% | 28% | -0.42% | -0.56% | -0.15% | 53% |
| sector_move | 23 | 43% | 9% | -0.51% | -0.61% | -0.19% | 26% |
| analyst | 21 | 62% | 33% | +0.86% | +0.53% | +0.83% | 67% |
| sector_intraday | 21 | 57% | 33% | +0.72% | +0.35% | +0.27% | 52% |
| relative_weakness | 17 | 41% | 18% | -0.14% | -0.53% | -0.14% | 41% |
| peer_readthrough | 11 | 45% | 45% | +1.36% | +0.75% | +1.09% | 64% |
| gapdown_rebound | 10 | 40% | 10% | -0.73% | -0.94% | -0.35% | 30% |
| rotation_laggard | 9 | 33% | 11% | -1.38% | -1.83% | -0.59% | 33% |
| sympathy | 9 | 56% | 22% | -0.51% | -0.86% | -0.14% | 44% |
| financing_fade | 8 | 62% | 38% | +0.53% | +0.22% | -0.13% | 50% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| earnings_reaction | 6 | 83% | 33% | +1.72% | +0.92% | +1.18% | 67% |
| relative_strength | 6 | 83% | 50% | +0.80% | +0.62% | +0.40% | 50% |
| ma_acquirer | 3 | 67% | 33% | +2.47% | +0.29% | +2.17% | 67% |
| news_heating | 3 | 0% | 0% | -0.64% | -0.92% | +0.08% | 67% |
| other types (fewer than 3 ideas each) | 11 | 27% | 18% | -0.64% | -0.96% | -0.54% | 45% |

## By type, last 10 sessions

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 31 | 52% | 29% | -0.51% | -0.77% | -0.22% | 55% |
| analyst | 13 | 46% | 31% | +0.41% | +0.13% | +0.66% | 62% |
| sector_intraday | 12 | 50% | 25% | +0.53% | -0.16% | +0.06% | 42% |
| relative_weakness | 11 | 45% | 18% | +0.19% | -0.39% | +0.10% | 36% |
| sector_move | 8 | 50% | 0% | -0.72% | -0.87% | -0.62% | 12% |
| sympathy | 8 | 62% | 25% | -0.54% | -0.95% | -0.14% | 50% |
| peer_readthrough | 3 | 33% | 33% | -0.03% | -1.56% | +0.16% | 67% |
| sell_the_news | 3 | 33% | 0% | -3.86% | -6.17% | -3.52% | 33% |
| gapdown_rebound | 3 | 0% | 0% | -1.29% | -1.71% | -0.99% | 0% |
| relative_strength | 3 | 100% | 100% | +1.51% | +1.40% | +1.57% | 100% |
| other types (fewer than 3 ideas each) | 4 | 75% | 0% | +0.54% | +0.40% | -0.31% | 50% |

## Why the wrong ones were wrong

36 of 109 wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.

| cause | 中文 | wrong ideas | share | avg move | types it shows up in |
|---|---|---|---|---|---|
| chased | 追在延伸处 | 9 | 25% | -1.78% | sector_intraday 4, relative_weakness 2, company_news 2 |
| priced_in | 已经在价格里 | 7 | 19% | -2.62% | company_news 4, analyst 1, sympathy 1 |
| tide | 被大盘带走 | 7 | 19% | -2.02% | analyst 4, company_news 2, sector_move 1 |
| noise | 没有可学的 | 4 | 11% | -0.23% | gapdown_rebound 1, sector_move 1, analyst 1 |
| no_catalyst | 没有自己的消息 | 3 | 8% | -1.25% | relative_weakness 2, company_news 1 |
| timing | 时间不对 | 3 | 8% | -1.07% | company_news 1, gapdown_rebound 1, sector_intraday 1 |
| reversal | 逆势 | 2 | 6% | -1.91% | gapdown_rebound 1, sector_intraday 1 |
| misread_news | 消息读反了 | 1 | 3% | -2.22% | company_news 1 |
