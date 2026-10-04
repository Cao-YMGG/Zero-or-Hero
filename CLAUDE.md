# Zero-or-Hero — notes for Claude

A self-evolving 0DTE options experiment on an **Alpaca paper account** ($500 start).
Never connect it to a live brokerage account or use real money (the Webull connector is a
live account — do not trade through it for this project).

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
