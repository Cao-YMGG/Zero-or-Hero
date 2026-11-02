"""Post short summaries to a Discord channel (owner, 2026-10-29).

The webhook URL lives only in the GitHub secret DISCORD_WEBHOOK_URL. Without it every call is a
no-op, so workflows keep running before the secret exists. Messages never include keys,
account numbers or order IDs.

    python -m zoh.notify bias --file journal/bias/2026-10-29.json
    python -m zoh.notify intraday --file journal/bias/intraday/2026-10-29.json
    python -m zoh.notify day [--date 2026-10-29]
    python -m zoh.notify check --file journal/checks/2026-11-02.json
"""
import argparse
import csv
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

from . import journal
from .strategy import ET, parse_occ

LIMIT = 1900  # Discord caps a message at 2000 characters
# One webhook per channel (journal/research: Discord channel plan, 2026-10-30); a channel without
# its own secret falls back to DISCORD_WEBHOOK_URL, and with neither nothing is sent.
CHANNELS = {"premarket": "DISCORD_WEBHOOK_PREMARKET", "intraday": "DISCORD_WEBHOOK_INTRADAY",
            "trades": "DISCORD_WEBHOOK_TRADES", "review": "DISCORD_WEBHOOK_REVIEW",
            "alerts": "DISCORD_WEBHOOK_ALERTS", "research": "DISCORD_WEBHOOK_RESEARCH",
            "opportunities": "DISCORD_WEBHOOK_OPPORTUNITIES"}
FALLBACK = "DISCORD_WEBHOOK_URL"
USERNAME = "Zero-or-Hero"


# The owner's own channel: anything without a webhook of its own (and no DISCORD_WEBHOOK_URL) is
# posted to #盘前判断 rather than dropped; until 2026-11-02 the close and the intraday picks were
# silently skipped because only the pre-market and opportunities webhooks existed.
HOME = "premarket"


def webhook(channel):
    return (os.environ.get(CHANNELS.get(channel, FALLBACK)) or os.environ.get(FALLBACK)
            or os.environ.get(CHANNELS[HOME]))


def has_own(channel):
    """True when the channel has its own webhook (not just the fallback)."""
    return bool(os.environ.get(CHANNELS.get(channel, "")))


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


# Plain Chinese for the owner (2026-11-02: "the Discord posts are unreadable"). Free text comes from
# the *_zh fields the routines write; the English fields are only a fallback.
DIRS = {"call": "看涨", "put": "看跌", "none": "不做"}
ACTIONS = {"real": "已下单", "shadow": "只记影子", "none": "只记录"}
VERDICTS = {"right": "对", "wrong": "错", "missed": "漏判", "open": "未定"}
CALLS = {"premarket_spy": "盘前 SPY", "premarket_sniper": "盘前狙击", "premarket_rotation": "盘前轮动",
         "intraday_pick": "盘中选股"}
TYPES = {"analyst_upgrade": "评级上调", "contract_customer": "大合同/大客户", "peer_readthrough": "同行带动",
         "sector_intraday": "盘中板块消息", "sector_move": "盘中板块消息", "rotation_laggard": "轮动补涨",
         "financing_fade": "借钱搞 AI 被抛", "sell_the_news": "利好出货", "news_heating": "热门板块利好",
         "pre_earnings_drift": "财报前买预期", "beat_drift": "大超预期后漂移", "gapdown_rebound": "低开反弹",
         "selloff_pushback": "大跌后卖方护盘", "event_fade": "行业大会当天被卖", "product_launch": "新产品",
         "investor_day": "投资者日", "ma_target": "被收购方", "ma_acquirer": "收购方", "open_drive": "开盘冲劲",
         "macro_day": "宏观数据日", "company_news": "公司消息", "intraday": "盘中选股"}
EXITS_CN = {"half": "3 倍卖一半", "trail": "跟踪止盈", "time": "收盘前卖出", "expired": "到期作废",
            "take_profit": "止盈", "stop_loss": "止损", "time_noquote": "无报价按 0"}


def _name(variant):
    from .site import NAMES
    return NAMES.get(variant, (variant,))[0]


def _contract(symbol):
    """'ORCL261030P00134000' -> 'ORCL 10-30 134 看跌'."""
    try:
        root, ymd, kind, strike = parse_occ(symbol)
    except (ValueError, IndexError):
        return symbol
    return f"{root} {ymd[2:4]}-{ymd[4:]} {strike:g} {DIRS.get(kind, kind)}"


def _dir(d):
    return DIRS.get(d or "none", d)


def _usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.0f}"


def opportunity_lines(items):
    return [f"{i}. {o.get('symbol')} {_dir(o.get('direction'))}｜{TYPES.get(o.get('type'), o.get('type'))}："
            f"{_short(o.get('why_zh') or o.get('why'), 120)}（{ACTIONS.get(o.get('action', 'none'), '只记录')}）"
            for i, o in enumerate(items or [], 1)]


def bias_message(bias, with_opportunities=True):
    zh = bias.get("zh") or {}
    p = bias.get("p_up")
    odds = f"（收盘高于开盘的概率 {float(p):.0%}）" if p is not None else ""
    lines = [f"**📋 盘前判断 {bias.get('date')}**",
             f"大盘 SPY：**{_dir(bias.get('bias'))}**{odds}",
             f"理由：{_short(zh.get('summary') or bias.get('summary'), 400)}"]
    s = bias.get("sniper")
    if zh.get("sniper"):
        lines.append(f"狙击：{_short(zh['sniper'], 300)}")
    elif s and s.get("symbol"):
        lines.append(f"狙击：**{s['symbol']} {_dir(s.get('direction'))}**，{_short(s.get('catalyst'), 200)}")
    else:
        lines.append("狙击：今天不选")
    rot = bias.get("rotation") or {}
    hot = zh.get("heating") or "、".join(_short(h, 40) for h in (rot.get("heating") or [])[:4])
    cold = zh.get("cooling") or "、".join(_short(c, 40) for c in (rot.get("cooling") or [])[:4])
    if hot:
        lines.append(f"资金流入：{hot}")
    if cold:
        lines.append(f"资金流出：{cold}")
    if with_opportunities and bias.get("opportunities"):
        lines += ["机会（只记录，收盘打分）："] + opportunity_lines(bias["opportunities"])
    return "\n".join(lines)


def intraday_message(intraday, with_opportunities=True):
    picks = intraday.get("picks") or []
    lines = [f"**⚡ 盘中选股 {intraday.get('date')}**"]
    if picks:
        p = picks[-1]
        lines.append(f"{p.get('time')} **{p.get('symbol')} {_dir(p.get('direction'))}**："
                     f"{_short(p.get('catalyst_zh') or p.get('catalyst'), 300)}")
    else:
        lines.append("这次不选")
    if with_opportunities and intraday.get("opportunities"):
        lines += ["机会（只记录，收盘打分）："] + opportunity_lines(intraday["opportunities"])
    return "\n".join(lines)


def opportunities_message(data, title="机会"):
    items = data.get("opportunities") or []
    if not items:
        return ""
    return "\n".join([f"**💡 {title} {data.get('date')}**（只记录不下单，收盘按股价打分）"]
                     + opportunity_lines(items))


def _rows(path, day):
    if not path.exists():
        return []
    return [r for r in csv.DictReader(path.open()) if r.get("date") == day]


def scored_lines(day, root=None):
    root = Path(root or journal.JOURNAL_DIR)
    out = []
    for o in _rows(root / "opportunities.csv", day):
        pct = float(o["entry_close_pct"])
        out.append(f"{'✅' if pct > 0 else '❌'} {o['symbol']} {_dir(o['direction'])}｜"
                   f"{TYPES.get(o['type'], o['type'])}：{o['time']} 起到收盘 {pct:+.2f}%"
                   f"（中间最好 {float(o['best_after_entry_pct']):+.2f}%）")
    return out


def day_message(day, root=None, with_opportunities=True):
    root = Path(root or journal.JOURNAL_DIR)
    lines = [f"**📊 收盘 {day}**"]
    trades = _rows(root / "trades.csv", day)
    real = [t for t in trades if t.get("mode") == "real"]
    shadow = [t for t in trades if t.get("mode") == "shadow"]
    if real:
        lines.append(f"今天平仓的真钱单（模拟盘，按买入价算）：**{_usd(sum(float(t.get('pnl') or 0) for t in real))}**")
    eq = [r for r in csv.reader((root / "equity.csv").open())] if (root / "equity.csv").exists() else []
    today = [r for r in eq if r and r[0] == day]
    if today:
        lines.append(f"主账本：${float(today[-1][1]):.2f}（起始 $500）")
    led = _rows(root / "ledger_equity.csv", day)
    if led:
        lines.append("单独账本：" + " · ".join(f"{_name(r.get('variant'))} ${float(r.get('equity', 0)):.0f}"
                                          for r in led))
    if real:
        lines.append("真钱交易：")
        for t in real:
            pnl = float(t.get("pnl") or 0)
            lines.append(f"{'✅' if pnl > 0 else '❌'} {_name(t['variant'])} {_contract(t['contract'])}："
                         f"{t['entry_price']} → {t['exit_price']}（{_usd(pnl)}，"
                         f"{EXITS_CN.get(t.get('exit_reason'), t.get('exit_reason'))}）")
    if shadow:
        lines.append("影子单（只记账，不下真钱）：")
        for t in shadow:
            pct = float(t.get("pnl_pct") or 0)
            lines.append(f"{'✅' if pct > 0 else '❌'} {_name(t['variant'])} {_contract(t['contract'])}：{pct:+.0%}")
    if not trades:
        lines.append("今天没有平仓的交易")
    calls = [g for g in _rows(root / "grades.csv", day) if g.get("variant") in CALLS]
    if calls:
        lines.append("判断：" + " · ".join(f"{CALLS[g['variant']]} {VERDICTS.get(g.get('verdict'), g.get('verdict'))}"
                                          for g in calls))
    scored = scored_lines(day, root)
    if with_opportunities and scored:
        lines += ["机会打分（从记录时间到收盘，按方向算）："] + scored
    return "\n".join(lines)


def check_message(data):
    """The post-market check the daily review writes (journal/checks/<date>.json, plain Chinese):
    were the morning calls right, did the real fills match the broker, what was learned."""
    text = (data.get("text") or "").strip()
    return f"**🔎 盘后核对 {data.get('date')}**\n{text}" if text else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["bias", "intraday", "opportunities", "day", "check", "test"])
    ap.add_argument("--file")
    ap.add_argument("--date")
    args = ap.parse_args()
    day = args.date or datetime.now(ET).date().isoformat()
    if args.kind == "test":
        test_all()
        return
    # With its own #机会清单 webhook, every opportunity list goes there; otherwise it rides along with
    # the pre-market, intraday or review message as before.
    split = has_own("opportunities")
    if args.kind == "day":
        post(day_message(day, with_opportunities=not split), "review")
        scored = scored_lines(day)
        if split and scored:
            post("\n".join([f"**💡 机会打分 {day}**（从记录时间到收盘，按方向算）"] + scored), "opportunities")
        return
    if args.kind == "check":
        path = Path(args.file) if args.file else journal.JOURNAL_DIR / "checks" / f"{day}.json"
        if path.exists():
            text = check_message(json.loads(path.read_text()))
            text and post(text, "review")
        return
    path = Path(args.file) if args.file else (
        journal.JOURNAL_DIR / "bias" / (f"intraday/{day}.json" if args.kind == "intraday" else f"{day}.json"))
    if not path.exists():
        print(f"notify: {path} missing")
        return
    data = json.loads(path.read_text())
    if args.kind == "bias":
        post(bias_message(data, with_opportunities=not split), "premarket")
        if split:
            text = opportunities_message(data, "盘前机会")
            text and post(text, "opportunities")
    elif args.kind == "intraday":
        post(intraday_message(data, with_opportunities=not split), "intraday")
        if split:
            text = opportunities_message(data, "盘中机会")
            text and post(text, "opportunities")
    else:
        text = opportunities_message(data, "复盘补充的机会")
        text and post(text, "opportunities" if split else "review")


if __name__ == "__main__":
    main()
