# market_data.py

from api_client import APIClient


COINGECKO_IDS = {
    "bitcoin": "bitcoin",
    "solana": "solana",
    "cardano": "cardano",
    "avalanche": "avalanche",
}


class MarketData:
    """Retrieve market data for GNOMEfinance assets."""

    def __init__(self):
        self.client = APIClient(
            "https://api.coingecko.com/api/v3"
        )

    def get_market_data(self, networks=None):
        """Return market data for selected networks."""

        if networks is None:
            networks = list(COINGECKO_IDS.keys())

        coin_ids = [
            COINGECKO_IDS[network]
            for network in networks
            if network in COINGECKO_IDS
        ]

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
            network = next(
                (
                    network
                    for network, coin_id in COINGECKO_IDS.items()
                    if coin_id == coin["id"]
                ),
                None,
            )

            if network:
                market_data[network] = {
                    "price": coin["current_price"],
                    "change_24h": coin[
                        "price_change_percentage_24h"
                    ],
                    "market_cap": coin["market_cap"],
                    "volume_24h": coin[
                        "total_volume"
                    ],
                }

        return market_data


if __name__ == "__main__":
    market = MarketData()

    data = market.get_market_data()

    for network, info in data.items():
        print(
            f"{network.upper()}: "
            f"${info['price']:,.2f} | "
            f"24h: {info['change_24h']:.2f}%"
        )
