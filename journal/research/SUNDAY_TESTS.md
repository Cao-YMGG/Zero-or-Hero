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
3. **Pre-market gap already in the price.** When the pre-market bias direction matches the
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
7. **Hold vs same-day exit for non-same-day options.** Compare carried positions (new rule
   since 2026-10-07) with what a 15:45 exit would have given.

8. **Earlier trail start.** On real prices, compare `trail_after` 1.0 (today) with 0.5 and
   0.6 (giveback 0.4) for rebound_scanner, catalyst_open and meta_follow2. 2026-10-12:
   CRM 252.5C peaked +66% and never armed the trail (now -70%); META 755C armed it and kept
   +73%. Report with and without the best trade.
   Also test a tighter trail on big runners: 2026-10-13 META 775C $0.93 -> peak $7.39 ->
   trail exit $4.15 (floor was $4.43 = 60% of peak; a 30-second poll in a fast drop filled
   below it). Compare giveback 0.4 flat vs 0.25 once the option is >= 5x, and a floor at
   peak minus a fixed share of the gain.
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

12. **Leader follow on real prices.** Each day, the large cap with the biggest move from the
   open beyond SPY's (>= +2% after 30 minutes, any weekday, nearest expiry) -> ~0.2-delta
   call, trail from +100%. Universe as in the `leader_follow` variant. Compare with
   meta_follow2 (META only, Mon/Wed/Fri) and with the same rule without the SPY adjustment.
   Entry time matters most: on 2026-10-13 META ran 735.8 -> 769 between 09:35 and 10:00 and
   pulled back to 761 by 10:10, so a 10:00 entry bought the top. Compare entries at 5, 10, 15
   and 30 minutes (thresholds 1.0 / 1.5 / 2.0% beyond SPY): earlier catches more of the run
   but more false starts reverse (DOSSIER_AMD: small early moves reversed 70% of the time).
   Report the last 3 months first, with and without the best trade.

13. **Tue/Thu with the next expiry.** Single-stock scanners only bought same-day options, so
   they sat out every Tuesday and Thursday (2026-10-13: MU -4.9% and AMD -2.2% gaps skipped;
   AAPL dipped -1% after the open and reclaimed to a new high). On real prices, compare the
   rebound rule and the reclaim rule on Tue/Thu using the next day's expiry against their
   Mon/Wed/Fri same-day results. Live twins since 10-14: rebound_scanner_any (shadow) and
   megacap_reclaim with any_expiry.

## Done

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
