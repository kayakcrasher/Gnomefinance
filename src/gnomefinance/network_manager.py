# network_manager.py

from network_config import NETWORKS


class NetworkManager:
    """Manage supported GNOMEfinance networks."""

    def __init__(self):
        self.networks = NETWORKS

    def get_network(self, network_id):
        """Return information about a specific network."""
        return self.networks.get(network_id)

    def get_supported_networks(self):
        """Return all supported networks."""
        return self.networks

    def get_active_networks(self):
        """Return networks currently marked active."""
        return {
            network_id: network
            for network_id, network in self.networks.items()
            if network["status"] == "active"
        }

    def get_symbol(self, network_id):
        """Return the symbol for a network."""
        network = self.get_network(network_id)

        if network is None:
            return None

        return network["symbol"]

    def display_networks(self):
        """Display supported networks."""
        print("GNOMEfinance Networks")
        print("---------------------")

        for network_id, network in self.networks.items():
            print(
                f"{network['name']} "
                f"({network['symbol']}) - "
                f"{network['status']}"
            )


if __name__ == "__main__":
    manager = NetworkManager()

    manager.display_networks()

    print()
    print("Solana symbol:", manager.get_symbol("solana"))
