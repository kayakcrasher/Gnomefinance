# price_service.py

import requests


COINGECKO_IDS = {
    "bitcoin": "bitcoin",
    "solana": "solana",
    "cardano": "cardano",
    "avalanche": "avalanche",
}


def get_prices(networks=None):
    """Fetch current USD prices for selected networks."""

    if networks is None:
        networks = list(COINGECKO_IDS.keys())

    coin_ids = [
        COINGECKO_IDS[network]
        for network in networks
        if network in COINGECKO_IDS
    ]

    if not coin_ids:
        return {}

    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    prices = {}

    for network in networks:
        coin_id = COINGECKO_IDS.get(network)

        if coin_id in data:
            prices[network] = data[coin_id]["usd"]

    return prices


if __name__ == "__main__":
    prices = get_prices()

    for network, price in prices.items():
        print(f"{network}: ${price:,.2f}")
