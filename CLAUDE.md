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

## Evolution protocol (weekly review session)
1. Read `journal/REVIEW.md`, `journal/trades.csv`, `journal/equity.csv`, `journal/BACKTEST.md`,
   `EVOLUTION.md`.
2. Diagnose: which variants make money live vs backtest? Is the fade control as good as the
   trend versions (then direction has no edge)? Are shadow fills far from real fills?
3. Change at most a few things per week, each with a stated hypothesis: add 1–2 new
   challenger variants, retire variants with ≥20 live trades and clearly negative
   expectancy, tune parameters, calibrate `backtest.iv` to observed option prices.
4. Keep the population ≤ 10 variants. Never change trade history; never raise risk above the
   phase table without logging why.
5. When equity approaches the next phase, make sure that phase has a fitting strategy
   (e.g. debit spreads or longer-dated options for `compounder`).
6. Run `python -m unittest`, append an entry to `EVOLUTION.md`, commit and push to `main`.

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
4. Write `journal/bias/<today>.json` in the schema from `journal/bias/README.md`, commit
   ("bias: <date> <call|put|none>") and push to `main` before 09:30 ET. Retry the push on
   conflict (`git pull --rebase`). Do not touch any other file. Never place trades.
