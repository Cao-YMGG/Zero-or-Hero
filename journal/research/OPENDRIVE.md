# Follow the open on real 0DTE option prices

Rule: at 10:00 ET buy a same-day call if the underlying is above its open (put if below; skip if within 0.1%), strike ~0.7% out of the money; sell at 3x entry, else at 15:30. SPY/QQQ every weekday; NVDA/TSLA on same-day expiry days (Fridays; Mon/Wed too since 2026-01-26). Real 1-minute option closes, 10% slippage each way in the tables (5% in opendrive.json). Macro calendar: config/macro_events.json plus 2024-25 CPI/NFP/FOMC dates.

Skipped: {'no_bars': 0, 'no_option': 16}. Data through 2026-10-15.

## all

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 163 | 25% | -16% | -18% | -20% | -95% | +305% |
| all days | last year | 596 | 24% | -22% | -23% | -23% | -96% | +547% |
| all days | since 2024-02 | 1331 | 23% | -26% | -27% | -28% | -96% | +1205% |
| puts (below the open at 10:00) | last 3 months | 89 | 21% | -27% | -31% | -35% | -97% | +305% |
| puts (below the open at 10:00) | last year | 278 | 23% | -25% | -27% | -29% | -95% | +547% |
| puts (below the open at 10:00) | since 2024-02 | 654 | 24% | -21% | -22% | -22% | -95% | +547% |
| calls (above the open at 10:00) | last 3 months | 74 | 30% | -2% | -6% | -9% | -94% | +260% |
| calls (above the open at 10:00) | last year | 318 | 25% | -19% | -20% | -21% | -98% | +419% |
| calls (above the open at 10:00) | since 2024-02 | 677 | 22% | -31% | -33% | -34% | -98% | +1205% |
| macro days | last 3 months | 28 | 18% | -43% | -54% | -65% | -99% | +248% |
| macro days | last year | 84 | 21% | -33% | -37% | -41% | -98% | +271% |
| macro days | since 2024-02 | 195 | 18% | -42% | -44% | -46% | -98% | +307% |
| gap and 10:00 move agree | last 3 months | 92 | 28% | -4% | -7% | -10% | -95% | +305% |
| gap and 10:00 move agree | last year | 314 | 25% | -20% | -21% | -23% | -96% | +385% |
| gap and 10:00 move agree | since 2024-02 | 673 | 24% | -24% | -26% | -26% | -97% | +1205% |
| gap and 10:00 move disagree | last 3 months | 70 | 21% | -31% | -35% | -39% | -96% | +250% |
| gap and 10:00 move disagree | last year | 277 | 23% | -22% | -24% | -26% | -96% | +547% |
| gap and 10:00 move disagree | since 2024-02 | 648 | 22% | -28% | -29% | -30% | -96% | +547% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 8 | 50% | +53% | +25% | -8% | -17% | +248% |
| like 2026-10-14 (macro, gap down, below open) | last year | 21 | 43% | +28% | +17% | +6% | -46% | +248% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 45 | 36% | +7% | +1% | -4% | -82% | +248% |
| gap down + below open (any day) | last 3 months | 44 | 30% | +2% | -5% | -12% | -89% | +305% |
| gap down + below open (any day) | last year | 126 | 25% | -18% | -21% | -23% | -90% | +305% |
| gap down + below open (any day) | since 2024-02 | 272 | 28% | -11% | -12% | -13% | -93% | +305% |

## SPY

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 42 | 24% | -17% | -23% | -30% | -100% | +250% |
| all days | last year | 179 | 21% | -27% | -30% | -32% | -98% | +547% |
| all days | since 2024-02 | 432 | 20% | -32% | -35% | -36% | -98% | +1205% |
| puts (below the open at 10:00) | last 3 months | 24 | 12% | -52% | -65% | -79% | -100% | +248% |
| puts (below the open at 10:00) | last year | 79 | 19% | -32% | -39% | -43% | -97% | +547% |
| puts (below the open at 10:00) | since 2024-02 | 212 | 20% | -32% | -34% | -36% | -97% | +547% |
| calls (above the open at 10:00) | last 3 months | 18 | 39% | +31% | +18% | +4% | -74% | +250% |
| calls (above the open at 10:00) | last year | 100 | 23% | -23% | -27% | -31% | -100% | +419% |
| calls (above the open at 10:00) | since 2024-02 | 220 | 20% | -33% | -39% | -41% | -100% | +1205% |
| macro days | last 3 months | 4 | 25% | -2% | -86% | -100% | -78% | +248% |
| macro days | last year | 20 | 20% | -29% | -45% | -61% | -99% | +271% |
| macro days | since 2024-02 | 56 | 16% | -47% | -52% | -58% | -99% | +271% |
| gap and 10:00 move agree | last 3 months | 24 | 29% | -1% | -12% | -23% | -94% | +248% |
| gap and 10:00 move agree | last year | 90 | 20% | -33% | -38% | -41% | -98% | +384% |
| gap and 10:00 move agree | since 2024-02 | 213 | 20% | -29% | -35% | -37% | -99% | +1205% |
| gap and 10:00 move disagree | last 3 months | 18 | 17% | -38% | -54% | -73% | -100% | +250% |
| gap and 10:00 move disagree | last year | 88 | 23% | -19% | -26% | -31% | -97% | +547% |
| gap and 10:00 move disagree | since 2024-02 | 215 | 20% | -34% | -37% | -39% | -97% | +547% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 2 | 50% | +96% | -57% | +nan% | +96% | +248% |
| like 2026-10-14 (macro, gap down, below open) | last year | 5 | 40% | +40% | -12% | -85% | -57% | +248% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 13 | 31% | +8% | -12% | -33% | -78% | +248% |
| gap down + below open (any day) | last 3 months | 12 | 17% | -37% | -63% | -89% | -94% | +248% |
| gap down + below open (any day) | last year | 33 | 18% | -38% | -47% | -55% | -96% | +248% |
| gap down + below open (any day) | since 2024-02 | 81 | 23% | -19% | -23% | -26% | -97% | +259% |

## QQQ

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 52 | 23% | -16% | -22% | -28% | -96% | +305% |
| all days | last year | 202 | 23% | -21% | -23% | -25% | -96% | +385% |
| all days | since 2024-02 | 528 | 22% | -27% | -28% | -29% | -96% | +385% |
| puts (below the open at 10:00) | last 3 months | 28 | 18% | -33% | -46% | -57% | -98% | +305% |
| puts (below the open at 10:00) | last year | 92 | 21% | -27% | -31% | -34% | -96% | +305% |
| puts (below the open at 10:00) | since 2024-02 | 262 | 23% | -21% | -23% | -24% | -96% | +307% |
| calls (above the open at 10:00) | last 3 months | 24 | 29% | +4% | -7% | -19% | -93% | +260% |
| calls (above the open at 10:00) | last year | 110 | 25% | -17% | -20% | -24% | -94% | +385% |
| calls (above the open at 10:00) | since 2024-02 | 266 | 20% | -33% | -35% | -37% | -98% | +385% |
| macro days | last 3 months | 8 | 12% | -56% | -97% | -99% | -99% | +229% |
| macro days | last year | 23 | 22% | -26% | -38% | -50% | -98% | +229% |
| macro days | since 2024-02 | 63 | 19% | -36% | -41% | -47% | -98% | +307% |
| gap and 10:00 move agree | last 3 months | 26 | 31% | +9% | -2% | -13% | -94% | +305% |
| gap and 10:00 move agree | last year | 102 | 26% | -14% | -18% | -21% | -96% | +385% |
| gap and 10:00 move agree | since 2024-02 | 257 | 23% | -27% | -28% | -29% | -97% | +385% |
| gap and 10:00 move disagree | last 3 months | 25 | 16% | -40% | -52% | -64% | -98% | +250% |
| gap and 10:00 move disagree | last year | 98 | 19% | -28% | -32% | -35% | -96% | +377% |
| gap and 10:00 move disagree | since 2024-02 | 267 | 21% | -29% | -30% | -31% | -96% | +377% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 1 | 100% | +229% | +nan% | +nan% | +229% | +229% |
| like 2026-10-14 (macro, gap down, below open) | last year | 4 | 75% | +136% | +104% | +52% | +206% | +229% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 11 | 45% | +32% | +12% | -11% | -91% | +229% |
| gap down + below open (any day) | last 3 months | 12 | 33% | +22% | -4% | -27% | -92% | +305% |
| gap down + below open (any day) | last year | 39 | 26% | -11% | -19% | -26% | -96% | +305% |
| gap down + below open (any day) | since 2024-02 | 103 | 27% | -10% | -13% | -16% | -95% | +305% |

## NVDA

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 32 | 31% | +11% | +2% | -7% | -86% | +276% |
| all days | last year | 101 | 28% | -13% | -16% | -19% | -88% | +276% |
| all days | since 2024-02 | 176 | 28% | -14% | -16% | -17% | -92% | +276% |
| puts (below the open at 10:00) | last 3 months | 17 | 35% | +30% | +15% | -2% | -68% | +276% |
| puts (below the open at 10:00) | last year | 48 | 27% | -11% | -17% | -23% | -77% | +276% |
| puts (below the open at 10:00) | since 2024-02 | 83 | 33% | +4% | +1% | -3% | -85% | +276% |
| calls (above the open at 10:00) | last 3 months | 15 | 27% | -11% | -29% | -49% | -98% | +235% |
| calls (above the open at 10:00) | last year | 53 | 28% | -16% | -20% | -25% | -94% | +235% |
| calls (above the open at 10:00) | since 2024-02 | 93 | 24% | -30% | -33% | -36% | -96% | +235% |
| macro days | last 3 months | 8 | 12% | -58% | -98% | -100% | -100% | +221% |
| macro days | last year | 20 | 20% | -41% | -55% | -70% | -99% | +221% |
| macro days | since 2024-02 | 37 | 14% | -54% | -62% | -70% | -98% | +235% |
| gap and 10:00 move agree | last 3 months | 22 | 32% | +13% | +0% | -13% | -88% | +276% |
| gap and 10:00 move agree | last year | 58 | 29% | -3% | -8% | -13% | -88% | +276% |
| gap and 10:00 move agree | since 2024-02 | 98 | 29% | -9% | -12% | -15% | -92% | +276% |
| gap and 10:00 move disagree | last 3 months | 10 | 30% | +6% | -19% | -47% | -71% | +232% |
| gap and 10:00 move disagree | last year | 42 | 26% | -25% | -32% | -39% | -84% | +274% |
| gap and 10:00 move disagree | since 2024-02 | 77 | 27% | -20% | -24% | -27% | -93% | +274% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 2 | 50% | +68% | -85% | +nan% | +68% | +221% |
| like 2026-10-14 (macro, gap down, below open) | last year | 4 | 50% | +77% | +29% | -65% | +86% | +221% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 9 | 33% | +20% | -7% | -39% | -67% | +235% |
| gap down + below open (any day) | last 3 months | 10 | 50% | +79% | +57% | +30% | +67% | +276% |
| gap down + below open (any day) | last year | 23 | 35% | +21% | +9% | -3% | -68% | +276% |
| gap down + below open (any day) | since 2024-02 | 40 | 38% | +25% | +19% | +12% | -68% | +276% |

## TSLA

| group | period | trades | win% | avg | avg w/o best | w/o best 2 | median | best |
|---|---|---|---|---|---|---|---|---|
| all days | last 3 months | 37 | 24% | -38% | -45% | -53% | -96% | +226% |
| all days | last year | 114 | 28% | -22% | -24% | -27% | -92% | +226% |
| all days | since 2024-02 | 195 | 28% | -20% | -22% | -23% | -92% | +235% |
| puts (below the open at 10:00) | last 3 months | 20 | 25% | -39% | -51% | -65% | -92% | +203% |
| puts (below the open at 10:00) | last year | 59 | 27% | -26% | -30% | -34% | -86% | +214% |
| puts (below the open at 10:00) | since 2024-02 | 97 | 29% | -19% | -21% | -24% | -86% | +235% |
| calls (above the open at 10:00) | last 3 months | 17 | 24% | -38% | -54% | -72% | -98% | +226% |
| calls (above the open at 10:00) | last year | 55 | 29% | -19% | -23% | -28% | -97% | +226% |
| calls (above the open at 10:00) | since 2024-02 | 98 | 27% | -22% | -24% | -27% | -97% | +226% |
| macro days | last 3 months | 8 | 25% | -36% | -71% | -84% | -81% | +211% |
| macro days | last year | 21 | 24% | -38% | -51% | -64% | -97% | +211% |
| macro days | since 2024-02 | 39 | 23% | -34% | -41% | -48% | -97% | +211% |
| gap and 10:00 move agree | last 3 months | 20 | 20% | -43% | -57% | -72% | -98% | +226% |
| gap and 10:00 move agree | last year | 64 | 27% | -27% | -31% | -35% | -89% | +226% |
| gap and 10:00 move agree | since 2024-02 | 105 | 29% | -19% | -22% | -24% | -86% | +226% |
| gap and 10:00 move disagree | last 3 months | 17 | 29% | -33% | -47% | -64% | -92% | +203% |
| gap and 10:00 move disagree | last year | 49 | 31% | -15% | -20% | -25% | -92% | +222% |
| gap and 10:00 move disagree | since 2024-02 | 89 | 27% | -21% | -23% | -26% | -95% | +235% |
| like 2026-10-14 (macro, gap down, below open) | last 3 months | 3 | 33% | -44% | -71% | -97% | -46% | +12% |
| like 2026-10-14 (macro, gap down, below open) | last year | 8 | 25% | -58% | -72% | -86% | -88% | +41% |
| like 2026-10-14 (macro, gap down, below open) | since 2024-02 | 12 | 33% | -27% | -48% | -66% | -88% | +208% |
| gap down + below open (any day) | last 3 months | 10 | 20% | -53% | -72% | -82% | -85% | +118% |
| gap down + below open (any day) | last year | 31 | 26% | -36% | -44% | -53% | -86% | +214% |
| gap down + below open (any day) | since 2024-02 | 48 | 27% | -30% | -35% | -41% | -85% | +220% |

## Exit rules compared (10% slippage, same entries)

take3 = all out at 3x (the tables above); hold = to 15:30; trail = arm at 2x, out at max(entry, 60% of peak); half3_hold / half3_trail = half at 3x, the rest held / trailed (40% giveback, floor = entry). Each cell: avg / avg without best / without best 2.

### all

| group | period | n | take3 | hold | trail | half3_hold | half3_trail |
|---|---|---|---|---|---|---|---|
| all days | last 3 months | 163 | -16% / -18% / -20% | +30% / +7% / -13% | -15% / -21% / -26% | +7% / -5% / -16% | -7% / -14% / -18% |
| all days | last year | 596 | -22% / -23% / -23% | -11% / -18% / -23% | -24% / -25% / -27% | -17% / -20% / -23% | -21% / -23% / -24% |
| all days | since 2024-02 | 1331 | -26% / -27% / -28% | -19% / -23% / -26% | -26% / -28% / -29% | -22% / -25% / -26% | -26% / -27% / -28% |
| puts (below the open at 10:00) | last 3 months | 89 | -27% / -31% / -35% | -47% / -59% / -64% | -23% / -34% / -39% | -37% / -44% / -49% | -27% / -34% / -38% |
| puts (below the open at 10:00) | last year | 278 | -25% / -27% / -29% | -29% / -34% / -38% | -23% / -27% / -29% | -27% / -30% / -32% | -28% / -30% / -32% |
| puts (below the open at 10:00) | since 2024-02 | 654 | -21% / -22% / -22% | -8% / -17% / -22% | -16% / -20% / -23% | -15% / -19% / -22% | -20% / -22% / -24% |
| calls (above the open at 10:00) | last 3 months | 74 | -2% / -6% / -9% | +122% / +72% / +29% | -6% / -16% / -26% | +60% / +33% / +11% | +17% / +1% / -6% |
| calls (above the open at 10:00) | last year | 318 | -19% / -20% / -21% | +4% / -8% / -18% | -24% / -27% / -30% | -7% / -14% / -19% | -15% / -18% / -21% |
| calls (above the open at 10:00) | since 2024-02 | 677 | -31% / -33% / -34% | -29% / -34% / -39% | -36% / -37% / -39% | -30% / -33% / -35% | -31% / -33% / -34% |
| gap and 10:00 move agree | last 3 months | 92 | -4% / -7% / -10% | +95% / +54% / +20% | -5% / -16% / -24% | +45% / +24% / +6% | +15% / +2% / -5% |
| gap and 10:00 move agree | last year | 314 | -20% / -21% / -23% | +18% / +6% / -4% | -21% / -25% / -28% | -1% / -8% / -13% | -14% / -18% / -20% |
| gap and 10:00 move agree | since 2024-02 | 673 | -24% / -26% / -26% | -9% / -15% / -20% | -29% / -31% / -33% | -17% / -20% / -22% | -23% / -25% / -26% |

### SPY

| group | period | n | take3 | hold | trail | half3_hold | half3_trail |
|---|---|---|---|---|---|---|---|
| all days | last 3 months | 42 | -17% / -23% / -30% | +99% / +9% / -45% | -36% / -43% / -46% | +41% / -6% / -36% | +7% / -22% / -35% |
| all days | last year | 179 | -27% / -30% / -32% | -14% / -35% / -48% | -40% / -43% / -45% | -20% / -32% / -38% | -28% / -34% / -37% |
| all days | since 2024-02 | 432 | -32% / -35% / -36% | -24% / -37% / -46% | -38% / -42% / -44% | -28% / -35% / -40% | -34% / -37% / -39% |
| puts (below the open at 10:00) | last 3 months | 24 | -52% / -65% / -79% | -84% / -91% / -93% | -45% / -58% / -65% | -68% / -78% / -85% | -55% / -68% / -82% |
| puts (below the open at 10:00) | last year | 79 | -32% / -39% / -43% | -40% / -58% / -69% | -34% / -41% / -45% | -36% / -46% / -54% | -38% / -44% / -49% |
| puts (below the open at 10:00) | since 2024-02 | 212 | -32% / -34% / -36% | -10% / -37% / -44% | -27% / -35% / -40% | -21% / -35% / -39% | -32% / -37% / -39% |
| calls (above the open at 10:00) | last 3 months | 18 | +31% / +18% / +4% | +343% / +141% / +13% | -23% / -31% / -39% | +187% / +81% / +11% | +89% / +24% / -4% |
| calls (above the open at 10:00) | last year | 100 | -23% / -27% / -31% | +7% / -31% / -54% | -44% / -47% / -50% | -8% / -28% / -41% | -19% / -32% / -37% |
| calls (above the open at 10:00) | since 2024-02 | 220 | -33% / -39% / -41% | -37% / -54% / -64% | -48% / -50% / -52% | -35% / -44% / -50% | -36% / -42% / -45% |
| gap and 10:00 move agree | last 3 months | 24 | -1% / -12% / -23% | +244% / +90% / -5% | -36% / -42% / -49% | +121% / +40% / -12% | +46% / -4% / -26% |
| gap and 10:00 move agree | last year | 90 | -33% / -38% / -41% | +39% / -3% / -28% | -46% / -49% / -52% | +3% / -19% / -33% | -25% / -39% / -45% |
| gap and 10:00 move agree | since 2024-02 | 213 | -29% / -35% / -37% | -5% / -23% / -34% | -43% / -48% / -49% | -17% / -27% / -33% | -31% / -37% / -40% |

### QQQ

| group | period | n | take3 | hold | trail | half3_hold | half3_trail |
|---|---|---|---|---|---|---|---|
| all days | last 3 months | 52 | -16% / -22% / -28% | +34% / -26% / -44% | -9% / -24% / -38% | +9% / -24% / -35% | -12% / -22% / -31% |
| all days | last year | 202 | -21% / -23% / -25% | -13% / -29% / -34% | -28% / -32% / -36% | -17% / -26% / -29% | -24% / -27% / -29% |
| all days | since 2024-02 | 528 | -27% / -28% / -29% | -17% / -23% / -29% | -26% / -32% / -34% | -22% / -26% / -29% | -26% / -29% / -31% |
| puts (below the open at 10:00) | last 3 months | 28 | -33% / -46% / -57% | -61% / -79% / -92% | -37% / -52% / -64% | -47% / -61% / -73% | -32% / -45% / -58% |
| puts (below the open at 10:00) | last year | 92 | -27% / -31% / -34% | -35% / -45% / -54% | -31% / -35% / -39% | -31% / -38% / -43% | -32% / -36% / -40% |
| puts (below the open at 10:00) | since 2024-02 | 262 | -21% / -23% / -24% | -4% / -16% / -24% | -13% / -26% / -30% | -13% / -19% / -24% | -17% / -24% / -26% |
| calls (above the open at 10:00) | last 3 months | 24 | +4% / -7% / -19% | +145% / +15% / -24% | +23% / -7% / -39% | +75% / +5% / -20% | +13% / -8% / -29% |
| calls (above the open at 10:00) | last year | 110 | -17% / -20% / -24% | +6% / -23% / -33% | -26% / -33% / -39% | -6% / -21% / -27% | -17% / -22% / -27% |
| calls (above the open at 10:00) | since 2024-02 | 266 | -33% / -35% / -37% | -31% / -43% / -47% | -39% / -41% / -44% | -32% / -39% / -41% | -35% / -37% / -39% |
| gap and 10:00 move agree | last 3 months | 26 | +9% / -2% / -13% | +146% / +26% / -9% | +33% / +5% / -24% | +78% / +13% / -9% | +26% / +7% / -11% |
| gap and 10:00 move agree | last year | 102 | -14% / -18% / -21% | +26% / -4% / -15% | -16% / -23% / -31% | +6% / -10% / -17% | -12% / -17% / -22% |
| gap and 10:00 move agree | since 2024-02 | 257 | -27% / -28% / -29% | -10% / -22% / -26% | -31% / -34% / -37% | -18% / -25% / -27% | -27% / -29% / -31% |

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
| 2026-10-14 | NVDA | CPI | -1.3% | -0.5% | NVDA261014P00222500 | 0.41 | 7.02 | +221% | take |
| 2026-10-14 | QQQ | CPI | -0.8% | -0.3% | QQQ261014P00731000 | 0.47 | 9.83 | +229% | take |
| 2026-10-14 | SPY | CPI | -0.4% | -0.2% | SPY261014P00768000 | 0.12 | 14.08 | +248% | take |
| 2026-10-14 | TSLA | CPI | -1.1% | -1.7% | TSLA261014P00362500 | 0.84 | 1.11 | -97% | time |
