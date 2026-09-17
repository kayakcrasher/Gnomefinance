# network_config.py

NETWORKS = {
    "bitcoin": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "type": "utxo",
        "status": "planned",
    },

    "solana": {
        "name": "Solana",
        "symbol": "SOL",
        "type": "account",
        "status": "active",
    },

    "cardano": {
        "name": "Cardano",
        "symbol": "ADA",
        "type": "utxo",
        "status": "planned",
    },

    "avalanche": {
        "name": "Avalanche",
        "symbol": "AVAX",
        "type": "account",
        "status": "planned",
    },
}


def get_network(network_id):
    """Return information about a network."""
    return NETWORKS.get(network_id)


def list_networks():
    """Return all configured networks."""
    return NETWORKS


def print_networks():
    """Display configured networks."""
    for network_id, network in NETWORKS.items():
        print(
            f"{network_id}: "
            f"{network['name']} ({network['symbol']}) - "
            f"{network['status']}"
        )


if __name__ == "__main__":
    print_networks()
