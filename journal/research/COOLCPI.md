# Call bought at the close of a release day, sold one or two days later

Real option prices (Alpaca), 2024-02+. Entry 15:50 on the release day, exit 15:50 one (d1) or two (d2) trading days later, ~1-week expiry. Costs 10% each way. Columns: n | win% | avg | without the best | without the best two.

| event | class | stock | pick | period | d1: n | win | avg | -best | -best2 | d2: n | win | avg | -best | -best2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CPI | COOL | SPY | atm | all | 16 | 38% | -10% | -14% | -17% | 16 | 50% | +4% | -3% | -9% |
| CPI | COOL | SPY | atm | last 6 months | 2 | 50% | +6% | -15% | - | 2 | 50% | -10% | -58% | - |
| CPI | COOL | SPY | otm1 | all | 16 | 31% | -11% | -18% | -22% | 16 | 50% | +6% | -8% | -19% |
| CPI | COOL | SPY | otm1 | last 6 months | 2 | 50% | +5% | -29% | - | 2 | 50% | -12% | -78% | - |
| CPI | COOL | QQQ | atm | all | 15 | 33% | -14% | -19% | -25% | 14 | 43% | +0% | -11% | -21% |
| CPI | COOL | QQQ | atm | last 6 months | 2 | 50% | +2% | -46% | - | 1 | 0% | -88% | - | - |
| CPI | COOL | QQQ | otm1 | all | 12 | 33% | -13% | -24% | -29% | 12 | 42% | +10% | -9% | -30% |
| CPI | COOL | QQQ | otm1 | last 6 months | - | - | - | - | - | 1 | 0% | -79% | - | - |
| CPI | INLINE | SPY | atm | all | 6 | 50% | -5% | -27% | -43% | 6 | 33% | -22% | -50% | -64% |
| CPI | INLINE | SPY | atm | last 6 months | 1 | 100% | +37% | - | - | 1 | 0% | -2% | - | - |
| CPI | INLINE | SPY | otm1 | all | 6 | 33% | +1% | -29% | -54% | 5 | 0% | -64% | -77% | -94% |
| CPI | INLINE | SPY | otm1 | last 6 months | 1 | 100% | +68% | - | - | 1 | 0% | -25% | - | - |
| CPI | INLINE | QQQ | atm | all | 4 | 0% | -49% | -56% | -58% | 5 | 20% | -45% | -61% | -70% |
| CPI | INLINE | QQQ | atm | last 6 months | - | - | - | - | - | 1 | 100% | +18% | - | - |
| CPI | INLINE | QQQ | otm1 | all | 3 | 0% | -66% | -67% | -68% | 4 | 25% | -56% | -79% | -94% |
| CPI | INLINE | QQQ | otm1 | last 6 months | - | - | - | - | - | 1 | 100% | +13% | - | - |
| CPI | HOT | SPY | atm | all | 8 | 50% | -2% | -12% | -17% | 9 | 44% | +5% | -11% | -25% |
| CPI | HOT | SPY | atm | last 6 months | 3 | 33% | -15% | -30% | -51% | 2 | 0% | -74% | -79% | - |
| CPI | HOT | SPY | otm1 | all | 10 | 60% | +22% | +6% | -7% | 10 | 50% | +33% | +10% | -6% |
| CPI | HOT | SPY | otm1 | last 6 months | 3 | 33% | -15% | -38% | -62% | 3 | 33% | -22% | -87% | -89% |
| CPI | HOT | QQQ | atm | all | 9 | 44% | +4% | -3% | -13% | 9 | 56% | -3% | -15% | -26% |
| CPI | HOT | QQQ | atm | last 6 months | 2 | 0% | -43% | -54% | - | 2 | 0% | -87% | -91% | - |
| CPI | HOT | QQQ | otm1 | all | 10 | 50% | +13% | +4% | -7% | 9 | 56% | +8% | -10% | -23% |
| CPI | HOT | QQQ | otm1 | last 6 months | 3 | 33% | -22% | -50% | -63% | 3 | 33% | -35% | -92% | -94% |
| NFP | COOL | SPY | atm | all | 8 | 38% | -6% | -15% | -23% | 7 | 57% | +1% | -13% | -29% |
| NFP | COOL | SPY | atm | last 6 months | 3 | 67% | +15% | -5% | -33% | 2 | 50% | +11% | -61% | - |
| NFP | COOL | SPY | otm1 | all | 8 | 38% | +3% | -15% | -27% | 8 | 50% | +4% | -15% | -37% |
| NFP | COOL | SPY | otm1 | last 6 months | 3 | 67% | +37% | -7% | -49% | 3 | 33% | +11% | -55% | -77% |
| NFP | COOL | QQQ | atm | all | 8 | 38% | -10% | -14% | -20% | 8 | 38% | -13% | -22% | -32% |
| NFP | COOL | QQQ | atm | last 6 months | 3 | 67% | -0% | -9% | -36% | 3 | 33% | -26% | -63% | -65% |
| NFP | COOL | QQQ | otm1 | all | 8 | 50% | -10% | -16% | -22% | 8 | 38% | -15% | -26% | -38% |
| NFP | COOL | QQQ | otm1 | last 6 months | 3 | 67% | -4% | -16% | -49% | 3 | 33% | -31% | -77% | -78% |
| NFP | INLINE | SPY | atm | all | 9 | 33% | -22% | -29% | -34% | 9 | 22% | -32% | -40% | -46% |
| NFP | INLINE | SPY | otm1 | all | 9 | 33% | -26% | -35% | -42% | 9 | 11% | -39% | -49% | -55% |
| NFP | INLINE | QQQ | atm | all | 9 | 22% | -21% | -29% | -36% | 9 | 33% | -29% | -38% | -43% |
| NFP | INLINE | QQQ | otm1 | all | 8 | 25% | -23% | -34% | -44% | 8 | 12% | -37% | -48% | -56% |
| NFP | HOT | SPY | atm | all | 11 | 0% | -36% | -39% | -42% | 11 | 18% | -33% | -41% | -48% |
| NFP | HOT | SPY | atm | last 6 months | 3 | 0% | -36% | -49% | -62% | 3 | 0% | -58% | -73% | -86% |
| NFP | HOT | SPY | otm1 | all | 11 | 0% | -44% | -47% | -51% | 11 | 18% | -40% | -50% | -56% |
| NFP | HOT | SPY | otm1 | last 6 months | 3 | 0% | -49% | -64% | -80% | 3 | 0% | -72% | -82% | -95% |
| NFP | HOT | QQQ | atm | all | 10 | 0% | -35% | -38% | -41% | 11 | 27% | -31% | -38% | -44% |
| NFP | HOT | QQQ | atm | last 6 months | 2 | 0% | -21% | -31% | - | 3 | 0% | -53% | -55% | -56% |
| NFP | HOT | QQQ | otm1 | all | 10 | 0% | -41% | -44% | -48% | 9 | 11% | -43% | -50% | -57% |
| NFP | HOT | QQQ | otm1 | last 6 months | 2 | 0% | -27% | -42% | - | 2 | 0% | -62% | -69% | - |
