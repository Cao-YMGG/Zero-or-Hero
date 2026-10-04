"""Diagnostics: account, market clock, live option chain and what each variant would do.

    python -m zoh.check
"""
from datetime import datetime, timedelta

from . import journal
from .alpaca import Alpaca
from .bot import chain_candidates
from .strategy import (ET, MARKET_OPEN, current_phase, evaluate_signal, parse_bar,
                       regular_session, select_contract)


def main():
    config = journal.load_config()
    api = Alpaca()
    acct = api.account()
    equity = float(acct["equity"])
    phase = current_phase(config, equity)
    print(f"account   status={acct['status']} equity=${equity:.2f} "
          f"buying_power=${float(acct['buying_power']):.2f} "
          f"options_level={acct.get('options_trading_level')}")
    print(f"phase     {phase['name']} risk/trade={phase['risk_per_trade']:.0%} "
          f"budget=${equity * phase['risk_per_trade']:.2f} champion={config['champion']}")
    print(f"positions {[(p['symbol'], p['qty']) for p in api.positions()]}")
    clock = api.clock()
    print(f"clock     open={clock['is_open']} next_open={clock['next_open']}")

    now = datetime.now(ET)
    sessions = api.calendar(now.date() - timedelta(days=7), now.date())
    today = now.date().isoformat()
    last = [s for s in sessions if s["date"] < today
            or (s["date"] == today and now.time() > MARKET_OPEN)][-1]
    day = datetime.fromisoformat(last["date"]).date()
    start = datetime.combine(day, MARKET_OPEN, ET)
    bars = regular_session([parse_bar(b) for b in api.stock_bars(
        config["underlying"], start, min(start + timedelta(hours=7), now - timedelta(minutes=16)))])
    print(f"\nreplay of {day}: {len(bars)} bars, open {bars[0]['o'] if bars else '-'} "
          f"close {bars[-1]['c'] if bars else '-'}")
    for variant in config["variants"]:
        hit = None
        for i in range(len(bars)):
            direction = evaluate_signal(bars[:i + 1], variant)
            if direction:
                hit = (bars[i]["t"] + timedelta(minutes=1), direction, bars[i]["c"])
                break
        print(f"  {variant['id']:14} " + (f"{hit[1]} at {hit[0]:%H:%M} spot {hit[2]:.2f}"
                                           if hit else "no signal"))

    expiry = datetime.fromisoformat(clock["next_open"]).date() if not clock["is_open"] \
        else now.date()
    spot = bars[-1]["c"] if bars else None
    if spot is None:
        return
    for kind in ("call", "put"):
        cands = chain_candidates(api, config["underlying"], expiry, kind, spot,
                                 datetime.combine(expiry, MARKET_OPEN, ET))
        cands.sort(key=lambda c: c["strike"])
        near = [c for c in cands if abs(c["strike"] - spot) <= spot * 0.01]
        print(f"\n{expiry} {kind}s near {spot:.2f} ({len(cands)} contracts in ±3%):")
        for c in near:
            print(f"  {c['symbol']} ask={c['ask']} bid={c['bid']} delta={c['delta']:+.2f} "
                  f"quote_time={c['quote_time']}")
        pick = select_contract(cands, 0.3, equity * phase["risk_per_trade"])
        print(f"  champion pick (delta 0.3, budget): {pick and pick['symbol']} "
              f"ask={pick and pick['ask']}")


if __name__ == "__main__":
    main()
