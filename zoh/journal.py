"""Config, daily state and the trade journal, all stored as files in the repo."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "strategy.json"
EVENTS_PATH = ROOT / "config" / "macro_events.json"
JOURNAL_DIR = ROOT / "journal"
TRADES_PATH = JOURNAL_DIR / "trades.csv"
EQUITY_PATH = JOURNAL_DIR / "equity.csv"
STATE_PATH = JOURNAL_DIR / "state.json"
LEDGER_PATH = JOURNAL_DIR / "ledger.json"
BIAS_DIR = JOURNAL_DIR / "bias"

TRADE_FIELDS = ["date", "variant", "mode", "contract", "direction", "entry_time", "entry_price",
                "exit_time", "exit_price", "qty", "pnl", "pnl_pct", "exit_reason", "phase",
                "equity_before"]
EQUITY_FIELDS = ["date", "equity", "phase", "champion"]


def load_config():
    return json.loads(CONFIG_PATH.read_text())


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n")


def load_events():
    """{"2026-10-14": ["CPI"], ...} from config/macro_events.json."""
    by_date = {}
    for kind, dates in json.loads(EVENTS_PATH.read_text()).items():
        if kind.startswith("_"):
            continue
        for day in dates:
            by_date.setdefault(day, []).append(kind)
    return by_date


def bias_path(day):
    return BIAS_DIR / f"{day.isoformat()}.json"


def intraday_path(day):
    """Claude's intraday picks: {"date": ..., "picks": [{"time", "symbol", "direction", ...}]}."""
    return BIAS_DIR / "intraday" / f"{day.isoformat()}.json"


def variant_by_id(config, variant_id):
    return next(v for v in config["variants"] if v["id"] == variant_id)


def load_state(today):
    prev = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    if prev.get("date") == today.isoformat():
        return prev
    return carry_over(prev, today)


def occ_root(contract):
    """Underlying of an OCC option symbol, e.g. MRVL261009C00297500 -> MRVL."""
    return contract[:-15]


def carry_over(prev, today):
    """A new day's state. Positions marked "hold" (contracts expiring after the day they were
    bought) carry over under "<variant>@<first day carried>", so the variant itself can trade again."""
    state = {"date": today.isoformat(), "done": False, "variants": {}}
    for vid, vs in (prev.get("variants") or {}).items():
        if vs.get("hold") and vs.get("shadow"):
            of = vs.get("of", vid)
            key = vid if "@" in vid else f"{vid}@{prev.get('date', '')}"
            kept = {"entered": True, "carried": True, "of": of, "shadow": vs["shadow"]}
            if vs.get("real"):
                kept["real"] = vs["real"]
                underlying = vs["real"].get("underlying") or occ_root(vs["real"]["contract"])
                if underlying:
                    state.setdefault("real_underlyings", []).append(underlying)
            state["variants"][key] = kept
    return state


def save_state(state):
    JOURNAL_DIR.mkdir(exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def _read(path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_trades():
    return _read(TRADES_PATH)


def read_equity():
    return _read(EQUITY_PATH)


def append_trade(row):
    JOURNAL_DIR.mkdir(exist_ok=True)
    new = not TRADES_PATH.exists()
    with TRADES_PATH.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_FIELDS)
        if new:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in TRADE_FIELDS})


def record_equity(row):
    """One row per date; a later run on the same date replaces it."""
    rows = [r for r in read_equity() if r["date"] != row["date"]] + [row]
    JOURNAL_DIR.mkdir(exist_ok=True)
    with EQUITY_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EQUITY_FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: r["date"]))


def load_ledger():
    return json.loads(LEDGER_PATH.read_text()) if LEDGER_PATH.exists() else None


def save_ledger(ledger):
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2) + "\n")
