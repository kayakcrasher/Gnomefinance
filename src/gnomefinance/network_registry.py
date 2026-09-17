# network_registry.py

from network_config import NETWORKS


class NetworkRegistry:
    """Registry for GNOMEfinance blockchain networks."""

    def __init__(self):
        self.networks = {}

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

        for network_id in self.networks:

            info = NETWORKS[
                network_id
            ]

            print(
                f"{info['name']} "
                f"({info['symbol']})"
            )


if __name__ == "__main__":

    registry = NetworkRegistry()

    print(
        "Available networks:"
    )

    for network_id in (
        registry.list_available()
    ):

        info = NETWORKS[
            network_id
        ]

        print(
            f"- {info['name']} "
            f"({info['symbol']})"
        )

    print()

    print(
        "Registry ready."
    )
