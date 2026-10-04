"""Minimal Alpaca REST client (stdlib only). Paper trading endpoint only."""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

TRADING_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"


class AlpacaError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class Alpaca:
    def __init__(self, key=None, secret=None):
        self.headers = {
            "APCA-API-KEY-ID": key or os.environ["APCA_API_KEY_ID"],
            "APCA-API-SECRET-KEY": secret or os.environ["APCA_API_SECRET_KEY"],
            "Content-Type": "application/json",
        }

    def _request(self, method, url, params=None, body=None, retries=4):
        if params:
            query = {k: v for k, v in params.items() if v is not None}
            url += "?" + urllib.parse.urlencode(query)
        data = json.dumps(body).encode() if body is not None else None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=data, method=method, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise AlpacaError(e.code, e.read().decode(errors="replace")) from None
            except (urllib.error.URLError, TimeoutError):
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    def _paged(self, url, params, key):
        params = dict(params)
        while True:
            page = self._request("GET", url, params)
            yield page.get(key) or ({} if key == "snapshots" else [])
            token = page.get("next_page_token")
            if not token:
                return
            params["page_token"] = token

    # --- trading -----------------------------------------------------------

    def account(self):
        return self._request("GET", f"{TRADING_URL}/v2/account")

    def positions(self):
        return self._request("GET", f"{TRADING_URL}/v2/positions")

    def clock(self):
        return self._request("GET", f"{TRADING_URL}/v2/clock")

    def calendar(self, start, end):
        return self._request("GET", f"{TRADING_URL}/v2/calendar",
                             {"start": start.isoformat(), "end": end.isoformat()})

    def submit_order(self, **order):
        return self._request("POST", f"{TRADING_URL}/v2/orders", body=order)

    def get_order(self, order_id):
        return self._request("GET", f"{TRADING_URL}/v2/orders/{order_id}")

    def cancel_order(self, order_id):
        return self._request("DELETE", f"{TRADING_URL}/v2/orders/{order_id}")

    # --- market data -------------------------------------------------------

    def stock_bars(self, symbol, start, end, timeframe="1Min", feed="iex", adjustment="raw"):
        """All bars between two aware datetimes. IEX (free, real time) by default; SIP is the
        full consolidated tape, available on the free tier for data older than 15 minutes."""
        params = {"timeframe": timeframe, "start": start.isoformat(), "end": end.isoformat(),
                  "feed": feed, "limit": 10000, "adjustment": adjustment}
        bars = []
        for page in self._paged(f"{DATA_URL}/v2/stocks/{symbol}/bars", params, "bars"):
            bars.extend(page)
        return bars

    def assets(self):
        return self._request("GET", f"{TRADING_URL}/v2/assets",
                             {"status": "active", "asset_class": "us_equity"})

    def daily_bars_multi(self, symbols, start, end, feed="sip"):
        """{symbol: [bars]} for many symbols, split-adjusted daily bars."""
        params = {"symbols": ",".join(symbols), "timeframe": "1Day", "start": start.isoformat(),
                  "end": end.isoformat(), "feed": feed, "limit": 10000, "adjustment": "all"}
        out = {}
        for page in self._paged(f"{DATA_URL}/v2/stocks/bars", params, "bars"):
            for symbol, bars in (page or {}).items():
                out.setdefault(symbol, []).extend(bars)
        return out

    def news(self, symbols, start, end, limit=50):
        params = {"symbols": ",".join(symbols), "start": start.isoformat(), "end": end.isoformat(),
                  "limit": limit, "sort": "desc", "include_content": "false"}
        return self._request("GET", f"{DATA_URL}/v1beta1/news", params).get("news") or []

    def option_chain(self, underlying, expiration, kind, strike_gte=None, strike_lte=None):
        """Snapshots (quote + greeks) for one expiry/side of an option chain."""
        params = {"feed": "indicative", "type": kind, "expiration_date": expiration.isoformat(),
                  "strike_price_gte": strike_gte, "strike_price_lte": strike_lte, "limit": 1000}
        snaps = {}
        for page in self._paged(f"{DATA_URL}/v1beta1/options/snapshots/{underlying}", params,
                                "snapshots"):
            snaps.update(page)
        return snaps

    def option_snapshots(self, symbols):
        if not symbols:
            return {}
        page = self._request("GET", f"{DATA_URL}/v1beta1/options/snapshots",
                             {"symbols": ",".join(symbols), "feed": "indicative"})
        return page.get("snapshots") or {}
