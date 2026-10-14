# Follow the open on real 0DTE option prices

Rule: at 10:00 ET buy a same-day call if the underlying is above its open (put if below; skip if within 0.1%), strike ~0.7% out of the money; sell at 3x entry, else at 15:30. SPY/QQQ every weekday; NVDA/TSLA on same-day expiry days (Fridays; Mon/Wed too since 2026-01-26). Real 1-minute option closes, 10% slippage each way in the tables (5% in opendrive.json). Macro calendar: config/macro_events.json plus 2024-25 CPI/NFP/FOMC dates.

Skipped: {'no_bars': 0, 'no_option': 16}. Data through 2026-10-13.

## all

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 160 | 24% | -18% | -21% | -22% | -95% | +305% |
| all days | last year | 593 | 24% | -23% | -24% | -25% | -96% | +547% |
| all days | since 2024-02 | 1325 | 23% | -27% | -28% | -28% | -96% | +1205% |
| puts (below the open at 10:00) | last 3 months | 86 | 20% | -33% | -36% | -40% | -97% | +305% |
| puts (below the open at 10:00) | last year | 273 | 22% | -28% | -30% | -31% | -95% | +547% |
| puts (below the open at 10:00) | since 2024-02 | 648 | 24% | -22% | -23% | -23% | -95% | +547% |
| calls (above the open at 10:00) | last 3 months | 74 | 30% | -2% | -6% | -9% | -94% | +260% |
| calls (above the open at 10:00) | last year | 320 | 25% | -19% | -21% | -22% | -98% | +419% |
| calls (above the open at 10:00) | since 2024-02 | 677 | 22% | -31% | -33% | -34% | -98% | +1205% |
| macro days | last 3 months | 25 | 8% | -76% | -88% | -92% | -100% | +211% |
| macro days | last year | 80 | 19% | -43% | -47% | -50% | -99% | +271% |
| macro days | since 2024-02 | 191 | 17% | -46% | -48% | -50% | -98% | +307% |
| gap and 10:00 move agree | last 3 months | 86 | 27% | -9% | -12% | -16% | -95% | +305% |
| gap and 10:00 move agree | last year | 311 | 24% | -23% | -24% | -25% | -96% | +385% |
| gap and 10:00 move agree | since 2024-02 | 667 | 23% | -25% | -26% | -27% | -97% | +1205% |
| gap and 10:00 move disagree | last 3 months | 73 | 22% | -29% | -33% | -37% | -96% | +250% |
| gap and 10:00 move disagree | last year | 277 | 23% | -22% | -24% | -26% | -96% | +547% |
| gap and 10:00 move disagree | since 2024-02 | 648 | 22% | -28% | -29% | -30% | -96% | +547% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 4 | 25% | -44% | -62% | -71% | -51% | +12% |
| like 2026-10-14 (macro, gap down, below open) | last year | 17 | 35% | -1% | -15% | -29% | -57% | +218% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 41 | 32% | -7% | -13% | -19% | -85% | +235% |
| gap down + below open (any day) | last 3 months | 38 | 26% | -8% | -17% | -25% | -89% | +305% |
| gap down + below open (any day) | last year | 121 | 24% | -23% | -26% | -28% | -90% | +305% |
| gap down + below open (any day) | since 2024-02 | 266 | 27% | -13% | -14% | -15% | -93% | +305% |

## SPY

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 40 | 22% | -21% | -28% | -35% | -100% | +250% |
| all days | last year | 178 | 21% | -28% | -31% | -34% | -98% | +547% |
| all days | since 2024-02 | 430 | 20% | -33% | -36% | -37% | -98% | +1205% |
| puts (below the open at 10:00) | last 3 months | 22 | 9% | -64% | -78% | -92% | -100% | +244% |
| puts (below the open at 10:00) | last year | 77 | 18% | -34% | -42% | -46% | -97% | +547% |
| puts (below the open at 10:00) | since 2024-02 | 210 | 20% | -33% | -35% | -37% | -97% | +547% |
| calls (above the open at 10:00) | last 3 months | 18 | 39% | +31% | +18% | +4% | -74% | +250% |
| calls (above the open at 10:00) | last year | 101 | 23% | -24% | -28% | -32% | -100% | +419% |
| calls (above the open at 10:00) | since 2024-02 | 220 | 20% | -33% | -39% | -41% | -100% | +1205% |
| macro days | last 3 months | 3 | 0% | -86% | -100% | -100% | -100% | -57% |
| macro days | last year | 19 | 16% | -44% | -61% | -78% | -100% | +271% |
| macro days | since 2024-02 | 55 | 15% | -52% | -58% | -63% | -99% | +271% |
| gap and 10:00 move agree | last 3 months | 22 | 27% | -8% | -19% | -30% | -94% | +230% |
| gap and 10:00 move agree | last year | 89 | 19% | -36% | -41% | -45% | -99% | +384% |
| gap and 10:00 move agree | since 2024-02 | 211 | 19% | -30% | -36% | -38% | -99% | +1205% |
| gap and 10:00 move disagree | last 3 months | 18 | 17% | -38% | -54% | -73% | -100% | +250% |
| gap and 10:00 move disagree | last year | 88 | 23% | -19% | -26% | -31% | -97% | +547% |
| gap and 10:00 move disagree | since 2024-02 | 215 | 20% | -34% | -37% | -39% | -97% | +547% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 1 | 0% | -57% | +nan% | +nan% | -57% | -57% |
| like 2026-10-14 (macro, gap down, below open) | last year | 4 | 25% | -12% | -85% | -99% | -78% | +205% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 12 | 25% | -12% | -33% | -56% | -80% | +211% |
| gap down + below open (any day) | last 3 months | 10 | 10% | -59% | -88% | -92% | -94% | +200% |
| gap down + below open (any day) | last year | 31 | 16% | -45% | -54% | -63% | -96% | +225% |
| gap down + below open (any day) | since 2024-02 | 79 | 23% | -22% | -25% | -29% | -97% | +259% |

## QQQ

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 52 | 23% | -16% | -23% | -28% | -96% | +305% |
| all days | last year | 202 | 22% | -23% | -25% | -27% | -96% | +385% |
| all days | since 2024-02 | 526 | 22% | -28% | -29% | -29% | -96% | +385% |
| puts (below the open at 10:00) | last 3 months | 28 | 18% | -34% | -46% | -57% | -98% | +305% |
| puts (below the open at 10:00) | last year | 91 | 20% | -30% | -34% | -37% | -96% | +305% |
| puts (below the open at 10:00) | since 2024-02 | 260 | 23% | -22% | -23% | -25% | -96% | +307% |
| calls (above the open at 10:00) | last 3 months | 24 | 29% | +4% | -7% | -19% | -93% | +260% |
| calls (above the open at 10:00) | last year | 111 | 24% | -17% | -21% | -25% | -94% | +385% |
| calls (above the open at 10:00) | since 2024-02 | 266 | 20% | -33% | -35% | -37% | -98% | +385% |
| macro days | last 3 months | 8 | 0% | -97% | -98% | -99% | -99% | -87% |
| macro days | last year | 22 | 18% | -38% | -50% | -62% | -98% | +209% |
| macro days | since 2024-02 | 62 | 18% | -40% | -46% | -51% | -98% | +307% |
| gap and 10:00 move agree | last 3 months | 24 | 29% | +5% | -8% | -20% | -94% | +305% |
| gap and 10:00 move agree | last year | 102 | 25% | -17% | -21% | -24% | -96% | +385% |
| gap and 10:00 move agree | since 2024-02 | 255 | 23% | -27% | -29% | -30% | -97% | +385% |
| gap and 10:00 move disagree | last 3 months | 27 | 19% | -33% | -44% | -55% | -98% | +250% |
| gap and 10:00 move disagree | last year | 98 | 19% | -28% | -32% | -35% | -96% | +377% |
| gap and 10:00 move disagree | since 2024-02 | 267 | 21% | -29% | -30% | -31% | -96% | +377% |
| like 2026-10-14 (macro, gap down, below open) | last year | 3 | 67% | +104% | +52% | -98% | +202% | +209% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 10 | 40% | +12% | -11% | -39% | -93% | +222% |
| gap down + below open (any day) | last 3 months | 10 | 30% | +13% | -19% | -49% | -92% | +305% |
| gap down + below open (any day) | last year | 38 | 24% | -17% | -26% | -32% | -96% | +305% |
| gap down + below open (any day) | since 2024-02 | 101 | 27% | -12% | -15% | -18% | -95% | +305% |

## NVDA

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 31 | 29% | +4% | -5% | -15% | -88% | +276% |
| all days | last year | 100 | 27% | -16% | -19% | -22% | -88% | +276% |
| all days | since 2024-02 | 175 | 27% | -15% | -17% | -19% | -92% | +276% |
| puts (below the open at 10:00) | last 3 months | 16 | 31% | +19% | +1% | -18% | -77% | +276% |
| puts (below the open at 10:00) | last year | 47 | 26% | -16% | -22% | -29% | -85% | +276% |
| puts (below the open at 10:00) | since 2024-02 | 82 | 32% | +1% | -2% | -5% | -85% | +276% |
| calls (above the open at 10:00) | last 3 months | 15 | 27% | -11% | -29% | -49% | -98% | +235% |
| calls (above the open at 10:00) | last year | 53 | 28% | -16% | -20% | -25% | -94% | +235% |
| calls (above the open at 10:00) | since 2024-02 | 93 | 24% | -30% | -33% | -36% | -96% | +235% |
| macro days | last 3 months | 7 | 0% | -98% | -100% | -100% | -100% | -85% |
| macro days | last year | 19 | 16% | -55% | -70% | -86% | -100% | +218% |
| macro days | since 2024-02 | 36 | 11% | -62% | -70% | -79% | -98% | +235% |
| gap and 10:00 move agree | last 3 months | 21 | 29% | +3% | -11% | -26% | -88% | +276% |
| gap and 10:00 move agree | last year | 57 | 28% | -7% | -12% | -18% | -88% | +276% |
| gap and 10:00 move agree | since 2024-02 | 97 | 28% | -11% | -14% | -17% | -92% | +276% |
| gap and 10:00 move disagree | last 3 months | 10 | 30% | +6% | -19% | -47% | -71% | +232% |
| gap and 10:00 move disagree | last year | 42 | 26% | -25% | -32% | -39% | -84% | +274% |
| gap and 10:00 move disagree | since 2024-02 | 77 | 27% | -20% | -24% | -27% | -93% | +274% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 1 | 0% | -85% | +nan% | +nan% | -85% | -85% |
| like 2026-10-14 (macro, gap down, below open) | last year | 3 | 33% | +29% | -65% | -85% | -45% | +218% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 8 | 25% | -5% | -39% | -82% | -76% | +235% |
| gap down + below open (any day) | last 3 months | 9 | 44% | +63% | +37% | +3% | -68% | +276% |
| gap down + below open (any day) | last year | 22 | 32% | +12% | -1% | -14% | -68% | +276% |
| gap down + below open (any day) | since 2024-02 | 39 | 36% | +20% | +13% | +6% | -68% | +276% |

## TSLA

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 37 | 24% | -37% | -45% | -52% | -95% | +226% |
| all days | last year | 113 | 28% | -22% | -24% | -26% | -92% | +226% |
| all days | since 2024-02 | 194 | 28% | -20% | -21% | -22% | -92% | +235% |
| puts (below the open at 10:00) | last 3 months | 20 | 25% | -37% | -50% | -64% | -83% | +203% |
| puts (below the open at 10:00) | last year | 58 | 28% | -24% | -29% | -33% | -86% | +214% |
| puts (below the open at 10:00) | since 2024-02 | 96 | 29% | -18% | -21% | -23% | -86% | +235% |
| calls (above the open at 10:00) | last 3 months | 17 | 24% | -38% | -54% | -72% | -98% | +226% |
| calls (above the open at 10:00) | last year | 55 | 29% | -19% | -23% | -28% | -97% | +226% |
| calls (above the open at 10:00) | since 2024-02 | 98 | 27% | -22% | -24% | -27% | -97% | +226% |
| macro days | last 3 months | 7 | 29% | -27% | -66% | -82% | -65% | +211% |
| macro days | last year | 20 | 25% | -35% | -48% | -63% | -98% | +211% |
| macro days | since 2024-02 | 38 | 24% | -33% | -39% | -46% | -98% | +211% |
| gap and 10:00 move agree | last 3 months | 19 | 21% | -40% | -55% | -70% | -98% | +226% |
| gap and 10:00 move agree | last year | 63 | 27% | -26% | -30% | -34% | -89% | +226% |
| gap and 10:00 move agree | since 2024-02 | 104 | 29% | -18% | -21% | -23% | -86% | +226% |
| gap and 10:00 move disagree | last 3 months | 18 | 28% | -35% | -49% | -64% | -92% | +203% |
| gap and 10:00 move disagree | last year | 49 | 31% | -15% | -20% | -25% | -92% | +222% |
| gap and 10:00 move disagree | since 2024-02 | 89 | 27% | -21% | -23% | -26% | -95% | +235% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 2 | 50% | -17% | -46% | +nan% | -17% | +12% |
| like 2026-10-14 (macro, gap down, below open) | last year | 7 | 29% | -52% | -68% | -84% | -86% | +41% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 11 | 36% | -20% | -43% | -63% | -86% | +208% |
| gap down + below open (any day) | last 3 months | 9 | 22% | -48% | -68% | -80% | -74% | +118% |
| gap down + below open (any day) | last year | 30 | 27% | -34% | -42% | -51% | -83% | +214% |
| gap down + below open (any day) | since 2024-02 | 47 | 28% | -28% | -34% | -39% | -84% | +220% |

## Every 'like 2026-10-14' trade

| day | sym | macro | gap | 10:00 move | contract | entry | max x | pnl (10%) | exit |
|---|---|---|---|---|---|---|---|---|---|
| 2024-02-13 | SPY | CPI | -1.3% | -0.1% | SPY240213P00490000 | 0.15 | 1.8 | -52% | time |
| 2024-05-01 | QQQ | FOMC | -0.3% | -0.1% | QQQ240501P00420000 | 1.33 | 1.27 | -100% | time |
| 2024-05-01 | SPY | FOMC | -0.1% | -0.1% | SPY240501P00497000 | 0.79 | 1.09 | -100% | time |
| 2024-06-07 | NVDA | NFP | -1.0% | -0.6% | NVDA240607P01185000 | 7.55 | 1.16 | -99% | time |
| 2024-08-02 | QQQ | NFP | -1.9% | -0.4% | QQQ240802P00446000 | 1.75 | 2.3 | -91% | time |
| 2024-08-02 | SPY | NFP | -1.3% | -0.3% | SPY240802P00530000 | 1.08 | 2.94 | -78% | time |
| 2024-08-02 | TSLA | NFP | -0.9% | -0.4% | TSLA240802P00212500 | 1.95 | 3.42 | +133% | time |
| 2024-09-06 | QQQ | NFP | -0.1% | -1.0% | QQQ240906P00452500 | 1.32 | 3.42 | +67% | time |
| 2024-09-11 | SPY | CPI | -0.0% | -0.7% | SPY240911P00541000 | 0.87 | 2.59 | -100% | time |
| 2025-01-10 | NVDA | NFP | -1.9% | -1.5% | NVDA250110P00134000 | 0.89 | 1.12 | -99% | time |
| 2025-01-10 | QQQ | NFP | -0.7% | -0.6% | QQQ250110P00505000 | 1.63 | 1.6 | -95% | time |
| 2025-01-10 | SPY | NFP | -0.6% | -0.5% | SPY250110P00579000 | 1.07 | 1.75 | -82% | time |
| 2025-01-10 | TSLA | NFP | -0.9% | -0.5% | TSLA250110P00387500 | 5.5 | 1.13 | -100% | time |
| 2025-04-04 | NVDA | NFP | -2.8% | -1.3% | NVDA250404P00097000 | 1.11 | 4.5 | +235% | take |
| 2025-04-04 | SPY | NFP | -2.4% | -0.1% | SPY250404P00520000 | 3.43 | 4.23 | +202% | take |
| 2025-04-04 | TSLA | NFP | -4.5% | -1.3% | TSLA250404P00250000 | 3.59 | 3.9 | +208% | take |
| 2025-04-10 | QQQ | CPI | -2.7% | -0.7% | QQQ250410P00447000 | 3.44 | 4.39 | +222% | take |
| 2025-04-10 | SPY | CPI | -3.0% | -0.6% | SPY250410P00525000 | 3.66 | 4.39 | +211% | take |
| 2025-08-01 | NVDA | NFP | -2.1% | -1.1% | NVDA250801P00170000 | 0.68 | 1.03 | -99% | time |
| 2025-08-01 | QQQ | NFP | -1.1% | -0.9% | QQQ250801P00550000 | 1.37 | 1.11 | -96% | time |
| 2025-08-01 | SPY | NFP | -0.9% | -0.8% | SPY250801P00617000 | 1 | 1.16 | -99% | time |
| 2025-08-01 | TSLA | NFP | -0.7% | -1.9% | TSLA250801P00297500 | 1.8 | 1.28 | -99% | time |
| 2025-09-05 | NVDA | NFP | -2.1% | -0.2% | NVDA250905P00167500 | 1.31 | 2.67 | -67% | time |
| 2025-09-17 | QQQ | FOMC | -0.0% | -0.2% | QQQ250917P00586000 | 1.01 | 2.71 | -98% | time |
| 2025-10-24 | TSLA | CPI | -0.5% | -1.4% | TSLA251024P00437500 | 2.79 | 2.51 | +41% | time |
| 2026-02-13 | QQQ | CPI | -0.0% | -0.2% | QQQ260213P00595000 | 1.31 | 1.14 | -98% | time |
| 2026-02-13 | TSLA | CPI | -0.7% | -0.1% | TSLA260213P00410000 | 1.86 | 1.25 | -100% | time |
| 2026-03-06 | SPY | NFP | -1.2% | -0.4% | SPY260306P00666000 | 0.84 | 1.26 | -99% | time |
| 2026-03-06 | TSLA | NFP | -1.8% | -0.5% | TSLA260306P00392500 | 1.35 | 1.12 | -97% | time |
| 2026-04-29 | NVDA | FOMC | -0.2% | -0.9% | NVDA260429P00210000 | 1.83 | 1.4 | -45% | time |
| 2026-04-29 | TSLA | FOMC | -0.2% | -0.2% | TSLA260429P00372500 | 2.4 | 1.47 | -86% | time |
| 2026-05-12 | QQQ | CPI | -0.7% | -0.3% | QQQ260512P00701000 | 0.78 | 5.81 | +202% | take |
| 2026-05-12 | SPY | CPI | -0.3% | -0.2% | SPY260512P00730000 | 0.36 | 1.75 | -100% | time |
| 2026-06-05 | NVDA | NFP | -1.9% | -1.2% | NVDA260605P00210000 | 0.62 | 8.56 | +218% | take |
| 2026-06-05 | QQQ | NFP | -1.4% | -0.9% | QQQ260605P00719000 | 1.08 | 12.94 | +209% | take |
| 2026-06-05 | SPY | NFP | -0.6% | -0.5% | SPY260605P00743000 | 0.3 | 24.0 | +205% | take |
| 2026-06-17 | TSLA | FOMC | -0.8% | -0.7% | TSLA260617P00395000 | 1.54 | 1.16 | -90% | time |
| 2026-07-29 | NVDA | FOMC | -0.6% | -1.2% | NVDA260729P00192500 | 1.14 | 2.17 | -85% | time |
| 2026-07-29 | SPY | FOMC | -0.1% | -0.4% | SPY260729P00732000 | 1.11 | 2.69 | -57% | time |
| 2026-07-29 | TSLA | FOMC | -0.1% | -0.5% | TSLA260729P00302500 | 1.28 | 3.78 | -46% | time |
| 2026-09-04 | TSLA | NFP | -3.8% | -0.6% | TSLA260904P00357500 | 2.13 | 3.03 | +12% | time |
