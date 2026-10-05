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
- `journal/`: written by GitHub Actions — `trades.csv`, `equity.csv`, `REVIEW.md`,
  `BACKTEST.md`, `state.json`. Do not hand-edit trade history.
- API keys live only in GitHub Secrets; this container usually has none, so anything that
  needs Alpaca runs through the workflows (push to a `claude/**` branch triggers
  Diagnostics & backtest; read the run logs).

## Cadence
- Weekdays 08:50 ET: pre-market bias (below).
- Weekdays 16:35 ET: daily post-market review and light evolution.
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
   Then diagnose: which variants make money live vs backtest? Is the fade control as good as the
   trend versions (then direction has no edge)? Are shadow fills far from real fills?
3. Change at most a few things per week, each with a stated hypothesis: add 1–2 new
   challenger variants, retire variants with ≥20 live trades and clearly negative
   expectancy, tune parameters, calibrate `backtest.iv` to observed option prices.
4. Keep the population ≤ 12 variants (raised from 10 when single-stock variants were added). Never change trade history; never raise risk above the
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
   news, today's scheduled releases/Fed speakers (also `config/macro_events.json`), VIX,
   yesterday's SPY close and trend, **crude oil (WTI/Brent) overnight move and why**,
   **US Treasury yields (2Y, 10Y) overnight change**, and the dollar index (DXY). Rising
   yields or an oil spike are usually equity headwinds; note what is already priced in.
3. Decide `call`, `put` or `none`. Prefer `none` when evidence is mixed: a skipped day costs
   nothing, a coin flip costs the spread and theta.
2b. Rotation map: with Webull daily bars, compute 1-week and 1-month returns for theme
   baskets — GPU (NVDA), CPU (AMD, INTC, ARM), memory/storage (MU, SNDK, WDC), optical
   (LITE, CIEN), power (GEV, VST), internet (META, GOOGL, MSFT, AMZN, AAPL), plus SPY/QQQ —
   and record which themes are heating up (money flowing in) and cooling (flowing out).
   Add newly hot themes (e.g. a new AI supply-chain link) as they appear.
3b. Sniper (optional, most days null): prefer names in themes that are heating up; good news
   in a cooling theme tends to fade. scan mega caps with same-day options for a fresh,
   non-earnings catalyst (Webull PRE_MARKET movers + news, and that morning's analyst upgrades/downgrades on mega caps, e.g. 24/7 Wall St. "top analyst research calls"; 2026-10-05 Melius upgraded MSFT to Buy, gap only +0.9%, and it ran +1.5% from the open in 15 minutes). Name at most one stock with
   direction and catalyst in `sniper`; see journal/bias/README.md for the bar it must clear.
4. Write `journal/bias/<today>.json` in the schema from `journal/bias/README.md`, commit
   ("bias: <date> <call|put|none>") and push to `main` before 09:30 ET. Retry the push on
   conflict (`git pull --rebase`). Do not touch any other file. Never place trades.
