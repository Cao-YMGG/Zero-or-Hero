# Strangle vs direction on big-move days — 25 large caps, last 2 years

Same-day expiry days only. Entry 09:45, ~0.3 delta per leg, 3% slippage. A strangle is a call and a put for equal dollars; its return is the average of the two legs. "trail": each leg trails after doubling; "2x": each leg sells at +100%. Odds = bootstrap P($500 → $2,000) staking 50% per trade.

## How far the stock moves after 09:45 (median |09:45 → close|)

| day type | days | median move | > 2% | > 3% |
|---|---|---|---|---|
| gap | 867 | 1.55% | 38% | 22% |
| rating | 54 | 1.18% | 35% | 20% |
| after_big | 219 | 1.71% | 46% | 23% |
| control | 246 | 0.94% | 18% | 7% |

## Options priced at 1.15x trailing intraday vol

| day type | strategy | trades | win% | avg / trade | median | best | odds $2k |
|---|---|---|---|---|---|---|---|
| gap | strangle trail | 867 | 22% | -29% | -36% | +521% | 1% |
| gap | strangle 2x | 867 | 63% | -26% | +1% | +248% | 0% |
| gap | with gap trail | 867 | 30% | -38% | -100% | +955% | 2% |
| gap | fade gap trail | 867 | 38% | -19% | -99% | +1141% | 7% |
| gap | call only trail | 867 | 34% | -24% | -100% | +1141% | 6% |
| gap | put only trail | 867 | 33% | -33% | -100% | +1077% | 3% |
| rating | strangle trail | 54 | 26% | -14% | -33% | +304% | 5% |
| rating | strangle 2x | 54 | 67% | -25% | +3% | +121% | 0% |
| rating | with rating trail | 54 | 35% | -11% | -100% | +708% | 10% |
| rating | with rating 2x | 54 | 35% | -24% | -100% | +127% | 4% |
| rating | call only trail | 54 | 37% | -9% | -100% | +708% | 11% |
| rating | put only trail | 54 | 33% | -20% | -100% | +707% | 8% |
| after_big | strangle trail | 219 | 24% | -21% | -31% | +521% | 3% |
| after_big | strangle 2x | 219 | 68% | -20% | +2% | +248% | 0% |
| after_big | call only trail | 219 | 30% | -22% | -100% | +1141% | 8% |
| after_big | put only trail | 219 | 43% | -20% | -90% | +362% | 5% |
| control | strangle trail | 245 | 17% | -39% | -40% | +897% | 1% |
| control | strangle 2x | 245 | 55% | -38% | +1% | +138% | 0% |
| control | call only trail | 245 | 29% | -39% | -100% | +1895% | 3% |
| control | put only trail | 245 | 29% | -39% | -100% | +504% | 2% |

## Options priced at 1.5x trailing intraday vol

| day type | strategy | trades | win% | avg / trade | median | best | odds $2k |
|---|---|---|---|---|---|---|---|
| gap | strangle trail | 867 | 13% | -53% | -79% | +530% | 0% |
| gap | strangle 2x | 867 | 42% | -50% | -79% | +179% | 0% |
| gap | with gap trail | 867 | 21% | -57% | -100% | +1160% | 1% |
| gap | fade gap trail | 867 | 24% | -48% | -100% | +834% | 2% |
| gap | call only trail | 867 | 23% | -47% | -100% | +1160% | 2% |
| gap | put only trail | 867 | 21% | -58% | -100% | +795% | 0% |
| rating | strangle trail | 54 | 20% | -48% | -93% | +176% | 0% |
| rating | strangle 2x | 54 | 41% | -55% | -93% | +20% | 0% |
| rating | with rating trail | 54 | 20% | -47% | -100% | +452% | 2% |
| rating | with rating 2x | 54 | 20% | -55% | -100% | +141% | 0% |
| rating | call only trail | 54 | 19% | -46% | -100% | +452% | 2% |
| rating | put only trail | 54 | 22% | -51% | -100% | +437% | 1% |
| after_big | strangle trail | 219 | 12% | -50% | -78% | +367% | 0% |
| after_big | strangle 2x | 219 | 45% | -48% | -78% | +179% | 0% |
| after_big | call only trail | 219 | 21% | -45% | -100% | +834% | 4% |
| after_big | put only trail | 219 | 25% | -55% | -100% | +205% | 0% |
| control | strangle trail | 246 | 9% | -66% | -94% | +638% | 1% |
| control | strangle 2x | 246 | 30% | -64% | -94% | +103% | 0% |
| control | call only trail | 246 | 16% | -65% | -100% | +1376% | 1% |
| control | put only trail | 246 | 15% | -66% | -100% | +240% | 0% |
