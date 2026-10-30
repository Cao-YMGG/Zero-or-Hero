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
# One webhook per channel (journal/research: Discord channel plan, 2026-10-30); a channel without
# its own secret falls back to DISCORD_WEBHOOK_URL, and with neither nothing is sent.
CHANNELS = {"premarket": "DISCORD_WEBHOOK_PREMARKET", "intraday": "DISCORD_WEBHOOK_INTRADAY",
            "trades": "DISCORD_WEBHOOK_TRADES", "review": "DISCORD_WEBHOOK_REVIEW",
            "alerts": "DISCORD_WEBHOOK_ALERTS", "research": "DISCORD_WEBHOOK_RESEARCH"}
FALLBACK = "DISCORD_WEBHOOK_URL"
USERNAME = "Zero-or-Hero"


def webhook(channel):
    return os.environ.get(CHANNELS.get(channel, FALLBACK)) or os.environ.get(FALLBACK)


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


def post(text, channel="review"):
    url = webhook(channel)
    if not url:
        print(f"notify: no webhook for {channel} ({CHANNELS.get(channel, FALLBACK)} or {FALLBACK}), skipped")
        return False
    for part in chunks(text):
        req = urllib.request.Request(url, data=json.dumps({"content": part, "username": USERNAME}).encode(),
                                     headers={"Content-Type": "application/json",
                                              "User-Agent": "zero-or-hero"})
        try:
            urllib.request.urlopen(req, timeout=15).read()
        except Exception as e:  # never fail a workflow over a chat message (the URL is never printed)
            print(f"notify: post to {channel} failed: {type(e).__name__} {getattr(e, 'code', '')}")
            return False
    print(f"notify: posted to {channel}")
    return True


def test_all():
    """One test message per configured channel; reports which secrets exist, never their values."""
    found = {c: bool(os.environ.get(s)) for c, s in CHANNELS.items()}
    print("notify: secrets present: " + ", ".join(f"{CHANNELS[c]}={'yes' if v else 'no'}" for c, v in found.items())
          + f", {FALLBACK}={'yes' if os.environ.get(FALLBACK) else 'no'}")
    for channel, present in found.items():
        if present:
            post(f"测试：Zero-or-Hero 的 #{channel} 频道已接通（{datetime.now(ET):%Y-%m-%d %H:%M} ET）。", channel)
    if os.environ.get(FALLBACK):
        post(f"测试：备用频道已接通，没配专用 webhook 的消息会发到这里（{datetime.now(ET):%H:%M} ET）。", "fallback")


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
    ap.add_argument("kind", choices=["bias", "intraday", "opportunities", "day", "test"])
    ap.add_argument("--file")
    ap.add_argument("--date")
    args = ap.parse_args()
    day = args.date or datetime.now(ET).date().isoformat()
    if args.kind == "test":
        test_all()
        return
    if args.kind == "day":
        text, channel = day_message(day), "review"
    else:
        path = Path(args.file) if args.file else (
            journal.JOURNAL_DIR / "bias" / (f"intraday/{day}.json" if args.kind == "intraday" else f"{day}.json"))
        if not path.exists():
            print(f"notify: {path} missing")
            return
        data = json.loads(path.read_text())
        text = (bias_message(data) if args.kind == "bias" else
                intraday_message(data) if args.kind == "intraday" else opportunities_message(data))
        channel = {"bias": "premarket", "intraday": "intraday", "opportunities": "review"}[args.kind]
    post(text, channel)


if __name__ == "__main__":
    main()
