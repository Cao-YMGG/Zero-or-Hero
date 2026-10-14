"""Build the GitHub Pages dashboard (site/index.html) from the journal and config.

    python -m zoh.site [--out site]
"""
import argparse
import json
from datetime import datetime
from html import escape
from pathlib import Path

from . import journal
from .review import leaderboard
from .strategy import ET, current_phase

START = 500.0
READY_FILLS = 30

CSS = """
:root { --bg:#f7f7f5; --card:#fff; --ink:#1d1d1f; --muted:#6b6b70; --line:#e3e3e0;
  --up:#1a7f4b; --down:#c0392b; --accent:#3557d4; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg:#121214; --card:#1c1c1f; --ink:#ececee; --muted:#9a9aa2; --line:#2e2e33;
  --up:#3ecf8e; --down:#ff6b5e; --accent:#7b96ff; } }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; }
main { max-width:960px; margin:0 auto; padding:24px 16px 48px; }
h1 { font-size:22px; margin:0 0 4px; } h2 { font-size:16px; margin:0 0 12px; }
.sub { color:var(--muted); font-size:13px; margin-bottom:20px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:16px; margin-bottom:16px; }
.tiles { display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:12px;
  margin-bottom:16px; }
.tile { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }
.tile .k { color:var(--muted); font-size:12px; } .tile .v { font-size:22px; font-weight:600; }
.up { color:var(--up); } .down { color:var(--down); } .muted { color:var(--muted); }
.scroll { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums; }
th, td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }
th { color:var(--muted); font-weight:500; }
td.n, th.n { text-align:right; }
.badge { display:inline-block; padding:1px 8px; border-radius:99px; font-size:12px;
  border:1px solid var(--line); }
.champ { border-color:var(--accent); color:var(--accent); }
ul { margin:0; padding-left:18px; } li { margin:2px 0; }
svg text { fill:var(--muted); font-size:11px; }
"""


# Plain-language names for the dashboard; unknown ids fall back to the id itself.
NAMES = {
    "rebound_scanner": ("低开反弹", "大盘股低开 ≥2%，15 分钟后买看涨，赌当天收复"),
    "rebound_scanner_wide": ("低开反弹·宽追踪", "同上，追踪止盈放得更宽（对照组）"),
    "rebound_scanner_any": ("低开反弹·每天", "同冠军规则，但周二周四也做（用最近到期日）"),
    "gapup_fade": ("高开回落", "大盘股高开 ≥2%，开盘 15 分钟后跌破开盘价，买看跌（每天，用最近到期日）"),
    "nvda_gapdown_put": ("NVDA 低开走弱", "NVDA 低开、10:00 仍在开盘价下方，买当天到期看跌（约 0.4 delta），3 倍止盈"),
    "catalyst_open": ("开盘狙击", "盘前选的有新消息的股票，09:31 开盘就买"),
    "catalyst_intraday": ("盘中狙击", "盘中检查发现的新消息股票，立刻买"),
    "catalyst_sniper": ("确认后狙击", "盘前选的股票，等它先涨 1% 再买（已停）"),
    "claude_bias": ("盘前判断 SPY", "按 Claude 盘前对 SPY 的看涨/看跌判断买"),
    "claude_confirm": ("盘前判断·确认", "盘前判断 + 开盘走势确认（已退役）"),
    "meta_follow2": ("META 跟势", "META 开盘 30 分钟比开盘价涨/跌 ≥2% 就跟（周一三五）"),
    "leader_follow": ("当日领涨股", "开盘 15 分钟后，比 SPY 多涨 ≥1.5% 最多的大盘股，买看涨"),
    "megacap_reclaim": ("大盘股收复", "大盘股开盘先跌 0.5% 再收回开盘价，买看涨（每天，没有当天到期就用最近到期日）"),
    "open_drive_run": ("开盘冲刺", "已退役"),
    "amd_gap_cheap_run": ("AMD 低开便宜看涨", "已退役"),
}
REASONS = {"trail": "追踪止盈", "time": "收盘前平仓", "expired": "到期作废",
           "take_profit": "止盈", "stop_loss": "止损", "time_noquote": "无报价按 0",
           "penny": "无买价 $0.01 卖出"}


def vname(vid):
    base, _, carried = vid.partition("@")
    name = NAMES.get(base, (base, ""))[0]
    return name + (f"（{carried[5:].replace('-', '/')} 留仓）" if carried else "")


def contract_label(occ):
    """'META261014C00775000' -> 'META 10/14 775 看涨'."""
    try:
        root, rest = occ[:-15], occ[-15:]
        strike = int(rest[7:]) / 1000
        kind = "看涨" if rest[6] == "C" else "看跌"
        return f"{root} {rest[2:4]}/{rest[4:6]} {strike:g} {kind}"
    except (ValueError, IndexError):
        return occ


def pct(x, digits=0):
    return f"{x * 100:+.{digits}f}%"


def money(x):
    return f"${x:,.0f}" if abs(x) >= 100 else f"${x:,.2f}"


def equity_chart(rows):
    points = [(r["date"], float(r["equity"])) for r in rows if r.get("equity")]
    if len(points) < 2:
        return '<p class="muted">资金曲线：至少两个交易日后显示。</p>'
    w, h, pad = 900, 220, 36
    values = [START] + [v for _, v in points]
    lo, hi = min(values) * 0.95, max(values) * 1.05
    def xy(i, v):
        x = pad + i * (w - 2 * pad) / (len(points) - 1)
        y = h - pad - (v - lo) / (hi - lo) * (h - 2 * pad)
        return f"{x:.1f},{y:.1f}"
    line = " ".join(xy(i, v) for i, (_, v) in enumerate(points))
    base_y = xy(0, START).split(",")[1]
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="资金曲线">'
            f'<line x1="{pad}" x2="{w - pad}" y1="{base_y}" y2="{base_y}" stroke="var(--line)" '
            f'stroke-dasharray="4 4"/>'
            f'<text x="{pad}" y="{float(base_y) - 4}">$500 起点</text>'
            f'<polyline points="{line}" fill="none" stroke="var(--accent)" stroke-width="2"/>'
            f'<text x="{pad}" y="{h - 8}">{escape(points[0][0])}</text>'
            f'<text x="{w - pad}" y="{h - 8}" text-anchor="end">{escape(points[-1][0])}</text>'
            f'</svg>')


def latest_bias():
    files = sorted(journal.BIAS_DIR.glob("20*.json"))
    return json.loads(files[-1].read_text()) if files else None


def bias_card(bias):
    if not bias:
        return '<div class="card"><h2>盘前判断</h2><p class="muted">还没有。</p></div>'
    call = {"call": "看涨 (call)", "put": "看跌 (put)", "none": "不做"}.get(bias.get("bias"), "?")
    rot = bias.get("rotation") or {}
    sniper = bias.get("sniper")
    parts = [f'<div class="card"><h2>盘前判断 · {escape(bias["date"])}</h2>',
             f'<p><b>SPY：{escape(call)}</b> <span class="muted">信心 '
             f'{bias.get("confidence", 0):.0%}</span><br>{escape(bias.get("summary", ""))}</p>']
    if sniper:
        parts.append(f'<p>狙击：<b>{escape(sniper["symbol"])} {escape(sniper["direction"])}</b> — '
                     f'{escape(sniper.get("catalyst", ""))}</p>')
    if rot:
        parts.append(f'<p>升温：{escape("；".join(rot.get("heating", [])))}<br>'
                     f'降温：{escape("；".join(rot.get("cooling", [])))}</p>')
    parts.append("</div>")
    return "".join(parts)


def leaderboard_card(config, trades):
    rows = []
    for r in leaderboard(config, trades):
        a = r["all"]
        champ = ' <span class="badge champ">冠军</span>' if r["id"] == config["champion"] else ""
        cls = "up" if a["avg"] > 0 else "down" if a["avg"] < 0 else "muted"
        stats = (f'<td class="n">{a["n"]}</td><td class="n">{a["win_rate"]:.0%}</td>'
                 f'<td class="n {cls}">{pct(a["avg"])}</td><td class="n">{pct(a["best"])}</td>'
                 ) if a["n"] else '<td class="n">0</td>' + '<td class="n muted">—</td>' * 3
        desc = NAMES.get(r["id"], ("", ""))[1]
        rows.append(f'<tr><td><b>{escape(vname(r["id"]))}</b>{champ}'
                    f'<div class="muted" style="font-size:12px;white-space:normal">{escape(desc)}</div>'
                    f'</td>{stats}</tr>')
    return ('<div class="card"><h2>各策略战绩（影子单，每笔平均收益）</h2>'
            '<p class="muted" style="font-size:12px">影子单 = 按实时报价模拟买卖、不花钱；'
            + ('只有冠军和开盘/盘中狙击会同时下真实单。' if config.get("champion_real", True)
             else '只有开盘/盘中狙击会同时下真实单（冠军暂时只记影子）。')
            + '每个策略至少 20 笔才看得出好坏。</p>'
            '<div class="scroll"><table>'
            '<tr><th>策略</th><th class="n">笔数</th><th class="n">赚钱比例</th>'
            '<th class="n">平均每笔</th><th class="n">最好一笔</th></tr>'
            + "".join(rows) + "</table></div></div>")


def _trade_rows(trades, with_money):
    rows = []
    for t in trades:
        p = float(t["pnl_pct"]) if t["pnl_pct"] else 0.0
        cls = "up" if p > 0 else "down" if p < 0 else "muted"
        held = t["entry_time"][:10] != t["exit_time"][:10]
        when = (f'{t["entry_time"][5:10].replace("-", "/")} {t["entry_time"][11:16]} → '
                f'{t["exit_time"][5:10].replace("-", "/") + " " if held else ""}{t["exit_time"][11:16]}')
        money_td = (f'<td class="n {cls}">{float(t["pnl"]):+,.0f}</td>' if with_money else "")
        rows.append(f'<tr><td>{escape(when)}</td><td>{escape(vname(t["variant"]))}</td>'
                    f'<td>{escape(contract_label(t["contract"]))}</td>'
                    f'<td class="n">{escape(t["entry_price"])} → {escape(t["exit_price"])}</td>'
                    f'<td class="n {cls}">{pct(p)}</td>{money_td}'
                    f'<td>{escape(REASONS.get(t["exit_reason"], t["exit_reason"]))}</td></tr>')
    return "".join(rows)


def trades_card(trades):
    real = [t for t in trades if t["mode"] == "real"][::-1]
    shadow = [t for t in trades if t["mode"] != "real"][-20:][::-1]
    if not trades:
        return '<div class="card"><h2>交易记录</h2><p class="muted">还没有交易。</p></div>'
    head = ('<tr><th>时间（美东）</th><th>策略</th><th>合约</th><th class="n">买 → 卖</th>'
            '<th class="n">收益</th>{money}<th>卖出原因</th></tr>')
    total = sum(float(t["pnl"] or 0) for t in real)
    return (f'<div class="card"><h2>真实交易（模拟盘真实下单）· 合计 '
            f'<span class="{"up" if total > 0 else "down"}">{total:+,.0f} 美元</span></h2>'
            '<div class="scroll"><table>' + head.format(money='<th class="n">盈亏 $</th>')
            + _trade_rows(real, True) + '</table></div>'
            '<p class="muted" style="font-size:12px">10/07 买入的两张 MRVL 周五看涨（-$289）'
            '因当时的 bug 没有记进交易表，合计未含（见 EVOLUTION.md 10/09）。'
            '10/13 起的真实单都按 $500 虚拟账本下单。</p></div>'
            '<div class="card"><h2>影子交易（最近 20 笔）</h2><div class="scroll"><table>'
            + head.format(money="") + _trade_rows(shadow, False) + '</table></div></div>')


def positions_card():
    """Today's open positions (shadow and real) from journal/state.json."""
    today = datetime.now(ET).date().isoformat()
    path = journal.STATE_PATH
    state = json.loads(path.read_text()) if path.exists() else {}
    if state.get("date") != today:
        return ""
    rows = []
    for vid, vs in sorted((state.get("variants") or {}).items()):
        pos = vs.get("shadow")
        if not pos:
            continue
        entry, last = float(pos["entry_price"]), pos.get("last")
        p = (float(last) / entry - 1) if last is not None and entry else None
        cls = "up" if p and p > 0 else "down" if p and p < 0 else "muted"
        real = vs.get("real")
        rows.append(f'<tr><td>{escape(vname(vid))}</td><td>{escape(contract_label(pos["contract"]))}</td>'
                    f'<td>{escape(pos["entry_time"][11:16] if pos["entry_time"][:10] == today else pos["entry_time"][5:16].replace("T", " ").replace("-", "/"))}</td>'
                    f'<td class="n">{entry:g}</td>'
                    f'<td class="n">{"—" if last is None else f"{float(last):g}"}</td>'
                    f'<td class="n {cls}">{pct(p) if p is not None else "—"}</td>'
                    f'<td class="n">{float(pos["peak"]):g}</td>'
                    f'<td>{"真实 " + str(real["qty"]) + " 张" if real else "影子"}</td></tr>')
    closed = sum(1 for vs in (state.get("variants") or {}).values() if vs.get("closed"))
    status = "今天已收盘" if state.get("done") else "交易中"
    if state.get("reset_needed"):
        status += " · 账户低于归零线，只记影子单，请在 Alpaca 后台重置模拟账户"
    body = ("<p class=\"muted\">现在没有持仓。</p>" if not rows else
            '<div class="scroll"><table><tr><th>策略</th><th>合约</th><th>买入时间</th>'
            '<th class="n">买入价</th><th class="n">现价（买价）</th><th class="n">收益</th>'
            '<th class="n">最高价</th><th>类型</th></tr>' + "".join(rows) + "</table></div>")
    return (f'<div class="card"><h2>今天的持仓 · {status}</h2>{body}'
            f'<p class="muted" style="font-size:12px">今天已平仓 {closed} 笔（见下方交易记录）。'
            f'交易时段每 30 分钟更新一次。</p></div>')


def evolution_card():
    path = journal.ROOT / "EVOLUTION.md"
    heads = [l[3:].strip() for l in path.read_text().splitlines() if l.startswith("## ")] \
        if path.exists() else []
    items = "".join(f"<li>{escape(h)}</li>" for h in heads[-6:][::-1])
    return f'<div class="card"><h2>最近的进化</h2><ul>{items}</ul></div>'


def _today_state():
    path = journal.JOURNAL_DIR / "state.json"
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def live_equity(state, trades):
    """During the day: today's starting equity (the virtual ledger's when it runs) plus real
    P&L booked today plus open real legs entered today, marked at their last bid. Carried
    legs from earlier days are left out (their value is already in the starting equity)."""
    if not state or state.get("done") or "equity_start" not in state:
        return None
    pnl = sum(float(t["pnl"] or 0) for t in trades
              if t["mode"] == "real" and t["date"] == state.get("date"))
    for vs in (state.get("variants") or {}).values():
        real, shadow = vs.get("real"), vs.get("shadow") or {}
        if real and shadow.get("last") is not None and real["entry_time"][:10] == state.get("date"):
            pnl += (float(shadow["last"]) - float(real["entry_price"])) * 100 * int(real["qty"])
    return float(state["equity_start"]) + pnl


def build(out):
    config = journal.load_config()
    trades = journal.read_trades()
    equity_rows = journal.read_equity()
    equity = float(equity_rows[-1]["equity"]) if equity_rows else START
    today_state = _today_state()
    live = live_equity(today_state, trades)
    if live is not None:
        equity = live
    phase = current_phase(config, equity)
    real = [t for t in trades if t["mode"] == "real" and t["variant"] == config["champion"]]
    change = equity / START - 1
    label = (f"账本资金 · 第 {today_state['generation']} 局" if today_state.get("generation")
             else "账户资金")
    tiles = [(label, money(equity), "up" if change > 0 else "down" if change < 0 else ""),
             ("相对 $500", pct(change), "up" if change > 0 else "down" if change < 0 else ""),
             ("阶段", f'{phase["name"]} · 每笔 {phase["risk_per_trade"]:.0%}', ""),
             ("冠军", vname(config["champion"]) + ("" if config.get("champion_real", True)
                                                  else "（只记影子）"), ""),
             ("实战检查：真实成交", f"{len(real)} / {READY_FILLS}", "")]
    tile_html = "".join(f'<div class="tile"><div class="k">{k}</div>'
                        f'<div class="v {c}" style="font-size:{18 if len(v) > 12 else 22}px">'
                        f'{escape(v)}</div></div>' for k, v, c in tiles)
    now = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>Zero or Hero</title><style>{CSS}</style></head>
<body><main>
<h1>Zero or Hero</h1>
<div class="sub">$500 末日期权自我进化实验 · Alpaca 模拟盘 · 更新于 {now}</div>
<div class="tiles">{tile_html}</div>
<div class="card"><h2>资金曲线</h2>{equity_chart(equity_rows)}</div>
{positions_card()}
{bias_card(latest_bias())}
{leaderboard_card(config, trades)}
{trades_card(trades)}
{evolution_card()}
<p class="muted" style="font-size:12px">模拟盘实验，不构成投资建议。</p>
</main></body></html>
"""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html)
    return out / "index.html"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site")
    print(build(parser.parse_args().out))


if __name__ == "__main__":
    main()
