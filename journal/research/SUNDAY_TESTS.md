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
36. **Go with the day's driver, generalized (2026-11-01).** nvda_gapdown_put (NVDA gap down, still
    0.1% under its open at 10:00, ~0.40-delta put, take profit at 3x) is the only ledger up this month
    (+$191) and won both days it met the rebound call on the other side (10-16, 10-30). Real option
    prices, 2 years, last 3 months first: the same rule on AMD, AVGO, MU, TSLA, META, AMZN, and "the
    weakest mega cap of the sector that gaps down most". If positive without the best two, it is the
    first candidate when a slot opens.
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
42. **The 11:30 check-in (2026-11-04).** Three sessions in a row the put mirror armed between 10:45 and 11:30 (11-02 MU,
   11-03 SMH briefly, 11-04 MU/MRVL) and neither the 10:16 nor the 13:16 check saw it. Extend bounce.py: CHECK at 11:30 and
   "any day SMH crosses below its open between 10:30 and 11:30" (not only cooling-theme gap-ups), 0.20-delta put from 11:33,
   live / hold / stock-stop exits, 2 years; count how many picks per month it would add and what the 13:16 check would have
   found instead. Decide the extra routine on that number.
43. **Theme-state filter, forward test (2026-11-04, THEMES.md).** From 11-05 every sniper and intraday pick carries the
   theme state at entry in its file; after 20 trades compare call results in heating / neutral / turning with the
   backtest's 57% / 34% / 21%. Also the rebound_scanner retirement watch: the variant has 12 trades (42% win, -14% avg,
   real -$196), the family 20 (rebound_scanner_wide 6, _any 2); the gate is per variant, so it retires at 20.
44. **Ops: two Trade runs overlapped 15:32-15:48 on 11-04** (again 15:04-15:46 on 11-06: dispatched run 74 and scheduled run 76; 14:42's run 75 was cancelled by the concurrency group, 15:04's was not) (the 08:31 dispatch run and the late scheduled run 70) although the
   workflow's concurrency group is `trade` with cancel-in-progress false; both tried to sell the same contracts and the
   already-sold guard kept the journal right. Check GitHub's queueing semantics for dispatch vs schedule and add a lease in
   state.json (a `running` stamp refreshed every loop; a second bot exits when it is fresh).

45. **The lock gate (2026-11-05).** Owner: "这是可预测的". Definition registered before the replay: at 10:00 ET
    LOCK = SPY below its open AND VIXY up >= 3% from its own open AND >= 8 of 10 mega caps (AAPL, MSFT, NVDA, AMZN,
    META, GOOGL, TSLA, AVGO, AMD, MU) below their opens. Replay since 2024-02 on 30-minute bars: how many lock days,
    SPY / QQQ / SMH 10:00-to-close on lock vs other below-open days, and the OPENDRIVE put rows (SPY/QQQ/NVDA/TSLA,
    take3 / hold / trail) split by the gate. Also test the weaker gates one at a time (VIXY alone, breadth alone) and
    the macro-day overlap. If lock days are few or half of them close up, "predictable" was hindsight and it is
    written down as such. If the gate holds: a shadow variant that buys the SPY put (and, with a turning theme and a
    sector negative, the weakest chip's put) at 10:00 on none days when locked. Result (11-05 evening, LOCKGATE.md): 694 sessions, 11 lock days, today the 11th. The other ten: SPY +0.1% avg from 10:00 to the close, 36% closed below the 10:00 price, six bounced; SPY 0DTE puts on lock days 20% win, -58% take3 / -88% hold (10), QQQ -83%. Breadth >= 8/10 alone (92 days) leans down (62%, -0.1%) but SPY puts still -26%; NVDA/TSLA puts on breadth days +20% last year (27, +4% w/o best 2, -19% last 3 months) are a candidate at most. VIXY >= 5% at 10:00: n=1 (today). Verdict: hindsight; no shadow variant. Next: extend the index-only replay to 2020-2023 (the 2022 lock days) and test the magnitude gate (VIXY >= 5%, SPY <= -1%).
46. **Tue/Thu blindness of the universe gap variants (2026-11-05).** `same_day_expiry` skips every universe name on
    days it has no same-day expiry, so nvda_gapdown_put (real ledger) and rebound_scanner (champion) never scan on
    Tuesdays and Thursdays. 11-05: NVDA -2.0% gap, -4% at 10:00, the 11-06 187.5P went 2.50 -> 7.07 (+183%) and the
    ledger-affordable 185P 1.74 -> 5.53. Replay both rules on Tue/Thu since 2024-02 with the nearest expiry (1-2 DTE,
    realopt daily bars) next to their Mon/Wed/Fri record; if the 1-DTE days are not worse, add `nvda_gapdown_put_near`
    (any_expiry, shadow) and decide which of the 12 gives up its slot.
47. **Overnight dip-buy (owner, 2026-11-05 talk).** Buy SPY / QQQ / the day's weakest theme ETF at 15:50 on a day that
    is down >= 1.5% open to close, sell at the next open (and at 10:00); split by lock days (45), by VIXY level and by
    whether the next day is a macro day. Stock only (no option bleed); OVERNIGHT.md has the night-move base rates.
48. **The 3% line on liquidation days (2026-11-05).** The intraday put mirror measures "within 3% of its own open";
    on 11-05 every chip was 4-6% below its open by 10:00 and the four right puts were excluded. Replay the mirror
    (BOUNCE.md data) with the line measured from the 10:00 price and from the 11:00 bounce high instead of the open.
49. **Pooled "sell at k x vs hold" table (2026-11-05 evening exchange).** The other Claude sent 49 rows of exits at
    >= 2x since 10-19 (exchange/claude-b/received/2026-11-05.reply-claude-b.json, `two_x_rows`: 22 filled 3x orders,
    11 at 2x, 8 trailed 40% after 2x, 8 held to time) and will add the price at the 2x moment and before the close on
    Saturday. Bring our half_at shadow records and stock_open_drive / spy_open_drive real fills in the same fields and
    compute k x vs hold on the pooled set; today's 757P (4 of 7 held to 15:30 at 17x, +$9,408) and the follow card
    (half 3x, half trailed: +2.7 per $1 vs +10.5 held) are the put-side examples. Their follow-card split to carry:
    VIX >= 24 the day before 15 days +57%, VIX < 24 37 days -5%.
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
51. **Real orders at the ask do not fill on illiquid same-day contracts (2026-11-06).** Three of three real orders canceled unfilled:
    LLY 1430C limit 0.91 (bid 0.28, spread 69% of the ask; fresh ask 1.11 after 90 s, no retry), GE 330C limit 0.54 twice (bid 0.09,
    spread 83%). The shadow booked both at the ask and lost -$144; reality $0. Replay journal/trades.csv real rows since 10-19:
    fill rate and slippage vs the quoted spread; then add a spread gate for real orders ((ask-bid)/ask > 0.5 -> no real order, log
    it) and book the shadow at the mid when the spread is that wide, so shadow results stop overstating losses on names like GE.
52. **catalyst_open strike rule on high-priced stocks (2026-11-06).** The $92 budget (20% of $457) cannot buy a 0.10-delta same-day
    call on a $1,350 stock: the bot took a 0.03-delta 1430C (6% OTM) that could not pay while LLY rose 2% from its open; the hero
    shadow's 0.10-delta 1390C went +64% then to zero. Options: choose the strike by percent OTM (<= 2%) with the budget as a cap on
    quantity, not on delta; or skip real orders when the affordable delta is below 0.06; or size catalyst_open from a bigger
    stake. Replay SNIPERS_REAL rows with both rules.

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
