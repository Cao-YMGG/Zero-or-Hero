# What the stake buys: our picks under four strike rules
Every sniper (target 0.10 delta) and intraday pick (0.20) since 2026-10-01 at its live entry minute, real option minute bars, costs 10% each way, one contract <= 20% of the main ledger that day. `old` = nearest the target among affordable contracts (live until 11-06); `floor` = the same with |delta| >= 0.06 (live since 11-08); `pct` = strike within 2% of the spot; `nobudget` = the target delta regardless of price. Per $1 of option: n | win% | avg / without the best / without the best two. Sunday test 52; see zoh/research/strikebudget.py.

## sniper (14 picks)

| rule | taken | skipped | median delta | median % OTM | delta < 0.06 | live exit | hold |
|---|---|---|---|---|---|---|---|
| old | 14 | 0 | 0.09 | 4.5% | 4 | 14 | 21% | -32% / -47% / -62% | 14 | 14% | -64% / -74% / -80% |
| floor | 10 | 4 | 0.10 | 3.4% | 0 | 10 | 20% | -37% / -57% / -65% | 10 | 20% | -63% / -77% / -87% |
| pct | 4 | 10 | 0.15 | 1.5% | 0 | 4 | 25% | -55% / -98% / -100% | 4 | 25% | -49% / -98% / -100% |
| nobudget | 14 | 0 | 0.10 | 3.8% | 0 | 14 | 29% | -13% / -35% / -52% | 14 | 21% | -48% / -69% / -79% |

Per-ledger dollars (the stake's whole contracts x the exit): old $-535; floor $-458; pct $-300; 

## intraday (13 picks)

| rule | taken | skipped | median delta | median % OTM | delta < 0.06 | live exit | hold |
|---|---|---|---|---|---|---|---|
| old | 12 | 1 | 0.15 | 2.1% | 1 | 12 | 25% | -28% / -47% / -53% | 12 | 33% | -30% / -47% / -54% |
| floor | 11 | 2 | 0.15 | 1.6% | 0 | 11 | 27% | -22% / -41% / -48% | 11 | 36% | -24% / -42% / -49% |
| pct | 7 | 6 | 0.17 | 1.4% | 0 | 7 | 43% | -21% / -53% / -67% | 7 | 43% | -24% / -53% / -67% |
| nobudget | 13 | 0 | 0.19 | 2.3% | 0 | 13 | 23% | -30% / -46% / -51% | 13 | 31% | -31% / -46% / -51% |

Per-ledger dollars (the stake's whole contracts x the exit): old $-321; floor $-244; pct $-142; 

## all (27 picks)

| rule | taken | skipped | median delta | median % OTM | delta < 0.06 | live exit | hold |
|---|---|---|---|---|---|---|---|
| old | 26 | 1 | 0.10 | 3.1% | 5 | 26 | 23% | -30% / -38% / -47% | 26 | 23% | -49% / -57% / -62% |
| floor | 21 | 6 | 0.11 | 2.6% | 0 | 21 | 24% | -29% / -39% / -49% | 21 | 29% | -43% / -53% / -59% |
| pct | 11 | 16 | 0.17 | 1.5% | 0 | 11 | 36% | -34% / -54% / -68% | 11 | 36% | -33% / -52% / -68% |
| nobudget | 27 | 0 | 0.11 | 2.9% | 0 | 27 | 26% | -21% / -33% / -41% | 27 | 26% | -39% / -50% / -58% |

Per-ledger dollars (the stake's whole contracts x the exit): old $-856; floor $-703; pct $-442; 

## Pick by pick

| day | pick | stock to close | old: delta / %OTM / live | floor | pct | nobudget |
|---|---|---|---|---|---|---|
| 2026-10-07 | sniper MRVL call | +1.3% | 0.10 / 7.6% / +5% | 0.10 / 7.6% / +5% | skip | 0.10 / 7.6% / +5% |
| 2026-10-08 | sniper PLTR call | -0.4% | 0.11 / 6.6% / -93% | 0.11 / 6.6% / -93% | skip | 0.11 / 6.6% / -93% |
| 2026-10-09 | sniper LITE call | -2.0% | 0.01 / 8.3% / -64% | skip | skip | 0.11 / 4.8% / -99% |
| 2026-10-12 | sniper CRM call | -1.6% | 0.05 / 10.5% / -84% | skip | skip | 0.09 / 7.4% / -73% |
| 2026-10-13 | sniper META call | +2.9% | 0.01 / 11.3% / +162% | skip | skip | 0.10 / 3.9% / +273% |
| 2026-10-15 | sniper AAPL call | -1.5% | 0.12 / 2.2% / -95% | 0.12 / 2.2% / -95% | 0.21 / 1.5% / -95% | 0.12 / 2.2% / -95% |
| 2026-10-16 | sniper AAPL call | -1.1% | 0.10 / 1.5% / -100% | 0.10 / 1.5% / -100% | 0.10 / 1.5% / -100% | 0.10 / 1.5% / -100% |
| 2026-10-19 | sniper MSFT call | +0.7% | 0.07 / 1.8% / -100% | 0.07 / 1.8% / -100% | 0.07 / 1.8% / -100% | 0.07 / 1.8% / -100% |
| 2026-10-22 | sniper UNH call | +1.5% | 0.11 / 2.6% / +143% | 0.11 / 2.6% / +143% | 0.23 / 1.4% / +73% | 0.11 / 2.6% / +143% |
| 2026-10-26 | sniper TSLA call | +1.5% | 0.10 / 3.6% / -24% | 0.10 / 3.6% / -24% | skip | 0.10 / 3.6% / -24% |
| 2026-10-27 | sniper AVGO call | +0.8% | 0.10 / 4.5% / -1% | 0.10 / 4.5% / -1% | skip | 0.10 / 4.5% / -1% |
| 2026-10-29 | sniper V call | +0.3% | 0.07 / 3.2% / -91% | 0.07 / 3.2% / -91% | skip | 0.07 / 3.2% / -91% |
| 2026-10-30 | sniper GEV call | +0.7% | 0.06 / 5.7% / -16% | 0.06 / 5.7% / -16% | skip | 0.08 / 5.1% / +166% |
| 2026-11-06 | sniper LLY call | -0.0% | 0.04 / 4.5% / -87% | skip | skip | 0.10 / 3.4% / -99% |
| 2026-10-06 | intraday AVGO call | -0.1% | 0.14 / 2.9% / -1% | 0.14 / 2.9% / -1% | skip | 0.20 / 2.3% / -6% |
| 2026-10-19 | intraday AMZN call | +1.1% | 0.17 / 1.1% / +171% | 0.17 / 1.1% / +171% | 0.17 / 1.1% / +171% | 0.17 / 1.1% / +171% |
| 2026-10-21 | intraday AMD call | -0.3% | 0.15 / 1.5% / +17% | 0.15 / 1.5% / +17% | 0.15 / 1.5% / +17% | 0.25 / 1.0% / +3% |
| 2026-10-22 | intraday MSFT put | -0.3% | 0.19 / 1.6% / +1% | 0.19 / 1.6% / +1% | 0.19 / 1.6% / +1% | 0.19 / 1.6% / +1% |
| 2026-10-23 | intraday ORCL call | -1.0% | 0.14 / 1.2% / -100% | 0.14 / 1.2% / -100% | 0.14 / 1.2% / -100% | 0.14 / 1.2% / -100% |
| 2026-10-26 | intraday INTC call | -1.6% | skip | skip | skip | 0.22 / 10.9% / -28% |
| 2026-10-27 | intraday ORCL call | -0.5% | 0.17 / 9.8% / -17% | 0.17 / 9.8% / -17% | skip | 0.19 / 9.0% / -18% |
| 2026-10-28 | intraday AMAT call | +0.6% | 0.07 / 8.8% / -8% | 0.07 / 8.8% / -8% | skip | 0.14 / 6.3% / -7% |
| 2026-10-29 | intraday ORCL put | +1.3% | 0.21 / 2.7% / -46% | 0.21 / 2.7% / -46% | 0.28 / 2.0% / -37% | 0.21 / 2.7% / -46% |
| 2026-10-30 | intraday AMZN put | +0.9% | 0.11 / 1.4% / -100% | 0.11 / 1.4% / -100% | 0.11 / 1.4% / -100% | 0.11 / 1.4% / -100% |
| 2026-11-02 | intraday AMZN call | -2.9% | 0.28 / 0.7% / -100% | 0.28 / 0.7% / -100% | 0.28 / 0.7% / -100% | 0.28 / 0.7% / -100% |
| 2026-11-06 | intraday GE call | -0.3% | 0.07 / 2.5% / -58% | 0.07 / 2.5% / -58% | skip | 0.07 / 2.5% / -58% |
| 2026-11-06 | intraday MU put | -0.8% | 0.06 / 6.5% / -100% | skip | skip | 0.21 / 2.9% / -99% |
