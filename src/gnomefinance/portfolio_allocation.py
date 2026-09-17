# portfolio_allocation.py

from portfolio_value import PortfolioValue


class PortfolioAllocation:
    """Calculate portfolio allocation percentages."""

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.portfolio_value = PortfolioValue(portfolio)

    def get_values(self):
        """Return USD values for each asset."""
        return self.portfolio_value.get_values()

    def get_total(self):
        """Return total portfolio value."""
        return self.portfolio_value.get_total()

    def get_percentages(self):
        """Return each asset's percentage of the portfolio."""

        values = self.get_values()
        total = self.get_total()

        if total <= 0:
            return {
                network: 0
                for network in values
            }

        return {
            network: (value / total) * 100
            for network, value in values.items()
        }

    def get_summary(self):
        """Return values and allocation percentages."""

        values = self.get_values()
        percentages = self.get_percentages()

        summary = {}

        for network in values:
            summary[network] = {
                "value_usd": values[network],
                "percentage": percentages[network],
            }

        return summary


if __name__ == "__main__":
    from portfolio import Portfolio

    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    allocation = PortfolioAllocation(portfolio)

    for network, data in allocation.get_summary().items():
        print(
            f"{network.upper()}: "
            f"${data['value_usd']:,.2f} "
            f"({data['percentage']:.2f}%)"
        )
