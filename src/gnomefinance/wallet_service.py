from network_registry import NetworkRegistry


class WalletService:
    """Manage read-only blockchain wallet operations."""

    def __init__(self, registry=None):
        self.registry = registry or NetworkRegistry()

    def get_network(self, network_id):
        """Return a registered blockchain network."""
        network = self.registry.get(network_id)

        if network is None:
            raise ValueError(
                f"Network is not registered: {network_id}"
            )

        return network

    def get_balance(self, network_id, address):
        """Get a wallet balance from a blockchain network."""
        network = self.get_network(network_id)

        if not network.validate_address(address):
            raise ValueError(
                f"Invalid {network.get_network_name()} address."
            )

        return network.get_balance(address)

    def get_transaction(self, network_id, transaction_id):
        """Get transaction information."""
        network = self.get_network(network_id)

        return network.get_transaction(transaction_id)

    def is_connected(self, network_id):
        """Check whether a network is reachable."""
        network = self.get_network(network_id)

        return network.is_connected()

    def get_network_info(self, network_id):
        """Return basic information about a registered network."""
        network = self.get_network(network_id)

        return {
            "name": network.get_network_name(),
            "symbol": network.get_symbol(),
            "connected": network.is_connected(),
        }

    def display_network_status(self):
        """Display connection status for registered networks."""
        print("GNOMEfinance Network Status")
        print("---------------------------")

        for network_id in self.registry.list_registered():
            network = self.registry.get(network_id)
            connected = network.is_connected()

            status = (
                "CONNECTED"
                if connected
                else "OFFLINE"
            )

            print(
                f"{network.get_network_name()} "
                f"({network.get_symbol()}): "
                f"{status}"
            )


if __name__ == "__main__":
    wallet_service = WalletService()
    wallet_service.display_network_status()
