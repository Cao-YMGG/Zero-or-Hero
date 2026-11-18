# Zero-or-Hero — notes for Claude

A self-evolving 0DTE options experiment on an **Alpaca paper account** ($500 start).
Never connect it to a live brokerage account or use real money. The Webull connector is the
owner's live account: its read-only market-data tools (snapshots, bars, rankings, earnings
calendar, company profile) may be used for research and the pre-market bias; never call any
Webull order/instruction/account tool. All trading goes through Alpaca paper only.

## Layout
- `config/strategy.json`: phases, champion, variants. Most evolution happens here.
- `zoh/strategy.py`: pure logic shared by live bot and backtest. Add new signals to `SIGNALS`.
- `zoh/bot.py` (live), `zoh/backtest.py`, `zoh/review.py` (scoring + auto-promotion),
  `zoh/check.py` (diagnostics). Stdlib only, Python 3.12.
- `zoh/ledgers.py`: variants listed in config `ledgers` trade real paper orders from their own
  $500 ledger (journal/ledgers.json, journal/ledger_equity.csv); the main ledger (journal/ledger.json)
  belongs to the champion and the snipers. Since 2026-11-09 (owner) a ledger variant buys one contract
  nearest 0.35 delta (about 1% from the money) for up to half its ledger, and its shadow is sized the
  same way; before, 20% of the ledger at 0.15 delta bought strikes 2-5% out that went to zero with the
  direction right (14 of 134 graded trades, STRIKEBUDGET.md). A ledger variant with `real_when` trades real
  only on days its condition held at the last close (stock_open_drive: SMH below its 20-day average, 2026-11-13). Real entries on SPY/QQQ contracts are
  re-quoted once up to 50% above the first ask (10% on single stocks, bot.retry_slack). Weekly-review studies: `.github/workflows/sunday.yml`
  (run by hand) and `zoh/research/` (exits.py, scanners.py, ...).
- `journal/`: written by GitHub Actions — `trades.csv`, `equity.csv`, `REVIEW.md`,
  `BACKTEST.md`, `state.json`. Do not hand-edit trade history.
- API keys live only in GitHub Secrets; this container usually has none, so anything that
  needs Alpaca runs through the workflows (push to a `claude/**` branch triggers
  Diagnostics & backtest; read the run logs).

## How rules are kept (2026-11-18, owner: "it changes all the time, what do we do" / "you can do it today")
The market keeps changing; the rules must not chase it. Everything below sits on one of four shelves:
- **Rules**: held over at least a year of history (or 100+ events) in rising and in falling markets alike. Executed.
- **Switches**: a rule with its condition written in. A measurable state turns it on and off; each has a come-off bar.
- **On trial**: seen in weeks, not years. Followed for now with shadow money only; each names its test and the result
  that sends it back.
- **Observations** (journal/research/OBSERVATIONS.md): single days and small samples. Context, never executed, never by
  themselves a reason to take or skip a trade. Read them at the Sunday review, not every morning.

How a thing moves between shelves:
- A pattern seen in days becomes an observation and, if it looks worth a rule, a SUNDAY_TESTS item with the bar written
  before the run. No rule from one day or one week. Three came that way and failed: the 11:21 check-in (three days'
  pattern; its ideas were then right on 2 of 8), "past the 3% line is a no" (one day; not there in 251 ideas) and the
  blanket ban on calls in a turning theme (28 trades; cost seven winners on 11-09).
- A test covers rising and falling months separately (split on SPY's or the theme's one-month return), leads with the
  last 3 months and reports the average without its best one and two. Both sides pass: a Rule. One side only: a Switch
  with that side as its condition. Otherwise it stays an observation.
- A Rule whose last-3-month number turns negative at a weekly review goes back on trial.
- Prefer a rule that reacts to what the market does today (an entry gate, a state switch) to one that forecasts from
  last week.

## Rules (held in rising and falling markets)
- **R1. The gap is priced at the open.** OVERNIGHT.md (2024-02+): the night move barely predicts open to close (SPY
  corr -0.11, QQQ -0.07, mega caps -0.04). So `p_up` is open to close, and the night session is for spotting news that
  broke after the close, not for direction.
- **R2. A gap cannot be shorted after the open.** DROPS.md (daily bars 2020-01 to 2026-11): mega-cap gaps <= -5% closed
  above their open 52% of the time (+0.3%), NVDA gaps <= -3% 56% (+1.7%).
- **R3. Stay out of the report window.** RUNUP.md (201 reports, 2 years): median 10-day run-up +1.6% vs SPY (60% up),
  but the reaction day is -1.6% (43% up) and options are pricey into the print. Never a sniper or a pick on the day
  before a report, the day of it or the first trading day after it (the bot refuses these entries too). A large cap
  reporting within 10 trading days is a pre-earnings drift candidate until then; peers' reports are read-through
  catalysts (TSMC/ASML for chips, big banks for financials). Check `config/earnings.json` and the Webull earnings
  calendar, which can move dates.
- **R4. A broker's rating change is a day-0, first-minutes effect.** Upgrades are +0.92% open to close over 340 events
  of two years (62 on our 25 names, 278 on 105 other large caps; +0.84% after the market), the same with SPY above or below its 20-day average
  the evening before (+0.85% / +1.06%) and after up or down sessions (+0.81% / +1.04%). Out of sample it is +0.88% from
  the open but only +0.22% from the 09:32 price, nothing more by day +10, and a three-week call loses 11-15% at every
  strike (SLOWDRIFT_WIDE.md). Downgrades lose at every strike (33 events, -16% to -40%). So the sniper is named only on a
  broker's rating or target change; no slower version; a put sniper on a downgrade alone is not a trade. What it has
  not shown is money at option prices: the same strike and exit on the 62 events is -9% sold on day one (+19% / +12% /
  +5% carried to expiry with the trail on; last 3 months, 10 events, +12% / -9% / -17%). Do not quote the 25 names'
  carry as evidence. rating_open is on trial (T4).
- **R5. A single-stock idea is mostly a bet on the market that day, and the day cannot be told in advance.** Upgrades on
  days SPY closed above its open: +1.34% (our names +2.53%); below it: +0.37% (-0.19%). The 251 scored ideas of 10-29
  to 11-17 (average beta 1.9): 76% right and +1.19% when SPY moved their way over the same minutes, 27% and -1.08% when
  it moved against. Neither SPY's 20-day state, the prior session, nor where SPY stands against its own open at 10:15,
  11:20 or 13:15 (continued on 7, 6 and 3 of 14 days) tells which day it is (SUNDAY_TESTS 72). So: no market-state
  filter, no leaning the lists to one side, and the entry gate (the stock at or above its open between 09:31 and 10:00
  for a call, at or below it for a put) is the only tide filter; it kept us out on 11-16, 11-17 and 11-18. Score every
  idea after the market too (stock move minus beta times SPY): a miss that is right after the market is `tide`, not a
  lesson about the stock.
- **R6. The maps describe; they do not forecast.** Rotation map: on 30 mornings the names I listed as heating beat the
  ones listed as cooling open to close on 12, and the theme model's heating themes beat SPY the next day on 50% of 772
  theme-days. A `turning` theme's own next 1-4 weeks are a coin flip (87 episodes: 34 continued, 25 recovered, 28
  neither) and its gap-ups still closed up 56-60% of the time. Drop lights (DROPS.md, 2020-01 to 2026-11): turning,
  diverge, breadth and rates are lit on 14-26% of all evenings, a -1.5% SPY day is only 1.3-1.6x as frequent after
  them, and 12 of 29 drops had no light. Only `stretched` (SMH >= 12% below its 20-day high while SPY is down < 1.5%
  over five sessions) has lift: a -1.5% SPY day within five sessions 55-60% of the time against 23-27% (15 runs since
  2020), and +1.5% days just as often: big days, not down days. Record all of them; say what they are in `reasons`; do
  not move `p_up`, the SPY call or a sniper on them alone.

## Switches (on only while the condition holds)
- **S1. stock_open_drive places real orders only after an evening with SMH below its 20-day average** (`real_when` in
  config; OPENGATE.md: 50% against 20% wins on real 0.35-delta prices, and the +1% from 10:00 the call needs on 44%
  against 35% of days in 2020-2023). Its shadow trades every signal. Come-off bar: 10 shadow signals on `above`
  evenings winning 4 or more. Outside 2026 Q2-Q3 the ledger loses either way (62 trades, 26% win, -35%).
- **S2. The sniper and the intraday pick are shadow-only** (owner, 2026-11-09): catalyst_open and catalyst_intraday
  carry real_risk 0 and the hero shadows keep the full-ledger samples. 14 live snipers ran -13% (-35% without the best
  one) and 13 intraday picks -30% (SNIPERS_REAL.md). Real money returns when the live rule is positive over 20 more
  picks.
- **S3. Calls on a `turning` theme's names** (>= 3 turn flags, `python -m zoh.research.themes --today`): no call pick
  or sniper on a bounce, sympathy or relative strength; a name with a same-day catalyst of its own may be picked
  (owner, 2026-11-09) while SUNDAY_TESTS 56 splits the sample. Our calls on a turning theme's names won 21% (28 trades,
  -68% avg) against 57% in heating themes.
- **S4. A put sniper needs a put day**: the SPY call is `put` (`p_up` <= 0.40) with aligned macro evidence (hot data,
  yields and dollar up, futures red). Then: a mega cap with no good news of its own, in a cooling theme or carrying a
  fresh negative (rate-sensitive, leveraged AI build-out, a peer's miss), gap under ~4%. Two days of evidence only
  (10-14 would have paid, the 10-07 put day lost). Intraday picks may be puts on any day.
- **S5. The three open-drive ledgers skip the week of monthly expiry** (`skip_opex_week` in config). A retest on real
  prices is owed; the other side's same-day SPY puts on 11-16 are a known counter-case.

## On trial (weeks, not years; shadow money only)
- **T1. One check-in a day, at 10:16** (since 2026-11-18). Over the 251 scored ideas, those listed at the 10:16 check
  were right 57%, paid 31%, +0.43% (123 ideas, positive on 10 of 14 days); those listed 10:45-12:00 32%, 8%, -0.83%
  (38, positive on 2 of 12 days); after 12:00 42%, 12%, -0.19% (26). The 17 intraday picks to 11-13 were right open to
  close on 16 and right from the pick on 6. Three weeks of a falling market. Test: SUNDAY_TESTS 74(b). Sent back (the
  11:21 check-in returns) if a mechanical entry at 11:21 is no worse than at 10:16 over two years or in rising months.
- **T2. The put mirror, judged at 10:16.** Mirror ideas listed at the 10:16 check were right on 10 of 12 (+1.70%, 7
  days); judged at 11:21, on 2 of 8 (-0.72%). After the market the type is -0.32%: what paid was the theme continuing
  down, not the choice of name. Test: SUNDAY_TESTS 74(a, c). Back to an idea, not a pick, if the 10:16 entry is not
  positive without its best two; if the ETF does as well as the weakest name, the mirror buys the ETF.
- **T3. Not at the extreme; priced past 3%.** Ideas listed within 0.25% of the day's extreme paid 14-20% (43 ideas)
  against 23-33% off it (144): no idea and no pick at the day's extreme. A pre-market catalyst counts as priced once
  the stock is >= 3% from its open by the check-in (one case, AMZN 11-02), though ideas already 3% their way paid 29%
  (51 ideas), no worse than the rest. Test: SUNDAY_TESTS 73.
- **T4. rating_open** (shadow: two contracts nearest 0.45 delta whatever they cost, half out at 2x, the rest trails
  from 1.5x; classes `upgrade` and `target` only). On real option prices to 11-13 the 13 rating-change snipers were
  right on 10 (+0.91%) and made +17% (+7% without the best, -4% without the best two; 10 entries); the 10 company-news
  snipers were right on 5 (-0.46%) and lost 56-71% at every strike. Ten entries make a candidate. Test: SUNDAY_TESTS 70.
- **T5. The pick bar: the tape must already agree** (the stock moving the pick's way from its open or since the
  headline), and a pick says what is still to come (news not yet out, a level not yet reached), not what the stock has
  done. From two option trades and the 17 picks above.
- **T6. Short lists, no controls** (since 2026-11-18): at most four ideas in the morning file and three at 10:16, each
  one I would pick if the bar allowed (`yes`) or one step short (`maybe`); no idea listed to argue against it; no
  morning put idea unless it is a put day (15 morning puts: right on 5, -1.96%). After the market the 219 ideas listed
  but not picked came to -0.06% (48% positive), the 31 picks and snipers to +0.65% (71%).
- **T7. Sniper gap limits**: a heavy catalyst (an upgrade by a major broker) qualifies with a pre-market gap up to
  ~3%, a weak one (a target raise) up to ~1.5%. From a handful of mornings.

## Reading habits (about my own misses, not the market: these do not expire)
- Read journal/news/LATEST.md first (Benzinga via Alpaca, refreshed 08:40 ET and every 30 minutes in the session;
  rating changes listed first), then web search. The Alpaca news endpoint takes any symbol. **Its times are UTC**: a
  headline stamped 13:30-21:00 came out in yesterday's session and is in yesterday's close (11-18: AVGO's $1B Anthropic
  line read as "last night", posted 15:01 ET).
- Read every headline on the candidate from the last 24 hours, not only the most visible, and again at the 08:30
  re-read: the whole news file for its symbol, not its top lines.
- A mega cap moving >= 2% pre-market with no visible headline is a question, not a non-event: search its own news and
  its peers' overnight results (SK Hynix/Samsung/TSMC for memory and chips, ASML for equipment).
- A policy or regulation headline has winners as well as losers: name both before filing it.
- For the candidate, check Webull get_analyst_target_price / get_analyst_rating (read-only): a price already above
  the median target leaves less room.
- No pre-market price for the candidate (Webull down and no Alpaca/IEX print): do not name it. When Webull is
  unavailable use Alpaca snapshots (zoh.alpaca, feed iex) and say so in the file.
- Relative strength or "money is moving into it" is not a catalyst. Search a leader's own news (product launches,
  model releases, analyst calls) before calling a move "no news".
- Say what I think before the close (`conviction`); never fill it in afterwards. "I do not know" is an answer.
- No paid data (owner, 2026-10-16). Every Discord-facing text in plain Chinese (owner, 2026-11-02).

## Cadence
- Weekdays 07:40 ET: pre-market bias (procedure below). If it starts before 08:00, research first and re-read the live
  pre-market numbers after 08:30; on 08:30 release days read the print before the SPY call.
- Weekdays ~10:16 ET: the intraday check-in, the only one of the day (T1):
  - Scan big intraday movers (Webull MIN_5 / DAY_1 rankings and snapshots, read-only) and the news since the open.
    Never touch the pre-market file after 09:30.
  - At most one pick, appended to `journal/bias/intraday/<today>.json` (schema in journal/bias/README.md) and pushed to
    main; most check-ins add none. A pick needs a cause still unfolding: news that broke in the session, a sector
    catalyst from the same day (then the strongest mega cap of that sector may be picked without in-session news of
    its own; owner, 2026-10-21: "we need samples"), or the put mirror; and the tape agreeing (T5). Never inside a
    report window (R3), never on relative strength with no news anywhere behind it, never at the day's extreme (T3).
  - Look at both sides (owner, 2026-11-03). Call side, the day's leader: a large cap up >= 2% beyond SPY while its
    sector or the index is flat or red; without in-session news of its own, a leader already >= 3% from its open goes
    into `opportunities`, not `picks`. Put side, the mirror (T2): when the morning filed a theme as cooling or turning
    and its ETF is already below its open after a gap up or a bounce, the weakest mega cap of that theme that is below
    its own open and outside a report window is the put pick, strongest when a sector negative broke the same morning
    (target cuts across the group, a raise of capital, dilution). The check-in judges it itself and writes no
    conditional line. Calls on a turning theme's names: S3.
  - A pick on a stock above ~$1,000 is a shadow sample only (the 20% stake, ~$92, buys nothing at the 0.06-delta
    floor): say so in the pick and prefer a sub-$700 name when one carries the same news.
  - Ideas that do not clear the bar go into the file's `opportunities` (T6: at most three, `yes` or `maybe`; no orders;
    scored at the close). Picks carry `catalyst_zh` and opportunities `why_zh`.
- Weekdays 16:35 ET: daily post-market review and light evolution. Grade every closed trade
  (real and shadow) and the day's pre-market calls in `journal/grades.csv` with the rubric in
  `journal/GRADING.md` (process score out of 10, separate from the result; peaks from
  `journal/exits.csv`). A win with a low score is luck, not evidence. Then write the post-market
  check `journal/checks/<today>.json` (`{"date", "text"}`, plain Chinese, a few short lines): the
  SPY call vs the open-to-close move, the sniper and intraday picks (stock move and option result),
  the morning predictions right/wrong, real fills vs the broker, one lesson. Push it to main; the
  Notify workflow posts it to Discord (owner, 2026-11-02: "you have to check after the close too").
- Weekdays 17:43 ET: opportunity post-mortem (owner, 2026-11-13: "set a task: improve it every day, and when you
  are wrong work out why you read it wrong"). `python -m zoh.research.opportunities` scores the day's ideas to the
  real close (paid = 1% or more the idea's way, right, wrong; each against SPY over the same minutes), then
  `--review` lists what owes a post-mortem: every wrong idea and every pick. Each gets one row in
  journal/opportunity_reviews.csv through `--add-reviews`: one cause from the fixed list (chased, no_catalyst,
  missed_news, misread_news, priced_in, tide, reversal, timing, luck, sound, noise, other) and what I thought, what
  happened and the lesson, in plain words; say "I do not know" as `other` rather than invent a reason. Then one
  improvement a day, taken from what the post-mortems show: to the scorer or the record (additive, a new column or
  split; a changed definition re-scores the whole log so old and new rows compare), to the type list, or to the
  reading habits above. A day with nothing worth changing says so. Nothing moves onto the Rules or Switches shelf
  here: a pattern goes to OBSERVATIONS.md and, if worth it, a SUNDAY_TESTS item. Write
  journal/postmortems/<date>.json (`{"date", "text"}`, plain Chinese: the tally, each wrong idea in one line with its
  cause, the day's change, the running count of causes) and push it; Notify posts it. The pre-market and intraday
  sessions read the cause table at the bottom of journal/research/OPPORTUNITY_SCORES.md before listing ideas.
  Every listed idea carries `conviction`: `yes` = I would pick it if the bar allowed, `maybe` = one step short (`no`,
  a control, was used from 11-13 to 11-18 and is no longer listed).
- Sundays 09:52 ET: weekly deep review (full protocol below, population cleanup, backtests). It also walks the
  shelves: runs the owed tests, moves what passed or failed, and reads OBSERVATIONS.md for patterns worth a test.

## Noise gate (applies to the daily review)
One trade per variant per day is mostly luck, so daily changes are limited to additive ones:
new shadow-only challengers or signals, checklist and calendar fixes, bug fixes, hypotheses.
Retiring a variant needs >= 20 live shadow trades with clearly negative expectancy, or a
"broken" verdict in the backtest Regime check. Changing the champion's parameters or phase
sizing needs >= 10 live trades of evidence, or a documented regime change.

Owner, 2026-11-09 ("可以，按你的来"): decisions about the paper ledgers are Claude's to make and to
report the same evening: strike and stake rules, exit rules, filters, a variant's real-or-shadow
status, population changes within the bars above. Only what touches real money (Webull, live
trading, the readiness verdict) waits for the owner. Filters change at most once a week, from a
SUNDAY_TESTS item with numbers: one day's loss produces an item, not a new rule in this file.
Owner, 2026-11-18 ("你想想，按你方向改" / "你可以今天做"): the once-a-week limit was lifted for that day's changes
(one check-in, short lists, sniper on rating changes only, the shelves above). It stands again from 11-19.

## Evolution protocol (weekly review session)
1. Read `journal/REVIEW.md`, `journal/trades.csv`, `journal/equity.csv`, `journal/BACKTEST.md`,
   `EVOLUTION.md`.
2. Regime first: markets change (themes, volatility, rate/oil sensitivity). Weight recent
   evidence over old: live shadow trades > the backtest's "Regime check" (last ~3 months) >
   the full-year backtest. Note in EVOLUTION.md whether the regime looks different from last
   week (volatility level, leading themes, stock/bond correlation) and retire variants the
   regime check marks "broken" even if their full-year numbers look fine.
   Research conclusions lead with the last-3-month numbers (Regime check columns); one- and
   two-year numbers are context only, because the story changes (a year ago the AI-CPU and
   Muse themes did not exist). A rule that is negative over two years but positive recently
   is a candidate, not a reject; the reverse is a reject.
   Every result also reports the average without its single best trade (and best two): option
   rules here live on fat tails, and on 2026-10-07 a +6% result became -12% once false events
   and one +415% trade were removed. A rule that is only positive because of one trade is a
   candidate at most.
   Then diagnose: average grade (journal/grades.csv) next to average result per variant; good
   scores with bad results need more trades, bad scores with good results are luck and are never
   promoted. Which variants make money live vs backtest? Is the fade control as good as the
   trend versions (then direction has no edge)? Are shadow fills far from real fills?
3. Change at most a few things per week, each with a stated hypothesis: add 1–2 new
   challenger variants, retire variants with ≥20 live trades and clearly negative
   expectancy, tune parameters, calibrate `backtest.iv` to observed option prices.
4. Keep the population ≤ 12 variants (cut to 7 on 2026-10-11 so each gathers trades faster). Never change trade history; never raise risk above the
   phase table without logging why.
5. When equity approaches the next phase, make sure that phase has a fitting strategy
   (e.g. debit spreads or longer-dated options for `compounder`).
6. Run `python -m unittest`, append an entry to `EVOLUTION.md`, commit and push to `main`.
7. Live-readiness scorecard (the owner may later trade the champion with real money on Webull,
   by hand, only when Claude says the evidence is there). Append to the EVOLUTION.md entry, each
   gate with its current number: (a) >= 30 real paper fills by the champion; (b) median real fill
   vs shadow quote vs model price measured; (c) expectancy per trade still positive at real fill
   prices; (d) paper equity actually up from $500; (e) has lived through at least one regime
   change. Verdict: "not ready", "close" or "ready" — be honest, "never" is allowed. Claude
   never connects the project to Webull or any live account and never places live trades;
   saying "ready" is a report, not an action.

## Daily pre-market bias (weekday session, before 09:30 ET)
Goal: one honest directional call for SPY today, so `claude_bias` and `claude_confirm` can be
scored against purely mechanical variants.
1. If today is not a NYSE trading day, stop without writing anything.
2. Research (Webull read-only snapshots with extended hours for SPY/QQQ/TLT/USO/UUP and
   pre-market movers; web search for the rest): S&P 500 futures vs prior close, overnight Asia/Europe, major
   news, today's scheduled releases/Fed speakers (also `config/macro_events.json`) and Treasury auctions (10Y/30Y
   results at 13:00 ET can turn the afternoon), VIX, yesterday's SPY close and trend, **crude oil (WTI/Brent)
   overnight move and why**, **US Treasury yields (2Y, 10Y) overnight change**, and the dollar index (DXY). Rising
   yields or an oil spike are usually equity headwinds; note what is already priced in. Night session (Webull
   snapshot with overnight_required=true; 20:00-04:00 ET): for news, not direction (R1).
3. Write `p_up`, the probability that SPY closes above its OPEN today (open to close, R1). Honest values sit near
   0.50-0.58 most days; a call needs >= 0.60, a put <= 0.40 (since 2026-10-23, owner talk). Scored 2026-11-15
   (WEEK46.md): 16 mornings, every `p_up` between 0.44 and 0.54, Brier 0.240 against 0.250 for a flat 0.50. The bar
   is not what keeps the call at `none`; an estimate that never leaves 0.45-0.55 is. Do not lower the bar. When the
   evidence is one-sided (data, yields, futures and breadth the same way), write the number that says so. Decide
   `call`, `put` or `none`; prefer `none` when evidence is mixed: a skipped day costs nothing, a coin flip costs the
   spread and theta.
2b. Rotation map (context and a filter on our own picks, R6): with Webull or Alpaca daily bars, compute 1-week and
   1-month returns for theme baskets: GPU (NVDA), CPU (AMD, INTC, ARM), memory (MU, SNDK), disk storage (WDC, STX;
   keep these two apart), optical (LITE, CIEN), power (GEV, VST), internet (META, GOOGL, MSFT, AMZN, AAPL), plus
   SPY/QQQ; and the sector baskets outside tech: banks (JPM, GS, BAC), health care (UNH, LLY), energy (XOM, CVX),
   consumer (WMT, COST, HD), industrials (CAT, GE), with XLF/XLV/XLE/XLY/XLI and IWM as checks. Record which are
   heating and cooling; add newly hot themes as they appear. Run `python -m zoh.research.themes --today` and
   `python -m zoh.research.drops --today` (Alpaca daily bars; keys are in the workflows and usually in this container)
   and record each theme's state and the lit lights in `rotation.theme_state`. Note a theme's own industry event in
   `rotation`.
2c. Earnings window (R3): list the large caps reporting within 10 trading days and the peers' reports in `reasons`.
3b. Sniper: at most one stock, with direction, `class` and catalyst in `sniper`; journal/bias/README.md has the bar.
   Named only on a broker's rating change (`upgrade`) or target change with the rating kept (`target`) on a mega cap
   with same-day or nearest-Friday options (R4); a company-news item (`news`: product, contract, partnership, sales,
   talks, a statement, a priced offering) goes into `opportunities` as `company_news`, and the sniper is null on a
   morning without a rating or target change that qualifies. Prefer upgrades to downgrades, names in heating themes
   (good news in a cooling theme tends to fade), a small gap (T7); non-tech mega caps qualify too (JPM, GS, UNH, LLY,
   XOM, WMT, COST, V...; mostly Friday expiries, so the sniper buys the nearest one). Scan Webull PRE_MARKET movers
   and news and that morning's analyst calls. Outside the report window (R3); a put only on a put day (S4); calls on
   a turning theme's names per S3; the reading habits above before naming it. Shadow-only (S2): catalyst_open trades
   every class at 0.10 delta and its hero the full ledger, rating_open the two rating classes (T4).
4. Write `journal/bias/<today>.json` in the schema from `journal/bias/README.md`, commit
   ("bias: <date> <call|put|none>") and push to `main` before 09:30 ET. Fill `opportunities` with the ideas of the
   morning I would back (T6: at most four, no controls) by type (journal/research/OPPORTUNITIES.md), traded or not;
   the close scores them in journal/opportunities.csv (owner, 2026-10-29). Also fill the `zh` block and each
   opportunity's `why_zh` in plain Chinese (journal/bias/README.md). Retry the push on conflict
   (`git pull --rebase`). Do not touch any other file. Never place trades.
