# solana_network.py

from network_interface import NetworkInterface


class SolanaNetwork(NetworkInterface):
    """Solana network adapter for GNOMEfinance."""

    def __init__(
        self,
        rpc_url="https://api.mainnet-beta.solana.com",
    ):
        self.rpc_url = rpc_url

    def get_balance(self, address):
        """Return the SOL balance for an address."""

        raise NotImplementedError(
            "Solana balance lookup is not "
            "connected yet."
        )

    def get_transaction(
        self,
        transaction_id,
    ):
        """Return transaction information."""

        raise NotImplementedError(
            "Solana transaction lookup is "
            "not connected yet."
        )

    def validate_address(self, address):
        """Perform basic Solana address validation."""

        if not isinstance(
            address,
            str,
        ):
            return False

        if not address:
            return False

        return len(address) >= 32

    def get_network_name(self):
        """Return the network name."""

        return "Solana"

    def get_symbol(self):
        """Return the native asset symbol."""

        return "SOL"

    def is_connected(self):
        """Return whether the RPC endpoint is configured."""

        return bool(self.rpc_url)


if __name__ == "__main__":

    solana = SolanaNetwork()

    print(
        "GNOMEfinance Solana Adapter"
    )

    print(
        "----------------------------"
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
        "RPC:",
        solana.rpc_url,
    )

    print(
        "Configured:",
        solana.is_connected(),
    )
