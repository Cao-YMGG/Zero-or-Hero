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
  belongs to the champion and the snipers. Weekly-review studies: `.github/workflows/sunday.yml`
  (run by hand) and `zoh/research/` (exits.py, scanners.py, ...).
- `journal/`: written by GitHub Actions — `trades.csv`, `equity.csv`, `REVIEW.md`,
  `BACKTEST.md`, `state.json`. Do not hand-edit trade history.
- API keys live only in GitHub Secrets; this container usually has none, so anything that
  needs Alpaca runs through the workflows (push to a `claude/**` branch triggers
  Diagnostics & backtest; read the run logs).

## Cadence
- Weekdays 08:50 ET: pre-market bias (below).
- Weekdays ~10:30 and ~13:00 ET: intraday check-in. Scan big intraday movers (Webull MIN_5 /
  DAY_1 rankings, read-only) and breaking news; if one has a fresh catalyst still unfolding,
  append one pick to `journal/bias/intraday/<today>.json` (schema in journal/bias/README.md)
  and push to main. Most check-ins add nothing. Read journal/news/LATEST.md for headlines since the open. Never touch the pre-market file after 09:30.
  Look for the day's leader: a large cap up >= 2% beyond SPY while its sector or the index is
  flat or red (META 2026-10-12/13 while chips sold off). Search that company's own news
  (product launches, model releases, analyst target changes) before calling a move "no news":
  on 2026-10-12 the Muse Wonder launch was missed and META ran +3.4%, then +4.5% the next day.
- Weekdays 16:35 ET: daily post-market review and light evolution. Grade every closed trade
  (real and shadow) and the day's pre-market calls in `journal/grades.csv` with the rubric in
  `journal/GRADING.md` (process score out of 10, separate from the result; peaks from
  `journal/exits.csv`). A win with a low score is luck, not evidence.
- Sundays 09:52 ET: weekly deep review (full protocol below, population cleanup, backtests).

## Noise gate (applies to the daily review)
One trade per variant per day is mostly luck, so daily changes are limited to additive ones:
new shadow-only challengers or signals, checklist and calendar fixes, bug fixes, hypotheses.
Retiring a variant needs >= 20 live shadow trades with clearly negative expectancy, or a
"broken" verdict in the backtest Regime check. Changing the champion's parameters or phase
sizing needs >= 10 live trades of evidence, or a documented regime change.

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
   news, today's scheduled releases/Fed speakers (also `config/macro_events.json`) and Treasury auctions (10Y/30Y auction results at 13:00 ET can turn the afternoon, as on 2026-10-07), VIX,
   yesterday's SPY close and trend, **crude oil (WTI/Brent) overnight move and why**,
   **US Treasury yields (2Y, 10Y) overnight change**, and the dollar index (DXY). Rising
   yields or an oil spike are usually equity headwinds; note what is already priced in.
   Night session (Webull snapshot with overnight_required=true; 20:00-04:00 ET): use it to spot
   news that broke after the close, not as a direction signal. journal/research/OVERNIGHT.md
   (2024-02+): the night move barely predicts open->close (SPY corr -0.11, QQQ -0.07, mega caps
   -0.04). One weak lean, SPY only: night down >= 0.3% then the pre-market recovers >= 0.2%,
   day +0.66% avg (32 days, 59% up); not true for QQQ or single stocks. 8:30 data overrides it.
3. Decide `call`, `put` or `none`. Prefer `none` when evidence is mixed: a skipped day costs
   nothing, a coin flip costs the spread and theta.
2b. Rotation map: with Webull daily bars, compute 1-week and 1-month returns for theme
   baskets — GPU (NVDA), CPU (AMD, INTC, ARM), memory (MU, SNDK), disk storage (WDC, STX) — keep these two apart, they split on 2026-10-07, optical
   (LITE, CIEN), power (GEV, VST), internet (META, GOOGL, MSFT, AMZN, AAPL), plus SPY/QQQ —
   and record which themes are heating up (money flowing in) and cooling (flowing out).
   Add newly hot themes (e.g. a new AI supply-chain link) as they appear.
   Outside tech, also track sector baskets every day: banks (JPM, GS, BAC), health care (UNH,
   LLY), energy (XOM, CVX), consumer (WMT, COST, HD), industrials (CAT, GE), with XLF/XLV/
   XLE/XLY/XLI and IWM as checks. Every universe and theme here was tech, so on 2026-10-14/15,
   when money left AI hardware for banks and health care (UNH +4.7%, LLY +3.6%), we had
   nothing pointed at where it went.
   A theme that is hottest into its own industry event (e.g. optical into the OCP summit)
   can be sold on the news: on 2026-10-12 LITE and CIEN fell ~10% with no news on the
   summit's first day. Do not name a sniper in such a theme on an event day, and note the
   event in `rotation`. On a rotation day out of one group, check the laggards of the
   group money is moving into (META +3.4% with no news on 2026-10-12).
2c. Earnings window: check `config/earnings.json` (and the Webull earnings calendar, which can
   move dates) for large caps reporting within 10 trading days. journal/research/RUNUP.md (201
   reports, 2 years): median 10-day run-up +1.6% vs SPY (60% up), but the reaction day is -1.6%
   (43% up) and options are pricey into the print. So these names are pre-earnings drift
   candidates for the sniper (META 2026-10-13 was two weeks out), never on the day before or
   the day of their report. Note peers' reports as read-through catalysts (TSMC/ASML for
   chips, big banks for financials) and record the window in `reasons`.
3b. Sniper (name one whenever a fresh catalyst with a small gap exists; null only when nothing
   qualifies; prefer upgrades over downgrades): prefer names in themes that are heating up; good news
   in a cooling theme tends to fade. scan mega caps with same-day options for a fresh,
   non-earnings catalyst (Webull PRE_MARKET movers + news, and that morning's analyst upgrades/downgrades on mega caps, e.g. 24/7 Wall St. "top analyst research calls"; 2026-10-05 Melius upgraded MSFT to Buy, gap only +0.9%, and it ran +1.5% from the open in 15 minutes). Name at most one stock with
   direction and catalyst in `sniper`; see journal/bias/README.md for the bar it must clear.
   Non-tech mega caps qualify too (JPM, GS, UNH, LLY, XOM, WMT, COST, V...). They mostly have
   Friday expiries only, so the sniper buys the nearest expiry; prefer them when the rotation
   map shows money moving into their sector.
   Headlines: read journal/news/LATEST.md first (Benzinga via Alpaca, refreshed 08:40 ET and every
   30 minutes in the session by the News feed workflow; rating changes listed first), then web
   search. For the candidate, check Webull get_analyst_target_price / get_analyst_rating (read-only):
   a price already above the median target leaves less room. No paid data (owner, 2026-10-16).
   If you cannot see a pre-market price for the candidate (e.g. Webull down and no Alpaca/IEX
   print), do not name it: on 2026-10-09 LITE was named blind and had gapped +6%.
   Relative strength or "money is moving into it" is not a catalyst. The sniper needs news of its
   own from the last day (rating change, target raise, product, contract, company statement);
   without one it is null. On 2026-10-15 AAPL was named on relative strength alone (no upgrade
   found), the chip selloff reversed by 10:00, money left the haven and AAPL fell 1.4% from the
   open: the real 355C went 0.36 -> 0.01 (-$140, 17% of the ledger). Low confidence is not the
   filter (the 0.35 picks LITE and META made +$45 and +$322); a missing catalyst is.
   When Webull is unavailable, use Alpaca snapshots (zoh.alpaca, feed iex) and say so in the file.
   Bearish days: when the SPY call is `put` with aligned macro evidence (hot data, yields and
   dollar up, futures red), the sniper may be a put. Look for a mega cap with no good news of
   its own, in a cooling theme or carrying a fresh negative (rate-sensitive, leveraged AI
   build-out, a peer's miss), with a gap under ~4%. Do not pick a call on a name whose story
   is momentum alone that day. On 2026-10-14 (hot core CPI) the META call never filled and
   META fell 2%, while ORCL fell 7.6% and AMD 3.5%. Puts are still rarer than calls: the market
   has trended up and the 10-07 put day lost.
4. Write `journal/bias/<today>.json` in the schema from `journal/bias/README.md`, commit
   ("bias: <date> <call|put|none>") and push to `main` before 09:30 ET. Retry the push on
   conflict (`git pull --rebase`). Do not touch any other file. Never place trades.
