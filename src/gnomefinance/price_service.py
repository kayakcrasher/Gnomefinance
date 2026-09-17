# price_service.py

from api_client import APIClient
from network_config import NETWORKS


class PriceService:
    """Fetch cryptocurrency prices for GNOMEfinance."""

    def __init__(self):
        self.client = APIClient(
            "https://api.coingecko.com/api/v3"
        )

    def get_prices(self, networks=None):
        """Return USD prices for selected networks."""

        if networks is None:
            networks = list(NETWORKS.keys())

        coin_ids = []

        for network in networks:
            info = NETWORKS.get(network)

            if info is None:
                continue

            coin_id = info.get("coingecko_id")

            if coin_id:
                coin_ids.append(coin_id)

        if not coin_ids:
            return {}

        data = self.client.get(
            "/simple/price",
            {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
            },
        )

        prices = {}

        for network in networks:

            info = NETWORKS.get(network)

            if info is None:
                continue

            coin_id = info.get("coingecko_id")

            if coin_id in data:
                prices[network] = data[
                    coin_id
                ]["usd"]

        return prices


if __name__ == "__main__":

    service = PriceService()

    prices = service.get_prices()

    print("GNOMEfinance Prices")
    print("-------------------")

    for network, price in prices.items():

        symbol = NETWORKS[network]["symbol"]

        print(
            f"{symbol}: "
            f"${price:,.2f}"
        )
