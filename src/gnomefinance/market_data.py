# market_data.py

from api_client import APIClient
from network_config import NETWORKS


class MarketData:
    """Retrieve market data for GNOMEfinance assets."""

    def __init__(self):
        self.client = APIClient(
            "https://api.coingecko.com/api/v3"
        )

    def get_market_data(self, networks=None):
        """Return market data for selected networks."""

        if networks is None:
            networks = list(NETWORKS.keys())

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

        data = self.client.get(
            "/coins/markets",
            {
                "vs_currency": "usd",
                "ids": ",".join(coin_ids),
                "price_change_percentage": "24h",
            },
        )

        market_data = {}

        for coin in data:

            network = None

            for network_id, info in NETWORKS.items():

                if info.get(
                    "coingecko_id"
                ) == coin["id"]:

                    network = network_id
                    break

            if network is None:
                continue

            market_data[network] = {
                "price": coin[
                    "current_price"
                ],
                "change_24h": coin.get(
                    "price_change_percentage_24h"
                ) or 0,
                "market_cap": coin[
                    "market_cap"
                ],
                "volume_24h": coin[
                    "total_volume"
                ],
            }

        return market_data


if __name__ == "__main__":

    market = MarketData()

    data = market.get_market_data()

    print("GNOMEfinance Market Data")
    print("------------------------")

    for network, info in data.items():

        symbol = NETWORKS[network]["symbol"]

        print(
            f"{symbol}: "
            f"${info['price']:,.2f} | "
            f"24h: "
            f"{info['change_24h']:.2f}%"
        )
