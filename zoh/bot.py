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

from . import journal
from .alpaca import Alpaca, AlpacaError
from .strategy import (ET, MARKET_OPEN, bs_delta, contracts_for, current_phase, check_exit,
                       cross_assets, day_context, evaluate_signal, hhmm, same_day_expiry,
                       sniper_pick, with_gap, parse_bar, parse_occ,
                       regular_session, round_limit, select_contract, years_to_close)

MAX_ENTRY_ATTEMPTS = 3
BIAS_RECHECK_SECONDS = 120
PUBLISH_SECONDS = 30 * 60  # push the journal and rebuild the dashboard during the session


def now_et():
    return datetime.now(ET)


def log(msg):
    print(f"[{now_et():%H:%M:%S}] {msg}", flush=True)


REAL_ONE_CONTRACT_CAP = 0.5  # with real_risk, buy one contract if it costs <= 50% of equity


def real_contracts(equity, real_risk, ask):
    """Contracts for a real_risk variant. If its stake cannot buy one (a pricey stock's option),
    still buy one when that costs at most half the account: paper money, aggressive by design."""
    if not real_risk:
        return 0
    qty = contracts_for(equity * real_risk, ask)
    if qty == 0 and 0 < ask * 100 <= equity * REAL_ONE_CONTRACT_CAP:
        qty = 1
    return qty


def may_trade_real(state, underlying):
    """Real orders stop when the account needs a reset, and one stock gets at most one real
    position a day: two rules on the same news are one bet, so shadows still log both."""
    return not state.get("reset_needed") and underlying not in state.get("real_underlyings", [])


def publish():
    """Commit today's journal so far and ask GitHub to rebuild the dashboard. Best effort."""
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


def chain_candidates(api, underlying, expiry, kind, spot, now, width=0.03):
    snaps = api.option_chain(underlying, expiry, kind, round(spot * (1 - width), 2),
                             round(spot * (1 + width), 2))
    years = years_to_close(now)
    candidates = []
    for symbol, snap in snaps.items():
        quote = snap.get("latestQuote") or {}
        strike = parse_occ(symbol)[3]
        delta = (snap.get("greeks") or {}).get("delta")
        if delta is None:
            delta = bs_delta(spot, strike, years, snap.get("impliedVolatility") or 0.16, kind)
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
        if underlying == self.underlying:
            candidates = chain_candidates(self.api, underlying, self.today, direction, spot, now)
        else:
            candidates = self.nearest_chain(underlying, direction, spot, now, width=0.08)
        pick = select_contract(candidates, variant.get("target_delta", 0.3), budget)
        if not pick:
            log(f"{variant['id']}: {direction} signal but nothing affordable within ${budget:.0f}")
            return
        qty = contracts_for(budget, pick["ask"])
        log(f"{variant['id']}: {direction} signal @ {spot:.2f} -> {pick['symbol']} "
            f"ask={pick['ask']} delta={pick['delta']:.2f} qty={qty}")
        vstate["entered"] = True
        vstate["shadow"] = {"contract": pick["symbol"], "direction": direction,
                            "entry_time": now.isoformat(timespec="seconds"),
                            "entry_price": pick["ask"], "peak": pick["ask"], "qty": qty}
        # The champion trades the phase stake; a variant with real_risk also trades real
        # paper orders at that fraction of equity, to collect real fills sooner.
        real_qty = qty if variant["id"] == self.state["champion"] else real_contracts(
            self.state["equity_start"], variant.get("real_risk", 0), pick["ask"])
        if real_qty and not may_trade_real(self.state, underlying):
            log(f"{variant['id']}: shadow only (real position on {underlying} already today "
                f"or account needs a reset)")
            real_qty = 0
        if real_qty and not self.dry_run:
            filled, price = self._order(pick["symbol"], real_qty, "buy", "limit", "in",
                                        round_limit(pick["ask"]))
            if filled:
                self.state.setdefault("real_underlyings", []).append(underlying)
                vstate["real"] = {"contract": pick["symbol"], "qty": filled,
                                  "entry_price": price,
                                  "entry_time": now_et().isoformat(timespec="seconds")}

    def close(self, variant, vstate, price, reason, now):
        shadow = vstate.pop("shadow")
        log(f"{variant['id']}: exit {shadow['contract']} @ {price} ({reason})")
        self._record(variant, "shadow", shadow, price, now, reason, shadow["qty"])
        real = vstate.pop("real", None)
        if real:
            filled, fill_price = self._order(real["contract"], real["qty"], "sell", "market", "out")
            if filled:
                self._record(variant, "real", real, fill_price, now_et(), reason, filled)
            else:
                log(f"!! real exit for {real['contract']} did not fill; final sweep will retry")
        vstate["closed"] = True

    def _record(self, variant, mode, pos, exit_price, now, reason, qty):
        entry = pos["entry_price"]
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

        for variant in variants:
            vstate = vstates.setdefault(variant["id"], {})
            shadow = vstate.get("shadow")
            if shadow:
                quote = (snaps.get(shadow["contract"]) or {}).get("latestQuote") or {}
                bid = quote.get("bp")
                if bid is None:
                    if at_exit:
                        self.close(variant, vstate, 0.0, "time_noquote", now)
                    continue
                shadow["peak"] = max(shadow["peak"], bid)
                shadow["last"], shadow["last_time"] = bid, now.isoformat(timespec="seconds")
                reason = "time" if at_exit else check_exit(shadow["entry_price"],
                                                           shadow["peak"], bid, variant)
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
                        if variant.get("universe") and not same_day_expiry(sym, self.today.weekday()):
                            continue
                        if sym not in own_bars:
                            try:
                                own_bars[sym] = closed_bars(self.api, sym, now)
                            except AlpacaError as e:
                                log(f"{sym} bars failed: {e}")
                                own_bars[sym] = []
                        sb = own_bars[sym]
                        candidates.append((sym, sb, with_gap(ctx, self.prev_close_of(sym),
                                                             sb[0]["o"] if sb else None)))
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
                    self._order(pos["symbol"], qty, "sell", "market", "sweep")


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
        phase = current_phase(config, equity)
        state.update({"equity_start": equity, "phase": phase["name"],
                      "risk_per_trade": phase["risk_per_trade"],
                      "champion": phase.get("champion", config["champion"])})
        if equity < config["dead_equity"]:
            # Keep collecting shadow data; real orders wait for the owner to reset the account.
            log(f"RESET NEEDED: equity ${equity:.2f} < ${config['dead_equity']}; shadow only today")
            state["reset_needed"] = True
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
        equity = float(api.account()["equity"])
        journal.record_equity({"date": state["date"], "equity": equity, "phase": state["phase"],
                               "champion": state["champion"]})
        log(f"day done, equity ${equity:.2f}")
    journal.save_state(state)


if __name__ == "__main__":
    main()
