"""Post short summaries to a Discord channel (owner, 2026-10-29).

The webhook URL lives only in the GitHub secret DISCORD_WEBHOOK_URL. Without it every call is a
no-op, so workflows keep running before the secret exists. Messages never include keys,
account numbers or order IDs.

    python -m zoh.notify bias --file journal/bias/2026-10-29.json
    python -m zoh.notify intraday --file journal/bias/intraday/2026-10-29.json
    python -m zoh.notify day [--date 2026-10-29]
"""
import argparse
import csv
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

from . import journal
from .strategy import ET

LIMIT = 1900  # Discord caps a message at 2000 characters


def chunks(text, limit=LIMIT):
    out, cur = [], ""
    for line in text.splitlines():
        while len(line) > limit:
            if cur:
                out.append(cur)
                cur = ""
            out.append(line[:limit])
            line = line[limit:]
        if len(cur) + len(line) + 1 > limit:
            out.append(cur)
            cur = ""
        cur += line + "\n"
    if cur.strip():
        out.append(cur)
    return out


def post(text):
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        print("notify: DISCORD_WEBHOOK_URL not set, skipped")
        return False
    for part in chunks(text):
        req = urllib.request.Request(url, data=json.dumps({"content": part}).encode(),
                                     headers={"Content-Type": "application/json",
                                              "User-Agent": "zero-or-hero"})
        try:
            urllib.request.urlopen(req, timeout=15).read()
        except Exception as e:  # never fail a workflow over a chat message
            print(f"notify: post failed: {e}")
            return False
    return True


def _short(text, n=160):
    text = (text or "").replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


def bias_message(bias):
    lines = [f"**盘前 {bias.get('date')}**  SPY: {bias.get('bias')}  (p_up {bias.get('p_up')})",
             _short(bias.get("summary"), 300)]
    s = bias.get("sniper")
    lines.append(f"狙击: {s['symbol']} {s.get('direction')} — {_short(s.get('catalyst'))}" if s and s.get("symbol")
                 else "狙击: 无")
    for o in bias.get("opportunities") or []:
        lines.append(f"• [{o.get('type')}] {o.get('symbol')} {o.get('direction')} — {_short(o.get('why'), 120)}"
                     f" ({o.get('action', 'none')})")
    rot = bias.get("rotation") or {}
    if rot.get("heating"):
        lines.append("升温: " + "; ".join(_short(h, 60) for h in rot["heating"][:4]))
    if rot.get("cooling"):
        lines.append("降温: " + "; ".join(_short(c, 60) for c in rot["cooling"][:4]))
    return "\n".join(lines)


def intraday_message(intraday):
    picks = intraday.get("picks") or []
    lines = [f"**盘中 {intraday.get('date')}**"]
    if picks:
        p = picks[-1]
        lines.append(f"{p.get('time')} {p.get('symbol')} {p.get('direction')} (信心 {p.get('confidence')}) — "
                     f"{_short(p.get('catalyst'), 300)}")
    for o in intraday.get("opportunities") or []:
        lines.append(f"• [{o.get('type')}] {o.get('symbol')} {o.get('direction')} — {_short(o.get('why'), 120)}")
    return "\n".join(lines)


def opportunities_message(data):
    lines = [f"**机会 {data.get('date')}**"]
    for o in data.get("opportunities") or []:
        lines.append(f"• {o.get('time', '10:00')} [{o.get('type')}] {o.get('symbol')} {o.get('direction')} — "
                     f"{_short(o.get('why'), 140)} ({o.get('action', 'none')})")
    return "\n".join(lines)


def _rows(path, day):
    if not path.exists():
        return []
    return [r for r in csv.DictReader(path.open()) if r.get("date") == day]


def day_message(day, root=None):
    root = Path(root or journal.JOURNAL_DIR)
    lines = [f"**收盘 {day}**"]
    eq = [r for r in csv.reader((root / "equity.csv").open())] if (root / "equity.csv").exists() else []
    today = [r for r in eq if r and r[0] == day]
    if today:
        lines.append(f"主账本 ${float(today[-1][1]):.2f}")
    led = _rows(root / "ledger_equity.csv", day)
    if led:
        lines.append("账本: " + ", ".join(f"{r.get('variant')} ${float(r.get('equity', 0)):.0f}" for r in led))
    trades = _rows(root / "trades.csv", day)
    real = [t for t in trades if t.get("mode") == "real"]
    if trades:
        pnl = sum(float(t.get("pnl") or 0) for t in real)
        lines.append(f"真实已实现 ${pnl:+.2f}")
        for t in trades:
            lines.append(f"• {t['mode']} {t['variant']} {t['contract']} {t['entry_price']}→{t['exit_price']} "
                         f"x{t['qty']} ${float(t.get('pnl') or 0):+.0f} ({t.get('exit_reason')})")
    for g in _rows(root / "grades.csv", day):
        if g.get("variant", "").startswith(("premarket", "intraday")):
            lines.append(f"判断 {g['variant']}: {g.get('verdict')}")
    opps = _rows(root / "opportunities.csv", day)
    if opps:
        lines.append("机会清单（进场到收盘，按方向计）:")
        for o in opps:
            lines.append(f"• [{o['type']}] {o['symbol']} {o['direction']} {o['time']}: "
                         f"{float(o['entry_close_pct']):+.2f}% (最好 {float(o['best_after_entry_pct']):+.2f}%, {o['action']})")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["bias", "intraday", "opportunities", "day"])
    ap.add_argument("--file")
    ap.add_argument("--date")
    args = ap.parse_args()
    day = args.date or datetime.now(ET).date().isoformat()
    if args.kind == "day":
        text = day_message(day)
    else:
        path = Path(args.file) if args.file else (
            journal.JOURNAL_DIR / "bias" / (f"intraday/{day}.json" if args.kind == "intraday" else f"{day}.json"))
        if not path.exists():
            print(f"notify: {path} missing")
            return
        data = json.loads(path.read_text())
        text = (bias_message(data) if args.kind == "bias" else
                intraday_message(data) if args.kind == "intraday" else opportunities_message(data))
    post(text)


if __name__ == "__main__":
    main()
