# Opportunity scores

251 rows, 201 ideas after dropping later mentions of the same stock and direction on the same day, 2026-10-29 to 2026-11-17 (14 sessions). Moves are the stock from the listed time to the close, signed the idea's way. `right` = closed the right side of the entry; `paid` = moved at least +1% the idea's way, about what a same-day 0.35-delta option needs (OPENGATE.md); `avg vs SPY` = the move minus what SPY did over the same minutes, signed the same way, so a put on a day everything fell gets no credit for the tape; `beat SPY` = share with that number above zero. A type earns attention at 20 ideas with `paid` and `avg vs SPY` both above the all-ideas line, and without its best idea. Rebuilt by `python -m zoh.research.opportunities`.

## All ideas

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| all ideas | 201 | 52% | 27% | -0.00% | -0.04% | +0.04% | 49% |

## By source

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| premarket | 100 | 54% | 32% | +0.23% | +0.15% | +0.21% | 55% |
| intraday | 84 | 46% | 19% | -0.28% | -0.33% | -0.21% | 40% |
| sniper | 11 | 64% | 45% | +0.11% | -0.23% | +0.53% | 64% |
| review | 6 | 67% | 17% | -0.15% | -0.40% | -0.21% | 50% |

## By direction

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| call | 116 | 48% | 25% | -0.13% | -0.19% | +0.11% | 48% |
| put | 85 | 56% | 29% | +0.17% | +0.08% | -0.06% | 51% |

## By action (picked or only listed)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| none | 184 | 52% | 27% | +0.02% | -0.02% | +0.02% | 48% |
| real | 10 | 50% | 30% | -0.33% | -0.64% | +0.16% | 60% |
| shadow | 6 | 50% | 33% | -0.12% | -0.84% | +0.16% | 50% |
| bot | 1 | 100% | 0% | +0.10% | - | +0.76% | 100% |

## By conviction (what I thought when I listed it; stated since 2026-11-13)

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| not stated | 155 | 54% | 28% | +0.10% | +0.05% | +0.08% | 48% |
| no | 21 | 48% | 24% | -0.43% | -0.60% | -0.34% | 48% |
| yes | 16 | 50% | 31% | -0.25% | -0.50% | +0.16% | 56% |
| maybe | 9 | 33% | 0% | -0.33% | -0.49% | -0.01% | 56% |

## By distance from the day's best price when listed (since 2026-11-17)

How far the stock was from its session high (a call) or low (a put) before the listed time: an idea listed at the extreme is one the day's move has already been made for (the post-mortems' top cause is `chased`).

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| at the day's extreme (under 0.25%) | 52 | 44% | 17% | -0.43% | -0.52% | -0.47% | 37% |
| 0.25% to 1% from it | 78 | 60% | 33% | +0.45% | +0.36% | +0.42% | 58% |
| 1% or more from it | 71 | 48% | 27% | -0.19% | -0.30% | -0.01% | 49% |

## The 13:16 would-be picks (the comeback bar)

No pick at the 13:16 check-in since 2026-11-16 (CLAUDE.md); the file lists what it would have picked with conviction yes. The pick comes back when 10 of these hold 4 or more that went 1% further their way. So far 1 logged, 0 went 1% further. Every mention counts here, also one that repeats a morning idea.

| date | time | stock | way | move to the close | vs SPY |
|---|---|---|---|---|---|
| 2026-11-16 | 13:17 | MU | put | +0.53% | +0.26% |

## By type

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 52 | 54% | 33% | -0.19% | -0.34% | -0.05% | 54% |
| sector_move | 22 | 45% | 9% | -0.36% | -0.46% | -0.14% | 27% |
| analyst | 19 | 63% | 37% | +0.96% | +0.60% | +0.93% | 68% |
| sector_intraday | 16 | 62% | 38% | +0.34% | +0.09% | +0.05% | 56% |
| relative_weakness | 15 | 40% | 13% | -0.51% | -0.63% | -0.48% | 40% |
| gapdown_rebound | 10 | 40% | 10% | -0.73% | -0.94% | -0.35% | 30% |
| rotation_laggard | 9 | 33% | 11% | -1.38% | -1.83% | -0.59% | 33% |
| peer_readthrough | 9 | 44% | 44% | +1.35% | +0.60% | +0.93% | 56% |
| sympathy | 9 | 67% | 33% | +0.31% | +0.05% | +0.33% | 56% |
| financing_fade | 8 | 62% | 38% | +0.53% | +0.22% | -0.13% | 50% |
| sell_the_news | 6 | 50% | 17% | -1.64% | -2.87% | -1.67% | 50% |
| earnings_reaction | 6 | 83% | 33% | +1.72% | +0.92% | +1.18% | 67% |
| relative_strength | 5 | 80% | 40% | +0.65% | +0.38% | +0.13% | 40% |
| ma_acquirer | 3 | 67% | 33% | +2.47% | +0.29% | +2.17% | 67% |
| news_heating | 3 | 0% | 0% | -0.64% | -0.92% | +0.08% | 67% |
| other types (fewer than 3 ideas each) | 9 | 22% | 22% | -0.81% | -1.23% | -0.42% | 44% |

## By type, last 10 sessions

| group | ideas | right | paid (>= +1%) | avg move | avg w/o best | avg vs SPY | beat SPY |
|---|---|---|---|---|---|---|---|
| company_news | 51 | 53% | 31% | -0.22% | -0.37% | -0.08% | 53% |
| sector_move | 21 | 48% | 10% | -0.31% | -0.41% | -0.09% | 29% |
| analyst | 17 | 59% | 41% | +1.00% | +0.59% | +0.91% | 65% |
| relative_weakness | 15 | 40% | 13% | -0.51% | -0.63% | -0.48% | 40% |
| sector_intraday | 13 | 62% | 38% | +0.41% | +0.11% | +0.02% | 54% |
| sympathy | 9 | 67% | 33% | +0.31% | +0.05% | +0.33% | 56% |
| earnings_reaction | 5 | 100% | 40% | +2.09% | +1.18% | +1.43% | 80% |
| peer_readthrough | 5 | 80% | 80% | +3.09% | +2.01% | +2.12% | 80% |
| rotation_laggard | 5 | 20% | 20% | -1.74% | -2.74% | -0.62% | 20% |
| sell_the_news | 5 | 40% | 20% | -2.09% | -3.74% | -2.14% | 40% |
| relative_strength | 5 | 80% | 40% | +0.65% | +0.38% | +0.13% | 40% |
| gapdown_rebound | 3 | 0% | 0% | -1.29% | -1.71% | -0.99% | 0% |
| other types (fewer than 3 ideas each) | 8 | 38% | 25% | -0.39% | -0.82% | -0.62% | 38% |

## Why the wrong ones were wrong

25 of 97 wrong ideas have a post-mortem (journal/opportunity_reviews.csv, written each evening since 2026-11-13). One cause each; a cause that keeps coming back is a habit to change.

| cause | 中文 | wrong ideas | share | avg move | types it shows up in |
|---|---|---|---|---|---|
| chased | 追在延伸处 | 7 | 28% | -1.83% | relative_weakness 2, sector_intraday 2, company_news 2 |
| priced_in | 已经在价格里 | 4 | 16% | -1.79% | company_news 3, analyst 1 |
| tide | 被大盘带走 | 4 | 16% | -1.00% | analyst 3, company_news 1 |
| noise | 没有可学的 | 3 | 12% | -0.22% | gapdown_rebound 1, sector_move 1, analyst 1 |
| no_catalyst | 没有自己的消息 | 2 | 8% | -1.53% | company_news 1, relative_weakness 1 |
| reversal | 逆势 | 2 | 8% | -1.91% | gapdown_rebound 1, sector_intraday 1 |
| timing | 时间不对 | 2 | 8% | -1.16% | company_news 1, gapdown_rebound 1 |
| misread_news | 消息读反了 | 1 | 4% | -2.22% | company_news 1 |
