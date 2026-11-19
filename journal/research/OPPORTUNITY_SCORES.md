# Opportunity scores

270 rows, 218 ideas after dropping later mentions of the same stock and direction on the same day, 2026-10-29 to 2026-11-19 (16 sessions). Moves are the stock from the listed time to the close, signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and `avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by `python -m zoh.research.opportunities`.

## All ideas

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| all ideas | 218 | 50% | 25% | -0.05% | -0.09% | +0.04% | 49% |

## By source

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| premarket | 104 | 52% | 30% | +0.06% | -0.01% | +0.14% | 53% |
| intraday | 96 | 47% | 19% | -0.18% | -0.27% | -0.11% | 42% |
| sniper | 12 | 58% | 42% | +0.05% | -0.26% | +0.49% | 67% |
| review | 6 | 67% | 17% | -0.15% | -0.40% | -0.21% | 50% |

## By direction

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| call | 126 | 47% | 24% | -0.27% | -0.33% | +0.07% | 48% |
| put | 92 | 55% | 27% | +0.24% | +0.15% | +0.00% | 49% |

## By action (picked or only listed)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| none | 194 | 50% | 26% | -0.04% | -0.08% | +0.03% | 47% |
| real | 13 | 54% | 23% | -0.22% | -0.44% | +0.12% | 62% |
| shadow | 10 | 50% | 20% | -0.18% | -0.59% | +0.11% | 60% |
| bot | 1 | 100% | 0% | +0.10% | - | +0.76% | 100% |

## By conviction (what I thought when I listed it; stated since 2026-11-13)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| not stated | 150 | 52% | 26% | +0.04% | -0.01% | +0.04% | 47% |
| no | 27 | 52% | 30% | -0.07% | -0.31% | +0.03% | 52% |
| yes | 23 | 52% | 22% | -0.20% | -0.37% | +0.12% | 61% |
| maybe | 18 | 33% | 17% | -0.63% | -1.15% | +0.00% | 44% |

## By distance from the day's best price when listed (since 2026-11-17)

How far the stock was from its session high (a call) or low (a put) before the listed time: an idea listed at the extreme is one the day's move has already been made for (the post-mortems' top cause is `chased`).

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| at the day's extreme (under 0.25%) | 53 | 43% | 13% | -0.47% | -0.56% | -0.50% | 38% |
| 0.25% to 1% from it | 89 | 58% | 34% | +0.44% | +0.35% | +0.47% | 56% |
| 1% or more from it | 76 | 46% | 24% | -0.34% | -0.44% | -0.08% | 47% |

## After the market (since 2026-11-18, all rows)

The move with beta times SPY's move over the same minutes taken out (60-day beta; these names carry about twice SPY). An idea is mostly a bet on the market that day; this is what is left for the stock itself. A group earns attention when it is positive here, not when the tape happened to go its way.

| group | ideas | positive after the market | avg after the market | w/o best | avg raw move |
|---|---|---|---|---|---|
| all ideas | 218 | 48% | -0.00% | -0.03% | -0.05% |
| picked (sniper or intraday pick) | 23 | 65% | +0.48% | +0.35% | -0.20% |
| listed, not picked | 195 | 46% | -0.06% | -0.09% | -0.04% |
| call | 126 | 48% | +0.22% | +0.17% | -0.27% |
| put | 92 | 48% | -0.30% | -0.37% | +0.24% |
| conviction no | 27 | 52% | +0.55% | +0.34% | -0.07% |
| conviction yes | 23 | 65% | +0.48% | +0.35% | -0.20% |
| conviction maybe | 18 | 28% | +0.01% | -0.28% | -0.63% |
| company_news | 57 | 54% | +0.17% | +0.06% | -0.39% |
| sector_move | 23 | 26% | -0.45% | -0.58% | -0.53% |
| analyst | 21 | 62% | +0.59% | +0.48% | +0.86% |
| sector_intraday | 20 | 40% | -0.34% | -0.45% | +0.43% |
| relative_weakness | 17 | 53% | +0.11% | -0.26% | -0.14% |
| peer_readthrough | 11 | 64% | +0.63% | +0.21% | +1.36% |
| gapdown_rebound | 10 | 60% | +0.59% | +0.33% | -0.73% |
| rotation_laggard | 9 | 33% | -0.77% | -1.16% | -1.38% |
| sympathy | 9 | 33% | +0.15% | -0.31% | -0.49% |
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
| company_news | 57 | 53% | 28% | -0.39% | -0.53% | -0.13% | 53% |
| sector_move | 23 | 43% | 9% | -0.53% | -0.63% | -0.22% | 26% |
| analyst | 21 | 62% | 33% | +0.86% | +0.53% | +0.83% | 67% |
| sector_intraday | 20 | 55% | 30% | +0.43% | +0.02% | +0.13% | 50% |
| relative_weakness | 17 | 41% | 18% | -0.14% | -0.53% | -0.14% | 41% |
| peer_readthrough | 11 | 45% | 45% | +1.36% | +0.75% | +1.09% | 64% |
| gapdown_rebound | 10 | 40% | 10% | -0.73% | -0.94% | -0.35% | 30% |
| rotation_laggard | 9 | 33% | 11% | -1.38% | -1.83% | -0.59% | 33% |
| sympathy | 9 | 56% | 22% | -0.49% | -0.84% | -0.14% | 44% |
| financing_fade | 8 | 62% | 38% | +0.53% | +0.22% | -0.13% | 50% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| earnings_reaction | 6 | 83% | 33% | +1.72% | +0.92% | +1.18% | 67% |
| relative_strength | 6 | 83% | 50% | +0.80% | +0.62% | +0.40% | 50% |
| ma_acquirer | 3 | 67% | 33% | +2.47% | +0.29% | +2.17% | 67% |
| news_heating | 3 | 0% | 0% | -0.64% | -0.92% | +0.08% | 67% |
| other types (fewer than 3 ideas each) | 9 | 22% | 22% | -0.81% | -1.23% | -0.42% | 44% |

## By type, last 10 sessions

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 50 | 56% | 28% | -0.25% | -0.41% | -0.15% | 50% |
| analyst | 19 | 58% | 37% | +0.88% | +0.51% | +0.81% | 63% |
| relative_weakness | 17 | 41% | 18% | -0.14% | -0.53% | -0.14% | 41% |
| sector_intraday | 15 | 47% | 20% | +0.16% | -0.41% | -0.13% | 40% |
| sector_move | 13 | 54% | 0% | -0.50% | -0.57% | -0.34% | 23% |
| sympathy | 9 | 56% | 22% | -0.49% | -0.84% | -0.14% | 44% |
| relative_strength | 6 | 83% | 50% | +0.80% | +0.62% | +0.40% | 50% |
| peer_readthrough | 4 | 50% | 50% | +1.10% | -0.03% | +0.86% | 75% |
| sell_the_news | 4 | 25% | 0% | -3.74% | -5.24% | -3.10% | 25% |
| gapdown_rebound | 3 | 0% | 0% | -1.29% | -1.71% | -0.99% | 0% |
| other types (fewer than 3 ideas each) | 11 | 36% | 18% | -0.34% | -0.63% | -0.28% | 36% |

## Why the wrong ones were wrong

31 of 108 wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.

| cause | 中文 | wrong ideas | share | avg move | types it shows up in |
|---|---|---|---|---|---|
| chased | 追在延伸处 | 9 | 29% | -1.78% | sector_intraday 4, relative_weakness 2, company_news 2 |
| tide | 被大盘带走 | 5 | 16% | -0.91% | analyst 4, company_news 1 |
| priced_in | 已经在价格里 | 4 | 13% | -1.79% | company_news 3, analyst 1 |
| noise | 没有可学的 | 4 | 13% | -0.23% | gapdown_rebound 1, sector_move 1, analyst 1 |
| no_catalyst | 没有自己的消息 | 3 | 10% | -1.25% | relative_weakness 2, company_news 1 |
| timing | 时间不对 | 3 | 10% | -1.07% | company_news 1, gapdown_rebound 1, sector_intraday 1 |
| reversal | 逆势 | 2 | 6% | -1.91% | gapdown_rebound 1, sector_intraday 1 |
| misread_news | 消息读反了 | 1 | 3% | -2.22% | company_news 1 |
