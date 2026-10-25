# Week 43 tests: open-drive exits and buckets, weekdays (Sunday tests 22b, 22c, 23)

Data: journal/research/opendrive.json (real 1-minute 0DTE option prices, strike ~0.7% OTM, 10% costs each way, 2024-02-06 to 2026-10-15) and scanners.json / exits.json (0.20-delta leader calls, rebound calls). Cells: avg / without the best / without the best two (n, win%). Periods: 3m = since 2026-07-16, 1y = since 2025-10-16. Scripts: the snippets in this file's commit (od.py, wd.py) re-read those json files.

```
## spy_open_drive (SPY>=0.5%, Mon-Thu, no release/opex)
  3m take3 +230% / +nan% / +nan% (n=1, win 100%) | hold +680% / +nan% / +nan% (n=1, win 100%) | trail +0% / +nan% / +nan% (n=1, win 0%) | half3_hold +455% / +nan% / +nan% (n=1, win 100%) | half3_trail +470% / +nan% / +nan% (n=1, win 100%)
  1y take3 +314% / +279% / +226% (n=4, win 100%) | hold +227% / +76% / -40% (n=4, win 75%) | trail +104% / +54% / +15% (n=4, win 75%) | half3_hold +270% / +209% / +141% (n=4, win 100%) | half3_trail +313% / +260% / +222% (n=4, win 100%)
  all take3 +101% / +78% / +54% (n=15, win 67%) | hold +53% / +8% / -23% (n=15, win 47%) | trail +44% / +18% / -0% (n=15, win 60%) | half3_hold +77% / +50% / +27% (n=15, win 67%) | half3_trail +97% / +71% / +50% (n=15, win 67%)
## spy_open_drive_wide (SPY>=0.3%)
  3m take3 +78% / +27% / -59% (n=4, win 50%) | hold +690% / +187% / -59% (n=4, win 50%) | trail -24% / -39% / -59% (n=4, win 25%) | half3_hold +384% / +112% / -59% (n=4, win 50%) | half3_trail +388% / +117% / -59% (n=4, win 50%)
  1y take3 +38% / +18% / -2% (n=20, win 40%) | hold +95% / -16% / -55% (n=20, win 25%) | trail -21% / -35% / -44% (n=20, win 40%) | half3_hold +67% / +7% / -18% (n=20, win 40%) | half3_trail +81% / +22% / -3% (n=20, win 40%)
  all take3 +19% / +9% / -2% (n=38, win 42%) | hold +32% / -26% / -46% (n=38, win 26%) | trail -10% / -22% / -29% (n=38, win 45%) | half3_hold +26% / -6% / -19% (n=38, win 42%) | half3_trail +39% / +8% / -5% (n=38, win 42%)
## SPY 0.3-0.5% only
  3m take3 +27% / -59% / -100% (n=3, win 33%) | hold +693% / -59% / -100% (n=3, win 33%) | trail -32% / -59% / -100% (n=3, win 33%) | half3_hold +360% / -59% / -100% (n=3, win 33%) | half3_trail +360% / -59% / -100% (n=3, win 33%)
  1y take3 -31% / -47% / -64% (n=16, win 25%) | hold +62% / -81% / -87% (n=16, win 12%) | trail -52% / -59% / -67% (n=16, win 31%) | half3_hold +16% / -63% / -75% (n=16, win 25%) | half3_trail +23% / -55% / -70% (n=16, win 25%)
  all take3 -33% / -45% / -56% (n=23, win 26%) | hold +19% / -80% / -84% (n=23, win 13%) | trail -46% / -52% / -57% (n=23, win 35%) | half3_hold -7% / -62% / -69% (n=23, win 26%) | half3_trail +1% / -53% / -63% (n=23, win 26%)
## stock_open_drive (NVDA/TSLA>=0.8%, Mon/Wed)
  3m take3 +6% / -13% / -36% (n=13, win 38%) | hold +31% / -24% / -46% (n=13, win 38%) | trail +36% / -18% / -40% (n=13, win 38%) | half3_hold +18% / -18% / -39% (n=13, win 38%) | half3_trail +24% / -13% / -35% (n=13, win 38%)
  1y take3 +31% / +24% / +16% (n=29, win 48%) | hold +85% / +56% / +29% (n=29, win 48%) | trail +48% / +25% / +13% (n=29, win 52%) | half3_hold +58% / +41% / +23% (n=29, win 48%) | half3_trail +54% / +36% / +21% (n=29, win 48%)
  all take3 +31% / +24% / +16% (n=29, win 48%) | hold +85% / +56% / +29% (n=29, win 48%) | trail +48% / +25% / +13% (n=29, win 52%) | half3_hold +58% / +41% / +23% (n=29, win 48%) | half3_trail +54% / +36% / +21% (n=29, win 48%)
## NVDA/TSLA>=0.8% any weekday, filters
  3m take3 -2% / -20% / -41% (n=14, win 36%) | hold +22% / -30% / -50% (n=14, win 36%) | trail +27% / -24% / -45% (n=14, win 36%) | half3_hold +10% / -25% / -44% (n=14, win 36%) | half3_trail +15% / -19% / -40% (n=14, win 36%)
  1y take3 +36% / +31% / +26% (n=40, win 50%) | hold +71% / +50% / +31% (n=40, win 48%) | trail +46% / +29% / +18% (n=40, win 55%) | half3_hold +54% / +41% / +29% (n=40, win 50%) | half3_trail +53% / +40% / +29% (n=40, win 50%)
  all take3 +14% / +11% / +8% (n=71, win 39%) | hold +30% / +18% / +7% (n=71, win 37%) | trail +20% / +10% / +4% (n=71, win 46%) | half3_hold +22% / +15% / +7% (n=71, win 39%) | half3_trail +23% / +15% / +9% (n=71, win 39%)
## SPY+NVDA+TSLA calls >=0.5% no filters
  3m take3 +1% / -8% / -18% (n=27, win 33%) | hold +23% / -2% / -29% (n=27, win 30%) | trail -4% / -31% / -44% (n=27, win 30%) | half3_hold +12% / -5% / -24% (n=27, win 33%) | half3_trail +16% / -1% / -20% (n=27, win 33%)
  1y take3 +8% / +3% / -1% (n=88, win 36%) | hold +25% / +12% / +2% (n=88, win 32%) | trail +15% / +2% / -6% (n=88, win 43%) | half3_hold +17% / +9% / +3% (n=88, win 36%) | half3_trail +20% / +13% / +6% (n=88, win 36%)
  all take3 -10% / -12% / -15% (n=163, win 31%) | hold -4% / -12% / -17% (n=163, win 26%) | trail -5% / -12% / -17% (n=163, win 37%) | half3_hold -7% / -11% / -15% (n=163, win 31%) | half3_trail -4% / -8% / -12% (n=163, win 31%)
## weekday, SPY calls >=0.3%, no release/opex, take3 and half3_trail
  M take3 +15% / -2% / -21% (n=14, win 36%) | half3_trail +16% / -19% / -36% (n=14, win 36%)
  T take3 +43% / +5% / -20% (n=10, win 60%) | half3_trail +124% / +5% / -27% (n=10, win 60%)
  W take3 -6% / -39% / -81% (n=8, win 38%) | half3_trail -6% / -52% / -81% (n=8, win 38%)
  T take3 +25% / -54% / -80% (n=6, win 33%) | half3_trail +11% / -54% / -80% (n=6, win 33%)
  F take3 -24% / -56% / -67% (n=8, win 38%) | half3_trail -29% / -56% / -67% (n=8, win 38%)

## leader_follow 15min 1.5% d0.20 trail2x
  3m M +122%/-17%/-31% n=9 | T +31%/-11%/-39% n=7 | W -36%/-58%/-72% n=8 | T -11%/-22%/-32% n=10 | F -29%/-43%/-54% n=9 || same-day expiry +38%/-37%/-45% n=17 | later expiry +1%/-11%/-17% n=26
  all M +12%/-2%/-16% n=90 | T -5%/-14%/-18% n=73 | W -17%/-25%/-28% n=55 | T -18%/-24%/-28% n=77 | F -27%/-30%/-33% n=68 || same-day expiry +0%/-15%/-31% n=81 | later expiry -12%/-15%/-16% n=282
2024-07-12 ['d0.05', 'd0.08', 'd0.15', 'd0.30', 'swing0.5', 'swing1.0']
## rebound (exits.json) d0.05 trail2x
  3m M -59%/-79%/-99% n=9 | T - | W -16%/-98%/-99% n=6 | T - | F +97%/+77%/+55% n=22 || same-day expiry +41%/+27%/+14% n=37 | later expiry -
  all M -63%/-73%/-81% n=18 | T - | W -16%/-98%/-99% n=6 | T - | F -35%/-39%/-43% n=147 || same-day expiry -37%/-41%/-44% n=171 | later expiry -
## rebound (exits.json) d0.08 trail2x
  3m M -33%/-70%/-98% n=9 | T - | W -13%/-99%/-100% n=6 | T - | F +95%/+75%/+54% n=22 || same-day expiry +46%/+34%/+20% n=37 | later expiry -
  all M -48%/-66%/-78% n=18 | T - | W -13%/-99%/-100% n=6 | T - | F -32%/-36%/-39% n=147 || same-day expiry -33%/-36%/-39% n=171 | later expiry -
## rebound (exits.json) d0.15 trail2x
  3m M -26%/-61%/-97% n=9 | T - | W +254%/-96%/-98% n=6 | T - | F +63%/+49%/+35% n=22 || same-day expiry +72%/+19%/+9% n=37 | later expiry -
  all M -38%/-55%/-70% n=18 | T - | W +254%/-96%/-98% n=6 | T - | F -24%/-27%/-29% n=147 || same-day expiry -16%/-28%/-30% n=171 | later expiry -
## rebound (exits.json) d0.30 trail2x
  3m M -18%/-42%/-67% n=9 | T - | W +66%/-80%/-92% n=6 | T - | F +56%/+41%/+29% n=22 || same-day expiry +39%/+18%/+8% n=37 | later expiry -
  all M -23%/-34%/-45% n=18 | T - | W +66%/-80%/-92% n=6 | T - | F -16%/-21%/-23% n=147 || same-day expiry -14%/-19%/-23% n=171 | later expiry -
## rebound (exits.json) swing0.5 trail2x
  3m M -18%/-43%/-68% n=9 | T - | W +120%/-87%/-94% n=6 | T - | F +54%/+39%/+27% n=22 || same-day expiry +47%/+16%/+7% n=37 | later expiry -
  all M -24%/-36%/-47% n=18 | T - | W +120%/-87%/-94% n=6 | T - | F -17%/-20%/-23% n=147 || same-day expiry -13%/-20%/-22% n=171 | later expiry -
## rebound (exits.json) swing1.0 trail2x
  3m M -30%/-66%/-96% n=9 | T - | W +252%/-98%/-100% n=6 | T - | F +72%/+58%/+44% n=22 || same-day expiry +76%/+23%/+13% n=37 | later expiry -
  all M -41%/-58%/-71% n=18 | T - | W +252%/-98%/-100% n=6 | T - | F -18%/-22%/-25% n=147 || same-day expiry -11%/-23%/-26% n=171 | later expiry -
```
