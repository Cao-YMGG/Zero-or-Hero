# megacap_reclaim on real option prices

2026-05-01 to 2026-10-31; AAPL, AMZN, MSFT, GOOGL, META, NVDA, TSLA; flush >= 0.5% in 15 minutes, back to the open before 12:00, nearest expiry, no macro days. Costs 10% each way. Columns: n | win% | avg | without the best | without the best two. The live rule is d0.15 with `trail2x`. See zoh/research/reclaim.py.

| contract | exit | last 3 months | all since May |
|---|---|---|---|
| d0.10 | trail2x | 127 | 29% | -33% | -36% | -39% | 253 | 32% | -27% | -30% | -32% |
| d0.10 | trail1.5x | 127 | 28% | -31% | -33% | -36% | 253 | 32% | -26% | -29% | -31% |
| d0.10 | half3_trail | 127 | 29% | -29% | -31% | -33% | 253 | 32% | -23% | -25% | -27% |
| d0.10 | hold | 127 | 13% | -45% | -57% | -60% | 253 | 15% | -28% | -34% | -41% |
| d0.15 | trail2x | 127 | 28% | -31% | -34% | -36% | 253 | 32% | -25% | -27% | -30% |
| d0.15 | trail1.5x | 127 | 31% | -29% | -32% | -34% | 253 | 34% | -23% | -25% | -27% |
| d0.15 | half3_trail | 127 | 28% | -26% | -29% | -31% | 253 | 32% | -22% | -24% | -25% |
| d0.15 | hold | 127 | 15% | -42% | -51% | -54% | 253 | 18% | -24% | -30% | -35% |
| d0.30 | trail2x | 127 | 30% | -31% | -33% | -35% | 253 | 34% | -21% | -24% | -27% |
| d0.30 | trail1.5x | 127 | 29% | -28% | -30% | -32% | 253 | 33% | -22% | -25% | -27% |
| d0.30 | half3_trail | 127 | 30% | -29% | -31% | -33% | 253 | 34% | -22% | -24% | -26% |
| d0.30 | hold | 127 | 21% | -27% | -34% | -37% | 253 | 24% | -19% | -22% | -26% |
