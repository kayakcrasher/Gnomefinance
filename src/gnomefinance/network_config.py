# network_config.py


NETWORKS = {
    "bitcoin": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "type": "utxo",
        "status": "planned",
        "coingecko_id": "bitcoin",
    },

    "solana": {
        "name": "Solana",
        "symbol": "SOL",
        "type": "account",
        "status": "active",
        "coingecko_id": "solana",
    },

    "cardano": {
        "name": "Cardano",
        "symbol": "ADA",
        "type": "utxo",
        "status": "planned",
        "coingecko_id": "cardano",
    },

    "avalanche": {
        "name": "Avalanche",
        "symbol": "AVAX",
        "type": "account",
        "status": "planned",
        "coingecko_id": "avalanche",
    },
}


def get_network(network_id):
    """Return information about a network."""

    return NETWORKS.get(network_id)


def list_networks():
    """Return all configured networks."""

    return NETWORKS


def get_coingecko_id(network_id):
    """Return the CoinGecko ID for a network."""

    network = get_network(network_id)

    if network is None:
        return None

    return network.get("coingecko_id")


def get_symbol(network_id):
    """Return the symbol for a network."""

    network = get_network(network_id)

    if network is None:
        return None

    return network.get("symbol")


def print_networks():
    """Display configured networks."""

    print("GNOMEfinance Networks")
    print("---------------------")

    for network_id, network in NETWORKS.items():

        print(
            f"{network['name']} "
            f"({network['symbol']}) - "
            f"{network['status']}"
        )


if __name__ == "__main__":
    print_networks()
