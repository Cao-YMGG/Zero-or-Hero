# A rating change from a price a buyer can have (2026-11-19)

R4 quoted "+0.92% open to close over 340 upgrades". Those events were kept only when the stock was not against the
rating at 09:32 (slowdrift.gather), and the first two minutes that pass the gate were inside the number. Two runs,
both after 0.1% a round trip, stock only. Scripts in the scratchpad (t76_collect, t76_analyse, t79_collect,
t79_analyse); SUNDAY_TESTS 76 and 78 hold the bars, written before the numbers were read.

## 1. Two years, the stored gated sample (502 events, 105 large caps outside our 25, minute bars)

| | events | from 09:30 | from 09:32 | from 09:35 | from 09:45 | from 10:00 |
|---|---|---|---|---|---|---|
| upgrades, gap under 3% | 219 | +0.61% (64% right) | **+0.04%** (50% right, -0.13% without the best five) | +0.02% | +0.01% | -0.01% |
| upgrades, every gap | 278 | +0.78% | +0.11% (-0.05%) | | | -0.08% |
| upgrades, gap 3% or more | 59 | +1.39% | +0.36% (-0.31%) | | | -0.32% |
| downgrades shorted, before 2026-04-29 | 153 | +0.67% | -0.02% (-0.25%) | -0.11% | -0.11% | **-0.15%** (47% right, -0.33%) |

Upgrades with a gap under 3%, from 09:32: SPY month rising -0.04% (145), falling +0.20% (74; -0.20% without the best
five); before 2026-04-29 -0.04% (176), since +0.39% (43; -0.23% without the best five); last 3 months -0.21% (13).
Minus SPY over the same minutes: -0.05%.

Bar (b) of item 78 (at least +0.30% from 09:32, positive without the best five, in both kinds of month): **failed**.
The from-the-open number is the gate's own first two minutes.

## 2. No gate, 2026-05 to 2026-11 (all the news endpoint gave on 2026-11-19: 124 upgrades, 121 downgrades, 130 names)

The endpoint returned nothing before 2026-04-29, and 33 of the 125 stored events of the same window were not in it,
so this is a partial draw of half a year, not the two-year ungated set item 76 asked for.

| upgrades | events | result |
|---|---|---|
| every one, at the 09:30 VWAP | 124 | +0.26%, 52% right, median 0.00%, -0.08% without the best five |
| pass the 09:32 gate (44%), from the open | 55 | +1.24% (first two minutes +0.69%) |
| pass the gate, from 09:32 | 55 | +0.54%, 53% right, -0.13% without the best five |
| fail the gate, from the open | 69 | -0.52% |
| gap under 3%, no gate, VWAP | 100 | -0.05%, 46% right |
| gap under 3%, gate, from 09:32 | 42 | +0.03%, 48% right |
| gap 3% or more, no gate, VWAP | 22 | +1.83%, 73% right, -0.06% without the best five (PLTR 08-04, ABNB 08-07: days after a report) |
| last 3 months, no gate, VWAP | 51 | +0.08% |

As an account (each day's events in equal parts, cash on other days): every upgrade at the VWAP +24.9% over the
six and a half months and -1.2% without its three best days; SPY held +2.1%.

Bar of item 76 (from the VWAP at least +0.30% over 300 events, both kinds of month, both groups of names, without
the best five): **failed** on the 124 events there were.

Downgrades shorted: nothing from the open (+0.03%); from 10:00 +0.38% (58% right, +0.22% without the best five, both
halves of the window positive). That was the best of fourteen cells read after the fact. On the 153 stored events
before 2026-04-29 (not looked at) it is -0.15%: bar (a) of item 78 **failed**, and the pattern is dropped.

## What it says

1. A rating change moves the stock in the gap and the first two minutes. From 09:32 on there is nothing a buyer can
   take after cost, in rising or in falling months, with or without the gate.
2. The gate does not create an edge; it marks the events that have already moved.
3. Two patterns found tonight after the fact (the late short on downgrades; the big-gap upgrade days) did not hold on
   events they were not found on.
4. Not tested here: option prices. rating_open (T4) keeps its shadow samples until SUNDAY_TESTS 70 runs.
