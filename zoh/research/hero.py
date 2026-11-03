"""Hero replay (owner, 2026-11-03): what our catalyst picks would have done traded the way the other
Claude's rule ledgers trade, the whole ledger on one contract, no trailing exit, sold at 15:45, in
$500 rounds counted as a hero (>= $5,000) or a zero (<= $50).

Inputs: journal/research/snipers.json (python -m zoh.research.snipers: real option minute bars for
every pre-market sniper and intraday pick since 2026-10-01, costs 10% each way), journal/trades.csv
(the real catalyst_open / catalyst_intraday fills, and the hero shadows' own trades since 11-03) and,
for real fills that were trailed out early, the contract's 15:45 price from Alpaca.

    python -m zoh.research.hero          # writes journal/research/HERO.md and hero.json
"""
import csv
import json
from datetime import datetime, timedelta

from .. import journal
from ..alpaca import Alpaca, AlpacaError
from ..realopt import option_minutes
from ..strategy import hhmm
from .exits import bid

OUT = journal.ROOT / "journal" / "research"
SLIP = 0.10
START, ZERO, HERO = 500.0, 50.0, 5000.0
LIVE, HOLD = "half3_arm1.5", "hold"  # live exit of the catalyst variants; the hero shadows' exit
DELTA = {"sniper": "d0.10", "intraday": "d0.20"}  # catalyst_open / catalyst_intraday target deltas
REAL_VARIANTS = {"catalyst_open": "sniper", "catalyst_intraday": "intraday"}
HERO_VARIANTS = {"catalyst_open_hero": "sniper", "catalyst_intraday_hero": "intraday"}


def legs_from_study(rows):
    """One leg per pick: the live entry at the hero shadow's delta, with the live and the hold
    multiple (exit value per $1 of cost) on day one and carried to expiry."""
    out = []
    for r in rows:
        e = r["entries"].get("live")
        p = e and e["picks"].get(DELTA[r["source"]])
        if not p:
            continue
        entry = max(p["px"] * (1 + SLIP), p["px"] + 0.01)
        carried = p.get("carry") or p["day1"]
        out.append({"day": r["day"], "t": e["t"], "source": r["source"], "sym": r["sym"], "kind": r["kind"],
                    "contract": p["contract"], "entry": round(entry, 2), "peak": p["peak"],
                    "live": 1 + p["day1"][LIVE], "hold": 1 + p["day1"][HOLD],
                    "live_carry": 1 + carried[LIVE], "hold_carry": 1 + carried[HOLD],
                    "stock": r["close"] / r["open"] - 1})
    return sorted(out, key=lambda x: (x["day"], x["t"]))  # the combined ledger compounds in time order


def simulate(legs, frac, mult_key, start=START, zero=ZERO, hero=HERO):
    """Trade every leg with `frac` of the ledger in whole contracts, compounding. A ledger at or
    below `zero` or at or above `hero` closes the round; the next round starts at `start` again."""
    ledger, rounds, taken, skipped, trail, peak = start, [], 0, 0, [], start
    for leg in legs:
        qty = int(ledger * frac // (leg["entry"] * 100))
        if qty < 1:
            skipped += 1
            trail.append({"day": leg["day"], "sym": leg["sym"], "qty": 0, "ledger": round(ledger, 2)})
            continue
        cost = qty * leg["entry"] * 100
        ledger += cost * (leg[mult_key] - 1)
        taken += 1
        peak = max(peak, ledger)
        trail.append({"day": leg["day"], "sym": leg["sym"], "qty": qty, "ledger": round(ledger, 2)})
        if ledger <= zero or ledger >= hero:
            rounds.append({"end": round(ledger, 2), "kind": "hero" if ledger >= hero else "zero",
                           "closed": leg["day"]})
            ledger = start
    net = sum(r["end"] - start for r in rounds) + ledger - start
    return {"frac": frac, "exit": mult_key, "taken": taken, "skipped": skipped,
            "rounds_closed": len(rounds), "zeros": sum(r["kind"] == "zero" for r in rounds),
            "heroes": sum(r["kind"] == "hero" for r in rounds), "open_ledger": round(ledger, 2),
            "peak_ledger": round(peak, 2), "net": round(net, 2), "rounds": rounds, "trail": trail}


def expiry_of(contract):
    root = contract.rstrip("0123456789CP")
    digits = contract[len(root):]
    return datetime.strptime(digits[:6], "%y%m%d").date()


def close_px(api, contract, day):
    """The contract's 15:45 bid on `day` (last bar at or before 15:46, else the day's last bar),
    at the study's 10% cost; None when the contract did not trade that day."""
    try:
        bars = option_minutes(api, [contract], day).get(contract) or []
    except AlpacaError:
        return None
    if not bars:
        return None
    late = [b for b in bars if hhmm("15:30") <= b["t"].time() <= hhmm("15:46")]
    return round(bid((late or bars)[-1]["c"], SLIP), 2)


def real_legs(api, root=journal.ROOT):
    """The real catalyst fills grouped by day and contract: `live` is what the ledger actually got
    per $1 of cost; `hold` the same contracts sold at 15:45 of the entry day and `hold_carry` at
    15:45 of expiry (the real fill where the bot itself sold at 15:45 or let it expire)."""
    groups = {}
    with open(root / "journal" / "trades.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["variant"] in REAL_VARIANTS and row["mode"] == "real":
                groups.setdefault((row["entry_time"][:10], row["contract"]), []).append(row)
    out = []
    for (day, contract), rows in sorted(groups.items()):
        qty = sum(int(r["qty"]) for r in rows)
        entry = float(rows[0]["entry_price"])
        cost = qty * entry * 100
        proceeds = sum(int(r["qty"]) * float(r["exit_price"]) * 100 for r in rows)
        entry_day = datetime.fromisoformat(rows[0]["entry_time"]).date()
        expiry = expiry_of(contract)
        last = max(rows, key=lambda r: r["exit_time"])
        last_day = datetime.fromisoformat(last["exit_time"]).date()
        timed = all(r["exit_reason"] in ("time", "expired") for r in rows)
        px1 = float(last["exit_price"]) if timed and last_day == entry_day else close_px(api, contract, entry_day)
        if expiry > entry_day:
            pxc = float(last["exit_price"]) if timed and last_day == expiry else close_px(api, contract, expiry)
        else:
            pxc = px1
        out.append({"day": day, "source": REAL_VARIANTS[rows[0]["variant"]], "sym": contract.rstrip("0123456789CP"),
                    "kind": rows[0]["direction"], "contract": contract, "qty": qty, "entry": entry,
                    "cost": round(cost, 2), "pnl": round(proceeds - cost, 2),
                    "exit": "+".join(r["exit_reason"] for r in rows),
                    "live": proceeds / cost if cost else 1.0,
                    "hold": (px1 * qty * 100 / cost) if px1 is not None and cost else None,
                    "hold_carry": (pxc * qty * 100 / cost) if pxc is not None and cost else None})
    return out


def shadow_legs(root=journal.ROOT):
    """The hero shadows' own trades (one leg per contract-day), for the live round counter."""
    groups = {}
    with open(root / "journal" / "trades.csv", newline="") as f:
        for row in csv.DictReader(f):
            if row["variant"] in HERO_VARIANTS:
                groups.setdefault((row["variant"], row["entry_time"][:10], row["contract"]), []).append(row)
    out = []
    for (variant, day, contract), rows in sorted(groups.items()):
        qty = sum(int(r["qty"]) for r in rows)
        entry = float(rows[0]["entry_price"])
        cost = qty * entry * 100
        proceeds = sum(int(r["qty"]) * float(r["exit_price"]) * 100 for r in rows)
        out.append({"day": day, "source": HERO_VARIANTS[variant], "variant": variant, "sym": contract.rstrip("0123456789CP"),
                    "contract": contract, "qty": qty, "entry": entry, "mult": proceeds / cost if cost else 1.0,
                    "pnl": round(proceeds - cost, 2)})
    return out


def avg(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return "-"
    s = sorted(xs)
    f = lambda v: f"{sum(v) / len(v) - 1:+.0%}"
    return f"{len(s)} | {sum(x > 1 for x in s) / len(s):.0%} | {f(s)} | {f(s[:-1]) if len(s) > 1 else '-'} | {f(s[:-2]) if len(s) > 2 else '-'}"


def sim_row(label, s):
    return (f"| {label} | {s['frac']:.0%} | {s['exit']} | {s['taken']} | {s['skipped']} | {s['rounds_closed']} | "
            f"{s['zeros']} | {s['heroes']} | ${s['peak_ledger']:,.0f} | ${s['open_ledger']:,.0f} | ${s['net']:+,.0f} |")


def report(legs, real, shadow, sims):
    L = ["# Hero replay: our picks traded like the other Claude's rule ledgers", "",
         "Every pre-market sniper (0.10 delta, the catalyst_open / catalyst_open_hero contract) and intraday "
         "pick (0.20 delta, catalyst_intraday / catalyst_intraday_hero) since 2026-10-01 on real option minute "
         "bars (journal/research/snipers.json, costs 10% each way), replayed as a $500 ledger that puts either "
         "20% (today's real sizing) or 100% (the hero shadows, the other Claude's rounds) into whole contracts "
         "and compounds. Exits: `live` = half at 3x, trail armed at 1.5x with a 40% giveback, sold at 15:45; "
         "`hold` = nothing until 15:45; `_carry` = held to 15:45 of expiry when the contract outlives the day. "
         "A round ends as a hero at >= $5,000 or a zero at <= $50 and restarts at $500. "
         "See zoh/research/hero.py.", "",
         "## Rounds", "",
         "| ledger | size | exit | taken | skipped (no whole contract) | rounds closed | zeros | heroes | peak | open ledger | net P&L |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, group in sims:
        for s in group:
            L.append(sim_row(label, s))
    L += ["", "## Per $1 of option cost", "",
          "| ledger | exit | n | win% | avg | without the best | without the best two |", "|---|---|---|---|---|---|---|"]
    for label, sel in (("sniper 0.10", [x for x in legs if x["source"] == "sniper"]),
                       ("intraday 0.20", [x for x in legs if x["source"] == "intraday"]),
                       ("all picks", legs)):
        for key, name in (("live", "live, day one"), ("hold", "hold, day one"),
                          ("live_carry", "live, carried"), ("hold_carry", "hold, carried")):
            L.append(f"| {label} | {name} | {avg([x[key] for x in sel])} |")
    hero_all = next(s for lab, g in sims if lab == "all picks" for s in g if s["frac"] == 1.0 and s["exit"] == "hold")
    ledger_after = {(t["day"], t["sym"]): t for t in hero_all["trail"]}
    L += ["", "## Each pick (hero sizing, hold to 15:45 day one: the ledger after each trade)", "",
          "| day | source | sym | dir | stock open->close | option entry | peak x | live | hold | hold carried | contracts | ledger after |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in legs:
        t = ledger_after.get((x["day"], x["sym"]), {})
        L.append(f"| {x['day']} | {x['source']} | {x['sym']} | {x['kind']} | {x['stock']:+.1%} | {x['entry']:.2f} | "
                 f"{x['peak']:.1f} | {x['live'] - 1:+.0%} | {x['hold'] - 1:+.0%} | {x['hold_carry'] - 1:+.0%} | "
                 f"{t.get('qty', '-')} | ${t.get('ledger', 0):,.0f} |")
    L += ["", "## The real fills (catalyst_open / catalyst_intraday, as traded at 20%)", "",
          "`live` is the realised multiple per $1 (real fills, fees aside); `hold` the same contract sold at 15:45 "
          "of the entry day; `hold carried` at 15:45 of expiry. Rows the bot itself closed at 15:45 or let expire "
          "use the real exit; the rest use the 15:45 bar's bid at 10% costs.", "",
          "| day | sym | contract | qty | entry | exit | real P&L | live | hold | hold carried |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for x in real:
        h = f"{x['hold'] - 1:+.0%}" if x["hold"] is not None else "n/a"
        hc = f"{x['hold_carry'] - 1:+.0%}" if x["hold_carry"] is not None else "n/a"
        L.append(f"| {x['day']} | {x['sym']} | {x['contract']} | {x['qty']} | {x['entry']:.2f} | {x['exit']} | "
                 f"${x['pnl']:+,.0f} | {x['live'] - 1:+.0%} | {h} | {hc} |")
    rl = [x for x in real if x["hold"] is not None]
    L += ["", "| ledger | exit | n | win% | avg | without the best | without the best two |", "|---|---|---|---|---|---|---|",
          f"| real fills | live (as traded) | {avg([x['live'] for x in real])} |",
          f"| real fills | hold, day one | {avg([x['hold'] for x in rl])} |",
          f"| real fills | hold, carried | {avg([x['hold_carry'] for x in rl])} |", ""]
    real_sims = {}
    if rl:
        L += ["| ledger | size | exit | taken | skipped (no whole contract) | rounds closed | zeros | heroes | peak | open ledger | net P&L |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for frac in (0.2, 1.0):
            for key in ("live", "hold", "hold_carry"):
                real_sims[(frac, key)] = simulate(rl, frac, key)
                L.append(sim_row("real fills", real_sims[(frac, key)]))
    L += ["", "## The hero shadows' own rounds (catalyst_open_hero / catalyst_intraday_hero, live since 2026-11-03)", ""]
    if shadow:
        legs_s = [{"day": x["day"], "sym": x["sym"], "entry": x["entry"], "mult": x["mult"]} for x in shadow]
        s = simulate(legs_s, 1.0, "mult")
        L += [f"{len(shadow)} trades, {s['rounds_closed']} rounds closed: {s['heroes']} hero, {s['zeros']} zero; "
              f"open ledger ${s['open_ledger']:,.0f}, net ${s['net']:+,.0f}.", "",
              "| day | variant | contract | qty | entry | result | P&L |", "|---|---|---|---|---|---|---|"]
        for x in shadow:
            L.append(f"| {x['day']} | {x['variant']} | {x['contract']} | {x['qty']} | {x['entry']:.2f} | "
                     f"{x['mult'] - 1:+.0%} | ${x['pnl']:+,.0f} |")
    else:
        L.append("No trades yet: the hero shadows only follow a named sniper or an intraday pick.")
    sims_all = {(s["frac"], s["exit"]): s for lab, g in sims if lab == "all picks" for s in g}
    hh, hl = sims_all[(1.0, "hold")], sims_all[(1.0, "live")]
    L += ["", "## Reading", ""]
    L.append(f"1. The hero recipe (whole ledger, no exits, hold to 15:45) on every pick named since 10-06: "
             f"{hh['taken']} trades, {hh['zeros']} zeros, {hh['heroes']} heroes, net ${hh['net']:+,.0f}, best ledger "
             f"${hh['peak_ledger']:,.0f}. Removing the exits did not make a hero; with the live exits at the same full "
             f"size: {hl['zeros']} zeros, {hl['heroes']} heroes, net ${hl['net']:+,.0f}, best ledger ${hl['peak_ledger']:,.0f}.")
    if real_sims:
        rlv, rho = real_sims[(1.0, "live")], real_sims[(1.0, "hold")]
        L.append(f"2. On the {len(rl)} real fills, full size with the exits the bot actually used: {rlv['heroes']} hero "
                 f"(best ledger ${rlv['peak_ledger']:,.0f}) and {rlv['zeros']} zeros, net ${rlv['net']:+,.0f}; the same "
                 f"fills held to 15:45: {rho['heroes']} hero, {rho['zeros']} zeros, net ${rho['net']:+,.0f}. Where a hero "
                 f"appears it comes from full size on a streak the trailing exits kept alive, not from holding.")
    L.append("3. The ticket is the root: see the per-$1 tables. A full-size ledger on a negative ticket is a zero "
             "machine with an occasional hero, and a hero that rests on one trade is a candidate at most "
             "(EVOLUTION 2026-10-07). Nothing in the real ledgers changes on this; the hero shadows stay as the "
             "owner asked (pure hold) so their rounds can be compared with the other Claude's, and the "
             "'real fills, 100%, live' row above is the second counter, rebuilt from trades.csv each run.")
    return "\n".join(L) + "\n"


def main():
    rows = json.loads((OUT / "snipers.json").read_text())
    legs = legs_from_study(rows)
    api = Alpaca()
    real = real_legs(api)
    shadow = shadow_legs()
    sims = []
    for label, sel in (("sniper 0.10", [x for x in legs if x["source"] == "sniper"]),
                       ("intraday 0.20", [x for x in legs if x["source"] == "intraday"]),
                       ("all picks", legs)):
        group = [simulate(sel, frac, key) for frac in (0.2, 1.0) for key in ("live", "hold", "hold_carry")]
        sims.append((label, group))
    (OUT / "hero.json").write_text(json.dumps({"legs": legs, "real": real, "shadow": shadow,
                                               "sims": {lab: g for lab, g in sims}}, indent=0, default=str) + "\n")
    text = report(legs, real, shadow, sims)
    (OUT / "HERO.md").write_text(text)
    print(text[:5000])


if __name__ == "__main__":
    main()
