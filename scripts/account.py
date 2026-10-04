"""Print the Alpaca paper account summary (no secrets are printed)."""
import json
import os
import urllib.request

BASE_URL = "https://paper-api.alpaca.markets"


def get(path):
    req = urllib.request.Request(
        BASE_URL + path,
        headers={
            "APCA-API-KEY-ID": os.environ["APCA_API_KEY_ID"],
            "APCA-API-SECRET-KEY": os.environ["APCA_API_SECRET_KEY"],
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def main():
    acct = get("/v2/account")
    for key in ("status", "currency", "cash", "equity", "buying_power",
                "options_trading_level", "crypto_status", "pattern_day_trader"):
        print(f"{key:24} {acct.get(key)}")

    positions = get("/v2/positions")
    print(f"\npositions: {len(positions)}")
    for p in positions:
        print(f"  {p['symbol']:10} qty={p['qty']} market_value={p['market_value']} "
              f"unrealized_pl={p['unrealized_pl']}")

    clock = get("/v2/clock")
    print(f"\nmarket open: {clock['is_open']}  next_open: {clock['next_open']}")


if __name__ == "__main__":
    main()
