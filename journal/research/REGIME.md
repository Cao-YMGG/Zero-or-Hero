# Does the market environment pick the play? (2026-10-16, on journal/research/opendrive.json)

Owner's idea: each period has its own play. Tested on the 10:00 follow-the-open entries
(1,331 trades since 2024-02, SPY/QQQ/NVDA/TSLA, 10% costs, non-macro days only). Labels use
only the prior close (no look-ahead): SPY trend = above/below both its 20- and 50-day average,
VIX close (Yahoo daily bars). Each cell: average / without best / without best two.

## 1. Environment labels known in advance: none finds a positive play

| SPY, hold to 15:30 | calls | puts |
|---|---|---|
| uptrend + VIX < 18 | -45% / -70% / -79% (90) | +25% / -35% / -50% (97) |
| downtrend + VIX >= 18 | -45% / -56% / -64% (45) | -29% / -45% / -58% (34) |
| VIX 20-25 (take3 exit) | +14% / +1% / -9% (34) | -69% / -81% / -90% (24) |

The intuitive "uptrend and calm, so buy calls" is one of the worst buckets.

## 2. Hot hand: a rule's recent record does not predict its next trade

Per symbol and side, last N trades (best one dropped) positive vs not, next trade (hold):
N=5 -39% vs -14%; N=10 +47% / +10% / -22% vs -20%; N=20 -21% vs -23%. No persistence.

## 3. What does separate: the day's own strength at 10:00

| calls, hold | 10:00 move from open | n | avg / -best / -best2 | win |
|---|---|---|---|---|
| all symbols | 0-0.3% | 242 | -35% / -51% / -56% | 11% |
| all symbols | 0.5-0.8% | 94 | +8% / -25% / -35% | 20% |
| all symbols | >= 0.8% | 109 | **+21% / +10% / +2%** | 31% |
| SPY (half3_hold) | 0.5-0.8% | 17 | +30% / +4% / -19% | 53% |

Puts lose at every move size, trend and VIX level.

Strong-move calls (>= 0.8%) by half year, hold: 2024H1 -25%, 2024H2 -43%, 2025H1 +30%,
2025H2 -34%, 2026H1 +57% / +22% / -7%, 2026H2 +65% / +29% / -5%. By symbol: TSLA +32% / +10%
/ -9% (50), NVDA +19% / -1% / -19% (39), QQQ -29% (18), SPY only 2 days.

## Verdict

The owner is right that results cluster by period (the strong-drive call worked in 2025H1 and
all of 2026, failed in 2024 and 2025H2). But no label we can see in advance (trend, VIX, the
rule's own recent record) picks the good periods. The usable "environment" is the day itself:
how hard the open drives. So: gate on move size, run several plays at once with their own
ledgers, weight recent live results, and retire a play quickly once its regime check breaks.
Half-year persistence was 1 of 3, so a play that worked for six months can stop without warning.

## 4. Trend days vs chop days (follow the open, or fade it?)

Environment = share of recent 10:00 moves (all four symbols, prior 10 or 20 days) that kept
going until the close (55% overall). If moves have been continuing, follow; if reversing, fade.
- Follow-the-open after "trend" stretches (>= 55%): calls -22% / -29% / -33% (292), puts
  -26% (299). No better than after chop stretches; the best cell was after chop (calls +50% /
  +11% / -21%, n=98), the opposite of the idea and not stable across 10 vs 20 days.
- The regime does not persist: the last 20 days' continuation rate vs the next 20 days
  correlates -0.09 (591 days). 2024H2 had the most continuation (60%) and follow-the-open lost
  the most there: option prices, not direction, decided it.

## Verdict (updated)

Looking back, each period had a play that worked. Looking forward, slow labels (trend, VIX,
trend-vs-chop, a rule's own record) change faster than we can recognise and use them. The
environments we can see in time are the fast ones: that day's calendar (CPI/FOMC, earnings
window, industry event, rotation day; already in CLAUDE.md) and how hard that day's open drives.
