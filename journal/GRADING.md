# Grading every trade and every call

Result alone is mostly luck (one trade per variant per day). Each trade, real and shadow, gets a
process score out of 10 so that a lucky win and an unlucky loss are not confused. The daily
post-market review fills `journal/grades.csv`; the weekly review averages it by variant.

## Who fills it

`python -m zoh.grade` runs at the end of the afternoon Trade job and appends every new closed
trade: thesis, entry and exit are computed from prices (underlying minute bars between entry and
exit; the peak from journal/exits.csv), discipline is pre-filled with the visible deductions
(direction against the day's SPY call, a macro day without a filter). The daily review checks the
discipline score, adds judgment deductions (blind pick, stale catalyst, budget-forced strike,
late entry) and the pre-market call verdicts. Rows marked "auto" have not been reviewed yet.

## Trade score (0-10)

| part | points | rule |
|---|---|---|
| 方向 thesis | 0-3 | Underlying from entry to exit (or close): 3 = moved our way far enough to reach the strike / the option could pay; 2 = moved our way, not enough; 1 = flat or mixed; 0 = against us. |
| 进场 entry | 0-2 | Best price after entry vs entry (peak multiple): 2 = >= 2x; 1 = 1.3-2x; 0 = < 1.3x (bought the top or a dead contract). |
| 出场 exit | 0-2 | Exit vs peak: 2 = kept >= 60% of the peak price; 1 = 30-60%, or the option never went above 1.3x (nothing to manage); 0 = < 30% after it had been >= 1.3x (gave it back). |
| 纪律 discipline | 0-3 | 3 = rule followed and it fits the day. Minus 1 for each: contradicts the day's SPY call; trades a macro day without a filter; pick made blind (no pre-market price) or stale catalyst; strike/expiry forced by budget (delta ~0); entry long after the move. |

`luck` = "lucky" when the trade made money with a score <= 5, "unlucky" when it lost with a score >= 6.
Peak = the highest price the bot saw while holding (journal/exits.csv from 2026-10-15; before that,
the journal state snapshots, which can miss a peak between commits).

## Call score (pre-market file)

- SPY call: right / wrong / missed (none on a day SPY moved >= 0.5% open to close) / ok (none on a quiet day).
- Sniper: right if the stock moved >= +1% open to close in the pick's direction, wrong if >= 1% against, flat otherwise; note whether the fill rule kept us out.

## Weekly use

Average score by variant next to its average result. A variant with good scores and bad results
needs more trades; bad scores and good results is luck and should not be promoted.
