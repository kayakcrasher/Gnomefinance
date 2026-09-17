# portfolio_input.py

from network_config import NETWORKS


class PortfolioInput:
    """Handle portfolio input for GNOMEfinance."""

    def __init__(self, portfolio):
        self.portfolio = portfolio

    def add_asset(self, network, amount):
        """Add an asset to the portfolio."""

        if network not in NETWORKS:
            raise ValueError(
                f"Unknown network: {network}"
            )

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero."
            )

        self.portfolio.add_asset(
            network,
            amount,
        )

    def set_asset(self, network, amount):
        """Set an asset to an exact amount."""

        if network not in NETWORKS:
            raise ValueError(
                f"Unknown network: {network}"
            )

        if amount < 0:
            raise ValueError(
                "Amount cannot be negative."
            )

        self.portfolio.assets[network] = amount

    def remove_asset(self, network):
        """Remove an asset from the portfolio."""

        if network in self.portfolio.assets:
            del self.portfolio.assets[network]

    def clear(self):
        """Remove all assets."""

        self.portfolio.assets.clear()

    def get_asset_amount(self, network):
        """Return the amount held for an asset."""

        return self.portfolio.get_amount(
            network
        )

    def get_assets(self):
        """Return all portfolio holdings."""

        return self.portfolio.get_all_assets()


if __name__ == "__main__":

    from portfolio import Portfolio

    portfolio = Portfolio()

    inputs = PortfolioInput(
        portfolio
    )

    inputs.add_asset(
        "bitcoin",
        0.065,
    )

    inputs.add_asset(
        "solana",
        5.4,
    )

    inputs.set_asset(
        "cardano",
        1500,
    )

    print(
        "GNOMEfinance Portfolio Input"
    )

    print(
        "----------------------------"
    )

    for network, amount in (
        inputs.get_assets().items()
    ):

        symbol = NETWORKS[
            network
        ]["symbol"]

        print(
            f"{symbol}: {amount}"
        )
