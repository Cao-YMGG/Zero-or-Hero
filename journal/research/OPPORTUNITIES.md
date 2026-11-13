# Opportunity types

Owner, 2026-10-29: "list every kind of opportunity". Each idea goes into the bias file's
`opportunities`, the intraday file or `journal/opportunities/<date>.json` with one of these `type`
keys; `zoh/research/opportunities.py` scores it after the close (journal/opportunities.csv:
stock move from the entry time to the close, signed by direction). A type that keeps scoring well
over the last 3 months (and without its best trade) earns a variant; most stay notes.

| key | 中文 | example | how we act now |
|---|---|---|---|
| analyst_upgrade | 盘前评级上调、缺口小 | MSFT 10-05 Melius | sniper (real) |
| contract_customer | 大合同 / 大客户表态 | AVGO 10-27 Anthropic SPV; V 10-29 Tencent | sniper (real) |
| peer_readthrough | 同行隔夜财报带动 | MU 10-28 on SK Hynix (missed) | sniper (real) |
| sector_intraday | 盘中板块催化 | AMAT 10-28; ORCL put 10-29 | intraday pick (real) |
| rotation_laggard | 轮动日里跌多了、坏消息出完被买回 | META 10-12, 10-29 | list only |
| financing_fade | 借钱 / 增发搞 AI、没给现金流计划 | MSFT 10-29 bond; META offering week | list only |
| sell_the_news | 降温板块里的利好高开 → 回落 | MSFT 10-29 (beat, -1.9% open to close) | list only |
| news_heating | 升温板块里的利好 → 延续 | LLY, MA, V 10-29 | sniper when not a report day |
| pre_earnings_drift | 财报前 10 天买预期 | META 10-13; RUNUP.md | sniper (never the day before / of) |
| beat_drift | 芯片 / AI 硬件大超预期后 20 天漂移 | the other Claude: +9% vs SPY, 30 events | list only |
| gapdown_rebound | 大盘股低开 >= 2% 反弹 | AMD dossier 58% | rebound_scanner (MWF) |
| selloff_pushback | 一次性坏消息大跌、卖方次日反驳 | WDC 10-03 | sniper |
| event_fade | 热门板块在自己的行业大会当天被卖 | optical into OCP 10-12 | list only (no sniper) |
| product_launch | 新产品 / 新模型 | META Muse Wonder 10-12 | sniper |
| investor_day | 投资者日 / 长期指引 | ORCL 10-28 +10% (missed) | intraday pick |
| ma_target / ma_acquirer | 收购：被收购方涨、收购方跌 | LITE / MRVL 10-29 | list only |
| open_drive | 开盘 30 分钟走出方向 | spy_open_drive, stock_open_drive | variants |
| macro_day | 宏观数据日 | GDP +3.4% 10-29, IWM +1.0% | list only |

Scoring since 2026-11-13 (owner: "the scoring could be better"; the record is rebuilt after every run in
journal/research/OPPORTUNITY_SCORES.md): each row is graded `paid` (the stock moved 1% or more the idea's way,
about what a same-day option needs), `right` (the right side, not enough) or `wrong`, and carries what SPY did
over the same minutes, so a put on a day everything fell gets no credit for the tape. A later mention of the
same stock and direction on the same day is a repeat and is not counted again. The workflow scores at about
15:48; a later run scores the row again to the real close (`final`). Use one of the keys above or one already in
the record (`analyst`, `company_news`, `sector_move`, `relative_weakness`, `relative_strength`, `sympathy`,
`earnings_reaction`, `put_mirror`): a new key starts a group of one. First read of the record (179 ideas, 12
sessions): no edge as a whole (54% right, 28% paid, +0.05% against SPY); rating changes lead (13 ideas, 54% paid,
+1.4% against SPY); ideas added at the intraday checks trail the pre-market ones (19% paid against 35%).

Evidence so far: journal/research/OPPORTUNITY_TESTS.md (daily bars), RUNUP.md, ANALYST.md,
the dossiers. Open questions: SUNDAY_TESTS.md items 29-33.
