# Financing fade and acquirer fade on real option prices

2024-11-01 to 2026-11-01, 61 large caps, Alpaca/Benzinga headlines. Puts, costs 10% each way unless stated. Columns: n | win% | avg | without the best | without the best two. See zoh/research/fades.py for the rules.

## Stock moves (a win is a fall)

| type | period | gap | open->close | 09:31->close | 10:00->close | 10:00->close, below open at 10:00 | news->close | next day |
|---|---|---|---|---|---|---|---|---|
| equity | last 3 months | 12 | 92% | +2% | +2% | +2% | 12 | 58% | +0% | +0% | -0% | 12 | 67% | +1% | +0% | +0% | 12 | 33% | -0% | -1% | -1% | 7 | 43% | -0% | -1% | -1% | - | 12 | 42% | -0% | -1% | -1% |
| equity | last year | 23 | 83% | +2% | +2% | +1% | 23 | 57% | +1% | +0% | -0% | 23 | 57% | +1% | +0% | -0% | 23 | 39% | +1% | -0% | -0% | 11 | 36% | -1% | -1% | -1% | - | 23 | 43% | -1% | -1% | -2% |
| equity | 2 years | 43 | 70% | +1% | +1% | +0% | 44 | 55% | +1% | +1% | +0% | 39 | 59% | +1% | +1% | +0% | 39 | 46% | +1% | +0% | +0% | 21 | 52% | +0% | +0% | -0% | 4 | 25% | -1% | -1% | -1% | 44 | 39% | -2% | -2% | -2% |
| debt | last 3 months | 6 | 33% | -0% | -0% | -1% | 6 | 50% | -0% | -0% | -0% | 2 | 50% | +0% | -0% | - | 2 | 50% | +1% | -1% | - | 1 | 0% | -1% | - | - | 4 | 50% | -0% | -0% | -0% | 6 | 67% | +0% | -1% | -1% |
| debt | last year | 25 | 44% | -0% | -0% | -0% | 25 | 60% | +1% | +0% | +0% | 16 | 44% | +0% | +0% | -0% | 16 | 50% | -0% | -0% | -0% | 15 | 47% | -0% | -0% | -1% | 9 | 33% | -0% | -0% | -0% | 25 | 60% | +0% | -0% | -0% |
| debt | 2 years | 46 | 39% | -0% | -0% | -0% | 46 | 52% | +0% | -0% | -0% | 27 | 59% | +0% | +0% | +0% | 27 | 48% | -0% | -0% | -0% | 22 | 45% | -0% | -0% | -0% | 19 | 32% | -1% | -1% | -1% | 46 | 57% | +0% | -0% | -0% |
| acquirer | last 3 months | 1 | 0% | -1% | - | - | 1 | 100% | +1% | - | - | 1 | 100% | +1% | - | - | 1 | 100% | +2% | - | - | - | - | 1 | 0% | -1% | - | - |
| acquirer | last year | 2 | 0% | -5% | -8% | - | 2 | 50% | -3% | -7% | - | 2 | 50% | -3% | -6% | - | 2 | 50% | -1% | -5% | - | - | - | 2 | 0% | -2% | -4% | - |
| acquirer | 2 years | 2 | 0% | -5% | -8% | - | 2 | 50% | -3% | -7% | - | 2 | 50% | -3% | -6% | - | 2 | 50% | -1% | -5% | - | - | - | 2 | 0% | -2% | -4% | - |
| acquirer_cash | last 3 months | 1 | 0% | -1% | - | - | 1 | 100% | +2% | - | - | 1 | 100% | +1% | - | - | 1 | 100% | +0% | - | - | 1 | 100% | +0% | - | - | - | 1 | 100% | +1% | - | - |
| acquirer_cash | last year | 3 | 33% | +1% | -0% | -1% | 3 | 33% | -0% | -1% | -1% | 3 | 33% | -0% | -1% | -1% | 3 | 100% | +1% | +0% | +0% | 1 | 100% | +0% | - | - | - | 3 | 100% | +2% | +1% | +0% |
| acquirer_cash | 2 years | 8 | 50% | -4% | -6% | -7% | 8 | 50% | +1% | +0% | -0% | 6 | 67% | +2% | +0% | +0% | 6 | 83% | +1% | +0% | -0% | 4 | 75% | +0% | -0% | -1% | 2 | 50% | +0% | -0% | - | 8 | 62% | -0% | -1% | -1% |

## Puts, entry 10:00 (pre-market events) or 2 minutes after the headline, sold 15:45 day one

| type | period | delta | half3_arm1.5 | trail1.5x | half3_trail | trail2x | hold |
|---|---|---|---|---|---|---|---|
| equity | last 3 months | d0.15 | 12 | 8% | -45% | -49% | -53% | 12 | 8% | -45% | -49% | -53% | 12 | 8% | -51% | -56% | -59% | 12 | 8% | -51% | -56% | -59% | 12 | 8% | -51% | -56% | -59% |
| equity | last 3 months | d0.25 | 12 | 8% | -39% | -45% | -49% | 12 | 8% | -39% | -45% | -49% | 12 | 8% | -47% | -53% | -56% | 12 | 8% | -47% | -53% | -56% | 12 | 8% | -47% | -53% | -56% |
| equity | last 3 months | d0.40 | 12 | 17% | -33% | -39% | -43% | 12 | 17% | -33% | -39% | -43% | 12 | 8% | -41% | -48% | -52% | 12 | 8% | -41% | -48% | -52% | 12 | 8% | -41% | -48% | -52% |
| equity | last year | d0.15 | 23 | 26% | -3% | -20% | -28% | 23 | 26% | +2% | -24% | -30% | 23 | 26% | -11% | -29% | -37% | 23 | 26% | -6% | -33% | -39% | 23 | 26% | -5% | -32% | -38% |
| equity | last year | d0.25 | 23 | 26% | -11% | -24% | -30% | 23 | 26% | -7% | -24% | -30% | 23 | 26% | -18% | -32% | -38% | 23 | 26% | -15% | -32% | -38% | 23 | 26% | -15% | -32% | -38% |
| equity | last year | d0.40 | 23 | 30% | -10% | -22% | -26% | 23 | 30% | -9% | -22% | -26% | 23 | 26% | -18% | -30% | -34% | 23 | 26% | -16% | -30% | -34% | 23 | 26% | -16% | -30% | -34% |
| equity | 2 years | d0.15 | 39 | 33% | +2% | -8% | -14% | 39 | 33% | +6% | -9% | -16% | 39 | 36% | -2% | -13% | -19% | 39 | 36% | +1% | -14% | -21% | 39 | 36% | +2% | -13% | -19% |
| equity | 2 years | d0.25 | 39 | 36% | -5% | -12% | -18% | 39 | 36% | -3% | -13% | -18% | 39 | 36% | -9% | -17% | -23% | 39 | 36% | -7% | -17% | -23% | 39 | 36% | -7% | -17% | -23% |
| equity | 2 years | d0.40 | 39 | 33% | -8% | -14% | -18% | 39 | 33% | -7% | -14% | -18% | 39 | 33% | -11% | -18% | -22% | 39 | 33% | -10% | -18% | -22% | 39 | 33% | -10% | -18% | -22% |
| debt | last 3 months | d0.15 | 6 | 17% | -33% | -44% | -55% | 6 | 17% | -33% | -44% | -55% | 6 | 17% | -48% | -61% | -70% | 6 | 17% | -48% | -61% | -70% | 6 | 17% | -48% | -61% | -70% |
| debt | last 3 months | d0.25 | 6 | 17% | -30% | -43% | -53% | 6 | 17% | -30% | -43% | -53% | 6 | 17% | -45% | -60% | -68% | 6 | 17% | -45% | -60% | -68% | 6 | 17% | -45% | -60% | -68% |
| debt | last 3 months | d0.40 | 6 | 17% | -29% | -42% | -52% | 6 | 17% | -29% | -42% | -52% | 6 | 17% | -38% | -53% | -60% | 6 | 17% | -38% | -53% | -60% | 6 | 17% | -38% | -53% | -60% |
| debt | last year | d0.15 | 25 | 20% | -39% | -42% | -45% | 25 | 20% | -39% | -42% | -45% | 25 | 16% | -45% | -49% | -52% | 25 | 16% | -45% | -49% | -52% | 25 | 12% | -48% | -52% | -55% |
| debt | last year | d0.25 | 25 | 12% | -36% | -39% | -42% | 25 | 12% | -36% | -39% | -42% | 25 | 12% | -42% | -46% | -49% | 25 | 12% | -42% | -46% | -49% | 25 | 12% | -42% | -46% | -49% |
| debt | last year | d0.40 | 25 | 8% | -37% | -40% | -43% | 25 | 8% | -37% | -40% | -43% | 25 | 8% | -40% | -43% | -47% | 25 | 8% | -40% | -43% | -47% | 25 | 8% | -40% | -43% | -47% |
| debt | 2 years | d0.15 | 46 | 20% | -37% | -39% | -41% | 46 | 20% | -37% | -39% | -41% | 46 | 15% | -42% | -44% | -46% | 46 | 15% | -42% | -44% | -46% | 46 | 13% | -36% | -46% | -48% |
| debt | 2 years | d0.25 | 46 | 13% | -36% | -38% | -40% | 46 | 13% | -36% | -38% | -40% | 46 | 13% | -40% | -42% | -44% | 46 | 13% | -40% | -42% | -44% | 46 | 13% | -33% | -42% | -44% |
| debt | 2 years | d0.40 | 46 | 11% | -30% | -36% | -38% | 46 | 11% | -29% | -36% | -38% | 46 | 9% | -32% | -39% | -41% | 46 | 9% | -32% | -39% | -41% | 46 | 9% | -32% | -39% | -41% |
| acquirer | last 3 months | d0.15 | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - |
| acquirer | last 3 months | d0.25 | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - |
| acquirer | last 3 months | d0.40 | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - |
| acquirer | last year | d0.15 | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - |
| acquirer | last year | d0.25 | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - |
| acquirer | last year | d0.40 | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - |
| acquirer | 2 years | d0.15 | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - | 1 | 100% | +48% | - | - |
| acquirer | 2 years | d0.25 | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - | 1 | 100% | +58% | - | - |
| acquirer | 2 years | d0.40 | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - | 1 | 100% | +50% | - | - |
| acquirer_cash | last 3 months | d0.15 | 1 | 0% | -4% | - | - | 1 | 0% | -4% | - | - | 1 | 0% | -46% | - | - | 1 | 0% | -46% | - | - | 1 | 0% | -46% | - | - |
| acquirer_cash | last 3 months | d0.25 | 1 | 0% | -3% | - | - | 1 | 0% | -3% | - | - | 1 | 0% | -42% | - | - | 1 | 0% | -42% | - | - | 1 | 0% | -42% | - | - |
| acquirer_cash | last 3 months | d0.40 | 1 | 0% | -14% | - | - | 1 | 0% | -14% | - | - | 1 | 0% | -35% | - | - | 1 | 0% | -35% | - | - | 1 | 0% | -35% | - | - |
| acquirer_cash | last year | d0.15 | 3 | 33% | +58% | -21% | -38% | 3 | 33% | +55% | -21% | -38% | 3 | 33% | +44% | -42% | -46% | 3 | 33% | +41% | -42% | -46% | 3 | 33% | -12% | -42% | -46% |
| acquirer_cash | last year | d0.25 | 3 | 33% | +48% | -15% | -27% | 3 | 33% | +38% | -15% | -27% | 3 | 33% | +35% | -34% | -42% | 3 | 33% | +26% | -34% | -42% | 3 | 33% | +51% | -34% | -42% |
| acquirer_cash | last year | d0.40 | 3 | 33% | +39% | -18% | -21% | 3 | 33% | +20% | -18% | -21% | 3 | 33% | +32% | -28% | -35% | 3 | 33% | +13% | -28% | -35% | 3 | 33% | +34% | -28% | -35% |
| acquirer_cash | 2 years | d0.15 | 8 | 25% | +8% | -22% | -31% | 8 | 25% | +7% | -22% | -31% | 8 | 25% | +3% | -28% | -38% | 8 | 25% | +2% | -28% | -38% | 8 | 25% | -18% | -28% | -38% |
| acquirer_cash | 2 years | d0.25 | 8 | 25% | +6% | -18% | -27% | 8 | 25% | +2% | -18% | -27% | 8 | 25% | +1% | -24% | -33% | 8 | 25% | -3% | -24% | -33% | 8 | 25% | +7% | -24% | -33% |
| acquirer_cash | 2 years | d0.40 | 8 | 25% | +3% | -18% | -27% | 8 | 25% | -4% | -18% | -27% | 8 | 25% | +0% | -21% | -30% | 8 | 25% | -7% | -21% | -30% | 8 | 25% | +1% | -21% | -30% |

## Puts carried to expiry (trail2x / hold), same entries

| type | period | delta | trail2x | hold |
|---|---|---|---|---|
| equity | last 3 months | d0.15 | 12 | 8% | -86% | -97% | -99% | 12 | 0% | -97% | -99% | -100% |
| equity | last 3 months | d0.25 | 12 | 8% | -81% | -91% | -98% | 12 | 0% | -91% | -97% | -98% |
| equity | last 3 months | d0.40 | 12 | 17% | -72% | -82% | -91% | 12 | 17% | -72% | -82% | -91% |
| equity | last year | d0.15 | 23 | 35% | -24% | -41% | -51% | 23 | 13% | -34% | -55% | -76% |
| equity | last year | d0.25 | 23 | 26% | -29% | -49% | -63% | 23 | 17% | -28% | -48% | -70% |
| equity | last year | d0.40 | 23 | 30% | -21% | -36% | -51% | 23 | 26% | -18% | -33% | -48% |
| equity | 2 years | d0.15 | 39 | 38% | -20% | -31% | -41% | 39 | 18% | +6% | -25% | -42% |
| equity | 2 years | d0.25 | 39 | 31% | -29% | -40% | -49% | 39 | 21% | -1% | -22% | -37% |
| equity | 2 years | d0.40 | 39 | 31% | -26% | -35% | -43% | 39 | 26% | -11% | -23% | -34% |
| debt | last 3 months | d0.15 | 6 | 17% | -64% | -95% | -96% | 6 | 0% | -92% | -95% | -96% |
| debt | last 3 months | d0.25 | 6 | 17% | -66% | -96% | -98% | 6 | 0% | -94% | -96% | -98% |
| debt | last 3 months | d0.40 | 6 | 17% | -74% | -91% | -99% | 6 | 17% | -69% | -91% | -99% |
| debt | last year | d0.15 | 25 | 20% | -62% | -70% | -78% | 25 | 8% | -55% | -89% | -96% |
| debt | last year | d0.25 | 25 | 28% | -48% | -60% | -67% | 25 | 12% | -47% | -71% | -85% |
| debt | last year | d0.40 | 25 | 32% | -30% | -45% | -57% | 25 | 24% | -38% | -53% | -65% |
| debt | 2 years | d0.15 | 46 | 24% | -55% | -59% | -63% | 46 | 13% | -30% | -50% | -69% |
| debt | 2 years | d0.25 | 46 | 28% | -43% | -50% | -57% | 46 | 15% | -20% | -40% | -53% |
| debt | 2 years | d0.40 | 46 | 30% | -25% | -33% | -41% | 46 | 26% | -18% | -32% | -40% |
| acquirer | last 3 months | d0.15 | 1 | 0% | -96% | - | - | 1 | 0% | -96% | - | - |
| acquirer | last 3 months | d0.25 | 1 | 0% | -85% | - | - | 1 | 0% | -85% | - | - |
| acquirer | last 3 months | d0.40 | 1 | 0% | -54% | - | - | 1 | 0% | -54% | - | - |
| acquirer | last year | d0.15 | 1 | 0% | -96% | - | - | 1 | 0% | -96% | - | - |
| acquirer | last year | d0.25 | 1 | 0% | -85% | - | - | 1 | 0% | -85% | - | - |
| acquirer | last year | d0.40 | 1 | 0% | -54% | - | - | 1 | 0% | -54% | - | - |
| acquirer | 2 years | d0.15 | 1 | 0% | -96% | - | - | 1 | 0% | -96% | - | - |
| acquirer | 2 years | d0.25 | 1 | 0% | -85% | - | - | 1 | 0% | -85% | - | - |
| acquirer | 2 years | d0.40 | 1 | 0% | -54% | - | - | 1 | 0% | -54% | - | - |
| acquirer_cash | last 3 months | d0.15 | 1 | 100% | +47% | - | - | 1 | 0% | -99% | - | - |
| acquirer_cash | last 3 months | d0.25 | 1 | 100% | +51% | - | - | 1 | 0% | -94% | - | - |
| acquirer_cash | last 3 months | d0.40 | 1 | 100% | +53% | - | - | 1 | 0% | -28% | - | - |
| acquirer_cash | last year | d0.15 | 3 | 67% | +52% | -25% | -98% | 3 | 33% | -50% | -98% | -99% |
| acquirer_cash | last year | d0.25 | 3 | 67% | +33% | -24% | -99% | 3 | 33% | +10% | -97% | -99% |
| acquirer_cash | last year | d0.40 | 3 | 67% | +16% | -23% | -100% | 3 | 33% | +10% | -64% | -100% |
| acquirer_cash | 2 years | d0.15 | 8 | 38% | -24% | -57% | -74% | 8 | 25% | -62% | -78% | -96% |
| acquirer_cash | 2 years | d0.25 | 8 | 50% | -18% | -42% | -57% | 8 | 38% | -23% | -58% | -76% |
| acquirer_cash | 2 years | d0.40 | 8 | 50% | -16% | -32% | -52% | 8 | 38% | -19% | -44% | -66% |

## Events

| day | sym | type | headline time | entry | gap | open->close | entry->close | below open at entry | d0.25 live rule | headline |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024-11-04 | TSLA | debt | 2024-11-01 17:16 | 09:59 | -1.8% | -0.7% | -0.3% | yes | -15% | 'Tesla Sells $499M Of Debt Backed by Solar Equipment Loans' - Bloomberg News |
| 2024-11-08 | BA | debt | 2024-11-08 12:09 | 12:11 | +0.1% | +0.4% | -0.1% | no | -85% | 'Boeing Is Exploring Possible $6B Sale For Jeppesen Unit; Planemaker Working With Adviser  |
| 2024-11-19 | MSTR | equity | 2024-11-18 16:02 | 09:59 | +1.2% | +10.6% | +8.1% | no | -68% | MicroStrategy Intends To Offer $1.75B Of Its 0% Convertible Senior Notes Due 2029 In Priva |
| 2024-11-19 | VST | debt | 2024-11-19 09:36 | 09:38 | -1.7% | +7.4% | +6.9% | no | -85% | Vistra Announces The Launch Of Senior Secured Notes Due 2026 And Senior Secured Notes Due  |
| 2024-11-20 | VST | debt | 2024-11-19 17:25 | 09:59 | +0.6% | -0.7% | +1.2% | yes | -41% | Vistra Reveals Pricing Of Private Offering Of $1.25B Of Senior Secured Notes |
| 2025-01-17 | CAT | equity | 2025-01-17 10:47 | 10:49 | +1.1% | +0.4% | +0.5% | yes | - | Caterpillar CFO Andrew R J Bonfield Reports Open Market Sale Of 10,000 Common Shares At An |
| 2025-01-30 | ORCL | debt | 2025-01-30 08:09 | 09:59 | +1.7% | +3.4% | +1.3% | no | -61% | Oracle Files For Six-Part Notes Offering; Size Not Disclosed |
| 2025-02-10 | LLY | debt | 2025-02-10 08:18 | 09:59 | -0.1% | -1.0% | +0.5% | yes | -23% | Eli Lilly Files for Six-Part Notes Offering; Size Not Disclosed |
| 2025-02-12 | SMCI | equity | 2025-02-11 16:08 | 09:59 | +9.5% | -6.1% | -5.2% | yes | +13% | Supermicro Announces Private Placement of $700M Of New 2.25% Convertible Senior Notes Due  |
| 2025-02-13 | SMCI | equity | 2025-02-13 03:17 | 09:59 | -1.7% | +8.3% | +9.0% | yes | -93% | Reported Earlier, Supermicro Prices $700M Private Placement Of 2.25% Convertible Senior No |
| 2025-02-18 | MSTR | equity | 2025-02-18 08:20 | 09:59 | -0.1% | -1.0% | -0.1% | yes | -9% | MicroStrategy Says Between Feb 10-17, Did Not Sell Any Class A Common Stock Under Its ATM  |
| 2025-02-19 | MSTR | equity | 2025-02-18 16:03 | 09:59 | +1.0% | -5.5% | -4.9% | yes | +203% | Strategy Reveals Proposed Private Offering Of $2B Of Convertible Senior Notes |
| 2025-03-03 | GS | equity | 2025-02-28 16:35 | 09:59 | +0.0% | -2.7% | -2.9% | no | +159% | Goldman Sachs Form 4 Filing Shows CEO David M Solomon Reports Open Market Sale Of 2,415 Sh |
| 2025-03-03 | MSTR | equity | 2025-03-03 08:14 | 09:59 | +14.8% | -14.2% | -6.9% | yes | +54% | MicroStrategy Announces That, During The Period Between February 24, 2025 And March 2, 202 |
| 2025-03-10 | MSTR | equity | 2025-03-10 08:09 | 09:59 | -6.7% | -10.8% | -6.8% | yes | +55% | Strategy Announces $21B STRK At-The-Market Program |
| 2025-03-12 | RKLB | equity | 2025-03-11 17:26 | 09:59 | +6.1% | -2.8% | +0.5% | yes | -46% | Rocket Lab Plans Offering Of Its Common Stock Having Aggregate Price Of Up To $500M Pursua |
| 2025-03-18 | GOOGL | acquirer_cash | 2025-03-17 16:05 | 09:59 | -0.4% | -1.8% | +1.2% | yes | -60% | "Alphabet And Wiz Held Deal Talks Last Year, Before Discussions Collapsed; Alphabet In Fre |
| 2025-03-18 | PFE | equity | 2025-03-18 12:48 | 12:50 | +0.6% | +0.5% | +0.5% | yes | -44% | Pfizer Proposes Offering In Haleon; Pfizer Intends To Sell 662M Ordinary Shares In Haleon; |
| 2025-03-25 | AMZN | debt | 2025-03-25 12:55 | 12:57 | +0.1% | +1.1% | +0.3% | no | -26% | Amazon MGM Studios Announces New Joint Venture With Michael G. Wilson And Barbara Broccoli |
| 2025-03-28 | CRWV | equity | 2025-03-28 01:10 | - | - | +2.6% | - | - | - | Reported Earlier, CoreWeave Prices Initial Public Offering Of 37.5M Class A Shares At $40  |
| 2025-04-03 | TSLA | debt | 2025-04-03 08:32 | 09:59 | -6.2% | +0.7% | -1.5% | no | -22% | Tesla Rival Lucid Raises $1 Billion Via Convertible Debt To Refinance 2026 Notes And Boost |
| 2025-05-05 | AAPL | debt | 2025-05-05 08:38 | 09:59 | -1.1% | -2.1% | -0.5% | yes | -22% | "Apple Plans To Sell Corporate Bonds In As Many As Four Parts; Apple Is Planning To Sell I |
| 2025-05-14 | UBER | equity | 2025-05-14 12:17 | 12:19 | -1.2% | -0.2% | -0.3% | no | +4% | Aurora Innovation Shares Fall As Uber Announces $1B Note Offering: What's Going On? |
| 2025-05-19 | QCOM | debt | 2025-05-19 09:33 | 09:35 | -1.0% | +1.8% | +2.0% | yes | -66% | Qualcomm Files For Three-Part Notes Offering; Size Not Disclosed |
| 2025-05-23 | ORCL | acquirer_cash | 2025-05-23 14:05 | 14:07 | -1.5% | +0.7% | -0.7% | no | +33% | 'Oracle to buy $40B of Nvidia chips for OpenAI's new US data centre'- Financial Times |
| 2025-06-02 | NBIS | equity | 2025-06-02 07:44 | 09:59 | -5.2% | +3.4% | +1.6% | no | -59% | Nebius Group Raises $1B Through Convertible Notes to Fuel AI Infrastructure Growth |
| 2025-06-05 | SNDK | equity | 2025-06-04 16:52 | 09:59 | -1.1% | -0.7% | +3.7% | yes | - | Sandisk Announces Secondary Public Offering Of 17M Shares Owned By Former Parent Western D |
| 2025-06-06 | SNDK | equity | 2025-06-06 07:12 | 09:59 | +1.5% | -1.4% | -0.8% | yes | - | Sandisk Announces Pricing For Expanded Secondary Offering; WDC to Sell 18.5M Shares, Price |
| 2025-06-16 | JPM | debt | 2025-06-13 17:44 | 09:59 | +0.8% | +1.3% | +0.3% | no | -40% | 'JPMorgan Readies $6.5 Billion Skechers Debt Sale for Next Week'- Bloomberg |
| 2025-06-24 | SMCI | debt | 2025-06-24 09:39 | 09:41 | +1.2% | +3.5% | +2.1% | no | -62% | Supermicro Raises $2 Billion Via Private Convertible Debt With 35% Conversion Premium |
| 2025-07-10 | AAPL | acquirer_cash | 2025-07-10 12:15 | 12:17 | -0.3% | +0.9% | +0.2% | no | -62% | Apple Acquisition Buzz: Its $60 Billion War Chest Is Enough To Buy Datadog And Tempus |
| 2025-07-23 | CRWV | debt | 2025-07-22 16:32 | 09:59 | +1.7% | -4.5% | -1.2% | yes | +17% | CoreWeave Announces Today That It Priced A Private Offering Of $1,.75B Aggregate Principal |
| 2025-08-06 | COIN | equity | 2025-08-06 01:34 | 09:59 | -0.1% | +2.0% | +1.9% | no | -58% | Reported Earlier, Coinbase Prices Upsized $2.6B Convertible Senior Notes Offering With $1. |
| 2025-08-18 | LLY | debt | 2025-08-18 09:44 | 09:46 | -0.9% | +0.5% | -0.1% | no | -35% | 'Eli Lilly Taps High-Grade Bond Market With Rare 40-Year Paper'- Bloomberg |
| 2025-08-19 | LLY | debt | 2025-08-18 17:34 | 09:59 | +1.2% | -0.4% | -0.5% | no | +11% | Eli Lilly Files For Six-Part Notes Offering Of Up To $6.75B |
| 2025-09-03 | LITE | equity | 2025-09-02 16:35 | 09:59 | -0.2% | +1.2% | +0.6% | no | - | Lumentum Plans $1.1B Convertible Senior Notes Offering Due 2032 |
| 2025-09-08 | UBER | debt | 2025-09-08 09:41 | 09:43 | +0.4% | +3.3% | +2.1% | no | -64% | 'Uber Taps Investment-Grade Bond Market for First Time This Year'- Bloomberg |
| 2025-09-10 | NBIS | equity | 2025-09-10 09:17 | 09:59 | -4.3% | +1.9% | -7.0% | no | +23% | Nebius Group Launches $1B Class A Share Offering; Plus $2B Convertible Notes Offering In T |
| 2025-09-11 | NBIS | equity | 2025-09-11 02:50 | 09:59 | -0.8% | -3.7% | -3.4% | yes | +15% | Nebius Group Prices $1B Public Offering Of Class A Ordinary Shares At $92.50 Per Share; Pr |
| 2025-09-17 | GS | debt | 2025-09-17 11:47 | 11:49 | +0.4% | +0.7% | +0.2% | no | -59% | 'Goldman Sachs Readies $5.5 Billion Debt Deal for Dayforce Buyout'- Bloomberg |
| 2025-09-18 | JPM | debt | 2025-09-18 10:09 | 10:11 | +0.0% | +0.4% | +0.0% | no | -4% | 'JPMorgan Said to Help Sell €200 Million of ECB's Worldline Bonds'- Bloomberg News |
| 2025-09-25 | GOOGL | equity | 2025-09-25 09:50 | 09:52 | -1.1% | +0.6% | +1.4% | yes | -81% | Google Supports Cipher Mining's $3 Billion Data Center Pact As Company Launches $800 Milli |
| 2025-09-30 | AVGO | debt | 2025-09-29 16:17 | 09:59 | +0.7% | -0.1% | +1.0% | yes | -51% | Broadcom Announces $5B Senior Notes Offering Across Multiple Maturities |
| 2025-10-02 | VST | debt | 2025-10-02 02:28 | 09:59 | +1.3% | -0.7% | +0.9% | yes | -69% | Reported Earlier, Vistra Prices $2B Senior Secured Notes Offering With $750M 2028 Notes At |
| 2025-10-06 | AMD | acquirer_cash | 2025-10-06 06:59 | 09:59 | +37.5% | -10.1% | -2.1% | yes | -7% | AMD To Supply OpenAi Hundreds Of Thousands Of AI Chips; AMD Expects $100B+ Revenue From Op |
| 2025-10-16 | GS | debt | 2025-10-16 11:00 | 11:02 | +0.4% | -1.6% | -2.7% | no | +59% | 'Deutsche Bank, Goldman to Sell $1.2 Billion Finastra Unit Debt'- Bloomberg |
| 2025-10-28 | MSFT | acquirer_cash | 2025-10-28 09:06 | 09:59 | +3.5% | -1.5% | -0.8% | yes | -3% | Watching Microsoft; Shares Spike Higher, Traders Circulate 'OpenAI Contracted To Buy Incre |
| 2025-11-18 | AMZN | debt | 2025-11-17 21:48 | 09:59 | -2.1% | -2.4% | -1.2% | yes | -7% | Amazon Raises $15 Billion In Oversubscribed Bond Sale Amid Surging AI Cost |
| 2025-12-05 | NFLX | acquirer_cash | 2025-12-05 07:08 | 09:59 | -4.3% | +1.5% | -2.5% | no | +173% | Netflix To Acquire Warner Bros In A Deal For $72B, $27.75/Share In Cash, Stock |
| 2025-12-08 | CRWV | equity | 2025-12-08 06:54 | 09:59 | -5.3% | +3.0% | +3.0% | no | -47% | CoreWeave Intends To Offer $2B Aggregate Principal Amount Of Its Convertible Senior Notes  |
| 2026-01-13 | VST | debt | 2026-01-13 01:59 | 09:59 | +0.8% | -1.5% | -0.4% | yes | -29% | Reported Earlier, Vistra Prices $2.25B Senior Secured Notes Offering, Including $1B Due 20 |
| 2026-02-04 | ORCL | equity | 2026-02-03 16:30 | 09:59 | -0.5% | -4.7% | +0.0% | yes | -33% | Oracle Files For Offering Of Up To $20B Of Common Stock |
| 2026-02-05 | GS | debt | 2026-02-05 09:58 | 10:00 | -1.3% | -1.3% | -0.5% | yes | -14% | 'Goldman Readies $3.75 Billion Debt Offering for DuPont Unit Deal'- Bloomberg |
| 2026-02-09 | GOOGL | debt | 2026-02-09 07:50 | 09:59 | -0.6% | +1.0% | +1.4% | yes | -100% | Alphabet Files Prospectus For Notes Offering; Terms Not Disclosed |
| 2026-02-11 | MSTR | debt | 2026-02-10 14:43 | 09:59 | +0.5% | -5.6% | -1.7% | yes | +8% | Michael Saylor Says Strategy Won't Sell Bitcoin Even At $8,000: 'We'll Refinance The Debt' |
| 2026-02-18 | SNDK | equity | 2026-02-17 16:50 | 09:59 | -1.4% | +3.1% | +0.7% | no | -49% | Sandisk Launches $3.086M Offering Of Common Shares |
| 2026-02-19 | XOM | debt | 2026-02-18 17:31 | 09:59 | +1.0% | -0.8% | -0.7% | yes | -46% | Exxon Mobil Files For Debt Shelf Offering; Size Not Disclosed |
| 2026-03-11 | JPM | debt | 2026-03-11 13:56 | 13:58 | +0.0% | -0.5% | +0.5% | yes | -16% | 'JPMorgan Tees Up EA Debt Sale as Iran War Shakes Credit Markets' - Bloomberg |
| 2026-03-12 | AMZN | debt | 2026-03-11 16:20 | 09:59 | -1.1% | -0.4% | -0.3% | yes | -2% | Amazon Files Pricing Term Sheet For Eight-Part, Euro Denominated Notes Offering Of Up To € |
| 2026-03-23 | NBIS | equity | 2026-03-20 16:06 | 09:59 | -0.8% | -2.2% | -4.6% | no | +57% | Nebius Group Announces Closing Of Private Offering Of Convertible Senior Notes, With Aggre |
| 2026-04-06 | GS | acquirer_cash | 2026-04-03 13:16 | 09:59 | -0.0% | +0.4% | -0.1% | no | -27% | Goldman Sachs Buys Innovator, Adds $31 Billion In Defined Outcome ETFs |
| 2026-04-09 | CRWV | equity | 2026-04-09 07:38 | 09:59 | +1.8% | +1.6% | +4.2% | yes | -6% | CoreWeave Intends To Offer $3B Aggregate Principal Amount Of Its Convertible Senior Notes  |
| 2026-04-10 | CRWV | equity | 2026-04-10 08:03 | 09:59 | +1.6% | +9.1% | +4.9% | no | -100% | CoreWeave Prices Upsized $3.5B Private Offering of 1.75% Convertible Senior Notes Due 2032 |
| 2026-04-16 | CRWV | debt | 2026-04-16 07:18 | 09:59 | +1.1% | -0.4% | +2.4% | yes | -78% | CoreWeave Announces Intended Private Offering Of $1B Of 9.750% Senior Unsecured Notes Due  |
| 2026-04-27 | WMT | debt | 2026-04-27 09:18 | 09:59 | -0.2% | -1.6% | -1.4% | yes | +33% | 'Walmart Plans to Sell Investment-Grade Bonds on Monday' - Bloomberg |
| 2026-05-12 | GOOGL | debt | 2026-05-12 04:56 | 09:59 | -0.3% | +0.0% | +0.2% | yes | -68% | Alphabet Announces Proposed Yen-Denominated Senior Notes Offering Across Five Maturities T |
| 2026-05-12 | NOW | debt | 2026-05-11 16:58 | 09:59 | +1.1% | -3.7% | -1.1% | yes | -9% | 'Software Firm ServiceNow Plans to Raise $4 Billion in Bond Sale' - Bloomberg |
| 2026-05-21 | NKE | debt | 2026-05-20 15:07 | 09:59 | -0.7% | +1.1% | +1.3% | yes | -82% | Nike Stock Soars As Energy Prices And Bond Yields Drop |
| 2026-06-03 | JPM | debt | 2026-06-03 12:29 | 12:31 | -0.4% | +0.3% | +0.3% | no | -42% | 'JPMorgan To Sell $1.85 Billion Debt For Belden's Ruckus Buyout' - Bloomberg News |
| 2026-06-08 | CIEN | equity | 2026-06-08 07:05 | 09:59 | +0.3% | -4.7% | +1.8% | yes | -22% | Ciena To Sell $2B Of Convertible Senior Notes Due 2031 In Private Offering |
| 2026-06-09 | CIEN | equity | 2026-06-09 03:37 | 09:59 | -0.2% | -5.8% | -3.3% | yes | +27% | Reported Earlier, Ciena Prices Upsized $2.5B Convertible Senior Notes Offering Due 2031 At |
| 2026-06-10 | SMCI | equity | 2026-06-10 08:08 | 09:59 | -12.4% | -17.8% | -17.9% | no | +287% | Super Micro Files For Common Stock Offering Of Up To $1.25B |
| 2026-06-12 | CRWV | debt | 2026-06-11 14:46 | 09:59 | +3.6% | +1.4% | +2.5% | yes | -100% | CoreWeave Prices $1.25B, €2B Senior Notes Due 2032 |
| 2026-06-15 | NVDA | debt | 2026-06-15 07:47 | 09:59 | +1.8% | +1.7% | +1.8% | yes | -100% | Nvidia Files Prospectus To Sell US$ Notes Across 2028, 2029, 2031, 2033, 2036, 2046 And 20 |
| 2026-06-22 | HOOD | equity | 2026-06-22 07:12 | 09:59 | -0.1% | -2.1% | -5.7% | no | +99% | Robinhood Intends To Offer $2B In Aggregate Principal Amount Of Convertible Senior Notes D |
| 2026-06-23 | HOOD | equity | 2026-06-23 03:53 | 09:59 | -3.9% | +1.5% | -1.4% | no | +4% | Reported Earlier, Robinhood Markets Prices $2B Private Offering Of 0.00% Convertible Senio |
| 2026-06-29 | RKLB | acquirer | 2026-06-29 07:05 | 09:59 | +8.0% | +7.3% | +5.0% | no | - | Rocket Lab To Acquire Iridium For ~$54 Per In Cash And Stock At EV Of ~$8B; IRDM Holders T |
| 2026-07-13 | HOOD | debt | 2026-07-13 14:26 | 14:28 | -0.6% | -1.3% | +0.2% | yes | -17% | 'Robinhood Eyes Its First Bond Sale Backed by Credit Card Bills' - Bloomberg |
| 2026-07-15 | GS | debt | 2026-07-14 16:33 | 09:59 | +0.7% | +0.3% | +0.7% | yes | -33% | 'Goldman Raises $10 Billion From Latest High-Grade Bond Sale' - Bloomberg |
| 2026-07-16 | BAC | debt | 2026-07-16 11:35 | 11:37 | +0.6% | -0.8% | +0.0% | yes | -24% | 'Bank of America Exits Chicago Plan to Sell Overdue Parking Debt' - Bloomberg |
| 2026-08-05 | BA | debt | 2026-08-05 14:09 | 14:11 | +0.3% | +0.9% | -0.1% | no | -31% | 'Boeing-Lockheed Rocket Joint Venture Taps Private Bond Market' - Bloomberg |
| 2026-08-10 | INTC | equity | 2026-08-10 07:46 | 09:59 | -3.4% | -0.7% | +0.3% | yes | -43% | Intel Announces $15B Offering Of Common Stock |
| 2026-08-11 | INTC | equity | 2026-08-11 02:43 | 09:59 | -0.8% | +1.0% | +0.3% | no | -25% | Intel Prices Upsized $20B Offering Of 210,526,315 Shares At $95 Per Share, Increased From  |
| 2026-08-13 | AMD | debt | 2026-08-13 08:55 | 09:59 | +0.0% | -0.0% | -2.6% | no | +32% | Advanced Micro Devices Files Automatic Shelf Registration Prospectus For Debt Offering Of  |
| 2026-08-13 | RKLB | equity | 2026-08-13 07:04 | 09:59 | -3.3% | +2.1% | -3.2% | no | +25% | Rocket Lab Announces $1.94B At-The-Market Common Stock Offering Program |
| 2026-08-19 | GOOGL | debt | 2026-08-19 11:00 | 11:02 | -0.5% | +0.7% | -0.2% | no | -0% | Alphabet Raises $3.9B in First Australian Bond Sale as AI Spending Surges |
| 2026-08-19 | NBIS | equity | 2026-08-19 07:39 | 09:59 | -6.5% | -3.7% | +2.4% | yes | -39% | Nebius Announces Proposed Private Offering Of $4.5B Of Convertible Senior Notes In Two Ser |
| 2026-08-20 | NBIS | equity | 2026-08-20 01:25 | 09:59 | -0.4% | -1.3% | +1.6% | yes | -62% | Reported Earlier, Nebius Group Prices Upsized $5.0B Convertible Senior Notes Offering $3.0 |
| 2026-08-28 | MRNA | equity | 2026-08-28 07:03 | 09:59 | -4.0% | +0.6% | +0.3% | no | -6% | Moderna Announces Pricing Of Upsized $2.6B 0.00% Convertible Senior Notes Due 2032; Initia |
| 2026-09-11 | VST | debt | 2026-09-11 02:57 | 09:59 | +1.2% | -0.3% | +0.8% | yes | -94% | Reported Earlier, Vistra Prices $1.5B Registered Offering Of Junior Subordinated Notes, Sp |
| 2026-09-14 | ORCL | equity | 2026-09-14 01:49 | 09:59 | -5.7% | +2.1% | +0.1% | no | -24% | Reported Saturday, Oracle's Larry Ellison Terminates Stock Sale Plan, Confirms No Other Pl |
| 2026-09-17 | CRWV | equity | 2026-09-17 07:08 | 09:59 | -2.3% | -1.9% | +0.0% | yes | -49% | CoreWeave Announces Private Offering Of $3B Of Convertible Senior Notes Due 2033 |
| 2026-09-18 | CRWV | equity | 2026-09-18 07:06 | 09:59 | -0.1% | +1.9% | +1.8% | no | -100% | CoreWeave Announces Pricing Of Upsized $3.7B Convertible Notes Due 2033 At 2.875%, Convers |
| 2026-09-22 | GS | acquirer_cash | 2026-09-22 09:06 | 09:59 | +0.8% | -1.8% | -0.1% | yes | -3% | 'Goldman in Talks to Buy $37 Billion Credit Firm Palmer Square' - Bloomberg |
| 2026-09-29 | AMD | acquirer | 2026-09-28 16:05 | 09:59 | +1.5% | -1.4% | -2.2% | no | +58% | AMD Announces $8.2B All-Stock Deal To Acquire AI Lab World Labs, With Founder Fei-Fei Li J |
| 2026-10-05 | QCOM | equity | 2026-10-02 16:33 | 09:59 | +0.1% | -2.2% | -0.4% | yes | -19% | Qualcomm Files Prospectus For Offering 25M Common Shares |
| 2026-10-15 | JPM | debt | 2026-10-15 11:27 | 11:29 | +0.6% | -0.5% | +0.4% | yes | -56% | 'JPMorgan Mulls Revival of Software Debt Deal Lenders Had Shunned' - Bloomberg Exclusive |
| 2026-10-19 | WMT | debt | 2026-10-19 11:40 | 11:42 | -0.3% | +0.2% | +0.2% | no | -32% | 'Walmart Sells US Debt, Eyes Canadian Market as Spending Grows' - Bloomberg |
| 2026-10-26 | META | equity | 2026-10-26 07:01 | 09:59 | -0.6% | -1.3% | -0.1% | yes | -100% | Meta Launches Offering Of 250M Depositary Shares And $22.5B Offering Of Class A Common Sto |
| 2026-10-27 | META | equity | 2026-10-27 06:31 | 09:59 | -0.5% | -1.2% | -0.7% | yes | -27% | Meta Prices Upsized $25 Billion Common Stock Offering and Depositary Shares |
