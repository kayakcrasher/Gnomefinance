# portfolio.py

from network_config import NETWORKS


class Portfolio:
    """Manage GNOMEfinance portfolio assets."""

    def __init__(self):
        self.assets = {}

    def add_asset(self, network, amount):
        """Add an amount of an asset to the portfolio."""
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}")

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        self.assets[network] = self.assets.get(network, 0) + amount

    def get_amount(self, network):
        """Return the amount held for a network."""
        return self.assets.get(network, 0)

    def get_all_assets(self):
        """Return all portfolio assets."""
        return self.assets

    def display(self):
        """Display the current portfolio."""
        print("GNOMEfinance Portfolio")
        print("----------------------")

        for network, amount in self.assets.items():
            info = NETWORKS[network]

            print(
                f"{info['name']}: "
                f"{amount} {info['symbol']}"
            )


if __name__ == "__main__":
    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    portfolio.display()
