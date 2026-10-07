# Weekly test list

The Sunday review works through this list on **real option prices** (Alpaca option bars,
zoh/realopt.py / realopt2.py helpers), costs 10% of the option price (5% as a bracket).
Lead with the last 3 months; 2026 and the full period are context. A rule that is positive
recently but negative over two years is a candidate; the reverse is a reject.
After each run, move the item to "Done" with the headline numbers, and record the result
in EVOLUTION.md.

## Open (added 2026-10-07)

1. **Champion pick when several stocks gap down.** Same rebound rule, but choose among the
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
6. **Analyst rule, strict headlines.** Rerun zoh/analyst.py + realopt2 with only
   "<firm> Upgrades|Downgrades <stock> to <rating>" headlines (the loose regex let 5 false
   events in, including TSLA 2026-05-11 +415%), plus a price-target-raise >= 20% bucket.
7. **Hold vs same-day exit for non-same-day options.** Compare carried positions (new rule
   since 2026-10-07) with what a 15:45 exit would have given.

## Done
