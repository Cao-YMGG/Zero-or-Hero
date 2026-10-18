# Weekly test list

The Sunday review works through this list on **real option prices** (Alpaca option bars,
zoh/realopt.py / realopt2.py helpers), costs 10% of the option price (5% as a bracket).
Lead with the last 3 months; 2026 and the full period are context. A rule that is positive
recently but negative over two years is a candidate; the reverse is a reject.
After each run, move the item to "Done" with the headline numbers, and record the result
in EVOLUTION.md.

## Open (added 2026-10-07)

1. ~~**Champion pick when several stocks gap down.**~~ DONE 2026-10-11, see below. Same rebound rule, but choose among the
   qualifying stocks by (a) list order (today's behaviour), (b) largest gap, (c) theme that
   is heating up (1-week return of its basket), (d) smallest gap. 2026-10-07: list order
   picked AMD (-94%), the largest gap was MU (1070C $0.30 -> peak $19.45).
2. **Macro-fear open, mega cap reclaims VWAP.** Days when SPY gaps down and TLT is down
   (yields up) pre-market; AAPL/AMZN/MSFT/GOOGL/META/NVDA/TSLA that dip after the open and
   then close a minute back above VWAP (or the open) before 12:00 -> buy the same-day call
   ~0.1-0.2 delta. Control: the same trigger on ordinary days. 2026-10-07: AMZN 257.5C
   $0.10 at 09:45, $2.16 at 15:10.
3. **Pre-market gap already in the price.** (2026-10-18, live so far: 3 directional calls, open->close 2 of 3 right, close->close 3 of 3; too few to judge, keep counting.) When the pre-market bias direction matches the
   gap (e.g. 2026-10-07 put on a gap down), does the 0DTE option bought after the open still
   pay? Compare open-to-close vs close-to-close direction hit rates for claude_bias.
4. **Afternoon butterflies, only on quiet afternoons.** SPY 0DTE call/put butterfly at 14:00,
   centered, $1/$2/$5 wide, held to the close (value at expiry) and sold at 15:50. Filter:
   VIX below its 20-day average, no scheduled event left after 14:00, SPY range since 12:00
   below its median. The other Claude found unfiltered 14:00 centered $5 flies about -10%
   (sold 15:50) and +1-2% (held to close). 2026-10-07: centered $1 fly 2.7x.
5. **Far, cheap directional butterflies** (cost <= 25% of the width), centered 0.3-0.6% away
   from spot in the direction of the day, at 12:00 and 14:00.
6. ~~**Analyst rule, strict headlines.**~~ PARTLY DONE (strict filter applied to the existing realopt2 rows; zoh/analyst.py itself not yet changed). Rerun zoh/analyst.py + realopt2 with only
   "<firm> Upgrades|Downgrades <stock> to <rating>" headlines (the loose regex let 5 false
   events in, including TSLA 2026-05-11 +415%), plus a price-target-raise >= 20% bucket.
9. **Delta floor for expensive underlyings.** With a small budget, rebound_scanner on MU
   (~$1,000) could only afford a 3.3%-OTM same-day call (Alpaca delta 0.00, target 0.08);
   it expired worthless. Test skipping (or switching to the cheapest affordable strike with
   delta >= half the target) when the best affordable delta is below 0.03.
10. **Rotation laggard, no news.** Mega-cap platform in a heating theme, down >= 5% from its
   20-day high, gapping +1% to +2.5% pre-market on a day the AI-hardware basket is red
   pre-market: buy at the open or after a +1% confirmation. One example so far
   (META 2026-10-12); count how often it happens and what the option made.
11. **Hot theme into its industry event.** Optical (LITE/CIEN), the hottest theme for a
   month (+18-34% 1m), fell ~10% on the first day of the OCP summit with no news
   (sell the news). Check past event days (OCP, Computex, GTC, Hot Chips) for the hottest
   basket's open-to-close and the 0DTE put.

14. **Pre-earnings drift with 2-4 week calls (compounder phase).** Buy ~0.3-delta calls
   expiring after the report, 10 trading days before it, sell the day before the report.
   RUNUP.md (stock only): +1.6% median excess, 60% up; +11.4% for names already running >5%.
   Real option prices, last 3 months first, with and without the best trade. Also test the
   0DTE version: the sniper's open buy on names 5-10 days before their report vs other days.

16. **Bearish macro days: SPY puts and put snipers.** (Partly answered by MACRO_SURPRISE.md: with 2019-12+ data a hot print does not make the afternoon follow through on SPY/QQQ; the put-sniper half is still open.) Days with a hot CPI/PPI/jobs print (or
   yields up >= 5bp and futures red by 09:00): buy a 0DTE SPY put at 09:35 and, separately, a
   ~0.1-delta put on the weakest mega cap in a cooling theme. Real option prices, last 3
   months first, with and without the best one/two trades, against all other days. Live so
   far: 10-07 put day -97% (afternoon auction reversal), 10-14 SPY put +52% at 10:01.

17. **Vertical spreads vs single legs (prep for the compounder phase at $2,000).** Same
   sniper days and the 0DTE SPY bias days: buy ~0.3 delta / sell ~0.1 delta vs the single
   ~0.1-0.3 delta leg, real option prices, last 3 months first, with and without the best
   trade. Then the 2-4 week version around hyperscaler capex and pre-earnings windows
   (AVGO/NVDA/AMD/MU into GOOGL/MSFT/META/AMZN reports). The account has options level 3
   (diagnostics 2026-10-13), so spreads are allowed. Expectation: spreads cut the fat tails
   this phase lives on, so they belong to `compounder`, not `zero-or-hero`.

20. **Follow-the-open with split exits (owner approved 2026-10-16).** (2026-10-18: added as spy_open_drive and stock_open_drive with half at 3x and the rest held to 15:45; each has its own ledger. Open until they have live trades.) zoh/research/opendrive.py now
   compares take3 / hold / trail / half3_hold / half3_trail on the same entries (the 3x cap cut
   the tails: 2026-10-16 SPY 766P $0.18 -> $3.56). If a split exit is positive over the last 3
   months without the best two trades, add a shadow "SPY 10:00 follow-the-open" variant.
   Result (EVOLUTION 10-16 evening, REGIME.md): only calls hold up. Use move size as the gate,
   not trend or VIX (no label known in advance picked the good periods; uptrend + calm calls
   were among the worst). Candidates: SPY calls >= 0.5% above the open at 10:00, half at 3x,
   rest to 15:30 (n=17, +30% / +4% / -19%); TSLA/NVDA calls >= 0.8% (+21% / +10% / +2% all,
   +57-65% in 2026). Never puts. Each gets its own $500 ledger under item 19.
   Gates from REGIME.md section 5: skip macro release days, monthly options-expiry week and
   Fridays; each ledger goes shadow-only after 5 straight losses, live again after a shadow win.

## Done

- **Items 12 and 15 (2026-10-18, journal/research/SCANNERS.md + scanners.json, real option prices, 10% costs).**
  - Leader follow (biggest move beyond SPY, ~0.2 delta call, trail2x), last 3 months / all: 5 min >= 1.0%: -21% / -20% (51 / 413); 10 min >= 1.5%: -7% / -11%; **15 min >= 1.5% (live rule): +15% / -14% / -21%** (43), all -10% (363); 30 min >= 2.0%: -6% / -18%. The live entry time is the best one, but it is positive only because of one trade: leader_follow stays shadow, no ledger. 0.30 delta at 15 minutes: +13% / -6% / -12%.
  - Gap-up fade (gap >= 2%, >= 0.2% below the open at 09:45, ~0.15 delta put): last 3 months -5% / -14% / -21% (32), all -14% (381); without the confirmation -39% (94) / -18% (803). Negative on every strike and exit, never fired live: gapup_fade retired. Gap-size buckets in SCANNERS.md.

- **Items 7, 8, 13, 18 (2026-10-18, journal/research/EXITS.md + exits.json, real option prices 2024-02 to 2026-10-16, 10% costs; avg / without best / without best two).**
  - Rebound (champion rule, Mon/Wed/Fri same day, 37 trades in the last 3 months): live 0.08 delta + trail2x **+46% / +34% / +20%**; all 171 trades -33%. Positive recently, negative over 2.7 years: a candidate, and it now trades its own ledger. 0.30 delta + half at 3x: +38% / +25% / +18% (all -10%), the least bad overall.
  - Item 13, Tue/Thu with the next day's expiry (29 trades, last 3 months): negative on every strike and exit (0.08 trail2x -13% / -22% / -29%). rebound_scanner_any retired.
  - Item 7, carry vs 15:45: carried Tue/Thu rebounds -42% vs -13% sold at 15:45 (0.08 delta, last 3 months); strict-upgrade picks carried +12% / -4% / -16% vs -13% / -19% / -23% sold (all 66). Only catalyst variants carry now.
  - Item 8, exits: arming the trail at 1.5x or 1.6x is no better than 2x (rebound +44% vs +46%; META much worse, -7% vs +94%). Tighter trail above 5x helps rebound ex-best but hurts META: unchanged. Half at 3x + trail on strict upgrades: -12% / -40% vs single trail -21% / -57% (last 3 months, 11 trades), also better over all 90: adopted for catalyst_open / catalyst_intraday (half_at 3).
  - Item 18, strike distance on strict upgrades (11 last 3 months / 90 all): 0.10 delta -21% / -16%, 0.20 -29% / -19%, 0.30 -31% / -17%, half / one daily swing out -37% / -31%. No strike makes the mechanical upgrade rule positive; nearer is not better. catalyst_open_near retired. On rebound the near strikes lose less overall but the 0.08 lottery is best recently.
  - meta_follow2 (21 trades last 3 months): 0.20 trail2x +59% / -18% / -29%: positive only because of one trade. Shadow only.
- **Item 19, multi-ledger (2026-10-18, built: zoh/ledgers.py, tests/test_ledgers.py).** A variant listed in config `ledgers` trades real paper orders from its own $500 ledger (20% a trade, one contract up to 30%), own generations below $50, real orders pause after 5 losses in a row and resume after a win; its P&L is kept out of the main ledger by moving the main anchor. Bar for a ledger: positive on real prices over the last 3 months without the best trade. Four pass: rebound_scanner, nvda_gapdown_put, spy_open_drive, stock_open_drive. meta_follow2 (one-trade result) and claude_bias (no real-price history) stay shadow. Ledgers are independent of each other's themes. Review shows a ledger table; journal/ledger_equity.csv gets a row per ledger each day.
- **Item 21 (2026-10-18, COOLCPI.md, FEEDS.md).** Cool CPI call at the close, sold 2 days later, real prices: SPY ATM +4% / -3% / -9% (16), QQQ +0% / -11% / -21%: the 74% underlying edge does not survive option prices. Rejected. IEX vs SIP vs OpenD (315 symbol-days): median difference 4 bp; the 10:00 direction flips on 7 of 315, all with moves under 0.3%, none at >= 0.5% (IEX is ~3% of the volume). The 0.5% / 0.8% gates are safe on IEX.

- **Item 1, champion pick (2026-10-11, journal/research/realopt.json, 211 trades / 72 days, data to 2026-09-14).**
  Choosing one stock per day, at 10% costs:
  | pick | last 3 months (12 days) | since 2026-01-26 (27 days) | all (72 days) |
  |---|---|---|---|
  | list order (today) | -36%/trade | -45% | -65% |
  | largest gap | -67% | -56% | -72% |
  | smallest gap | -36% | -55% | -65% |
  | buy every qualifier, equal split (per day) | -39%/day | -48% | -64% |
  The +49%/trade "all qualifiers" figure for the last 3 months comes from one day (2026-07-17, 13 stocks gapped down and nearly all rebounded 2-6x); without it the basket is -61%/day. Verdict: no pick rule fixes the rule; largest gap is the worst. Keep list order. The MU (10-07) and AAPL (10-09) wins were one-day luck.
  Theme-heating filter not run (needs point-in-time basket returns; carried to next week).
- **Item 6 (partial), sniper entry, open vs +1% confirmation, strict upgrade headlines only:** open buy -3%/trade since 2026-01-26 (18), +33% last 3 months (6); confirm buy -12% (17), +24% (5). Without the single best trade every window is negative (-23% to -63%). Live: catalyst_sniper 0 of 3, catalyst_open 1 of 2 (LITE +113% real). Opening buy is less bad than waiting for +1%.
