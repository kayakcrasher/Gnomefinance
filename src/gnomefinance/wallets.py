# wallets.py

from network_config import NETWORKS


class Wallet:
    """Basic wallet foundation for GNOMEfinance."""

    def __init__(self, network, address=None):
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}")

        self.network = network
        self.address = address

    def set_address(self, address):
        """Set the wallet address."""
        self.address = address

    def get_network(self):
        """Return the wallet network."""
        return NETWORKS[self.network]["name"]

    def get_address(self):
        """Return the wallet address."""
        return self.address

    def display(self):
        """Display wallet information."""
        network = NETWORKS[self.network]

        print(f"Network: {network['name']}")
        print(f"Symbol:  {network['symbol']}")
        print(f"Address: {self.address or 'Not connected'}")


if __name__ == "__main__":
    btc_wallet = Wallet("bitcoin")
    sol_wallet = Wallet("solana")

    btc_wallet.display()
    print()
    sol_wallet.display()
