# network_registry.py

from network_config import NETWORKS
from solana_network import SolanaNetwork


class NetworkRegistry:
    """Registry for GNOMEfinance blockchain networks."""

    def __init__(self):
        self.networks = {}

        self.register_default_networks()

    def register(
        self,
        network_id,
        network,
    ):
        """Register a blockchain network."""

        if network_id not in NETWORKS:
            raise ValueError(
                f"Unknown network: {network_id}"
            )

        self.networks[network_id] = network

    def register_default_networks(self):
        """Register currently implemented networks."""

        self.register(
            "solana",
            SolanaNetwork(),
        )

    def unregister(
        self,
        network_id,
    ):
        """Remove a registered network."""

        self.networks.pop(
            network_id,
            None,
        )

    def get(
        self,
        network_id,
    ):
        """Return a registered network."""

        return self.networks.get(
            network_id
        )

    def has(
        self,
        network_id,
    ):
        """Return True if a network is registered."""

        return network_id in self.networks

    def list_registered(self):
        """Return all registered networks."""

        return self.networks

    def list_available(self):
        """Return all configured networks."""

        return NETWORKS

    def clear(self):
        """Remove all registered networks."""

        self.networks.clear()

    def display(self):
        """Display registered networks."""

        print(
            "GNOMEfinance Network Registry"
        )

        print(
            "-----------------------------"
        )

        for network_id, network in (
            self.networks.items()
        ):

            print(
                f"{network.get_network_name()} "
                f"({network.get_symbol()})"
            )


if __name__ == "__main__":

    registry = NetworkRegistry()

    registry.display()

    print()

    solana = registry.get(
        "solana"
    )

    print(
        "Solana registered:",
        registry.has("solana"),
    )

    print(
        "Network:",
        solana.get_network_name(),
    )

    print(
        "Symbol:",
        solana.get_symbol(),
    )

    print(
        "Connected:",
        solana.is_connected(),
    )
