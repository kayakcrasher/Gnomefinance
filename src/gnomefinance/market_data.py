# market_data.py

from api_client import APIClient
from network_config import NETWORKS
from error_handler import APIError, NetworkError
from market_cache import MarketCache


class MarketData:
    """Retrieve and cache market data."""

    def __init__(self, cache_ttl=60):
        self.client = APIClient(
            "https://api.coingecko.com/api/v3"
        )

        self.cache = MarketCache(
            ttl=cache_ttl
        )

    def get_market_data(self, networks=None):
        """Return market data for selected networks."""

        if networks is None:
            networks = list(NETWORKS.keys())

        cached_data = self.cache.get()

        if cached_data is not None:
            return self.filter_networks(
                cached_data,
                networks,
            )

        coin_ids = []

        for network in networks:

            info = NETWORKS.get(network)

            if info is None:
                continue

            coin_id = info.get(
                "coingecko_id"
            )

            if coin_id:
                coin_ids.append(coin_id)

        if not coin_ids:
            return {}

        try:

            data = self.client.get(
                "/coins/markets",
                {
                    "vs_currency": "usd",
                    "ids": ",".join(coin_ids),
                    "price_change_percentage": "24h",
                },
            )

        except (
            APIError,
            NetworkError,
        ):

            return {}

        market_data = {}

        for coin in data:

            network = self.find_network(
                coin["id"]
            )

            if network is None:
                continue

            market_data[network] = {
                "price": coin.get(
                    "current_price",
                    0,
                ),
                "change_24h": coin.get(
                    "price_change_percentage_24h"
                ) or 0,
                "market_cap": coin.get(
                    "market_cap",
                    0,
                ),
                "volume_24h": coin.get(
                    "total_volume",
                    0,
                ),
            }

        self.cache.set(
            market_data
        )

        return self.filter_networks(
            market_data,
            networks,
        )

    def find_network(self, coin_id):
        """Find a GNOMEfinance network by CoinGecko ID."""

        for network_id, info in (
            NETWORKS.items()
        ):

            if info.get(
                "coingecko_id"
            ) == coin_id:

                return network_id

        return None

    def filter_networks(
        self,
        market_data,
        networks,
    ):
        """Return only requested networks."""

        return {
            network: market_data[network]
            for network in networks
            if network in market_data
        }

    def clear_cache(self):
        """Force the next request to fetch fresh data."""

        self.cache.clear()


if __name__ == "__main__":

    market = MarketData(
        cache_ttl=60
    )

    print(
        "GNOMEfinance Market Data"
    )

    print(
        "------------------------"
    )

    first = market.get_market_data()

    print(
        "First request complete."
    )

    second = market.get_market_data()

    print(
        "Second request complete."
    )

    print(
        "Cache age:",
        f"{market.cache.age():.2f} seconds"
    )

    print(
        "Assets:",
        list(second.keys())
    )
