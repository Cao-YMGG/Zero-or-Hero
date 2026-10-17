# Hot vs cool data days (2026-10-17)

Source: claude-c's export exchange/claude-c/2026-10-16.macro-surprises-2019-12.json (Moomoo
economic calendar: previous / consensus / actual for every CPI and NFP since 2019-12; class:
CPI MoM + core MoM surprise > +0.05 HOT, < -0.05 COOL; NFP > +40K HOT, < -40K COOL). Our free
sources had no consensus, so until now every release day was treated the same. Daily bars: Yahoo.

## SPY on release days, 2019-12 to 2026-10

| CPI | n | gap (open vs prior close) | open -> close | next 2 days |
|---|---|---|---|---|
| HOT | 34 | -0.27%, 41% up | +0.12%, 59% up | +0.31%, 59% up |
| INLINE | 13 | +0.12% | -0.01%, 46% up | -0.85%, 31% up |
| COOL | 34 | +0.42%, 82% up | **-0.34%, 35% up** | **+0.59%, 74% up** |

A cool print is priced in the gap; the session then fades and the gain comes over the next two
days. QQQ is the same shape (COOL open->close 35% up, next 2 days 76% up). NFP is much weaker.

## Our 10:00 follow-the-open entries on release days (half3_hold, opendrive.json, 2024-02+)

| class | 10:00 move | n | avg / -best / -best2 | win |
|---|---|---|---|---|
| HOT | down (put, with the data) | 29 | **+71% / +46% / +30%** | 52% |
| HOT | up (call, against it) | 28 | -74% / -81% / -87% | 14% |
| COOL | up (call, with the data) | 31 | -66% / -75% / -84% | 13% |
| COOL | down (put, against it) | 24 | -16% / -48% / -57% | 25% |
| INLINE | either | 48 | -63% to -81% | 4-12% |

HOT + put is only 12 distinct days (29 trades are 4 symbols on the same days): 2024 -58% (8
trades, 1 win), 2025 +8% (7), 2026 +177% / +130% / +101% (14, 79% win). NFP +92% (20) beats CPI
+25% (9). Same shape as the other plays: it worked in this year's environment, not in 2024.

## What it changes

- Release days are not one environment. HOT with the open already falling is the one place a
  put follows through; COOL and INLINE days lose on every 0DTE follow trade.
- Never chase a cool-print gap up with a 0DTE call. A COOL print is a next-day / two-day call
  (to test: day-after open->close and a 1-2 day option), not a same-day one.
- Live use needs the class at 08:35 the same morning: pre-market routine already reads the
  print; compare actual to consensus with the thresholds above and write it in `reasons`.

## Update 2026-10-17: longer history (claude-c: SPY/QQQ 09:30 / 10:00 / 16:00 on every release day since 2019-12)

**Hot-data put does not hold up on the underlying.** HOT day, SPY below the open at 10:00: the
move kept going to the close on 50% of 20 days (avg +0.03%); QQQ 38% of 21 (reversed on average).
By period SPY 40% (2020-21), 67% (2022-23), 44% (2024-26). The +71% option result above came from
a few days and intraday peaks (half at 3x), not from a reliable afternoon follow-through.
Downgraded: shadow only if at all, never real.

**Cool-print gap up fades, again.** COOL day, SPY above the open at 10:00: kept going 39% of 18
(avg -0.22%; 2024-26 29%). Do not chase a cool print with a 0DTE call.

**The robust one: buy a cool CPI at the close, hold two days.** SPY up 74% of 34 (+0.59%), QQQ
76% (+0.74%), and positive in every period: SPY 67% / 78% / 75% (2020-21 / 2022-23 / 2024-26).
HOT CPI same window is mixed (55-67%); NFP weaker either way. This is a multi-day call, not 0DTE:
test a 1-week ATM call bought at the CPI close with real option prices (16 COOL CPIs since 2024-02).

**Other lists from claude-c:** oil down >= 2% days (99): SMH open->close up only 48%, NVDA 45%;
the 73% is close-to-close and sits in the gap, nothing for a 10:00 entry. TSLA own events (8):
next close vs prior close down 7/8, but next open->close only 5/8 down (-1.7% avg): the drop is in
the overnight gap, so a put bought the next morning catches little of it.
