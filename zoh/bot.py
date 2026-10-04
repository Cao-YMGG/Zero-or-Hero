"""Live 0DTE paper-trading loop.

Every variant in config/strategy.json trades in "shadow" mode (simulated fills on live
quotes: buy at the ask, mark and sell at the bid). The champion variant also sends real
orders to the Alpaca paper account. Results go to journal/ so the review step can compare
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
                       day_context, evaluate_signal, hhmm, parse_bar, parse_occ,
                       regular_session, round_limit, select_contract, years_to_close)

MAX_ENTRY_ATTEMPTS = 3
BIAS_RECHECK_SECONDS = 120


def now_et():
    return datetime.now(ET)


def log(msg):
    print(f"[{now_et():%H:%M:%S}] {msg}", flush=True)


def closed_bars(api, symbol, now):
    start = datetime.combine(now.date(), MARKET_OPEN, ET)
    bars = regular_session([parse_bar(b) for b in api.stock_bars(symbol, start, now)])
    return [b for b in bars if b["t"] + timedelta(minutes=1) <= now]


def previous_close(api, symbol, today):
    start = datetime.combine(today - timedelta(days=10), MARKET_OPEN, ET)
    daily = [parse_bar(b) for b in api.stock_bars(symbol, start, datetime.now(ET), "1Day")]
    prior = [b for b in daily if b["t"].date() < today]
    return prior[-1]["c"] if prior else None


def fetch_bias(day):
    """Claude's pre-market bias for `day`, from the checkout or freshly pushed to main."""
    path = journal.bias_path(day)
    if path.exists():
        return json.loads(path.read_text())
    rel = path.relative_to(journal.ROOT).as_posix()
    subprocess.run(["git", "fetch", "-q", "origin", "main"], timeout=60, check=False)
    shown = subprocess.run(["git", "show", f"origin/main:{rel}"], capture_output=True, text=True,
                           timeout=30, check=False)
    return json.loads(shown.stdout) if shown.returncode == 0 else None


def chain_candidates(api, underlying, expiry, kind, spot, now):
    snaps = api.option_chain(underlying, expiry, kind, round(spot * 0.97, 2),
                             round(spot * 1.03, 2))
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
        log(f"context: events={self.events.get(self.today.isoformat(), [])} "
            f"prev_close={self.prev_close}")

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

    # --- orders ----------------------------------------------------------

    def _order(self, symbol, qty, side, kind, tag, limit=None):
        order = {"symbol": symbol, "qty": str(qty), "side": side, "type": kind,
                 "time_in_force": "day",
                 "client_order_id": f"zoh-{self.today:%y%m%d}-{tag}-{systime.time():.0f}"}
        if limit is not None:
            order["limit_price"] = str(limit)
        log(f"ORDER {side} {qty} {symbol} {kind} {limit or ''}")
        filled = wait_for_fill(self.api, self.api.submit_order(**order))
        qty_filled = int(float(filled.get("filled_qty") or 0))
        price = float(filled["filled_avg_price"]) if qty_filled else None
        log(f"  -> {filled['status']} filled={qty_filled} @ {price}")
        return qty_filled, price

    # --- trade lifecycle ---------------------------------------------------

    def try_enter(self, variant, vstate, direction, spot, now):
        vstate["attempts"] = vstate.get("attempts", 0) + 1
        budget = self.state["equity_start"] * self.state["risk_per_trade"]
        candidates = chain_candidates(self.api, self.underlying, self.today, direction, spot, now)
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
        if variant["id"] == self.state["champion"] and not self.dry_run:
            filled, price = self._order(pick["symbol"], qty, "buy", "limit", "in",
                                        round_limit(pick["ask"]))
            if filled:
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
        ctx = day_context(self.today, self.events, self.prev_close,
                          bars[0]["o"] if bars else None, self.load_bias())
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
                reason = "time" if at_exit else check_exit(shadow["entry_price"],
                                                           shadow["peak"], bid, variant)
                if reason:
                    self.close(variant, vstate, bid, reason, now)
            elif (not vstate.get("entered") and not at_exit and bars
                  and vstate.get("attempts", 0) < MAX_ENTRY_ATTEMPTS
                  and now.time() <= hhmm(variant.get("entry_cutoff", "13:00"))):
                direction = evaluate_signal(bars, variant, ctx)
                if direction:
                    try:
                        self.try_enter(variant, vstate, direction, bars[-1]["c"], now)
                    except AlpacaError as e:
                        log(f"{variant['id']}: entry failed: {e}")

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
            log(f"GAME OVER: equity ${equity:.2f} < ${config['dead_equity']}")
            state["done"] = True
            journal.save_state(state)
            return
        journal.save_state(state)
    log(f"equity ${state['equity_start']:.2f} phase={state['phase']} "
        f"champion={state['champion']} until={until} exit={exit_at} dry_run={args.dry_run}")

    bot = Bot(api, config, state, args.dry_run, exit_at)
    first_bar_ready = datetime.combine(now.date(), MARKET_OPEN, ET) + timedelta(minutes=2)
    if now < first_bar_ready:
        systime.sleep((first_bar_ready - now).total_seconds())

    while True:
        now = now_et()
        try:
            bot.step(now)
        except (AlpacaError, OSError) as e:
            log(f"step failed: {e}")
        journal.save_state(state)
        if now.time() >= until:
            break
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
