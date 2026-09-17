# price_service.py

from api_client import APIClient


COINGECKO_IDS = {
    "bitcoin": "bitcoin",
    "solana": "solana",
    "cardano": "cardano",
    "avalanche": "avalanche",
}


class PriceService:
    """Fetch cryptocurrency prices for GNOMEfinance."""

    def __init__(self):
        self.client = APIClient(
            "https://api.coingecko.com/api/v3"
        )

    def get_prices(self, networks=None):
        """Return USD prices for selected networks."""

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
            "/simple/price",
            {
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
            },
        )

        prices = {}

        for network in networks:
            coin_id = COINGECKO_IDS.get(network)

            if coin_id in data:
                prices[network] = data[coin_id]["usd"]

        return prices


if __name__ == "__main__":
    service = PriceService()

    prices = service.get_prices()

    print("GNOMEfinance Prices")
    print("-------------------")

    for network, price in prices.items():
        print(f"{network}: ${price:,.2f}")
