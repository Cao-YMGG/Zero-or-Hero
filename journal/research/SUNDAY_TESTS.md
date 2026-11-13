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

24. **Dip-buy with 30-60 day calls, live shadow log (owner idea 2026-10-21).** DIPS.md: positive
   in the last 3 months only (call, +50%/-50% exit: +22% / +18% / +14%, n=26, 3% costs), negative
   over the last year (-8%, n=117), and random entries did as well over 2.7 years. Debit spreads
   were worse than single calls; at 10% costs everything loses. Track the daily signals and their
   real option outcomes for a month before building a bot variant (needs multi-day holding and
   $500-2,500 a contract, more than the main ledger).
   Started 2026-10-26: zoh/research/dipwatch.py runs after each Trade afternoon job and writes
   journal/dipwatch.csv (signal, contract, close; outcomes filled 20 sessions later). Review the
   rows on 2026-11-29.

26. **Open-to-10:00 move under 0.1% vs Fridays (the other Claude's question, 2026-10-23).** Split
   leader_follow, megacap_reclaim and the catalyst picks by the SPY open-to-10:00 bucket and by
   weekday on real option prices.
30. **Sell the news by theme state (2026-10-29, OPPORTUNITY_TESTS.md).** Gap-ups >= 2% in a cooling
    sector: last 3 months 113 events, -0.72% open to close, 37% up (heating +0.62%, 54%). Price it with
    0.2-delta puts on real option bars: does -0.7% pay the spread and theta? Split earnings vs
    non-earnings gaps (the daily test mixes them).
31. **Rotation laggard and financing fade (owner, 2026-10-29).** Laggard after a group shock: 32
    events +0.40% (no edge without the best trade); chip-selloff days -> internet laggard: 3 months
    8 events +1.29%, 75% up. Better laggard choice (exclude names that reported in the last 5 days;
    10-29 would have picked NFLX, not META). Financing fade: list mega-cap debt/equity raise dates
    from the Alpaca news feed (2 years), open->close and +5 days vs SPY, split "with a FCF plan"
    (ORCL 10-28 +10%) vs without (MSFT 10-29 -1.9% open to close, META offering week -12%).
32. **Buy the expectation (owner, 2026-10-29).** RUNUP.md: +1.6% vs SPY in the 10 days before a
    report, reaction day -1.6%. Options version: buy a ~0.3-delta call expiring after the report 8-10
    trading days before, sell the day before; real option prices for the 201 reports (IV ramps into
    the print). If positive over the last 3 months and without the best two, it replaces a weak
    variant (population is at 12).
33. **Post-earnings filter for rebound_scanner / megacap_reclaim (other Claude, 2026-10-28/29).**
    Their 1,986 reports: no bounce edge after a move beyond the implied one. Our 5 live rebound
    shadows were not earnings gaps. Test the AMZN 10-30 case and the 2-year scanner backtest with and
    without skip_after_report_days 3 before changing the champion.
36. **Go with the day's driver, generalized (2026-11-01).** DONE 11-08 (GAPDOWN.md, zoh/research/gapdown.py): the
    nvda_gapdown_put rule (gap down, still 0.1% under the open at 10:00, the put the $500 ledger can buy nearest 0.40
    delta, take3) on ten mega caps since 2024-02, same-day-expiry days, costs 10% each way, last 3 months / last year /
    since 2024-02 (n, avg / without the best / without the best two): NVDA 9 +112% / +91% / +73%, 26 +22% / +12% / +3%,
    43 +28% / +22% / +16% -- the only name positive at every horizon. AVGO 11 +54% / +36% / +16%, 30 +17% / +10% / +2%,
    49 -7% / -12% / -17% (candidate at most: positive recently, negative over two years). AMD 10 +34% / +10% / -20%,
    then -8% over two years; MU -34% / -1% / +1%; TSLA -57% / -25% / -18%; META +3% / -14% / -15%; AMZN +9% / -17% /
    +1%; GOOGL +24% / -21% / -3%; MSFT -25% / -18% / -21%; AAPL +20% / -35% / -31%. Pooled 412 same-day trades: -7% over
    two years, +19% / +15% / +12% in the last 3 months (77). "The biggest gap-down of the group" (one a day, 141 same-day
    trades): -19% / -21% / -23% over two years, -17% in the last 3 months -- rejected; picking the biggest gap picks MU,
    TSLA and AMD, the names where the rule loses. Without a budget (0.40 delta regardless of price) the picture is the
    same. So the edge is NVDA's, not the rule's; no second gap-down ledger, AVGO goes on the watch list for a re-run
    in a month.
33b. **Post-earnings day one (2026-11-01, partial).** Live: megacap_reclaim bought AMZN 245C on 10-30
    (day one after its report, -$56) and the intraday AMZN put lost -$198 the same day; rebound_scanner
    picked NVDA, not the post-report gaps. A report calendar for 2 years is still missing, so the
    scanner backtest with/without skip_after_report_days is not done. The owner was asked (10-30/31)
    whether to keep day-one names out of the sniper and intraday picks; no answer yet.

37. **Intraday picks far from the open, and a stop on same-day picks (2026-11-02).** AMZN 11-02
    was picked at +4.0% from its open on a pre-market upgrade and went 0.43 -> 0.61 -> 0.01 while the
    stock gave back 2.5%; leader_follow (buy the strongest after +1.5%) is -16% over 3 months without
    its best trade. On minute bars for every pick and opportunity since 10-01, and the scanner
    universe for 3 months: entry->close by distance from the open at entry (< 1%, 1-3%, >= 3%) and by
    catalyst timing (in session vs pre-market); then on real option prices, the live exit vs a -50%
    stop vs "sell if the stock loses half its move since the pick". Last 3 months first, without the
    best one and two.
38. **Put sniper on a "none" day for a fresh negative of the stock's own (2026-11-02).** Tested the
    same night on real option prices (journal/research/FADES.md, zoh/research/fades.py; 100 events in
    two years over 61 large caps: 44 equity offerings, 46 debt offerings, 10 acquirers). Equity
    offerings gap down (11 of the last 12, -2% average) and the day from 10:00 is a coin flip: last 3
    months 12 events, the stock fell after 10:00 in 4, the 0.25-delta put with the live exit rule
    -39% (-45% without the best); entered at the 09:31 close with the below-open gate, 6 events,
    -21% / -37% / -51%; two years 14 gated events +2% / -16% / -25%. Offerings >= $5B (ORCL 02-04,
    INTC 08-10/11, META 10-26/27, NBIS, MSTR): 7 events, put -34%, 1 win. Debt offerings: puts -30%
    to -36% in every period. Stock-financed acquirers: the classifier found 2 (AMD/World Labs 09-29
    +58%, RKLB/Iridium 0%); cash acquirers 8, mixed (NFLX/WBD +173%, GOOGL/Wiz -60%). Verdict:
    rejected as a real-money rule; today's ORCL (+3.0% after 10:00) and MRVL (+7.0%) are the tail,
    the median offering day drifts about 1% after the open. Stays an opportunity type. Open: the
    acquirer sample (needs headlines that carry size and stock component; score them live), and a
    size x theme filter (mega-cap AI capex raises in a cooling theme) once there are 20 of them.

39. **Day-two cross-sectional reversal (other Claude's question, 2026-11-03).** They measured a -0.60
    rank correlation between 11-02 and 11-03 returns across 100 stocks (below the 1st percentile since
    2010; long-run mean -0.01, and the day after a high-dispersion day reverses only 51% of the time).
    Today fit it: ORCL -8.9% then +5.8%, WDC/STX/SNDK sold hardest then +3-5% at the open, XLP/WMT/COST
    gave back the week's rotation; MRVL (own fresh negative) was the exception. Not measured here. Test
    on our 61-name daily file: rank correlation day t vs t+1 by month, conditional on dispersion deciles
    and on the theme state (cooling vs heating), last 3 months first, then 2 years; what matters for us
    is whether 'yesterday's worst mega cap in a cooling theme' has an open-to-close edge on day two
    (the 11-03 ORCL/memory bounce) and whether that beats the gap-up fade of item 30. Prior: no.

40. **Failed bounce in a cooling theme, the put mirror (2026-11-03, BOUNCE.md, zoh/research/bounce.py).**
    Two years of real option prices: 14 days where SMH was down >= 10% over the prior month and gapped up
    >= 1%; 6 of them (43%) were back below the open at 11:00 and had a chip below its own open outside a
    report window. The 11:03 0.20-delta put on that weakest chip: live exit +28% per $1 (33% win), -7%
    without the best, -53% without the best two; half at 3x then hold +43% / +11% / -31%; pure hold +11%
    / -27% / -72%; a stock stop (sell when the stock reclaims its open) adds nothing. The SMH put is
    similar (+45% / -1% / -35% live). Two trades carry it (AVGO 2025-04-08 +205%, MRVL 2026-11-02 +178%),
    one is a disaster (MU 2025-04-09, the tariff-pause day, -93%), three small losers. Held bounces
    (above the open at 11:00) closed higher 7 of 8 times, +1.4% open to close. Verdict: candidate at most;
    stays a checklist item for the intraday check (the 2026-11-03 put mirror), not a mechanical rule;
    re-run when the sample reaches 15 failed days. Note the rule picks the weakest chip, which on 11-02
    was MRVL (not MU): its put did +178% live.

41. **Two-month call verticals, the owner's parameters (2026-11-04, VERTICALS.md, zoh/research/verticals.py).** First pass:
   `dip` (20 sessions after a turning fire) +10% on debit over two years (127, 56% win, +7% without the best two), `fire` -1%,
   `heat` -7%, control -3%; chips dip +17% (27). Next: hold 45 and 60 sessions instead of 30 (57 of 127 dips left on the time
   stop), dip at 10 / 30 sessions after the fire, split entries with an earnings date inside the window from those without,
   ETF spreads with $5-wide strikes only, and the put-vertical mirror on `heat` (the trend entry lost in every window).
42. **The 11:30 check-in (2026-11-04).** DONE 11-08, stock only (MIDDAY.md, zoh/research/midday.py, 30-minute bars
   2024-02 to 2026-11-05): SMH above its open at 10:00 and below it at 11:00 or 11:30 happened on 84 days (2.6 a month,
   13 in the last 3 months). SMH 11:30 -> close +0.26% average, 63% up; the weakest cached chip (NVDA/AMD/MU/AVGO) below
   its own open at 11:30: +0.28%, 59% up; chips already <= -2% at 11:30: 48% up, median -0.20%; last 3 months the weakest
   chip 11:30 -> close 36% up (11 days, median -0.20%). What the 13:16 check sees from 13:30 is the same (+0.18%). So the
   mirror arming between the check-ins is not a put signal on average; 11-02 (MU -3.4%) and 11-04 were the tail. The
   11:21 check-in stays as a judgment check (owner), no mechanical rule; the option leg of the failed-bounce put is in
   BOUNCE.md (-7% without the best). The 1-minute option replay (0.20-delta put from 11:33) was not run.
43. **Theme-state filter, forward test (2026-11-04, THEMES.md).** From 11-05 every sniper and intraday pick carries the
   theme state at entry in its file; after 20 trades compare call results in heating / neutral / turning with the
   backtest's 57% / 34% / 21%. Also the rebound_scanner retirement watch: the variant has 12 trades (42% win, -14% avg,
   real -$196), the family 20 (rebound_scanner_wide 6, _any 2); the gate is per variant, so it retires at 20.
44. **Ops: two Trade runs overlapped 15:32-15:48 on 11-04** -- CLOSED 11-08: they did not. The job timestamps show the
   queued run starting only after the dispatched run ended (11-04 run 70 jobs 20:48:50Z after run 68 ended 20:48:48Z;
   11-05 run 72 20:45:29Z after run 71; 11-06 run 76 20:45:49Z after run 74), each exiting within a minute because the day
   was done. The "overlap" came from reading run created_at as the start. The two cron runs arrive 6-7 hours late most
   days (14:40-15:30 ET) and queue behind the 08:30 dispatch, which is why the dispatch exists; no lease needed. Side
   finding: the Dashboard workflow's GitHub Pages deploy failed 4 times this week ("Deployment failed, try again later",
   GitHub side) and the next push healed it.
45. **The lock gate (2026-11-05).** Owner: "这是可预测的". Definition registered before the replay: at 10:00 ET
    LOCK = SPY below its open AND VIXY up >= 3% from its own open AND >= 8 of 10 mega caps (AAPL, MSFT, NVDA, AMZN,
    META, GOOGL, TSLA, AVGO, AMD, MU) below their opens. Replay since 2024-02 on 30-minute bars: how many lock days,
    SPY / QQQ / SMH 10:00-to-close on lock vs other below-open days, and the OPENDRIVE put rows (SPY/QQQ/NVDA/TSLA,
    take3 / hold / trail) split by the gate. Also test the weaker gates one at a time (VIXY alone, breadth alone) and
    the macro-day overlap. If lock days are few or half of them close up, "predictable" was hindsight and it is
    written down as such. If the gate holds: a shadow variant that buys the SPY put (and, with a turning theme and a
    sector negative, the weakest chip's put) at 10:00 on none days when locked. Result (11-05 evening, LOCKGATE.md): 694 sessions, 11 lock days, today the 11th. The other ten: SPY +0.1% avg from 10:00 to the close, 36% closed below the 10:00 price, six bounced; SPY 0DTE puts on lock days 20% win, -58% take3 / -88% hold (10), QQQ -83%. Breadth >= 8/10 alone (92 days) leans down (62%, -0.1%) but SPY puts still -26%; NVDA/TSLA puts on breadth days +20% last year (27, +4% w/o best 2, -19% last 3 months) are a candidate at most. VIXY >= 5% at 10:00: n=1 (today). Verdict: hindsight; no shadow variant. Next: extend the index-only replay to 2020-2023 (the 2022 lock days) and test the magnitude gate (VIXY >= 5%, SPY <= -1%). DONE 11-08 (LOCKGATE_2020_2023.md, `--start 2020-01-02 --end 2024-01-31 --suffix 2020_2023`): 1027 sessions, 15 lock days (26 with 2024-26). SPY 10:00 -> close on them +1.4% average, median +0.5%, only 4 of 15 (27%) closed below the 10:00 price; lock and SPY <= -1% at 10:00: 4 days, +2.9% (2022-01-24 +2.5%, 01-28 +3.1%, 05-06 +1.2%); VIXY >= 5% alone: 3 days, +4.7%. Breadth >= 8/10 alone: 163 days, 48% down, +0.1%. The macro column is empty there because the release calendar starts in 2024. Verdict unchanged and harder: lock days are mostly reversal days; 11-05 was one of the few that kept falling. Item closed.
46. **Tue/Thu blindness of the universe gap variants (2026-11-05).** DONE 11-08 (GAPDOWN.md, zoh/research/gapdown.py):
   the nvda_gapdown_put rule replayed since 2024-02 with the nearest expiry, the ledger's contract (one contract <= $150,
   |delta| >= 0.06, nearest 0.40), take3 exit, costs 10% each way. Mon/Wed/Fri same-day: last 3 months 9 trades 67% win
   +112% / +91% / +73% (median +208%), last year 26 trades +22% / +12% / +3%, since 2024-02 43 trades +28% / +22% / +16%.
   Tue/Thu with the next expiry (1-2 DTE): last 3 months 7 trades 43% +39% / +12% / -26% (median -45%), last year 28
   trades -19% / -27% / -36%, since 2024-02 56 trades -22% / -27% / -31%. The 11-05 187.5P (+183%) is the best of the
   seven. Verdict: the blindness protects the ledger; no `nvda_gapdown_put_near`, no any_expiry on the real variant.
   rebound_scanner on Tue/Thu was not re-run (EXITS.md already has rebound_tt negative).
47. **Overnight dip-buy (owner, 2026-11-05 talk).** DONE 11-08, stock only (DIPBUY.md, zoh/research/dipbuy.py, 30-minute
   bars): 16 days since 2024-02 with SPY >= 1.5% down open to close (11-05 has no next day in the data yet). Bought at the
   close: SPY to the next open -0.08% average (69% up, median +0.18%), QQQ 0.00%, the day's weakest ETF (SMH on 14 of 16)
   +0.47% (56% up); to the next 10:00 about zero; to the next close SPY +0.93% (62%), QQQ +1.21% (69%), weakest +1.92%
   (75%). Next-day CPI/NFP/FOMC (3 days): -0.3% to -1.2%. All-days base rate +0.06% to the open. Verdict: the overnight leg
   alone has no edge worth a rule; the bounce, when it comes, is the next session (OVERNIGHT.md, day-after-crash 54%
   up). Stays an opportunity type, no shadow variant.
48. **The 3% line on liquidation days (2026-11-05).** PARTIAL 11-08 (MIDDAY.md): only two days since 2024-02 had SMH
   <= -3% from its open at 10:00 in the 30-minute data (2025-02-27, 2026-06-25); chips beyond 3% below their open at
   10:00: 7 legs, 57% up, +0.21% to the close (the 06-25 bounce +2 to +7% vs the 02-27 slide -3 to -5%). Too few to
   judge. The 11-05 line stays a checklist note (measure from the 10:00 price on a liquidation day), no mechanical
   change; re-run with 1-minute bars when there are 10 such days.
49. **Pooled "sell at k x vs hold" table (2026-11-05 evening exchange).** DONE 11-08 on our side (SELLK.md,
   zoh/research/sellk.py): 79 real and shadow contracts since 10-19 with a 15:45 price. Per $1: the recorded live exits
   -14% / -19% / -23%, hold to 15:45 -22% / -29% / -36%, sell all at 2x -28%, at 3x -29%, half at 3x then hold -25%; 47%
   of trades reached 1.5x, 33% 2x, 18% 3x, 5% 5x. Among the 26 that reached 2x: recorded +118%, hold +98%, sell 3x +75%,
   half 3x + hold +87%; among the 14 that reached 3x: hold +212%, recorded +185%, half 5x + hold +196%. Puts (11): hold
   +166% vs recorded +81% vs sell 3x +42%; calls (68): hold -52% vs recorded -30%. So a fixed k x take is worse than the
   trail we run, and holding only pays on the put side (small n, the ORCL 10-30 put at 6.3x). The other Claude's rows with
   both legs (9, appendix) agree: the k leg 2.9x, the held or trailed leg 5.1x average, 2.7x median, 4 of 9 above 3x,
   all conditional on winners (757P 17.4x). Their machine-readable two columns had not arrived by Sunday morning.
50. **Structure layer for the check-ins (owner, 2026-11-06, from the EvaPanda alert at 12:18: "SPY lower high on the 5-min,
    will chop into the close; chips weak, NVDA near its low").** What the alert does that we do not: it fires on a structural
    change, not on a clock, and it names levels (day high 742, a mid level 738.2, prior close 733). Quick replay on the cached
    30-minute bars (2024-02 to 2026-11-05, 693 sessions), SPY from 12:00 to the close: up >0.3% at 10:00 and faded >0.3% by
    12:00 while still above the open: n=8, 100% closed above the 12:00 price, +1.75% avg; 12:00 at least 0.4% below the
    morning high and above the open ("lower high"): n=25, 60% up, +0.52%; up at 10:00 and below the open by 12:00: n=11,
    36% up, -0.23%; day after a >=2.5% SPY drop: n=8, 38% up, -0.18%; all days 52% / 0.00%. So a noon lower high is not a
    bearish signal on its own (if anything the opposite, small n); losing the open by noon is. To build: (a) a `structure`
    block in every intraday file: open, prior close, day high/low, VWAP, 10:00 and 12:00 prices, higher-high / lower-high
    state for SPY, QQQ, SMH and the pick; (b) an event-driven Discord notice (no orders) from the bot when SPY or SMH loses
    its open, takes out the day's low/high, or makes a lower high after 11:00; (c) replay with 1-minute bars: VWAP cross and
    lower-high after 11:00 as a put-mirror confirmation vs the current "below its open at 11:21" rule.
51. **Real orders at the ask do not fill on illiquid same-day contracts (2026-11-06).** DONE 11-08: spread gate live
   (PR #108: (ask-bid)/ask > 0.5 -> shadow at the mid, no real order). Replay of the broker's orders since 10-19: 30 buy
   orders, 25 filled (83%); fills 2.0% below the limit (= the shadow ask) at the median, 3.6% on average, 8 of 25 at the
   ask; the five cancels were all limit-at-ask on thin quotes (ORCL 0.24 10-23, AMAT 1.32 10-28, LLY 0.91, GE 0.54 x2).
   Exits: real minus shadow median $0.00 a contract (mean -$0.04). One shadow exit was a stale quote: TSLA 392.5C on
   11-04 booked 1.14 at 15:45 while the real market sell filled at 0.01 (the stock closed 8 points under the strike) --
   item 54.
52. **catalyst_open strike rule on high-priced stocks (2026-11-06).** DONE 11-08: delta floor 0.06 live (PR #108).
   Replay (STRIKEBUDGET.md, zoh/research/strikebudget.py): the 27 picks since 10-01 at their live entry minute under four
   strike rules with the real stake (20% of the main ledger). `old` (nearest the target among affordable): 26 taken, 5 of
   them under 0.06 delta, per $1 -30% / -38% / -47%, ledger dollars -$856. `floor`: 21 taken, 6 skipped, -29% / -39% /
   -49%, -$703. `pct` (strike within 2% of the spot): 11 taken, -34% / -54% / -68%, -$442 (rejected: it mostly skips).
   `nobudget` (the target delta, no stake): -21% / -33% / -41%, so the small stake costs about 9 points per $1 by forcing
   strikes. The floor saves ~$150 of 27 picks and nothing else: the catalyst family is negative under every rule
   (snipers 14 picks live rule -13% / -35% / -52%; intraday 13 picks -30% / -46% / -51%).
53. **prev_close feed and the overnight carry (2026-11-06).** DONE 11-08, first half: bot.previous_close used IEX daily
   bars, which end on IEX's last print. SPY IEX vs SIP close since 08-01: mean 0.010%, max 0.059% (11-05, 733.43 vs
   733.00); NVDA mean 0.031%, max 0.103%. Now SIP with the request ending at today's midnight (free history), IEX as the
   fallback (PR). Second half not done: the overnight gap distribution of carried catalyst contracts (how often the stock
   gaps against a carried pick by more than the option is worth).
54. **Shadow exits at stale quotes (2026-11-08, from item 51).** TSLA 392.5C 11-04: shadow 'time' exit booked at 1.14 while
   the real market sell filled at 0.01 with the stock 8 points under the strike; the shadow stock_open_drive row shows
   +58% against a real -99%. The spread gate (PR #108) books wide entries at the mid; exits still take the last quote.
   Replay exits.csv 'time' rows against the contract's 15:45 minute-bar close (sellk.json has both) and, if the shadow is
   systematically high, book the shadow exit at the bid (or the mid when the spread is over 50%).

55. **Entry retry slack on a fast tape (2026-11-09).** PARTLY DONE 11-09 evening (owner: 按你的来): index
   contracts (SPY/QQQ/IWM) retry up to +50%, single stocks keep 10% (bot.retry_slack, PR #111); the
   replay below is still open. spy_open_drive's real SPY 753C: limit 0.37 at the ask unfilled
   for 90 s, fresh ask 0.51 (+38%) beyond ENTRY_RETRY_SLACK 10% -> no retry, $0 real, while the shadow at 0.37 made
   +280% (half at 4.0x, trail 1.405). The 10% slack was set for illiquid single-stock contracts whose fresh ask is a
   stale quote; on SPY (spread 3%, 566K volume) the fresh ask is real. Replay every unfilled real entry since 10-01 (the
   bot logs 'no retry, fresh ask X vs Y') with a retry capped at +25% / +50% / uncapped, and every filled entry with a
   hypothetical +25% worse fill, by family (SPY/QQQ open-drive vs single-stock catalyst). Proposal if it pays: slack
   by family (index 0DTE 0.5, single stock 0.1), owner's call because it raises the entry price of real orders.
56. **The turning-theme filter's cost on catalyst days (2026-11-09).** AMD +7.4% open to close (+13.3% day) on an
   Oppenheimer upgrade and the NVDA-alternative trade, AVGO +4.6%, MU +4.3%: all in the turning chip theme, all
   un-pickable by the rule (28 calls on turning names won 21%, -68% avg). Split those 28 by cause: own catalyst (upgrade,
   contract, product) vs bounce-buying without news vs sector sympathy. If the own-catalyst subset is not negative, the
   filter should exempt it (keep blocking bounces and sympathy). Also list every turning-theme catalyst day since 10-01
   with the 0.2-delta same-day call result, so the filter's cost has a number next to its benefit.
57. **Sniper by catalyst class (2026-11-09).** WMT call on two target raises (JPM $145 06:33, UBS $149 11:04): +0.9% open
   to close, all of it after 14:00; the 131C 0.24 -> 0.19 carried. 10-16 and 11-02 were the same class (target raise /
   small-broker upgrade) and also went nowhere by the check-in. Table every pre-market sniper since 10-01 by class
   (major-broker upgrade, target raise only, product/trial/contract, priced offering, other) with stock open to close,
   the live option result and the hero result. If 'target raise only' is negative on >= 8 samples, the checklist demotes
   it: a target raise alone goes to `opportunities`, the sniper needs an upgrade, a product or a contract.

58. **Put-mirror live sample ledger (2026-11-10).** The 11:00 confirmation gave its first clean loss: SMH lost its 479.00 open at
   11:5x (not armed at 10:16 or 11:21), MU the name; untradable (the day's one catalyst entry went to AMZN at 10:18) and scored
   as a sample: MU 714.56 at 11:21 / 707.10 at 13:17 -> 725.11 close (+1.5% / +2.5% against the put, best for the put +2.1% at
   the 12:4x low 699.63), SMH closed +1.1% above its open. Live armings so far: 11-02 win (MU 860P 1.51 -> 27 live exit, +1315%
   held), 11-04 unjudged (MU -3.4% at the close, no 11:21 check yet), 11-05 not re-armed (SMH -5.8% from open but the 11:00
   bounce), 11-06 flat (MU put pick 689.69 -> 690.00, best +2.0%), 11-10 loss. Put every arming (date, arm time, SMH vs open at
   11:21 / 13:17 / close, name, name's move from 11:21 and 13:17 to the close, 0.2-delta put result) in one table and keep it
   current; the rule stays as is until the table has 10 rows. Item 40's BOUNCE.md numbers (arming between the check-ins is not a
   put signal on average) already say the tail carries it.
59. **The pick extension line by the name's own range (2026-11-10).** AMZN 11-02 (picked +4.0% from its open -> 255C -98%) and
   AMZN 11-10 (picked +2.0% from its open on a 06:38 catalyst plus a 09:55 piece -> 277.5C -64% at the close, topped 272.88 within
   minutes) both topped right after the pick. The 3% line was set on chips (AMD/MU days of 5-7%); a platform name's normal day is
   ~2%, so +2.0% on AMZN is already an extended move. Test on the 13 intraday picks plus the 10:16 / 11:21 / 13:16 opportunity rows
   with an entry-time price: extension from the open divided by the name's 20-day average open-to-high range (Alpaca daily bars),
   result from the pick to the close and the 0.2-delta option result, bucketed at < 0.5x, 0.5-1.0x, > 1.0x. If the > 1.0x bucket
   is the losing one, the line becomes 'one average range' instead of a flat 3%; until then it is an item, not a rule.

60. **A trail for the open-drive family (2026-11-11).** First live trade under the 0.35-delta ledger rule: stock_open_drive TSLA
   392.5C 1.69 at 10:01 -> 3.73 at 10:56 (+121%, TSLA 395.43) -> 0.09 at the 15:45 market sell (-$160, the ledger $493 -> $333);
   11-04 the same variant's TSLA 392.5C went 3.3x -> 0.01 and 11-09 spy_open_drive's 753C sold half at 4x and trailed the rest
   (+280%, the shadow's only big win). The family has half_at 3.0 and no trail (spy_open_drive_put trails after 2x). SELLK.md
   pooled: hold (-22%) is worse than the recorded exits (-14%) over 79 contracts, and among the 26 that reached 2x hold (+98%)
   beats sell-at-2x (+80%) and half-at-2x-hold (+89%): the pooled table does not say 'sell earlier'. Replay the open-drive
   contracts only (SPY/QQQ and NVDA/TSLA since 10-19, exits.csv peaks plus minute bars) with trail 40% after 1.5x, after 2x,
   half at 2x + trail, and hold, by family; if a trail beats hold on these 0.35-delta contracts without the best trade, set
   trail_after on spy_open_drive and stock_open_drive (a ledger decision, Claude's under the 11-09 mandate; one day is not
   evidence, hence the item).
   11-12 addendum, the hero arm as the 'hold' control: the catalyst legs with a trail and their heroes on the same contract are
   a live A/B. Four matched pairs so far (trail leg vs hero): 11-06 GE 330C -98% / -98%, 11-10 AMZN 277.5C -100% / -100%, 11-11
   AAPL 357.5C -4% / -100%, 11-11 MSFT 515P +10% / -100%: trail -48% avg, hero -100%. Unmatched heroes (different strike) tell
   the same story this week: TSM 415C 1.01 -> 7.13 peak -> 1.40 at the 11-12 close, AMD 617.5C 1.65 -> 4.17 -> 1.66, AVGO 377.5C
   1.49 -> 2.80 -> 1.01, while the trail legs took +56%, (none affordable), +12%. Keep the heroes as they are (they are the
   control, not a strategy) and count the pairs on Sunday with the per-$1 table.
   11-12 evening, from opendrive.json (real 0DTE prices, 10% costs, ~0.7% out of the money, data to 2026-10-15), the live-like
   trades by exit. NVDA/TSLA calls at +0.8% (89 trades; 53% reached 2x, 31% 3x): hold +27% (+4% without the best two), trail
   (arms at 2x, out at 60% of the peak) +19% (-2%), half at 3x + trail +15% (+1%), all out at 3x +3% (-2%). SPY calls at +0.5%
   (19): all out at 3x +68% (+28%), half at 3x + trail +65% (+25%), hold +30% (-31%). SPY puts at -0.5% (27): -28% to -38%
   under every exit. So the backtest does not support a trail or a 3x take on stock_open_drive: hold is its best arm, and one
   contract with half_at 3.0 and no single_take is already a hold; the 11-04 and 11-11 TSLA round trips are the price of the
   tail. On spy_open_drive the 3x take (single_take) is right. Left for Sunday: the same table on 0.35-delta strikes and
   through 11-12, next to the hero-vs-trail pairs (single-stock catalyst contracts 1-4% out of the money are a different
   animal from 0.4%-OTM open-drive contracts).

61. **Were the drops traceable? (owner, 2026-11-13 talk: "these drops all had signs you could follow").** DONE 11-12 evening
   (owner: "do not wait for Sunday, compute it now"; journal/research/DROPS.md, zoh/research/drops.py), result at the end. Test the claim both
   ways, not only on the days that fell. (a) Events: every day since 2024-02 with SPY <= -1.5% close to close or SMH <= -4%, and
   for 2026-10-01 onward by hand: 10-30, 11-02, 11-05 (theme drops) and 11-09, 11-12 (NVDA event gaps). (b) Lights on the evening
   before, each computable from data we already have: chips `turning` in THEMES (fired 10-13), SMH >= 12% below its 20-day
   closing high with SPY down < 1.5% over five days (the other Claude's condition, chosen after 11-05), AI-chain breadth
   (share of the 16 names below their 20-day average), 10Y change over five days, and for the recent weeks a hand count of
   financing / target-cut headlines on the chain (Melius 11-02, ORCL $20B, the AMZN supplier loan) and of company-specific
   negatives on NVDA (from 11-08). (c) The base rate that decides it: on ALL evenings with the same lights on, how often a drop
   followed within 1, 3 and 5 sessions; report hit rate, false-alarm rate and the lift over the unconditional rate, without the
   best-known episode (2026-11-05) as well. THEMES already says `turning` alone is a coin flip for the theme (87 episodes: 34
   continued, 25 recovered, 28 neither). (d) Split by kind: theme drops vs single-name event gaps; for event gaps measure the
   gap against the open-to-close move (11-09 NVDA -7% gap then +3.2% from the open; 11-12 -13% gap then +10.0%), i.e. whether
   'seeing it coming' could have been traded after the open at all. Use: if a combination of lights shows a lift >= 2x on >= 20
   lit evenings, it becomes a sizing input for the ledgers on lit evenings (a ledger decision under the 11-09 mandate), not a
   short signal; if not, it stays what it is today, a filter on what we do not buy.
   RESULT (2020-01-02 to 2026-11-12, 1,726 evenings; the last two years 502). (a) Recall on the recent leg is perfect: turning,
   diverge and breadth were lit before 10-14, 10-16, 10-22, 10-30 and 11-05, stretched before 10-22 and 11-05; the same lights
   were lit on every evening from 10-13 to 11-10, the up days included (11-09 +2.4%, 11-11 +1.3%). (b) Base rate, last two
   years: turning is lit on 14% of evenings and a -1.5% SPY day follows within five sessions 29% of the time against 23% on any
   evening (1.3x; SMH -4% days 1.9x); breadth lit 26%, 37% vs 23% (1.6x); rates 1.6x (1.3x since 2020, 0.7x in 2026); diverge 0.4x
   (SPY near its high is the calm regime). 12 of 29 drops (48 of 125 since 2020) had no light at all. Per episode: 2 of 12
   turning runs had a drop within five sessions of the first lit evening, 4 within ten. (c) `stretched` clears the bar written
   above: 2.4x on 22 lit evenings in two years, 2.2x on 64 since 2020, 2.3x on 54 before the known episode; 9 of 15 runs had a
   -1.5% day within five sessions. But +1.5% days are 2.0-2.2x as frequent too, the next session averages -0.06% and SPY five
   sessions later was up in 7 of the 15 runs: a volatility state, not a direction. The bar was badly written (it did not ask
   for asymmetry) and the backtest has only 4 live-like trades on stretched evenings, so no sizing change follows from it; the
   light is recorded in the morning file as a big-day light. (d) Event gaps: mega-cap gaps <= -5%, 131 in two years, open ->
   close +0.31%, 52% above the open; NVDA gaps <= -3%, 16, +1.73%, 56%; SPY gaps <= -0.7%, 46, +0.11%, 54%: nothing to short
   after 09:30. (e) The lights against opendrive.json (135 live-like trades to 2026-10-05): calls after a breadth evening 34
   trades, 59% win, +57% take3 (+42% without the best two) against 74 trades, 31%, -5% (-15%) after other evenings; lit beats
   unlit in each period slice; it is NVDA/TSLA (22 trades, 59%, +58% vs 67 trades, 28%, -15%), not SPY (12 vs 7, no
   difference). Six lights, two sides and four exits were looked at, so this cell is a candidate, not a rule: item 62.

62. **Chip breadth as a gate for stock_open_drive calls, and the put side (2026-11-12, from DROPS.md).** DONE 11-12, 23:50 ET
   (owner: "62 too, do not wait for Sunday"; journal/research/OPENGATE.md, zoh/research/opengate.py), result at the end. After an evening with
   >= 75% of the chip names below their own 20-day average, NVDA/TSLA calls at +0.8% from the open at 10:00 won 59% (+58% take3,
   +41% without the best two; 22 trades) against 28% (-15%; 67 trades) after other evenings, and lit beat unlit in the last 3
   months, the last year and before. Against it: the cell was found among 6 lights x 2 sides x 4 exits; the data ends 2026-10-15;
   and the live ledger's trades on lit evenings are 1 win (10-19 TSLA +259%) and 3 losses (11-04, 11-09, 11-11 TSLA, two of
   which peaked at 2.2-3.3x). To do: re-run opendrive through 11-12 on 0.35-delta strikes with the light of the evening before
   in each row; test the alternatives that would make chip breadth a proxy (SMH below its 20-day average, a VIX level, SPY's own
   20-day breadth); report lit vs unlit without the best two and for the last 3 months. If it holds, breadth becomes next week's
   one filter change: stock_open_drive trades only after a lit evening. Until then the review tags each stock_open_drive trade
   lit or unlit (`python -m zoh.research.drops --today` in the morning file). Separately, SPY puts at <= -0.5% lost under every
   exit (27 trades, 22-33% win, -28% to -38%): spy_open_drive_put holds a $500 real ledger and has not traded; decide on Sunday
   whether it stays real.
   RESULT (OPENGATE.md; 168 signals 2024-02-01 to 2026-11-12 re-priced at the contract nearest 0.35 delta, and the same 10:00
   signals on the stock alone for 2020 to 2023, which the option data does not reach).
   (a) The breadth light is not the gate. On the 0.35-delta strike held to 15:30 the split is still there (lit 28 trades, 54%
   win, +56%, +17% without the best two; not lit 67 trades, 25%, +8%, -23%), but it fails the bar written before the prices
   were read: shuffling the lit days reaches the gap in the average 17.6% of the time (0.9% for the win rate, before counting
   the 48 cells it was found in); there is no dose: 75-99% of chips below their average 18 trades 67% win, all twelve 10
   trades 30%; the lit trades sit in 9 of the 12 quarters and 2026 Q3 holds 7 of their 15 wins; the six trades after
   the discovery data (10-19 to 11-09) were all lit and one won (-41%), the ledger's own five 1 win; and in 2020 to 2023 the
   stock did the same after lit and unlit evenings (+0.27% against +0.28% from 10:00 to 15:30; 154 and 419 signals).
   (b) The plainer state it stands in for does better. The light never lit with SMH above its 20-day average, and `SMH
   below its 20-day average` adds 16 trades of the same kind: 44 trades, 50% win, +74%, +38% without the best two, against
   51 trades, 20%, -23%, -56% (shuffles reach it 1.6% and 0.2% of the time, picked from 15 states after reading them). On
   the ledger's own rule (Mon/Wed, the stronger name, no macro day, no monthly-expiry week): 15 trades 67% win +189% against
   14 trades 21% -60%. Out of sample on the stock alone, 2020 to 2023: the +1% from 10:00 that the call needs came on 44%
   of such days against 35% (231 and 342 signals; 46/37, 48/34, 42/35, 42/36 by year), 33% against 27% in 2024 to 2026. The
   call made money on 30 of 38 days with that +1% and on 2 of 57 without. So: a tilt of 6 to 9 points on the win rate, a
   third of what the option sample shows. A refinement found on the way (dip above the 100-day average 67% win, below it
   24%) does not survive 2020 to 2023 (43% against 44%) and is dropped.
   (c) What the ledger rests on: 2 of 12 calendar quarters averaged above zero (2026 Q2 +163% on 15 trades, none after a lit
   evening; 2026 Q3 +102% on 18). Without them: 62 trades, 26% win, -35%, and both sides lose (SMH below 31 trades 35% win
   -7%; above 31 trades 16% -63%). stock_open_drive was given its ledger on 10-16 on its last three months of real prices,
   which were 2026 Q3.
   DECISION (ledger decision, 11-09 mandate; the one filter change for the week of 11-16): stock_open_drive places real
   orders only after an evening with SMH below its 20-day average (`real_when` in config, judged by the bot at the last
   close; unknown state = shadow only); the shadow trades every signal as before. It changes nothing this week or next:
   SMH is below its average now (501.92 against 520.72) and 11-16 to 11-20 is the monthly-expiry week, which the ledger
   skips. Come-off bar: once the shadow has 10 signals on `above` evenings, the gate is removed if they won 4 or more, or
   averaged above zero without the best one. The breadth light stays in the morning file as a volatility note only. SPY
   calls get no gate (2020-23: +0.04% below against +0.23% above).
   The put hand stays real. On its own strike, days and exit it is not `negative under every exit`: 17 trades, 47% win,
   +21% under the trail, +1% without the best, -18% without the best two (all weekdays, 27 trades: 37%, -8%, -21%, -34%).
   New and against it: in 2020 to 2023, after SPY was 0.5% or more below its open at 10:00, it bounced 1% or more by 15:30
   on 31% of days and fell 1% further on 18% (62 signals; 2024-26: 10% and 17%, 30 signals): the bounce is the commoner
   tail. No evening state helps: the SMH split flips sign between the two periods. About six signals a year, at most half
   of $500 each, paused after five losses in a row; the owner chose it on 11-05 as a tail position with these odds in view.

## Done
- **Items 25, 29, 34 (2026-11-01), SNIPERS_REAL.md / snipers.json:** every pre-market sniper (13 with a
  live entry) and intraday pick (10) since 10-01 on real option minute bars, 10% costs each way. Snipers,
  live entry, sold 15:45: d0.10 -14% / -38% / -57% (avg / without best / without best two), d0.20 -31%,
  d0.30 -24%, d0.45 -23%. A wider delta does not fix it. Entry at 09:40 or 10:00 is no better. The lever is
  the trail arm: half at 3x with the trail armed at 1.5x instead of 2x improves every delta (snipers
  d0.10 -14% -> -7%; intraday carried d0.20 -6% -> +21% / +1% / -21%). The trail arm is an exit rule, so it
  goes to the owner as a proposal. The stock moved our way on 8 of 13 sniper days, but the median move
  (~+1% open to close) seldom pays for a same-day option. GEV 10-30 at a 09:31 entry would have made +166%
  (d0.10); the bias landed at 09:37 and the real entry was 09:38 at a higher price with a zero-bid
  contract (both fixed: routine at 08:20, zero-bid filter PR #89).
- **Item 35 (2026-11-01):** three real exits before 09:45 since 10-01: LITE +16% and ORCL half +20% better
  than the shadow, ORCL trail -31% worse; net -$18. All 30 real entries filled a median 2% under the shadow
  ask and exits a median 1.4% over the shadow price. No change.
- **Item 27 (2026-11-01):** same name in two variants on 7 days. NVDA gap-down days (10-16, 10-30): the
  rebound call lost 100% both times while nvda_gapdown_put won (+48%, +203%). TSLA 10-19 both won, TSLA
  10-26 the later 400C lost. No rule change; see item 36.
- **Item 28 (2026-11-01):** 2 of 10 intraday picks went untraded (INTC 10-26, ORCL 10-27), both before the
  +-15% strike band (PR #83); none since.
- **Item 22 (2026-10-25), WEEK43_EXITS.md / SECTORS.md:** (a) sector ETF follow at 10:00 (lead >= 0.8% beyond SPY):
  negative everywhere, 0.20 delta trail2x -24% / -29% / -33% last 3 months (24), -30% all (157); heating filter
  and bigger leads do not fix it. Rejected. (b) SPY follow-the-open 0.3-0.5% bucket (Mon-Thu, no release/opex):
  take3 -31% / -47% / -64% last year (16), -33% all (23); the >= 0.5% days carry the rule. (c) spy_open_drive
  (>= 0.5%) exits since 2024 (15): take3 +101% / +78% / +54%, half3_trail +97% / +71% / +50%, half3_hold (live)
  +77% / +50% / +27%, hold (live one-contract rule) +53% / +8% / -23%. stock_open_drive (NVDA/TSLA >= 0.8%,
  Mon/Wed) last year (29): hold +85% / +56% / +29% beats take3 +31% / +24% / +16% (last 3 months all negative
  without the best trade). Exit changes for spy_open_drive go to the owner.
- **Item 23 (2026-10-25):** leader_follow by weekday (0.20 delta, trail2x, all): Mon +12% / -2% / -16% (90),
  Tue -5%, Wed -17%, Thu -18%, Fri -27% / -30% / -33% (68); last 3 months Fri -29% / -43% / -54% (9) -> skips
  Fridays from 2026-10-26. Rebound calls are mostly Friday trades and the last 3 months were good (Fri +97% /
  +77% / +55%, 22): no change. megacap_reclaim has no real-price study yet. Carried intraday picks: no
  history to test; upgrade picks carried to expiry stay better than sold the first day (exits.json: +41% / +19%
  / +2% vs -4%, 46-60 trades).

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
