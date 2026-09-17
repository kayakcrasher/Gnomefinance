from network_interface import NetworkInterface
from solana_rpc import SolanaRPC


class SolanaNetwork(NetworkInterface):
    """Solana network adapter for GNOMEfinance."""

    def __init__(
        self,
        rpc_url="https://api.mainnet-beta.solana.com",
        timeout=10,
    ):
        self.rpc = SolanaRPC(
            rpc_url=rpc_url,
            timeout=timeout,
        )

    def get_balance(self, address):
        """Return the SOL balance for an address."""
        return self.rpc.get_balance_sol(address)

    def get_transaction(self, transaction_id):
        """Transaction lookup will be connected next."""
        raise NotImplementedError(
            "Solana transaction lookup is not connected yet."
        )

    def validate_address(self, address):
        """Basic Solana address validation."""
        if not isinstance(address, str):
            return False

        if not address:
            return False

        return 32 <= len(address) <= 44

    def get_network_name(self):
        return "Solana"

    def get_symbol(self):
        return "SOL"

    def is_connected(self):
        """Check whether the Solana RPC is reachable."""
        return self.rpc.is_connected()


if __name__ == "__main__":
    solana = SolanaNetwork()

    print("GNOMEfinance Solana Network")
    print("----------------------------")
    print("Network:", solana.get_network_name())
    print("Symbol:", solana.get_symbol())
    print("RPC connected:", solana.is_connected())
