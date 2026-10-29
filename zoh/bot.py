"""Live 0DTE paper-trading loop.

Every variant in config/strategy.json trades in "shadow" mode (simulated fills on live
quotes: buy at the ask, mark and sell at the bid). The champion variant, and any variant
with "real_risk" (fraction of equity), also sends real orders to the Alpaca paper account. Results go to journal/ so the review step can compare
variants and promote a better one.

Run from GitHub Actions in two legs (each job is capped at 6 hours):
    python -m zoh.bot --until 12:45   # morning leg
    python -m zoh.bot                 # afternoon leg, runs to the exit time and closes out
"""
import argparse
import json
import subprocess
import time as systime
from datetime import datetime, timedelta

from . import journal, ledgers
from .alpaca import Alpaca, AlpacaError
from .strategy import (ET, MARKET_OPEN, bs_delta, contracts_for, current_phase, check_exit,
                       cross_assets, day_context, evaluate_signal, hhmm, same_day_expiry,
                       rank_by_move, reported_recently, reports_soon, sniper_pick, with_gap, parse_bar, parse_occ,
                       regular_session, round_limit, select_contract, years_to_close,
                       years_to_expiry, implied_vol)

MAX_ENTRY_ATTEMPTS = 3
BIAS_RECHECK_SECONDS = 120
PUBLISH_SECONDS = 30 * 60  # push the journal and rebuild the dashboard during the session


def now_et():
    return datetime.now(ET)


def log(msg):
    print(f"[{now_et():%H:%M:%S}] {msg}", flush=True)


REAL_ONE_CONTRACT_CAP = 0.5  # default; config "real_one_contract_cap" overrides

# One real position per theme per day: on 2026-10-07 three real orders were all chip calls and
# fell together. Names not listed are their own theme.
THEMES = {
    "semis": {"NVDA", "AMD", "INTC", "MU", "AVGO", "MRVL", "ARM", "TSM", "SMCI", "QCOM", "SKHY"},
    "optical": {"LITE", "CIEN", "COHR", "CRDO", "ANET"},
    "storage": {"WDC", "STX", "SNDK", "NTAP"},
    "internet": {"META", "GOOGL", "GOOG", "MSFT", "AMZN", "AAPL", "NFLX"},
    "index": {"SPY", "QQQ", "IWM"},
    "crypto": {"COIN", "HOOD", "MSTR"},
}


def theme_of(symbol):
    return next((name for name, members in THEMES.items() if symbol in members), symbol)


def real_contracts(equity, real_risk, ask, cap=REAL_ONE_CONTRACT_CAP):
    """Contracts for a real_risk variant. If its stake cannot buy one (a pricey stock's option),
    still buy one when that costs at most `cap` of the account: paper money, aggressive by design."""
    if not real_risk:
        return 0
    qty = contracts_for(equity * real_risk, ask)
    if qty == 0 and 0 < ask * 100 <= equity * cap:
        qty = 1
    return qty


def may_trade_real(state, underlying):
    """Real orders stop when the account needs a reset, and one theme gets at most one real
    position a day: two rules on the same news (or the same sector move) are one bet, so
    shadows still log both."""
    if state.get("reset_needed"):
        return False
    return all(theme_of(u) != theme_of(underlying) for u in state.get("real_underlyings", []))


def ledger_equity(ledger, account_equity):
    """The experiment's equity: the virtual ledger's when one is running, else the account's.
    (No new generation here: that only happens at the start of a day.)"""
    if ledger is None:
        return account_equity
    return ledger["base"] + account_equity - ledger["anchor"]


def ledger_can_start(ledger, account_equity, cfg):
    """A new ledger anchors on the account's equity, so only start it once the account has
    really been reset to a large balance (guards against stale keys on the old $50 account)."""
    return ledger is not None or account_equity >= cfg.get("min_account", 0)


def virtual_equity(ledger, account_equity, base, dead, today):
    """The experiment's own $base account inside a bigger paper account. Its equity is base plus
    the account's change since the generation began; below `dead` a new generation starts at
    base, so a wipe-out restarts without a manual reset. Returns (equity, ledger)."""
    if ledger is None:
        ledger = {"base": base, "generation": 1, "anchor": account_equity, "started": today,
                  "history": []}
    equity = ledger["base"] + account_equity - ledger["anchor"]
    if equity < dead:
        ledger["history"].append({"generation": ledger["generation"], "started": ledger["started"],
                                  "ended": today, "final_equity": round(equity, 2)})
        ledger.update(generation=ledger["generation"] + 1, anchor=account_equity, started=today)
        equity = ledger["base"]
    return equity, ledger


def carries(variant):
    """Hold a non-expiring option overnight? Only news picks (catalyst signal) by default:
    on real prices carried upgrade picks did better (+12% vs -13% sold at 15:45) and carried
    Tue/Thu rebounds much worse (-42% vs -13%). A variant can override with "carry"."""
    return variant.get("carry", variant.get("signal") == "catalyst")


def half_out(shadow, bid, variant):
    """True once, when the bid first reaches the variant's half_at multiple of the entry."""
    k = variant.get("half_at")
    return bool(k) and "banked" not in shadow and bid >= k * shadow["entry_price"]


def start_ledgers(config, today):
    """Roll the per-variant ledgers for today and fix each one's stake and pause state, like
    equity_start for the main ledger. Returns {variant: {"equity", "paused", "generation"}}."""
    cfg = config["ledgers"]
    book = ledgers.roll(ledgers.load(), cfg, today)
    ledgers.save(book)
    trades = journal.read_trades()
    out = {}
    for vid in cfg.get("variants", []):
        out[vid] = {"equity": ledgers.equity(book, vid, cfg), "generation": book[vid]["generation"],
                    "paused": ledgers.paused(trades, vid, cfg)}
        log(f"ledger {vid}: generation {out[vid]['generation']}, ${out[vid]['equity']:.2f}"
            + (" (paused)" if out[vid]["paused"] else ""))
    return out


def publish():
    """Refresh the headline feed, commit today's journal so far and ask GitHub to rebuild the
    dashboard. Best effort: a failure here never stops trading."""
    try:
        from . import news
        news.refresh(quiet=True)
    except Exception as e:  # noqa: BLE001 - news is optional
        log(f"news refresh failed: {e}")
    try:
        subprocess.run(["bash", ".github/commit-journal.sh", "intraday"], timeout=120, check=True,
                       cwd=journal.ROOT)
        subprocess.run(["gh", "workflow", "run", "pages.yml", "--ref", "main"], timeout=60,
                       check=False, cwd=journal.ROOT)
        log("published journal and requested a dashboard rebuild")
    except (OSError, subprocess.SubprocessError) as e:
        log(f"publish failed: {e}")


def closed_bars(api, symbol, now):
    start = datetime.combine(now.date(), MARKET_OPEN, ET)
    bars = regular_session([parse_bar(b) for b in api.stock_bars(symbol, start, now)])
    return [b for b in bars if b["t"] + timedelta(minutes=1) <= now]


def previous_close(api, symbol, today):
    start = datetime.combine(today - timedelta(days=10), MARKET_OPEN, ET)
    daily = [parse_bar(b) for b in api.stock_bars(symbol, start, datetime.now(ET), "1Day")]
    prior = [b for b in daily if b["t"].date() < today]
    return prior[-1]["c"] if prior else None


def fetch_bias(day, path=None, refresh=False):
    """Claude's pre-market bias for `day`, from the checkout or freshly pushed to main.

    With refresh, always read main (the intraday file can gain picks during the day)."""
    path = path or journal.bias_path(day)
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    rel = path.relative_to(journal.ROOT).as_posix()
    subprocess.run(["git", "fetch", "-q", "origin", "main"], timeout=60, check=False)
    shown = subprocess.run(["git", "show", f"origin/main:{rel}"], capture_output=True, text=True,
                           timeout=30, check=False)
    return json.loads(shown.stdout) if shown.returncode == 0 else None


PENNY = 0.01  # limit price for selling an expiring option that has no bid


STOCK_WIDTH = 0.15  # strike band for single-stock chains (fraction of spot)
ENTRY_RETRY_SLACK = 0.10  # an unfilled entry is retried once at a fresh ask up to 10% higher


def chain_candidates(api, underlying, expiry, kind, spot, now, width=0.03):
    snaps = api.option_chain(underlying, expiry, kind, round(spot * (1 - width), 2),
                             round(spot * (1 + width), 2))
    # Time to the contract's own expiry: with years-to-today's-close a Friday COIN 185C read on
    # Thursday (10-29) got delta 0.00 when the feed had no greeks, and leader_follow bought it.
    years = years_to_expiry(now, expiry)
    candidates = []
    for symbol, snap in snaps.items():
        quote = snap.get("latestQuote") or {}
        strike = parse_occ(symbol)[3]
        delta = (snap.get("greeks") or {}).get("delta")
        if delta is None:
            iv = snap.get("impliedVolatility")
            if not iv:
                bid, ask = quote.get("bp") or 0, quote.get("ap") or 0
                iv = implied_vol((bid + ask) / 2 if bid else ask, spot, strike, years, kind) or 0.16
            delta = bs_delta(spot, strike, years, iv, kind)
        candidates.append({"symbol": symbol, "strike": strike, "ask": quote.get("ap") or 0,
                           "bid": quote.get("bp") or 0, "delta": delta,
                           "quote_time": quote.get("t")})
    return candidates


def wait_for_fill(api, order, timeout=90):
    deadline = systime.time() + timeout
    while True:
        order = api.get_order(order["id"])
        if order["status"] in ("filled", "canceled", "expired", "rejected"):
            return order
        if systime.time() > deadline:
            try:
                api.cancel_order(order["id"])
            except AlpacaError:
                pass
            systime.sleep(2)
            return api.get_order(order["id"])
        systime.sleep(3)


class Bot:
    def __init__(self, api, config, state, dry_run, exit_at):
        self.api = api
        self.config = config
        self.state = state
        self.dry_run = dry_run
        self.exit_at = exit_at
        self.underlying = config["underlying"]
        self.today = datetime.fromisoformat(state["date"]).date()
        self.events = journal.load_events()
        self.earnings = journal.load_earnings()
        try:
            self.prev_close = previous_close(api, self.underlying, self.today)
        except AlpacaError as e:
            log(f"previous close unavailable: {e}")
            self.prev_close = None
        self.bias = None
        self.bias_checked_at = 0.0
        self.intraday = None
        self.intraday_checked_at = 0.0
        self.prev_closes = {}
        log(f"context: events={self.events.get(self.today.isoformat(), [])} "
            f"prev_close={self.prev_close}")

    def prev_close_of(self, symbol):
        if symbol not in self.prev_closes:
            try:
                self.prev_closes[symbol] = previous_close(self.api, symbol, self.today)
            except AlpacaError as e:
                log(f"previous close for {symbol} unavailable: {e}")
                self.prev_closes[symbol] = None
        return self.prev_closes[symbol]

    def load_bias(self):
        if self.bias is None and systime.time() - self.bias_checked_at >= BIAS_RECHECK_SECONDS:
            self.bias_checked_at = systime.time()
            try:
                self.bias = fetch_bias(self.today)
            except (OSError, ValueError, subprocess.SubprocessError) as e:
                log(f"bias fetch failed: {e}")
            if self.bias:
                log(f"claude bias: {self.bias.get('bias')} "
                    f"(confidence {self.bias.get('confidence')}): {self.bias.get('summary', '')}")
        return self.bias

    def load_intraday(self):
        """Claude's latest intraday pick ({"symbol", "direction", "catalyst", "time"}) or None."""
        if systime.time() - self.intraday_checked_at >= BIAS_RECHECK_SECONDS:
            self.intraday_checked_at = systime.time()
            try:
                data = fetch_bias(self.today, journal.intraday_path(self.today), refresh=True)
            except (OSError, ValueError, subprocess.SubprocessError) as e:
                log(f"intraday fetch failed: {e}")
                data = None
            picks = (data or {}).get("picks") or []
            latest = picks[-1] if picks else None
            if latest and latest != self.intraday:
                log(f"claude intraday pick: {latest}")
            self.intraday = latest
        return self.intraday

    # --- orders ----------------------------------------------------------

    def _order(self, symbol, qty, side, kind, tag, limit=None):
        order = {"symbol": symbol, "qty": str(qty), "side": side, "type": kind,
                 "time_in_force": "day",
                 "client_order_id": f"zoh-{self.today:%y%m%d}-{tag}-{systime.time():.0f}"}
        if limit is not None:
            order["limit_price"] = str(limit)
        log(f"ORDER {side} {qty} {symbol} {kind} {limit or ''}")
        try:
            submitted = self.api.submit_order(**order)
        except AlpacaError as e:  # e.g. not enough buying power with several real variants
            log(f"  -> rejected: {e}")
            return 0, None
        filled = wait_for_fill(self.api, submitted)
        qty_filled = int(float(filled.get("filled_qty") or 0))
        price = float(filled["filled_avg_price"]) if qty_filled else None
        log(f"  -> {filled['status']} filled={qty_filled} @ {price}")
        return qty_filled, price

    # --- trade lifecycle ---------------------------------------------------

    def nearest_chain(self, underlying, direction, spot, now, width):
        """Today's expiry if listed, else the next few calendar days (single stocks: Tue/Thu)."""
        for ahead in range(0, 5):
            expiry = self.today + timedelta(days=ahead)
            candidates = chain_candidates(self.api, underlying, expiry, direction, spot, now, width)
            if candidates:
                return candidates
        return []

    def try_enter(self, variant, vstate, direction, spot, now, underlying=None):
        vstate["attempts"] = vstate.get("attempts", 0) + 1
        # A spent account keeps scoring shadows at the start stake until it is reset.
        stake = (self.config["backtest"]["start_equity"] if self.state.get("reset_needed")
                 else self.state["equity_start"])
        budget = stake * self.state["risk_per_trade"]
        underlying = underlying or self.underlying
        if underlying != self.underlying and reports_soon(underlying, self.today,
                                                           getattr(self, "earnings", {})):
            log(f"{variant['id']}: no entry on {underlying}, it reports today or the next trading day")
            return
        if underlying == self.underlying:
            candidates = chain_candidates(self.api, underlying, self.today, direction, spot, now)
        else:
            # Single stocks look 15% either side: on high-IV names with a 3-4 day expiry the
            # whole +-8% band cost more than the budget, so the ORCL (10-27) and INTC (10-26)
            # intraday picks were skipped while cheaper, further-OTM strikes were listed.
            candidates = self.nearest_chain(underlying, direction, spot, now, width=STOCK_WIDTH)
        pick = select_contract(candidates, variant.get("target_delta", 0.3), budget)
        if not pick:
            log(f"{variant['id']}: {direction} signal but nothing affordable within ${budget:.0f}")
            return
        qty = contracts_for(budget, pick["ask"])
        log(f"{variant['id']}: {direction} signal @ {spot:.2f} -> {pick['symbol']} "
            f"bid={pick['bid']} ask={pick['ask']} delta={pick['delta']:.2f} qty={qty}")
        vstate["entered"] = True
        vstate["shadow"] = {"contract": pick["symbol"], "direction": direction,
                            "entry_time": now.isoformat(timespec="seconds"),
                            "entry_price": pick["ask"], "peak": pick["ask"], "qty": qty}
        # The champion trades the phase stake; a variant with real_risk also trades real
        # paper orders at that fraction of equity, to collect real fills sooner.
        champion_real = self.config.get("champion_real", True)
        own = (self.state.get("ledgers") or {}).get(variant["id"])
        if own is not None:
            # Its own $500 ledger: sized on that ledger, independent of the main one's themes.
            cfg = self.config["ledgers"]
            real_qty = 0 if own["paused"] else real_contracts(
                own["equity"], cfg.get("risk", 0.2), pick["ask"],
                cfg.get("one_contract_cap", REAL_ONE_CONTRACT_CAP))
            if own["paused"]:
                log(f"{variant['id']}: shadow only (its ledger is paused after a losing streak)")
        elif variant["id"] == self.state["champion"] and champion_real:
            real_qty = qty
        else:
            real_qty = real_contracts(
                self.state["equity_start"], variant.get("real_risk", 0), pick["ask"],
                self.config.get("real_one_contract_cap", REAL_ONE_CONTRACT_CAP))
        if real_qty and own is None and not may_trade_real(self.state, underlying):
            log(f"{variant['id']}: shadow only (real position in theme {theme_of(underlying)} "
                f"already today, or account needs a reset)")
            real_qty = 0
        if real_qty and not self.dry_run:
            filled, price = self._buy_entry(pick["symbol"], real_qty, pick["ask"])
            if filled:
                if own is None:
                    self.state.setdefault("real_underlyings", []).append(underlying)
                vstate["real"] = {"contract": pick["symbol"], "qty": filled, "underlying": underlying,
                                  "entry_price": price,
                                  "entry_time": now_et().isoformat(timespec="seconds")}

    def _buy_entry(self, symbol, qty, ask):
        """Limit buy at the ask; when that is unfilled after 90 s, re-quote once and pay the fresh
        ask if it is at most ENTRY_RETRY_SLACK above the first. The AMAT 445C (10-28) and ORCL
        128C (10-23) intraday picks went unfilled at the ask, 2 of 18 entries, with no retry."""
        filled, price = self._order(symbol, qty, "buy", "limit", "in", round_limit(ask))
        if filled:
            return filled, price
        try:
            snap = self.api.option_snapshots([symbol]).get(symbol) or {}
        except AlpacaError as e:
            log(f"  re-quote of {symbol} failed: {e}")
            return 0, None
        fresh = (snap.get("latestQuote") or {}).get("ap") or 0
        if not fresh or fresh > ask * (1 + ENTRY_RETRY_SLACK):
            log(f"  {symbol}: no retry, fresh ask {fresh} vs {ask}")
            return 0, None
        return self._order(symbol, qty, "buy", "limit", "in2", round_limit(fresh))

    def sell_half(self, variant, vstate, bid, now):
        """Take half off at the variant's half_at multiple; the rest keeps trailing. The shadow
        banks half the price (its final row records the blended exit); the real position sells
        half its contracts when it has two or more, or its only one when the variant sets
        single_take."""
        shadow = vstate["shadow"]
        shadow["banked"] = round(0.5 * bid, 4)
        log(f"{variant['id']}: half out of {shadow['contract']} @ {bid} "
            f"({bid / shadow['entry_price']:.1f}x)")
        real = vstate.get("real")
        if real and real["qty"] == 1 and variant.get("single_take") and not self.dry_run:
            # One contract cannot split: sell it all at the half_at multiple (spy_open_drive, owner
            # 2026-10-26: all out at 3x +101% / +78% / +54% vs held to the close +53% / +8% / -23%).
            filled, price, _ = self._sell_out(real["contract"], 1, "take")
            if filled:
                self._record(variant, "real", real, price, now_et(), "take", filled, shadow.get("peak"))
                vstate.pop("real")
        elif real and real["qty"] >= 2 and not self.dry_run:
            half = real["qty"] // 2
            filled, price, _ = self._sell_out(real["contract"], half, "half")
            if filled:
                self._record(variant, "real", real, price, now_et(), "half", filled, shadow.get("peak"))
                real["qty"] -= filled

    def close(self, variant, vstate, price, reason, now):
        shadow = vstate.pop("shadow")
        if "banked" in shadow:  # half was sold earlier at its half_at multiple
            price = round(shadow["banked"] + 0.5 * price, 4)
        log(f"{variant['id']}: exit {shadow['contract']} @ {price} ({reason})")
        self._record(variant, "shadow", shadow, price, now, reason, shadow["qty"], shadow.get("peak"))
        real = vstate.pop("real", None)
        if real:
            filled, fill_price, how = self._sell_out(real["contract"], real["qty"], "out")
            if filled:
                self._record(variant, "real", real, fill_price, now_et(),
                             reason if how == "market" else "penny", filled, shadow.get("peak"))
            elif (sold := self._already_sold(real)) is not None:
                # Another run (or an earlier attempt) already sold it: book that fill, not 0.
                log(f"!! {real['contract']} was already sold today at {sold}; booking that fill")
                self._record(variant, "real", real, sold, now_et(), reason, real["qty"], shadow.get("peak"))
            elif self._expires_today(real["contract"]):
                # Expiring with no bid and the penny limit unfilled: the contract expires
                # worthless, so book it at 0 rather than lose the trade from the journal.
                log(f"!! real exit for {real['contract']} did not fill; booked as expired at 0")
                self._record(variant, "real", real, 0.0, now_et(), "expired", real["qty"],
                             shadow.get("peak"))
            else:
                log(f"!! real exit for {real['contract']} did not fill; final sweep will retry")
        vstate["closed"] = True

    def _already_sold(self, real):
        """Average price of today's filled sells of this contract when the account no longer holds
        it (2026-10-19: a second run tried to close positions the first run had sold at 15:45 and
        booked them as expired at 0). None when it is still held or no fill is found."""
        try:
            if any(p.get("symbol") == real["contract"] for p in self.api.positions()):
                return None
            start = datetime.combine(self.today, MARKET_OPEN, ET) - timedelta(hours=1)
            fills = [o for o in self.api.orders(start) if o.get("symbol") == real["contract"]
                     and o.get("side") == "sell" and float(o.get("filled_qty") or 0) > 0]
        except AlpacaError as e:
            log(f"already-sold check failed: {e}")
            return None
        if not fills:
            return None
        qty = sum(float(o["filled_qty"]) for o in fills)
        return round(sum(float(o["filled_qty"]) * float(o["filled_avg_price"]) for o in fills) / qty, 4)

    def _expires_today(self, contract):
        return parse_occ(contract)[1] <= f"{self.today:%y%m%d}"

    def _sell_out(self, contract, qty, tag):
        """Market sell; if that fails on an expiring contract, try a $0.01 limit.

        With no bid Alpaca rejects market sells ("no available quote ... reenter with a
        limit"); a penny limit may be accepted and occasionally filled. Owner approved the
        experiment on 2026-10-12. Returns (qty filled, price, "market" | "penny").
        """
        filled, price = self._order(contract, qty, "sell", "market", tag)
        if filled or not self._expires_today(contract):
            return filled, price, "market"
        log(f"penny: market sell of {contract} failed; trying a $0.01 limit")
        filled, price = self._order(contract, qty, "sell", "limit", tag + "p", limit=PENNY)
        log(f"penny: {contract} {'filled' if filled else 'not filled'} at the $0.01 limit")
        return filled, price, "penny"

    def _record(self, variant, mode, pos, exit_price, now, reason, qty, peak=None):
        entry = pos["entry_price"]
        if mode == "real" and variant["id"] in ledgers.members(self.config):
            pnl = round((exit_price - entry) * 100 * qty, 2)
            book = ledgers.load()
            ledgers.roll(book, self.config["ledgers"], self.state["date"])
            ledgers.book(book, variant["id"], pnl)
            ledgers.save(book)
            ledgers.shift_main_anchor(pnl)
        journal.append_exit({"date": self.state["date"], "variant": variant["id"], "mode": mode,
                             "contract": pos["contract"], "entry_price": entry,
                             "exit_price": exit_price, "peak": peak if peak is not None else "",
                             "exit_reason": reason})
        journal.append_trade({
            "date": self.state["date"], "variant": variant["id"], "mode": mode,
            "contract": pos["contract"], "direction": parse_occ(pos["contract"])[2],
            "entry_time": pos["entry_time"], "entry_price": entry,
            "exit_time": now.isoformat(timespec="seconds"), "exit_price": exit_price,
            "qty": qty, "pnl": round((exit_price - entry) * 100 * qty, 2),
            "pnl_pct": round(exit_price / entry - 1, 4) if entry else "",
            "exit_reason": reason, "phase": self.state["phase"],
            "equity_before": self.state["equity_start"],
        })

    # --- main loop -----------------------------------------------------------

    def step(self, now):
        bars = closed_bars(self.api, self.underlying, now)
        cross = {sym: closed_bars(self.api, sym, now) for sym in cross_assets(self.config["variants"])}
        ctx = day_context(self.today, self.events, self.prev_close,
                          bars[0]["o"] if bars else None, self.load_bias(), cross)
        pick = sniper_pick(ctx)
        pick_bars = []
        own_bars = {}
        if pick and any(v["signal"] == "catalyst" for v in self.config["variants"]):
            try:
                pick_bars = closed_bars(self.api, pick["symbol"], now)
            except AlpacaError as e:
                log(f"sniper bars for {pick['symbol']} failed: {e}")
        intraday, intraday_bars, intraday_ctx = None, [], ctx
        if any(v.get("source") == "intraday" for v in self.config["variants"]):
            intraday = self.load_intraday()
            if intraday and intraday.get("symbol"):
                try:
                    intraday_bars = closed_bars(self.api, intraday["symbol"], now)
                except AlpacaError as e:
                    log(f"intraday bars for {intraday['symbol']} failed: {e}")
                intraday_ctx = {**ctx, "bias": {"sniper": intraday}}
        variants = self.config["variants"]
        vstates = self.state["variants"]
        open_symbols = [vs["shadow"]["contract"] for vs in vstates.values() if vs.get("shadow")]
        snaps = self.api.option_snapshots(open_symbols)
        at_exit = now.time() >= self.exit_at

        # Positions carried over from an earlier day sit under their own key ("<id>@<date>",
        # with "of" naming the variant), so the variant itself can still trade today.
        by_id = {v["id"]: v for v in variants}
        pairs = [(v, vstates.setdefault(v["id"], {})) for v in variants]
        pairs += [(by_id[vs["of"]], vs) for vs in list(vstates.values()) if vs.get("of") in by_id]
        for variant, vstate in pairs:
            shadow = vstate.get("shadow")
            if shadow:
                # A news pick that does not expire today is held overnight (trail still applies)
                # and closes at the exit time of its expiry day; every other variant sells at the
                # exit time anyway (journal/research/EXITS.md: carried rebounds -42% vs -13%).
                # Nothing is carried into the underlying's report (today or next trading day).
                root, expiry = parse_occ(shadow["contract"])[:2]
                expires_today = expiry <= f"{self.today:%y%m%d}"
                closes_today = (expires_today or not carries(variant)
                                or reports_soon(root, self.today, self.earnings))
                if at_exit and not closes_today:
                    vstate["hold"] = True
                quote = (snaps.get(shadow["contract"]) or {}).get("latestQuote") or {}
                bid = quote.get("bp")
                if bid is None:
                    if at_exit and closes_today:
                        self.close(variant, vstate, 0.0, "time_noquote", now)
                    continue
                shadow["peak"] = max(shadow["peak"], bid)
                shadow["last"], shadow["last_time"] = bid, now.isoformat(timespec="seconds")
                if not at_exit and half_out(shadow, bid, variant):
                    self.sell_half(variant, vstate, bid, now)
                if at_exit:
                    reason = "time" if closes_today else None
                else:
                    reason = check_exit(shadow["entry_price"], shadow["peak"], bid, variant,
                                        banked="banked" in shadow)
                if reason:
                    self.close(variant, vstate, bid, reason, now)
            elif (not vstate.get("entered") and not at_exit and bars
                  and vstate.get("attempts", 0) < MAX_ENTRY_ATTEMPTS
                  and now.time() <= hhmm(variant.get("entry_cutoff", "13:00"))):
                if variant.get("source") == "intraday":
                    candidates = ([(intraday["symbol"], intraday_bars, intraday_ctx)]
                                  if intraday and intraday.get("symbol") else [])
                elif variant["signal"] == "catalyst":
                    candidates = [(pick["symbol"], pick_bars, ctx)] if pick else []
                else:
                    # fixed single stock, a scanner universe, or the main underlying
                    symbols = variant.get("universe") or (
                        [variant["underlying"]] if variant.get("underlying") else [])
                    candidates = []
                    for sym in symbols:
                        if (variant.get("universe") and not variant.get("any_expiry")
                                and not same_day_expiry(sym, self.today.weekday())):
                            continue
                        if variant.get("skip_after_report_days") is not None and reported_recently(
                                sym, self.today, getattr(self, "earnings", {}),
                                variant["skip_after_report_days"]):
                            continue
                        # No new position into a print (COIN 10-29: leader_follow bought a call on
                        # its report day at earnings-inflated prices).
                        if reports_soon(sym, self.today, getattr(self, "earnings", {})):
                            continue
                        if sym not in own_bars:
                            try:
                                own_bars[sym] = closed_bars(self.api, sym, now)
                            except AlpacaError as e:
                                log(f"{sym} bars failed: {e}")
                                own_bars[sym] = []
                        sb = own_bars[sym]
                        their_ctx = with_gap(ctx, self.prev_close_of(sym), sb[0]["o"] if sb else None)
                        if bars:
                            their_ctx["index_ret"] = bars[-1]["c"] / bars[0]["o"] - 1
                        candidates.append((sym, sb, their_ctx))
                    if variant.get("pick") == "strongest":
                        candidates = rank_by_move(candidates, variant.get("sides"))
                    if not symbols:
                        candidates = [(None, bars, ctx)]
                for sym, their_bars, their_ctx in candidates:
                    direction = evaluate_signal(their_bars, variant, their_ctx) if their_bars else None
                    if direction:
                        try:
                            self.try_enter(variant, vstate, direction, their_bars[-1]["c"], now, sym)
                        except AlpacaError as e:
                            log(f"{variant['id']}: entry failed on {sym}: {e}")
                        break

    def sweep(self):
        """Flatten every option position expiring today, tracked or not."""
        expiry = f"{self.today:%y%m%d}"
        for pos in self.api.positions():
            if pos.get("asset_class") == "us_option" and parse_occ(pos["symbol"])[1] == expiry:
                qty = abs(int(float(pos["qty"])))
                if qty and not self.dry_run:
                    log(f"sweep: closing {qty} {pos['symbol']}")
                    self._sell_out(pos["symbol"], qty, "sweep")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--until", help="stop this leg at HH:MM ET (default: exit time)")
    parser.add_argument("--dry-run", action="store_true", help="shadow trades only")
    parser.add_argument("--publish", action="store_true",
                        help="push the journal every 30 minutes and rebuild the dashboard")
    args = parser.parse_args()

    config = journal.load_config()
    api = Alpaca()
    now = now_et()
    if now.time() < hhmm("08:30"):
        log("before 08:30 ET; the later scheduled run handles today")
        return
    session = api.calendar(now.date(), now.date())
    if not session or session[0]["date"] != now.date().isoformat():
        log("market closed today")
        return
    close_time = hhmm(session[0]["close"])
    exit_at = min(hhmm(config["exit_time"]),
                  (datetime.combine(now.date(), close_time) - timedelta(minutes=15)).time())
    until = min(hhmm(args.until), exit_at) if args.until else exit_at

    state = journal.load_state(now.date())
    if state["done"]:
        log("today already finished")
        return
    if "equity_start" not in state:
        equity = float(api.account()["equity"])
        ledger = journal.load_ledger() if config.get("ledger") else None
        if config.get("ledger") and not ledger_can_start(ledger, equity, config["ledger"]):
            log(f"virtual ledger not started: account ${equity:.2f} is below "
                f"${config['ledger']['min_account']:.0f} (not reset yet, or stale API keys)")
        elif config.get("ledger"):
            equity, ledger = virtual_equity(ledger, equity, config["ledger"]["base"],
                                            config["dead_equity"], now.date().isoformat())
            journal.save_ledger(ledger)
            state["generation"] = ledger["generation"]
            log(f"virtual ledger: generation {ledger['generation']}, equity ${equity:.2f}")
        phase = current_phase(config, equity)
        state.update({"equity_start": equity, "phase": phase["name"],
                      "risk_per_trade": phase["risk_per_trade"],
                      "champion": phase.get("champion", config["champion"])})
        if equity < config["dead_equity"]:
            # Keep collecting shadow data; real orders wait for the owner to reset the account.
            log(f"RESET NEEDED: equity ${equity:.2f} < ${config['dead_equity']}; shadow only today")
            state["reset_needed"] = True
        if config.get("ledgers"):
            state["ledgers"] = start_ledgers(config, now.date().isoformat())
        journal.save_state(state)
    log(f"equity ${state['equity_start']:.2f} phase={state['phase']} "
        f"champion={state['champion']} until={until} exit={exit_at} dry_run={args.dry_run}")

    bot = Bot(api, config, state, args.dry_run, exit_at)
    first_bar_ready = datetime.combine(now.date(), MARKET_OPEN, ET) + timedelta(minutes=2)
    if now < first_bar_ready:
        systime.sleep((first_bar_ready - now).total_seconds())

    last_publish = systime.time()
    while True:
        now = now_et()
        try:
            bot.step(now)
        except (AlpacaError, OSError) as e:
            log(f"step failed: {e}")
        journal.save_state(state)
        if now.time() >= until:
            break
        if args.publish and systime.time() - last_publish >= PUBLISH_SECONDS:
            last_publish = systime.time()
            publish()
        systime.sleep(config["poll_seconds"])

    if until >= exit_at:
        bot.sweep()
        state["done"] = True
        account = float(api.account()["equity"])
        ledger = journal.load_ledger() if config.get("ledger") and state.get("generation") else None
        equity = ledger_equity(ledger, account)
        journal.record_equity({"date": state["date"], "equity": round(equity, 2),
                               "phase": state["phase"], "champion": state["champion"]})
        log(f"day done, equity ${equity:.2f}" + (f" (account ${account:.2f})" if ledger else ""))
        if config.get("ledgers"):
            ledgers.record_equity(ledgers.load(), config["ledgers"], state["date"],
                                  {v for v, s in (state.get("ledgers") or {}).items() if s["paused"]})
    journal.save_state(state)


if __name__ == "__main__":
    main()
