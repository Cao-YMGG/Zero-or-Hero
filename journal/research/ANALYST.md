# Analyst rating changes as 0DTE catalysts — 171 pre-market events, 25 large caps, last 2 years

Moves are signed in the rating's direction (an upgrade counts the stock's rise as positive, a downgrade its fall). Baseline = every day of the same stocks, taking the open→close move in the gap's direction.

## Stock moves

| group | n | gap (median) | open→close (median) | open→close > 0 | > +1% | > +2% |
|---|---|---|---|---|---|---|
| all rating changes | 171 | +1.5% | +0.3% | 54% | 35% | 23% |
| upgrades | 111 | +1.6% | +0.6% | 57% | 41% | 29% |
| downgrades | 60 | +1.2% | -0.0% | 48% | 22% | 12% |
| small gap (< 2%) | 102 | +0.5% | +0.3% | 55% | 34% | 22% |
| big gap (>= 2%) | 69 | +3.8% | +0.2% | 52% | 35% | 25% |
| baseline: all days, follow the gap | 12650 | +0.8% | -0.1% | 49% | 30% | 17% |

## Sniper rule with options (same-day expiry days only)

54 events fell on a same-day expiry day. The rule fires when the stock is >= 1% from the open in the rating's direction between 09:45 and 12:00. Options are priced with Black-Scholes at 1.15x the day's realized intraday vol, 3% slippage. "half at 2x" sells half at +100% and trails the rest.

| rule | trades | fired | win% | avg / trade | median | best | ≥ 2x |
|---|---|---|---|---|---|---|---|
| d0.2 trail (sniper today) | 30 | 56% | 53% | +11% | +18% | +353% | 6 |
| d0.3 half at 2x + trail | 30 | 56% | 53% | +25% | +63% | +316% | 6 |
| d0.08 trail (lottery) | 30 | 56% | 53% | +41% | +17% | +658% | 8 |
| ↳ d0.2 trail (sniper today), upgrades | 18 | | 56% | +20% | +39% | +242% | 5 |
| ↳ d0.2 trail (sniper today), downgrades | 12 | | 50% | -2% | -42% | +353% | 1 |
| ↳ d0.3 half at 2x + trail, upgrades | 18 | | 56% | +43% | +67% | +316% | 5 |
| ↳ d0.3 half at 2x + trail, downgrades | 12 | | 50% | -1% | -15% | +193% | 1 |
| ↳ d0.08 trail (lottery), upgrades | 18 | | 56% | +48% | +31% | +415% | 6 |
| ↳ d0.08 trail (lottery), downgrades | 12 | | 50% | +30% | -41% | +658% | 2 |

## By stock (stock moves)

| stock | events | upgrades | open→close median | > 0 |
|---|---|---|---|---|
| INTC | 7 | 7 | +2.7% | 86% |
| ANET | 3 | 3 | +1.7% | 100% |
| NVDA | 4 | 3 | +1.6% | 75% |
| COIN | 10 | 6 | +1.1% | 70% |
| META | 5 | 5 | +1.1% | 60% |
| AMD | 14 | 8 | +0.9% | 57% |
| PLTR | 7 | 6 | +0.8% | 71% |
| UBER | 5 | 2 | +0.6% | 80% |
| ADBE | 11 | 2 | +0.4% | 55% |
| LITE | 5 | 4 | +0.3% | 60% |
| QCOM | 4 | 1 | +0.2% | 50% |
| GOOGL | 6 | 4 | +0.1% | 50% |
| AAPL | 21 | 11 | +0.0% | 52% |
| STX | 3 | 3 | -0.0% | 33% |
| ARM | 5 | 3 | -0.0% | 40% |
| MSFT | 8 | 7 | -0.0% | 38% |
| MU | 5 | 2 | -0.1% | 40% |
| NFLX | 14 | 9 | -0.2% | 43% |
| AMZN | 2 | 1 | -0.2% | 50% |
| CRM | 6 | 2 | -0.3% | 50% |
| TSLA | 12 | 10 | -0.5% | 50% |
| AVGO | 2 | 1 | -0.7% | 50% |
| ORCL | 6 | 6 | -1.5% | 33% |
| WDC | 2 | 2 | -2.1% | 0% |
| SMCI | 4 | 3 | -7.0% | 25% |

## Every event (option column: d0.2 trail (sniper today))

| day | stock | rating | gap | open→close | option | headline |
|---|---|---|---|---|---|---|
| 2024-10-08 | QCOM | down | +1.2% | -0.9% | — | Keybanc Downgrades Qualcomm to Sector Weight |
| 2024-10-16 | AAPL | up | -1.0% | +0.1% | no fire | Apple Mini Gets An AI Upgrade 3 Years After Last Facelift — Price Starts At $499 |
| 2024-10-17 | UBER | down | +2.4% | +0.0% | — | Daiwa Capital Downgrades Uber Technologies to Neutral, Announces $84 Price Target |
| 2024-10-24 | TSLA | up | +14.5% | +6.5% | — | Elon Musk Promises Free Hardware 4 Upgrades if Tesla's Hardware 3 Fails Full Self-Driving  |
| 2024-10-30 | GOOGL | up | +6.5% | -3.4% | no fire | Seaport Global Upgrades Alphabet to Buy, Announces $200 Price Target |
| 2024-11-06 | SMCI | down | +24.7% | -8.8% | — | JP Morgan Downgrades Super Micro Computer to Underweight, Lowers Price Target to $23 |
| 2024-11-07 | PLTR | down | -0.5% | -0.1% | — | Jefferies Downgrades Palantir Technologies to Underperform, Maintains Price Target to $28 |
| 2024-12-09 | AMD | down | +2.1% | +3.6% | +16% | B of A Securities Downgrades Advanced Micro Devices to Neutral, Lowers Price Target to $15 |
| 2024-12-09 | TSLA | up | +2.2% | -2.0% | no fire | Tesla Stock Hits $400 In Overnight Trading On Robinhood Amid Analyst Upgrades And FSD Opti |
| 2024-12-16 | NFLX | down | -0.5% | +0.3% | — | Loop Capital Downgrades Netflix to Hold, Raises Price Target to $950 |
| 2024-12-17 | TSLA | up | +2.8% | +0.8% | — | Mizuho Upgrades Tesla to Outperform, Raises Price Target to $515 |
| 2024-12-19 | MU | down | +13.3% | +3.3% | — | B of A Securities Downgrades Micron Technology to Neutral, Lowers Price Target to $110 |
| 2024-12-26 | AAPL | up | -0.0% | +0.3% | — | Tech Bull Predicts 26% Upside For Apple Stock, Sees 'Golden Era Of Growth' For Cupertino D |
| 2024-12-31 | AAPL | up | +0.1% | -0.8% | — | iPhone 17 To Get Display Upgrade As Apple Finally Ditches 60Hz Technology? New Leak Reiter |
| 2025-01-02 | GOOGL | down | -0.7% | +0.6% | — | JMP Securities Downgrades Alphabet to Market Perform, Maintains Price Target to $220 |
| 2025-01-02 | UBER | down | -3.1% | -1.6% | — | JMP Securities Downgrades Uber Technologies to Market Perform, Maintains Price Target to $ |
| 2025-01-07 | AAPL | down | +0.8% | +0.3% | — | MoffettNathanson Downgrades Apple to Sell, Lowers Price Target to $188 |
| 2025-01-08 | ADBE | down | +1.3% | -0.5% | — | Deutsche Bank Downgrades Adobe to Hold, Lowers Price Target to $475 |
| 2025-01-10 | AMD | down | +3.0% | +1.8% | -100% | Goldman Sachs Downgrades Advanced Micro Devices to Neutral, Lowers Price Target to $129 |
| 2025-01-15 | AMD | down | -1.3% | -2.1% | no fire | AMD Shares Hint At A Reversal As Charts Show Bullish Stick Sandwich Following A Double Dow |
| 2025-01-16 | NFLX | up | +1.5% | -2.2% | — | Seaport Global Upgrades Netflix to Buy, Announces $955 Price Target |
| 2025-01-17 | LITE | up | +5.3% | +0.3% | no fire | Barclays Upgrades Lumentum Holdings to Overweight, Raises Price Target to $125 |
| 2025-01-21 | AAPL | down | +2.6% | +0.6% | — | Jefferies Downgrades Apple to Underperform, Lowers Price Target to $200.75 |
| 2025-01-22 | NFLX | up | +14.8% | -4.4% | — | Canaccord Genuity Upgrades Netflix to Buy, Raises Price Target to $1150 |
| 2025-01-23 | NFLX | up | +0.4% | +2.8% | — | Wolfe Research Upgrades Netflix to Outperform, Announces $1100 Price Target |
| 2025-01-29 | AAPL | down | +1.7% | -2.2% | no fire | Oppenheimer Downgrades Apple to Perform |
| 2025-01-29 | COIN | up | +0.0% | +3.3% | — | Mizuho Upgrades Coinbase Glb to Neutral, Raises Price Target to $290 |
| 2025-02-04 | MSFT | up | +0.4% | -0.1% | — | Windows 11 Disaster? Microsoft Quietly Removes Workaround For Unsupported PCs, Potentially |
| 2025-02-04 | PLTR | up | +22.8% | +1.0% | — | Morgan Stanley Upgrades Palantir Technologies to Equal-Weight, Raises Price Target to $95 |
| 2025-02-27 | TSLA | up | +0.1% | -3.2% | — | Elon Musk's Tesla Upgrades Giga Texas: Driverless Cars, Cybercab Preparations, GPU Trainin |
| 2025-03-05 | PLTR | up | +2.3% | +4.4% | — | William Blair Upgrades Palantir Technologies to Market Perform |
| 2025-03-05 | ANET | up | +2.0% | +0.7% | — | UBS Upgrades Arista Networks to Buy, Raises Price Target to $115 |
| 2025-03-13 | MSFT | up | -0.0% | -1.1% | — | DA Davidson Upgrades Microsoft to Buy, Raises Price Target to $450 |
| 2025-03-13 | INTC | up | +13.6% | +0.9% | — | B of A Securities Upgrades Intel to Neutral, Raises Price Target to $25 |
| 2025-03-17 | NFLX | up | +2.4% | +1.1% | — | MoffettNathanson Upgrades Netflix to Buy, Raises Price Target to $1100 |
| 2025-03-19 | TSLA | up | +2.8% | +1.8% | -97% | Cantor Fitzgerald Upgrades Tesla to Overweight, Maintains Price Target to $425 |
| 2025-03-21 | SMCI | up | +0.4% | +7.4% | +19% | JP Morgan Upgrades Super Micro Computer to Neutral, Raises Price Target to $45 |
| 2025-03-24 | LITE | up | +5.9% | +4.4% | — | Raymond James Upgrades Lumentum Holdings to Strong Buy, Lowers Price Target to $82 |
| 2025-03-26 | MU | down | -1.9% | +4.0% | +353% | China Renaissance Downgrades Micron Technology to Hold, Announces $84 Price Target |
| 2025-03-27 | AMD | down | +3.7% | -0.5% | — | Jefferies Downgrades Advanced Micro Devices to Hold, Lowers Price Target to $120 |
| 2025-04-04 | NVDA | down | +2.8% | +4.7% | +75% | Nvidia Slips Into Bearish Trend As HSBC Downgrades AI Giant |
| 2025-04-09 | AAPL | up | -0.3% | +15.6% | +100% | Jefferies Upgrades Apple to Hold, Lowers Price Target to $167.88 |
| 2025-04-10 | WDC | up | -1.4% | -2.6% | — | Benchmark Upgrades Western Digital to Buy, Announces $55 Price Target |
| 2025-04-14 | AAPL | up | +6.7% | -4.2% | no fire | Keybanc Upgrades Apple to Sector Weight |
| 2025-04-17 | MSFT | down | -0.6% | +1.6% | — | Keybanc Downgrades Microsoft to Sector Weight |
| 2025-04-21 | AMZN | down | +1.7% | +1.3% | +45% | Raymond James Downgrades Amazon.com to Outperform, Lowers Price Target to $195 |
| 2025-04-21 | CRM | down | +2.8% | +1.7% | — | DA Davidson Downgrades Salesforce to Underperform, Announces $200 Price Target |
| 2025-04-24 | AAPL | down | -0.1% | -1.7% | — | AAPL Stock Faces Analyst Downgrades On Looming Tariffs, Supply Chain Pressures: 'A Lose-Lo |
| 2025-04-24 | ADBE | up | +0.5% | +2.1% | — | Adobe Empowers Creators With Breakthrough Speed, Precision, And Flexibility Through New Cr |
| 2025-04-29 | ANET | up | +1.4% | +1.7% | — | Rosenblatt Upgrades Arista Networks to Neutral, Raises Price Target to $85 |
| 2025-05-01 | WDC | up | +1.9% | -1.7% | — | JP Morgan Upgrades Western Digital to Overweight, Raises Price Target to $57 |
| 2025-05-02 | AAPL | down | +3.4% | +0.4% | -100% | Jefferies Downgrades Apple to Underperform, Raises Price Target to $170.62 |
| 2025-05-19 | NFLX | down | +1.5% | -1.5% | — | JP Morgan Downgrades Netflix to Neutral, Raises Price Target to $1220 |
| 2025-05-29 | CRM | down | +4.5% | -1.3% | — | RBC Capital Downgrades Salesforce to Sector Perform, Lowers Price Target to $275 |
| 2025-06-04 | AAPL | down | +0.2% | +0.0% | no fire | Needham Downgrades Apple to Hold, Maintains Price Target to $225 |
| 2025-06-09 | TSLA | down | +3.1% | -7.9% | no fire | Baird Downgrades Tesla to Neutral, Maintains Price Target to $320 |
| 2025-06-13 | ORCL | up | +0.9% | +6.8% | +142% | BMO Capital Upgrades Oracle to Outperform, Raises Price Target to $235 |
| 2025-06-27 | GOOGL | up | +0.0% | +2.9% | no fire | JMP Securities Upgrades Alphabet to Market Outperform, Maintains Price Target to $220 |
| 2025-06-27 | UBER | down | +1.1% | +0.6% | -100% | Canaccord Genuity Downgrades Uber Technologies to Hold, Lowers Price Target to $84 |
| 2025-06-30 | ORCL | up | +7.7% | -3.5% | — | Stifel Upgrades Oracle to Buy, Raises Price Target to $250 |
| 2025-07-03 | META | up | +1.8% | -1.0% | — | Needham Upgrades Meta Platforms to Hold |
| 2025-07-09 | MSFT | up | +0.7% | +0.6% | -100% | Oppenheimer Upgrades Microsoft to Outperform, Announces $600 Price Target |
| 2025-07-10 | AMD | up | +3.3% | +0.8% | — | HSBC Upgrades Advanced Micro Devices to Buy, Announces $200 Price Target |
| 2025-07-10 | ORCL | up | +2.0% | -2.1% | — | Piper Sandler Upgrades Oracle to Overweight, Raises Price Target to $270 |
| 2025-07-10 | COIN | down | +0.4% | -4.4% | — | HC Wainwright & Co. Downgrades Coinbase Global to Sell, Lowers Price Target to $300 |
| 2025-07-15 | GOOGL | up | +0.7% | -0.4% | — | Semafor: Google To Invest $25B In Data Centers Across Pennsylvania And Neighboring States  |
| 2025-07-21 | TSLA | up | +1.4% | -1.8% | no fire | Elon Musk Says Tesla's Self-Driving Tech Is About To Get Major Boost From Austin Robotaxi  |
| 2025-07-25 | TSLA | down | -1.1% | -2.4% | no fire | China Renaissance Downgrades Tesla to Hold, Announces $349 Price Target |
| 2025-07-31 | MSFT | up | +8.2% | -3.9% | — | Keybanc Upgrades Microsoft to Overweight, Announces $630 Price Target |
| 2025-08-04 | COIN | down | -1.5% | +0.4% | — | Compass Point Downgrades Coinbase Global to Sell, Lowers Price Target to $248 |
| 2025-08-05 | PLTR | up | +6.9% | +0.8% | — | Deutsche Bank Upgrades Palantir Technologies to Hold, Raises Price Target to $160 |
| 2025-08-12 | NVDA | up | +0.5% | +0.1% | — | Dell Unveils AI Platform Upgrades To Tackle Enterprise Data Complexity |
| 2025-08-13 | LITE | up | +3.0% | -2.5% | — | B of A Securities Upgrades Lumentum Holdings to Neutral, Raises Price Target to $135 |
| 2025-08-15 | CRM | up | +1.2% | +2.7% | +88% | DA Davidson Upgrades Salesforce to Neutral, Maintains Price Target to $225 |
| 2025-08-22 | NVDA | up | -1.4% | +3.1% | +59% | DeepSeek Unveils Upgrade Of Flagship AI Model With Support For Chinese Chips As Beijing Ra |
| 2025-08-26 | AMD | up | +3.2% | -1.2% | — | Truist Securities Upgrades Advanced Micro Devices to Buy, Raises Price Target to $213 |
| 2025-09-04 | AMD | down | +1.4% | -1.2% | — | Seaport Global Downgrades Advanced Micro Devices to Neutral |
| 2025-09-11 | AAPL | down | -0.0% | -1.4% | — | Phillip Securities Downgrades Apple to Reduce, Announces $200 Price Target |
| 2025-09-17 | NFLX | up | +1.7% | +0.6% | — | Loop Capital Upgrades Netflix to Buy, Raises Price Target to $1350 |
| 2025-09-19 | TSLA | up | +1.2% | +1.0% | -100% | Baird Upgrades Tesla to Outperform, Raises Price Target to $548 |
| 2025-09-24 | AMZN | up | +1.6% | -1.8% | no fire | Wells Fargo Upgrades Amazon.com to Overweight, Raises Price Target to $280 |
| 2025-09-24 | ADBE | down | +1.7% | +0.7% | — | Morgan Stanley Downgrades Adobe to Equal-Weight, Lowers Price Target to $450 |
| 2025-09-25 | INTC | up | +1.2% | +7.5% | — | Seaport Global Upgrades Intel to Neutral |
| 2025-10-03 | AAPL | down | +1.0% | -1.3% | no fire | Jefferies Downgrades Apple to Underperform, Lowers Price Target to $205.16 |
| 2025-10-03 | COIN | up | +0.3% | +1.8% | -100% | Rothschild & Co Upgrades Coinbase Global to Buy, Raises Price Target to $417 |
| 2025-10-06 | MU | up | +3.8% | -2.1% | -100% | Morgan Stanley Upgrades Micron Technology to Overweight, Raises Price Target to $220 |
| 2025-10-07 | AMD | up | +5.5% | -1.6% | — | Jefferies Upgrades Advanced Micro Devices to Buy, Raises Price Target to $300 |
| 2025-10-07 | NFLX | up | +1.2% | +1.1% | — | Seaport Global Upgrades Netflix to Buy, Announces $1385 Price Target |
| 2025-10-14 | AMD | up | +1.3% | -0.5% | — | Wolfe Research Upgrades Advanced Micro Devices to Outperform, Announces $300 Price Target |
| 2025-10-14 | MU | down | +3.0% | -0.1% | — | New Street Research Downgrades Micron Technology to Neutral |
| 2025-10-15 | NVDA | up | +2.7% | -2.7% | no fire | HSBC Upgrades NVIDIA to Buy, Raises Price Target to $320 |
| 2025-10-16 | AAPL | up | -0.4% | -0.3% | — | Can Apple Make Success Of Vision Pro Yet? Ming-Chi Kuo Calls M5 Chip The 'Most Important'  |
| 2025-10-20 | AAPL | up | +1.4% | +2.5% | +231% | Loop Capital Upgrades Apple to Buy, Raises Price Target to $315 |
| 2025-10-20 | LITE | down | +0.4% | +1.9% | — | Barclays Downgrades Lumentum Holdings to Equal-Weight, Maintains Price Target to $165 |
| 2025-10-23 | SMCI | up | -1.5% | -7.4% | — | Super Micro Computer Secures $12B In New Orders In Q2 2026, Says Design Win Upgrades Pushe |
| 2025-10-24 | COIN | up | +3.8% | +5.8% | +72% | JP Morgan Upgrades Coinbase Global to Overweight, Raises Price Target to $404 |
| 2025-10-27 | MSFT | up | +1.6% | -0.0% | no fire | Guggenheim Upgrades Microsoft to Buy, Announces $586 Price Target |
| 2025-10-30 | COIN | up | -1.5% | -4.4% | — | HC Wainwright & Co. Upgrades Coinbase Global to Buy, Raises Price Target to $425 |
| 2025-11-05 | SMCI | up | -5.1% | -6.5% | — | KGI Securities Upgrades Super Micro Computer to Outperform, Announces $60 Price Target |
| 2025-11-18 | GOOGL | up | +1.0% | -1.3% | — | Loop Capital Upgrades Alphabet to Buy, Raises Price Target to $320 |
| 2025-11-25 | COIN | down | +3.2% | -2.6% | — | Argus Research Downgrades Coinbase Global to Hold |
| 2025-12-03 | UBER | up | +2.6% | +0.9% | — | Arete Research Upgrades Uber Technologies to Buy, Raises Price Target to $125 |
| 2025-12-08 | NFLX | down | +0.4% | +3.1% | — | Rosenblatt Downgrades Netflix to Neutral, Lowers Price Target to $105 |
| 2025-12-15 | ADBE | down | +1.1% | +0.4% | — | Keybanc Downgrades Adobe to Underweight, Announces $310 Price Target |
| 2025-12-18 | MU | up | +13.8% | -3.1% | — | B of A Securities Upgrades Micron Technology to Buy, Raises Price Target to $300 |
| 2026-01-05 | INTC | up | +5.6% | -5.3% | — | Melius Research Upgrades Intel to Buy, Announces $50 Price Target |
| 2026-01-05 | NFLX | down | +0.1% | -0.6% | — | CFRA Downgrades Netflix to Hold, Announces $100 Price Target |
| 2026-01-05 | ADBE | down | +1.0% | -0.4% | — | Jefferies Downgrades Adobe to Hold, Lowers Price Target to $400 |
| 2026-01-08 | COIN | up | -0.5% | +0.4% | — | B of A Securities Upgrades Coinbase Global to Buy, Maintains Price Target to $340 |
| 2026-01-09 | ADBE | down | +0.9% | +0.6% | +61% | BMO Capital Downgrades Adobe to Market Perform, Lowers Price Target to $375 |
| 2026-01-13 | AMD | up | +3.6% | +2.7% | — | Keybanc Upgrades Advanced Micro Devices to Overweight, Announces $270 Price Target |
| 2026-01-13 | INTC | up | +4.2% | +3.1% | — | Keybanc Upgrades Intel to Overweight, Announces $60 Price Target |
| 2026-01-13 | ARM | down | +2.0% | +0.9% | — | B of A Securities Downgrades ARM Holdings to Neutral, Announces $120 Price Target |
| 2026-01-15 | AVGO | up | +2.7% | -1.7% | — | Wells Fargo Upgrades Broadcom to Overweight, Raises Price Target to $430 |
| 2026-01-16 | STX | up | +4.1% | -2.2% | no fire | Susquehanna Upgrades Seagate Technology Hldgs to Neutral, Raises Price Target to $280 |
| 2026-01-20 | INTC | up | +0.7% | +2.7% | — | HSBC Upgrades Intel to Hold, Raises Price Target to $50 |
| 2026-01-21 | ARM | up | +3.6% | +2.6% | — | Susquehanna Upgrades ARM Holdings to Positive, Maintains Price Target to $150 |
| 2026-01-26 | META | up | +1.0% | +1.1% | -100% | Rothschild & Co Upgrades Meta Platforms to Buy, Raises Price Target to $900 |
| 2026-02-04 | LITE | up | +8.7% | -1.6% | — | B. Riley Securities Upgrades Lumentum Holdings to Buy, Raises Price Target to $526 |
| 2026-02-05 | UBER | up | -0.9% | +2.7% | — | Citizens Upgrades Uber Technologies to Market Outperform, Announces $100 Price Target |
| 2026-02-09 | ORCL | up | +4.0% | +5.5% | — | DA Davidson Upgrades Oracle to Buy, Maintains Price Target to $180 |
| 2026-02-18 | PLTR | up | +2.2% | -0.4% | — | Mizuho Upgrades Palantir Technologies to Outperform, Announces $195 Price Target |
| 2026-02-24 | QCOM | up | +1.5% | +1.6% | — | Wells Fargo Upgrades Qualcomm to Equal-Weight, Raises Price Target to $150 |
| 2026-02-25 | ORCL | up | +2.1% | -0.9% | — | Oppenheimer Upgrades Oracle to Outperform, Announces $185 Price Target |
| 2026-03-06 | NFLX | up | +0.2% | -0.3% | no fire | CFRA Upgrades Netflix to Buy, Announces $115 Price Target |
| 2026-03-16 | QCOM | down | -1.0% | +1.3% | — | Seaport Global Downgrades Qualcomm to Sell, Announces $100 Price Target |
| 2026-03-16 | ADBE | down | +0.4% | -1.5% | — | Argus Research Downgrades Adobe to Hold |
| 2026-03-20 | ARM | up | +5.5% | -3.3% | no fire | HSBC Upgrades ARM Holdings to Buy, Raises Price Target to $205 |
| 2026-03-26 | ARM | up | +0.2% | -1.6% | — | Needham Upgrades ARM Holdings to Buy, Announces $200 Price Target |
| 2026-03-26 | QCOM | down | +1.2% | -1.4% | — | Bernstein Downgrades Qualcomm to Market Perform, Lowers Price Target to $140 |
| 2026-04-06 | NFLX | up | +2.3% | -2.0% | — | Goldman Sachs Upgrades Netflix to Buy, Raises Price Target to $120 |
| 2026-04-07 | ARM | down | +3.3% | -0.0% | — | Morgan Stanley Downgrades ARM Holdings to Equal-Weight, Raises Price Target to $150 |
| 2026-04-07 | ANET | up | +1.3% | +4.5% | — | Rosenblatt Upgrades Arista Networks to Buy, Raises Price Target to $180 |
| 2026-04-08 | AVGO | down | -5.3% | +0.3% | +29% | Seaport Global Downgrades Broadcom to Neutral |
| 2026-04-08 | COIN | down | -7.3% | +6.8% | — | Barclays Downgrades Coinbase Global to Underweight, Lowers Price Target to $140 |
| 2026-04-09 | ORCL | up | -0.7% | -3.1% | — | Oracle Unveils Next-Gen AI Upgrades Across FCCM, Database, And Fusion Applications To Tran |
| 2026-04-14 | TSLA | up | +1.5% | +1.8% | — | UBS Upgrades Tesla to Neutral, Maintains Price Target to $352 |
| 2026-04-15 | MSFT | up | +1.2% | +3.3% | +141% | 'OpenAI Plans New Pricing for ChatGPT Ads, Explores Other Upgrades' - The Information |
| 2026-04-22 | STX | up | +3.6% | -0.0% | — | Barclays Upgrades Seagate Technology Hldgs to Overweight, Raises Price Target to $625 |
| 2026-04-24 | AMD | up | +10.3% | +3.3% | -100% | DA Davidson Upgrades Advanced Micro Devices to Buy, Raises Price Target to $375 |
| 2026-04-27 | AMD | down | +0.4% | +3.4% | -100% | Northland Capital Markets Downgrades Advanced Micro Devices to Market Perform, Announces $ |
| 2026-04-27 | ADBE | down | +1.9% | +0.6% | — | Mizuho Downgrades Adobe to Neutral, Lowers Price Target to $270 |
| 2026-05-04 | GOOGL | down | +0.0% | +0.6% | -100% | Freedom Broker Downgrades Alphabet to Hold, Raises Price Target to $400 |
| 2026-05-06 | AMD | up | +15.3% | +2.9% | -100% | Goldman Sachs Upgrades Advanced Micro Devices to Buy, Raises Price Target to $450 |
| 2026-05-11 | TSLA | up | -1.4% | +5.4% | +242% | Elon Musk Says Tesla AI Vision Deploys Airbags 'Before Impact' To Cut Injury, Death Risk,  |
| 2026-05-19 | AAPL | up | -0.3% | +0.7% | — | Soaring Smartphone Prices Kill Upgrade Demand In China |
| 2026-05-20 | INTC | up | +4.9% | +2.4% | — | Inside The AI Chip Crunch: Intel Pressures PC Makers To Upgrade Fast |
| 2026-06-05 | TSLA | up | +0.5% | -7.0% | no fire | JP Morgan Upgrades Tesla to Neutral, Raises Price Target to $475 |
| 2026-06-11 | INTC | up | +6.1% | +3.0% | — | B of A Securities Upgrades Intel to Buy, Raises Price Target to $135 |
| 2026-06-12 | ADBE | down | +7.5% | -0.8% | -100% | Stifel Downgrades Adobe to Hold, Lowers Price Target to $200 |
| 2026-07-01 | CRM | up | +3.6% | +0.6% | — | Guggenheim Upgrades Salesforce to Buy, Announces $228 Price Target |
| 2026-07-02 | PLTR | up | +2.6% | +0.2% | — | DA Davidson Upgrades Palantir Technologies to Buy, Raises Price Target to $175 |
| 2026-07-02 | ADBE | up | +2.2% | +1.9% | — | HSBC Upgrades Adobe to Buy, Raises Price Target to $308 |
| 2026-07-07 | META | up | +1.2% | +1.3% | — | Erste Group Upgrades Meta Platforms to Buy |
| 2026-07-09 | CRM | down | +5.0% | -2.6% | — | Keybanc Downgrades Salesforce to Sector Weight |
| 2026-07-10 | STX | up | -3.2% | +5.7% | +67% | Wells Fargo Upgrades Seagate Technology Hldgs to Overweight, Raises Price Target to $1100 |
| 2026-07-14 | AAPL | down | +1.1% | -0.4% | — | Keybanc Downgrades Apple to Underweight, Announces $250 Price Target |
| 2026-07-21 | CRM | down | +3.9% | -1.8% | — | Morgan Stanley Downgrades Salesforce to Equal-Weight, Lowers Price Target to $185 |
| 2026-07-21 | ADBE | down | +5.1% | -1.9% | — | Morgan Stanley Downgrades Adobe to Underweight, Lowers Price Target to $240 |
| 2026-07-28 | AAPL | up | +0.9% | +0.0% | — | Apple Launches New Klarna-Powered Leasing Program, Giving Customers More Flexible Ways To  |
| 2026-08-04 | PLTR | up | +15.5% | +12.1% | — | Deutsche Bank Upgrades Palantir Technologies to Buy, Maintains Price Target to $200 |
| 2026-08-10 | AAPL | down | +2.0% | -0.5% | no fire | Jefferies Downgrades Apple to Underperform, Lowers Price Target to $263.66 |
| 2026-08-25 | AMD | up | +3.8% | +1.1% | — | Raymond James Upgrades Advanced Micro Devices to Strong Buy, Raises Price Target to $641 |
| 2026-08-25 | META | up | +0.9% | +1.1% | — | Meta Platforms Rolls Out New Account Security Features For WhatsApp; Upgrades Two-Step Sec |
| 2026-09-02 | AAPL | up | +0.5% | -0.6% | no fire | NIO CEO William Li Touts ‘iPhone-Like’ Firefly Strategy as EV Maker Plots New Tech Upgrade |
| 2026-09-10 | META | up | +0.0% | -1.4% | — | JP Morgan Upgrades Meta Platforms to Overweight, Raises Price Target to $820 |
| 2026-09-10 | AAPL | up | +0.4% | +3.1% | — | Apple’s Foldable iPhone Could Trigger a Massive 'Upgrade Cycle,' Says Gary Black — But Thi |
| 2026-09-14 | COIN | up | +3.2% | +5.9% | — | Compass Point Upgrades Coinbase Global to Neutral, Raises Price Target to $177 |
| 2026-09-18 | NFLX | down | +5.4% | -0.7% | no fire | Wells Fargo Downgrades Netflix to Underweight, Lowers Price Target to $57 |
| 2026-09-23 | MSFT | up | +0.6% | -0.0% | no fire | Stifel Upgrades Microsoft to Buy, Raises Price Target to $575 |
| 2026-09-29 | NFLX | up | +1.6% | -0.0% | — | Deutsche Bank Upgrades Netflix to Buy, Lowers Price Target to $95 |
