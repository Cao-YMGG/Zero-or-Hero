"""Pure strategy logic shared by the live bot, the backtester and the tests.

Bars are dicts with keys t (aware datetime in US/Eastern), o, h, l, c.
A variant is a dict from config/strategy.json describing one strategy.
"""
import math
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)
TRADING_MINUTES_PER_YEAR = 252 * 390


def hhmm(text):
    hours, minutes = map(int, text.split(":"))
    return time(hours, minutes)


def minutes_after_open(minutes):
    return (datetime(2000, 1, 1, 9, 30) + timedelta(minutes=minutes)).time()


def parse_bar(raw):
    t = datetime.fromisoformat(raw["t"].replace("Z", "+00:00")).astimezone(ET)
    return {"t": t, "o": raw["o"], "h": raw["h"], "l": raw["l"], "c": raw["c"]}


def regular_session(bars):
    return [b for b in bars if MARKET_OPEN <= b["t"].time() < MARKET_CLOSE]


# --- day context -------------------------------------------------------------
# Facts about the day that signals and filters may use:
#   events: macro releases today (e.g. ["CPI"]), gap_pct: open vs previous close in %,
#   bias: Claude's pre-market call ({"bias": "call"|"put"|"none", ...}) or None,
#   cross: today's bars for other assets ({"TLT": [...], "USO": [...]}).

def day_context(day, events_by_date, prev_close=None, open_price=None, bias=None, cross=None):
    gap = (open_price / prev_close - 1) * 100 if prev_close and open_price else None
    return {"events": events_by_date.get(day.isoformat(), []), "gap_pct": gap, "bias": bias,
            "cross": cross or {}, "weekday": day.weekday()}


def cross_assets(variants):
    return sorted({v["asset"] for v in variants if v.get("signal") == "cross"})


def passes_filters(variant, ctx):
    """Day-level filters a variant can declare in config, checked before its signal."""
    days = variant.get("days")
    if days == "event" and not ctx["events"]:
        return False
    if days == "non_event" and ctx["events"]:
        return False
    weekdays = variant.get("weekdays")  # e.g. [0, 2, 4]: single-stock same-day expiries
    if weekdays is not None and ctx.get("weekday") not in weekdays:
        return False
    return True


def _gap_direction(ctx, min_gap_pct):
    gap = ctx.get("gap_pct")
    if gap is None or abs(gap) < min_gap_pct:
        return None
    return "call" if gap > 0 else "put"


# --- signals -------------------------------------------------------------
# Each signal sees today's closed bars so far plus the day context and returns
# "call", "put" or None.

def _flip(direction, variant):
    if direction and variant.get("fade"):
        return "put" if direction == "call" else "call"
    return direction


def signal_orb(bars, variant, ctx=None):
    """Opening-range breakout: close beyond the high/low of the first N minutes."""
    end = minutes_after_open(variant.get("or_minutes", 30))
    rng = [b for b in bars if b["t"].time() < end]
    after = [b for b in bars if b["t"].time() >= end]
    if len(rng) < 3 or not after:
        return None
    hi = max(b["h"] for b in rng)
    lo = min(b["l"] for b in rng)
    buffer = variant.get("buffer_pct", 0) / 100
    last = after[-1]["c"]
    direction = None
    if last > hi * (1 + buffer):
        direction = "call"
    elif last < lo * (1 - buffer):
        direction = "put"
    return _flip(direction, variant)


def signal_momentum(bars, variant, ctx=None):
    """Trend day: after N minutes, follow the move from the open if it exceeds a threshold."""
    if not bars or bars[-1]["t"].time() < minutes_after_open(variant.get("after_minutes", 60)):
        return None
    ret = bars[-1]["c"] / bars[0]["o"] - 1
    threshold = variant.get("threshold_pct", 0.3) / 100
    direction = None
    if ret >= threshold:
        direction = "call"
    elif ret <= -threshold:
        direction = "put"
    return _flip(direction, variant)


def signal_gap(bars, variant, ctx):
    """Overnight gap: once N minutes have traded, follow (or fade) a gap of at least X%."""
    if not bars or bars[-1]["t"].time() < minutes_after_open(variant.get("after_minutes", 1)):
        return None
    direction = _gap_direction(ctx, variant.get("min_gap_pct", 0.3))
    sides = variant.get("sides")  # e.g. ["up"]: only act on up gaps
    if direction and sides and ("up" if direction == "call" else "down") not in sides:
        return None
    return _flip(direction, variant)


def signal_bias(bars, variant, ctx):
    """Claude's pre-market call. With confirm, the move since the open must agree."""
    bias = (ctx.get("bias") or {}).get("bias")
    if bias not in ("call", "put"):
        return None
    if not bars or bars[-1]["t"].time() < minutes_after_open(variant.get("after_minutes", 5)):
        return None
    if variant.get("confirm"):
        ret = bars[-1]["c"] / bars[0]["o"] - 1
        threshold = variant.get("threshold_pct", 0.1) / 100
        if (bias == "call" and ret < threshold) or (bias == "put" and ret > -threshold):
            return None
    return _flip(bias, variant)


def signal_cross(bars, variant, ctx):
    """Another asset leads SPY: after N minutes, trade SPY on that asset's move since its open.

    sign +1: asset up -> SPY call (e.g. TLT up = yields down); -1: asset up -> SPY put (oil).
    """
    if not bars or bars[-1]["t"].time() < minutes_after_open(variant.get("after_minutes", 10)):
        return None
    other = [b for b in (ctx.get("cross") or {}).get(variant["asset"], [])
             if b["t"] <= bars[-1]["t"]]
    if len(other) < 2:
        return None
    ret = (other[-1]["c"] / other[0]["o"] - 1) * variant.get("sign", 1)
    threshold = variant.get("threshold_pct", 0.2) / 100
    direction = None
    if ret >= threshold:
        direction = "call"
    elif ret <= -threshold:
        direction = "put"
    return _flip(direction, variant)


def sniper_pick(ctx):
    """Claude's single-stock pick for today: {"symbol", "direction", "catalyst", ...} or None."""
    pick = (ctx.get("bias") or {}).get("sniper") or None
    if not pick or pick.get("direction") not in ("call", "put") or not pick.get("symbol"):
        return None
    return pick


def signal_catalyst(bars, variant, ctx):
    """Trade Claude's pre-market single-stock pick once its price confirms after the open.

    `bars` here are the picked stock's bars (the bot swaps them in); fires when the move from
    the open, in the picked direction, reaches move_pct after N minutes.
    """
    pick = sniper_pick(ctx)
    if not pick or not bars:
        return None
    if bars[-1]["t"].time() < minutes_after_open(variant.get("after_minutes", 15)):
        return None
    move = bars[-1]["c"] / bars[0]["o"] - 1
    need = variant.get("move_pct", 1.0) / 100
    if (pick["direction"] == "call" and move >= need) or (pick["direction"] == "put"
                                                          and move <= -need):
        return pick["direction"]
    return None


SIGNALS = {"orb": signal_orb, "momentum": signal_momentum, "gap": signal_gap,
           "bias": signal_bias, "cross": signal_cross, "catalyst": signal_catalyst}
LIVE_ONLY_SIGNALS = {"bias", "catalyst"}  # no history to backtest


def evaluate_signal(bars, variant, ctx=None):
    ctx = ctx or {"events": [], "gap_pct": None, "bias": None}
    if not passes_filters(variant, ctx):
        return None
    return SIGNALS[variant["signal"]](bars, variant, ctx)


# --- exits -----------------------------------------------------------------

def check_exit(entry, peak, price, variant):
    """Exit reason for an open long option, or None. Time exits are the caller's job."""
    tp = variant.get("take_profit")
    if tp is not None and price >= entry * (1 + tp):
        return "take_profit"
    sl = variant.get("stop_loss")
    if sl is not None and price <= entry * (1 - sl):
        return "stop_loss"
    trail_after = variant.get("trail_after")
    if trail_after is not None and peak >= entry * (1 + trail_after):
        floor = max(entry, peak * (1 - variant.get("trail_giveback", 0.4)))
        if price <= floor:
            return "trail"
    return None


# --- option math -----------------------------------------------------------

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def years_to_close(now, close=MARKET_CLOSE):
    minutes = (datetime.combine(now.date(), close, now.tzinfo) - now).total_seconds() / 60
    return max(minutes, 0) / TRADING_MINUTES_PER_YEAR


def bs_price(spot, strike, years, iv, kind):
    if years <= 0 or iv <= 0:
        return max(spot - strike, 0.0) if kind == "call" else max(strike - spot, 0.0)
    sd = iv * math.sqrt(years)
    d1 = (math.log(spot / strike) + 0.5 * sd * sd) / sd
    d2 = d1 - sd
    if kind == "call":
        return spot * norm_cdf(d1) - strike * norm_cdf(d2)
    return strike * norm_cdf(-d2) - spot * norm_cdf(-d1)


def bs_delta(spot, strike, years, iv, kind):
    if years <= 0 or iv <= 0:
        itm = spot > strike if kind == "call" else spot < strike
        return (1.0 if itm else 0.0) * (1 if kind == "call" else -1)
    sd = iv * math.sqrt(years)
    d1 = (math.log(spot / strike) + 0.5 * sd * sd) / sd
    return norm_cdf(d1) if kind == "call" else norm_cdf(d1) - 1


def parse_occ(symbol):
    """'SPY261005C00580000' -> ('SPY', '261005', 'call', 580.0)."""
    root, rest = symbol[:-15], symbol[-15:]
    kind = "call" if rest[6] == "C" else "put"
    return root, rest[:6], kind, int(rest[7:]) / 1000


# --- sizing & selection ------------------------------------------------------

def current_phase(config, equity):
    phases = sorted(config["phases"], key=lambda p: p["min_equity"])
    chosen = phases[0]
    for phase in phases:
        if equity >= phase["min_equity"]:
            chosen = phase
    return chosen


def contracts_for(budget, price):
    if price <= 0:
        return 0
    return int(budget // (price * 100))


def select_contract(candidates, target_delta, budget):
    """Pick the affordable contract whose |delta| is closest to the target.

    candidates: dicts with symbol, strike, ask, delta. Returns one or None.
    """
    affordable = [c for c in candidates if c["ask"] > 0 and c["ask"] * 100 <= budget
                  and c["delta"] is not None]
    if not affordable:
        return None
    return min(affordable, key=lambda c: (abs(abs(c["delta"]) - target_delta), c["ask"]))


def round_limit(price, up=True):
    """Penny-pilot ticks: $0.01 below $3, $0.05 above."""
    tick = 0.01 if price < 3 else 0.05
    steps = math.ceil(price / tick - 1e-9) if up else math.floor(price / tick + 1e-9)
    return round(max(steps, 1) * tick, 2)
