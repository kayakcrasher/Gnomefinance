# portfolio_service.py

from portfolio import Portfolio
from portfolio_value import PortfolioValue


class PortfolioService:
    """Provide portfolio data to GNOMEfinance."""

    def __init__(self):
        self.portfolio = Portfolio()

    def add_asset(self, network, amount):
        """Add an asset to the portfolio."""

        self.portfolio.add_asset(
            network,
            amount,
        )

    def get_assets(self):
        """Return all portfolio holdings."""

        return self.portfolio.get_all_assets()

    def get_values(self):
        """Return USD values for each asset."""

        value_service = PortfolioValue(
            self.portfolio
        )

        return value_service.get_values()

    def get_total_value(self):
        """Return total portfolio USD value."""

        value_service = PortfolioValue(
            self.portfolio
        )

        return value_service.get_total()

    def get_summary(self):
        """Return portfolio holdings and USD values."""

        assets = self.get_assets()
        values = self.get_values()

        summary = {}

        for network, amount in assets.items():
            summary[network] = {
                "amount": amount,
                "value_usd": values.get(
                    network,
                    0,
                ),
            }

        return summary


if __name__ == "__main__":

    service = PortfolioService()

    service.add_asset(
        "bitcoin",
        0.065,
    )

    service.add_asset(
        "solana",
        5.4,
    )

    service.add_asset(
        "cardano",
        1500,
    )

    service.add_asset(
        "avalanche",
        25,
    )

    print("GNOMEfinance Portfolio")
    print("----------------------")

    for network, data in service.get_summary().items():

        print(
            f"{network}: "
            f"{data['amount']} "
            f"= ${data['value_usd']:,.2f}"
        )

    print("----------------------")

    print(
        f"TOTAL: "
        f"${service.get_total_value():,.2f}"
    )
