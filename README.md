# Zero-or-Hero

以小博大的实验：**$500 模拟资金**（Alpaca Paper），先用 SPY 末日期权（0DTE）搏大，资金长大后自动切换到更稳的打法；系统根据自己的战绩不断进化。

> 只用模拟盘。不连真实账户，不动真钱。

## 规则

| 规则 | 内容 |
|---|---|
| 起始资金 | $500，一次性投入，亏完不补 |
| 归零线 | 净值 < $50 → GAME OVER，停止交易 |
| 品种 | SPY 当日到期期权，只买不卖（风险封顶为权利金） |
| 每天 | 冠军策略最多 1 笔真实（模拟盘）交易，15:45 ET 前全部平仓，不隔夜 |
| 仓位 | 按阶段决定单笔投入占净值比例（见下） |

### 阶段（按净值自动切换）

| 阶段 | 净值 | 单笔投入 | 思路 |
|---|---|---|---|
| zero-or-hero | < $2,000 | 30% | 高赔率，搏翻倍 |
| compounder | $2,000 – $10,000 | 10% | 守住战果，稳步复利 |
| preserve | ≥ $10,000 | 3% | 保本为主（策略待进化） |

## 怎么运转

```
每个交易日 (GitHub Actions: Trade)
 ├─ 所有变体都做「影子交易」：用实时报价模拟买在 ask、卖在 bid
 ├─ 冠军变体额外向 Alpaca 模拟盘真实下单
 ├─ 收盘后写入 journal/（trades.csv / equity.csv / REVIEW.md）
 └─ review：挑战者最近 20 笔明显优于冠军 → 自动晋升，记入 EVOLUTION.md

每周 (Claude 进化会话)
 └─ 读日志和回测 → 提出假设 → 新增/淘汰变体、调参数 → 记入 EVOLUTION.md
```

- `config/strategy.json` — 阶段、冠军、全部策略变体（进化主要改这里）
- `zoh/strategy.py` — 信号、出场、期权定价、选合约（实盘和回测共用）
- `zoh/bot.py` — 实盘循环；`zoh/backtest.py` — 历史回测；`zoh/review.py` — 评分与晋升；`zoh/check.py` — 诊断
- `journal/` — 所有交易记录、每日净值、回测报告、复盘
- `EVOLUTION.md` — 每一次策略变化的原因和证据

## 运行

本地需要环境变量 `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY`（Paper Key）。GitHub 上配在仓库 Secrets。

```bash
python -m unittest            # 单元测试
python -m zoh.check           # 账户、期权链、各变体信号
python -m zoh.backtest --days 365 --out journal/BACKTEST.md
python -m zoh.bot --dry-run   # 盘中运行，只做影子交易
python -m zoh.review
```
