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
