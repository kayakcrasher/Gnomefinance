"""Live prices and price history from CoinGecko."""

import time

from .api_client import APIClient
from .assets import ASSETS
from .cache import TTLCache
from .config import (
    COINGECKO_API_KEY,
    COINGECKO_URL,
    CURRENCY,
    MARKET_CACHE_TTL,
)
from .errors import GNOMEfinanceError, ValidationError

HISTORY_RANGES = (1, 7, 30, 90, 365)


def make_coingecko_client():
    headers = {}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    return APIClient(COINGECKO_URL, headers=headers)


class MarketData:
    def __init__(self, client=None, cache_ttl=MARKET_CACHE_TTL):
        self.client = client or make_coingecko_client()
        self.cache = TTLCache(ttl=cache_ttl)

    def get_quotes(self, force=False):
        """Return {asset_id: quote} for every known asset.

        A quote has price, change_24h (%), market_cap, volume_24h, and
        "stale": True when we could not reach the API and are showing the
        last good data instead.
        """
        if not force:
            cached = self.cache.get("quotes")
            if cached is not None:
                return cached

        try:
            quotes = self._fetch_quotes()
        except GNOMEfinanceError:
            stale = self.cache.get_stale("quotes")
            if stale is None:
                raise
            return {
                asset_id: {**quote, "stale": True}
                for asset_id, quote in stale.items()
            }

        self.cache.set("quotes", quotes)
        return quotes

    def get_price(self, asset_id):
        quote = self.get_quotes().get(asset_id)
        return None if quote is None else quote["price"]

    def get_history(self, asset_id, days=7):
        """Return [[timestamp_ms, price], ...] for the last ``days`` days."""
        if asset_id not in ASSETS:
            raise ValidationError(f"Unknown asset: {asset_id}")

        days = int(days)
        if days not in HISTORY_RANGES:
            raise ValidationError(f"days must be one of {HISTORY_RANGES}")

        key = f"history:{asset_id}:{days}"
        cached = self.cache.get(key, max_age=self._history_ttl(days))
        if cached is not None:
            return cached

        data = self.client.get(
            f"/coins/{ASSETS[asset_id]['coingecko_id']}/market_chart",
            {"vs_currency": CURRENCY, "days": days},
        )
        points = [
            [int(ts), float(price)]
            for ts, price in data.get("prices", [])
            if price is not None
        ]
        self.cache.set(key, points)
        return points

    def clear_cache(self):
        self.cache.clear()

    def _fetch_quotes(self):
        by_coingecko_id = {
            info["coingecko_id"]: asset_id for asset_id, info in ASSETS.items()
        }

        data = self.client.get(
            "/coins/markets",
            {
                "vs_currency": CURRENCY,
                "ids": ",".join(by_coingecko_id),
                "price_change_percentage": "24h",
            },
        )

        quotes = {}
        now = time.time()

        for coin in data:
            asset_id = by_coingecko_id.get(coin.get("id"))
            if asset_id is None or coin.get("current_price") is None:
                continue

            quotes[asset_id] = {
                "price": float(coin["current_price"]),
                "change_24h": float(coin.get("price_change_percentage_24h") or 0),
                "market_cap": coin.get("market_cap") or 0,
                "volume_24h": coin.get("total_volume") or 0,
                "updated": now,
                "stale": False,
            }

        return quotes

    @staticmethod
    def _history_ttl(days):
        # Long ranges barely change minute to minute; cache them longer.
        return 60 if days == 1 else 300 if days <= 7 else 1800
