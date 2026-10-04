"""Score every variant from the journal, write journal/REVIEW.md and promote a better champion.

Promotion rule (mechanical evolution): over each variant's last WINDOW shadow trades, a
challenger replaces the champion when both have at least MIN_TRADES, the challenger's
average return per trade beats the champion's by MARGIN, and the challenger is net
positive. Every promotion is logged in EVOLUTION.md.
"""
from datetime import date

from . import journal

WINDOW = 20
MIN_TRADES = 10
MARGIN = 0.10


def score(trades):
    pnl = [float(t["pnl_pct"]) for t in trades if t["pnl_pct"] != ""]
    if not pnl:
        return {"n": 0, "win_rate": 0.0, "avg": 0.0, "total": 0.0, "best": 0.0, "worst": 0.0}
    return {"n": len(pnl), "win_rate": sum(p > 0 for p in pnl) / len(pnl),
            "avg": sum(pnl) / len(pnl), "total": sum(pnl), "best": max(pnl), "worst": min(pnl)}


def leaderboard(config, trades):
    rows = []
    for variant in config["variants"]:
        mine = [t for t in trades if t["variant"] == variant["id"] and t["mode"] == "shadow"]
        rows.append({"id": variant["id"], "all": score(mine), "recent": score(mine[-WINDOW:])})
    return sorted(rows, key=lambda r: r["recent"]["avg"], reverse=True)


def promotion(config, board):
    champ = next((r for r in board if r["id"] == config["champion"]), None)
    if not champ or champ["recent"]["n"] < MIN_TRADES:
        return None
    for row in board:
        rec = row["recent"]
        if (row["id"] != champ["id"] and rec["n"] >= MIN_TRADES and rec["total"] > 0
                and rec["avg"] > champ["recent"]["avg"] + MARGIN):
            return champ, row
    return None


def render(config, board, trades, equity, promoted):
    real = [t for t in trades if t["mode"] == "real"]
    real_pnl = sum(float(t["pnl"]) for t in real)
    last = equity[-1] if equity else None
    lines = [f"# Review — {date.today()}", "",
             f"- Champion: **{config['champion']}**",
             f"- Equity: **${float(last['equity']):,.2f}** (phase {last['phase']})" if last
             else "- Equity: no trading days yet",
             f"- Real trades: {len(real)}, realised P&L ${real_pnl:+,.2f}", ""]
    if promoted:
        lines += [f"**Promoted {promoted[1]['id']} over {promoted[0]['id']}** "
                  f"(recent avg {promoted[1]['recent']['avg']:+.1%} vs "
                  f"{promoted[0]['recent']['avg']:+.1%}).", ""]
    lines += [f"## Shadow leaderboard (last {WINDOW} trades / all)", "",
              "| variant | n | win% | avg/trade | sum | best | worst | all-time n | all-time avg |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in board:
        rec, a = r["recent"], r["all"]
        mark = " 👑" if r["id"] == config["champion"] else ""
        lines.append(f"| {r['id']}{mark} | {rec['n']} | {rec['win_rate']:.0%} | {rec['avg']:+.1%} "
                     f"| {rec['total']:+.0%} | {rec['best']:+.0%} | {rec['worst']:+.0%} "
                     f"| {a['n']} | {a['avg']:+.1%} |")
    if real:
        lines += ["", "## Last real trades", "",
                  "| date | variant | contract | entry | exit | qty | P&L | reason |",
                  "|---|---|---|---|---|---|---|---|"]
        for t in real[-10:]:
            lines.append(f"| {t['date']} | {t['variant']} | {t['contract']} | {t['entry_price']} "
                         f"| {t['exit_price']} | {t['qty']} | {float(t['pnl']):+.2f} "
                         f"| {t['exit_reason']} |")
    return "\n".join(lines) + "\n"


def main():
    config = journal.load_config()
    trades = journal.read_trades()
    board = leaderboard(config, trades)
    promoted = promotion(config, board)
    if promoted:
        old, new = promoted
        config["champion"] = new["id"]
        journal.save_config(config)
        with (journal.ROOT / "EVOLUTION.md").open("a") as f:
            f.write(f"\n## {date.today()} — auto-promotion\n\n"
                    f"- `{new['id']}` replaces `{old['id']}` as champion: last {WINDOW} shadow "
                    f"trades avg {new['recent']['avg']:+.1%} vs {old['recent']['avg']:+.1%} "
                    f"(n={new['recent']['n']} / {old['recent']['n']}).\n")
    text = render(config, board, trades, journal.read_equity(), promoted)
    (journal.JOURNAL_DIR / "REVIEW.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
