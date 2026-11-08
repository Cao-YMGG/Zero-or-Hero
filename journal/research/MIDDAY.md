# The 11:30 check-in and the 3% line, stock only
30-minute SIP bars 2024-02 to 2026-11-05. Columns: n | share up | average | median. Sunday tests 42 and 48; see zoh/research/midday.py. Stock moves only: a 0.20-delta same-day put turns a -1% stock move into roughly +50-100% and a +0.5% move into -60% or worse (BOUNCE.md), so the win rate below is the floor, not the option's.

## Item 42: SMH above its open at 10:00, below it at 11:00 or 11:30

84 days (2.6 a month; last 3 months: 13).

| leg | n | up | avg | median |
|---|---|---|---|---|
| SMH 11:30 -> close (a put wants negative) | 84 | 63% | +0.26% | +0.23% |
| SMH 13:30 -> close (what the 13:16 check sees) | 84 | 62% | +0.18% | +0.15% |
| weakest chip below its open at 11:30: 11:30 -> close | 80 | 59% | +0.28% | +0.18% |
| the same chip 13:30 -> close | 80 | 50% | +0.19% | +0.02% |
| weakest chip, chip <= -2% from its open at 11:30: 11:30 -> close | 33 | 48% | +0.11% | -0.20% |
| weakest chip, -2% to -1%: 11:30 -> close | 29 | 66% | +0.40% | +0.29% |
| weakest chip, -1% to 0: 11:30 -> close | 18 | 67% | +0.40% | +0.17% |
| last 3 months, SMH 11:30 -> close | 13 | 62% | +0.22% | +0.14% |
| last 3 months, weakest chip 11:30 -> close | 11 | 36% | +0.15% | -0.20% |

Days a month: 2025-12 4, 2026-01 1, 2026-02 2, 2026-03 3, 2026-04 2, 2026-05 2, 2026-06 4, 2026-07 4, 2026-08 3, 2026-09 5, 2026-10 5, 2026-11 1

### Last 3 months, day by day

| day | SMH at 11:30 | SMH 11:30->close | weakest | at 11:30 | 11:30->close | 13:30->close |
|---|---|---|---|---|---|---|
| 2026-08-25 | -0.06% | +0.13% | AVGO | -0.11% | -1.12% | -0.17% |
| 2026-08-26 | +0.04% | +0.15% | AVGO | -1.57% | +1.24% | +1.03% |
| 2026-09-15 | -0.56% | -0.24% | AVGO | -1.52% | -0.58% | +0.30% |
| 2026-09-17 | -0.06% | +0.14% | - | +0.00% | +0.00% | +0.00% |
| 2026-09-24 | +0.02% | +1.49% | AVGO | -0.52% | +0.83% | +0.11% |
| 2026-09-25 | -0.06% | +0.21% | MU | -1.29% | +0.00% | -0.02% |
| 2026-09-30 | -0.12% | -0.08% | AMD | -1.19% | +1.58% | +1.15% |
| 2026-10-02 | -0.05% | -0.19% | MU | -2.81% | -0.20% | -0.41% |
| 2026-10-13 | -0.01% | +1.78% | - | +0.00% | +0.00% | +0.00% |
| 2026-10-22 | -1.66% | -0.91% | AMD | -2.30% | -0.65% | -0.51% |
| 2026-10-28 | +0.00% | +0.67% | AMD | -1.20% | +2.21% | +1.87% |
| 2026-10-30 | -1.28% | -0.60% | NVDA | -1.31% | -0.65% | +0.70% |
| 2026-11-04 | -1.62% | +0.31% | MU | -2.35% | -1.00% | -1.68% |

## Item 48: liquidation days (SMH <= -3% from its open at 10:00): 2 days

| chips by distance from their own open | n | share up | avg | median |
|---|---|---|---|---|
| beyond 3% below at 10:00 (the line excludes them): 10:00 -> close | 7 | 57% | +0.21% | +1.65% |
| within 3% below at 10:00: 10:00 -> close | 1 | 0% | -3.79% | -3.79% |
| above their open at 10:00: 10:00 -> close | - |
| beyond 3% below at 11:00: 11:00 -> close | 5 | 40% | -1.40% | -3.25% |
| within 3% below at 11:00: 11:00 -> close | 3 | 33% | -1.13% | -0.82% |
| above their open at 11:00: 11:00 -> close | - |

| day | SMH at 10:00 | NVDA 10:00 / ->close | AMD | MU | AVGO |
|---|---|---|---|---|---|
| 2025-02-27 | -3.3% | -6.1% / -5.3% | -1.6% / -3.8% | -3.1% / -3.1% | -4.2% / -5.1% |
| 2026-06-25 | -5.3% | -3.9% / +1.8% | -6.7% / +4.9% | -7.8% / +6.7% | -3.5% / +1.7% |
