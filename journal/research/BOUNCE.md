# Failed bounce in a cooling theme: the put mirror on real option prices

14 days in 2 years where SMH was down >= 10% over the prior month and gapped up >= 1% (Alpaca daily and minute bars, option minute bars, costs 10% each way). 'Failed' = SMH back below its open at 11:00. Pick = weakest of NVDA, AMD, MU, AVGO, INTC, MRVL from its own open at 11:00, below its open, outside a report window; put bought at 11:03 on the nearest expiry. Columns: n | win% | avg | without the best | without the best two. See zoh/research/bounce.py.

## Base rate

| window | gap-up days | failed by 11:00 | SMH open->close, failed days | SMH open->close, held days | pick found |
|---|---|---|---|---|---|
| last 3 months | 2 | 1 (50%) | -3.97% (1/1 down) | +1.58% (0/1 down) | 1 |
| 1 year | 6 | 3 (50%) | -2.17% (2/3 down) | +2.36% (0/3 down) | 3 |
| all | 14 | 6 (43%) | +0.48% (3/6 down) | +1.44% (1/8 down) | 6 |

## Pick put (weakest chip)

| window | delta | exit | n | win% | avg | -best | -best2 |
|---|---|---|---|---|---|---|---|
| last 3 months | d0.10 | half3_arm1.5 | 1 | 100% | +192% | - | - |
| last 3 months | d0.10 | half3_hold | 1 | 100% | +192% | - | - |
| last 3 months | d0.10 | hold | 1 | 100% | +181% | - | - |
| last 3 months | d0.10 | trail2x | 1 | 100% | +181% | - | - |
| last 3 months | d0.10 | stock_stop | 1 | 100% | +181% | - | - |
| last 3 months | d0.20 | half3_arm1.5 | 1 | 100% | +178% | - | - |
| last 3 months | d0.20 | half3_hold | 1 | 100% | +178% | - | - |
| last 3 months | d0.20 | hold | 1 | 100% | +156% | - | - |
| last 3 months | d0.20 | trail2x | 1 | 100% | +156% | - | - |
| last 3 months | d0.20 | stock_stop | 1 | 100% | +156% | - | - |
| last 3 months | d0.30 | half3_arm1.5 | 1 | 100% | +126% | - | - |
| last 3 months | d0.30 | half3_hold | 1 | 100% | +126% | - | - |
| last 3 months | d0.30 | hold | 1 | 100% | +126% | - | - |
| last 3 months | d0.30 | trail2x | 1 | 100% | +126% | - | - |
| last 3 months | d0.30 | stock_stop | 1 | 100% | +126% | - | - |
| 1 year | d0.10 | half3_arm1.5 | 3 | 67% | +103% | +59% | -58% |
| 1 year | d0.10 | half3_hold | 3 | 67% | +66% | +4% | -58% |
| 1 year | d0.10 | hold | 3 | 33% | +9% | -76% | -95% |
| 1 year | d0.10 | trail2x | 3 | 67% | +83% | +35% | -58% |
| 1 year | d0.10 | stock_stop | 3 | 33% | +9% | -76% | -95% |
| 1 year | d0.20 | half3_arm1.5 | 3 | 33% | +39% | -30% | -60% |
| 1 year | d0.20 | half3_hold | 3 | 67% | +69% | +14% | -60% |
| 1 year | d0.20 | hold | 3 | 33% | +7% | -68% | -76% |
| 1 year | d0.20 | trail2x | 3 | 67% | +62% | +15% | -60% |
| 1 year | d0.20 | stock_stop | 3 | 33% | +7% | -68% | -76% |
| 1 year | d0.30 | half3_arm1.5 | 3 | 67% | +69% | +36% | -53% |
| 1 year | d0.30 | half3_hold | 3 | 67% | +47% | +8% | -53% |
| 1 year | d0.30 | hold | 3 | 33% | +3% | -59% | -64% |
| 1 year | d0.30 | trail2x | 3 | 67% | +48% | +8% | -53% |
| 1 year | d0.30 | stock_stop | 3 | 33% | +3% | -59% | -64% |
| all | d0.10 | half3_arm1.5 | 6 | 50% | +67% | +30% | -11% |
| all | d0.10 | half3_hold | 6 | 50% | +49% | +8% | -38% |
| all | d0.10 | hold | 6 | 33% | +27% | -26% | -78% |
| all | d0.10 | trail2x | 6 | 50% | +64% | +18% | -23% |
| all | d0.10 | stock_stop | 6 | 33% | +28% | -25% | -77% |
| all | d0.20 | half3_arm1.5 | 6 | 33% | +28% | -7% | -53% |
| all | d0.20 | half3_hold | 6 | 50% | +43% | +11% | -31% |
| all | d0.20 | hold | 6 | 33% | +11% | -27% | -72% |
| all | d0.20 | trail2x | 6 | 50% | +39% | +7% | -31% |
| all | d0.20 | stock_stop | 6 | 33% | +12% | -26% | -71% |
| all | d0.30 | half3_arm1.5 | 6 | 50% | +38% | +11% | -20% |
| all | d0.30 | half3_hold | 6 | 50% | +26% | -3% | -35% |
| all | d0.30 | hold | 6 | 33% | +4% | -29% | -68% |
| all | d0.30 | trail2x | 6 | 50% | +27% | -2% | -34% |
| all | d0.30 | stock_stop | 6 | 33% | +11% | -21% | -58% |

## SMH put (index version)

| window | delta | exit | n | win% | avg | -best | -best2 |
|---|---|---|---|---|---|---|---|
| last 3 months | d0.10 | half3_arm1.5 | 1 | 100% | +179% | - | - |
| last 3 months | d0.10 | half3_hold | 1 | 100% | +179% | - | - |
| last 3 months | d0.10 | hold | 1 | 100% | +158% | - | - |
| last 3 months | d0.10 | trail2x | 1 | 100% | +158% | - | - |
| last 3 months | d0.10 | stock_stop | 1 | 100% | +158% | - | - |
| last 3 months | d0.20 | half3_arm1.5 | 1 | 100% | +137% | - | - |
| last 3 months | d0.20 | half3_hold | 1 | 100% | +137% | - | - |
| last 3 months | d0.20 | hold | 1 | 100% | +137% | - | - |
| last 3 months | d0.20 | trail2x | 1 | 100% | +137% | - | - |
| last 3 months | d0.20 | stock_stop | 1 | 100% | +137% | - | - |
| last 3 months | d0.30 | half3_arm1.5 | 1 | 100% | +93% | - | - |
| last 3 months | d0.30 | half3_hold | 1 | 100% | +93% | - | - |
| last 3 months | d0.30 | hold | 1 | 100% | +93% | - | - |
| last 3 months | d0.30 | trail2x | 1 | 100% | +93% | - | - |
| last 3 months | d0.30 | stock_stop | 1 | 100% | +93% | - | - |
| 1 year | d0.10 | half3_arm1.5 | 3 | 67% | +65% | +8% | -36% |
| 1 year | d0.10 | half3_hold | 3 | 33% | +15% | -67% | -98% |
| 1 year | d0.10 | hold | 3 | 33% | +8% | -67% | -98% |
| 1 year | d0.10 | trail2x | 3 | 67% | +58% | +8% | -36% |
| 1 year | d0.10 | stock_stop | 3 | 33% | +11% | -62% | -98% |
| 1 year | d0.20 | half3_arm1.5 | 3 | 67% | +50% | +6% | -33% |
| 1 year | d0.20 | half3_hold | 3 | 33% | +6% | -60% | -87% |
| 1 year | d0.20 | hold | 3 | 33% | +6% | -60% | -87% |
| 1 year | d0.20 | trail2x | 3 | 67% | +50% | +6% | -33% |
| 1 year | d0.20 | stock_stop | 3 | 33% | +9% | -55% | -87% |
| 1 year | d0.30 | half3_arm1.5 | 3 | 67% | +29% | -3% | -29% |
| 1 year | d0.30 | half3_hold | 3 | 33% | -7% | -58% | -86% |
| 1 year | d0.30 | hold | 3 | 33% | -7% | -58% | -86% |
| 1 year | d0.30 | trail2x | 3 | 67% | +29% | -3% | -29% |
| 1 year | d0.30 | stock_stop | 3 | 33% | -5% | -54% | -86% |
| all | d0.10 | half3_arm1.5 | 6 | 50% | +57% | +8% | -35% |
| all | d0.10 | half3_hold | 6 | 33% | +32% | -22% | -73% |
| all | d0.10 | hold | 6 | 33% | +44% | -27% | -73% |
| all | d0.10 | trail2x | 6 | 50% | +69% | +3% | -35% |
| all | d0.10 | stock_stop | 6 | 33% | +57% | -11% | -53% |
| all | d0.20 | half3_arm1.5 | 6 | 50% | +45% | -1% | -35% |
| all | d0.20 | half3_hold | 6 | 33% | +23% | -27% | -68% |
| all | d0.20 | hold | 6 | 33% | +32% | -27% | -68% |
| all | d0.20 | trail2x | 6 | 50% | +54% | -1% | -35% |
| all | d0.20 | stock_stop | 6 | 33% | +45% | -12% | -50% |
| all | d0.30 | half3_arm1.5 | 6 | 50% | +17% | -12% | -38% |
| all | d0.30 | half3_hold | 6 | 33% | -1% | -34% | -66% |
| all | d0.30 | hold | 6 | 33% | -1% | -34% | -66% |
| all | d0.30 | trail2x | 6 | 50% | +17% | -12% | -38% |
| all | d0.30 | stock_stop | 6 | 33% | +12% | -18% | -46% |

## Each failed day with a pick (0.20 delta)

| day | SMH 1m | gap | SMH 11:00 | SMH close | pick | pick 11:00 -> close | peak x | live | half3_hold | hold | stock stop | SMH put live / hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-03-12 | -13% | +2.9% | -0.44% | +0.11% | INTC | -2.5% -> -0.7% | 0.9 | -60% | -60% | -60% | -60% | -58% / -58% |
| 2025-04-08 | -18% | +4.4% | -0.26% | -6.75% | AVGO | -1.2% -> -6.7% | 3.2 | +205% | +205% | +202% | +202% | +271% / +330% |
| 2025-04-09 | -16% | +1.0% | -0.50% | +16.03% | MU | -3.4% -> +17.6% | 0.8 | -93% | -93% | -93% | -89% | -95% / -95% |
| 2026-07-21 | -10% | +4.0% | -0.25% | +0.57% | AVGO | -1.6% -> -0.9% | 0.8 | -60% | -60% | -60% | -60% | -33% / -33% |
| 2026-07-31 | -18% | +3.5% | -2.41% | -3.11% | MU | -8.4% -> -10.5% | 3.5 | -1% | +87% | -76% | -76% | +45% / -87% |
| 2026-11-02 | -15% | +1.3% | -0.59% | -3.97% | MRVL | -3.9% -> -10.5% | 3.0 | +178% | +178% | +156% | +156% | +137% / +137% |
