# chart_data.py

from portfolio_value import PortfolioValue


class ChartData:
    """Prepare portfolio data for charts."""

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.portfolio_value = PortfolioValue(portfolio)

    def get_asset_values(self):
        """Return asset names and USD values."""

        values = self.portfolio_value.get_values()

        return {
            network.upper(): value
            for network, value in values.items()
        }

    def get_labels(self):
        """Return chart labels."""

        return list(self.get_asset_values().keys())

    def get_values(self):
        """Return chart values."""

        return list(self.get_asset_values().values())

    def get_chart_data(self):
        """Return complete chart data."""

        return {
            "labels": self.get_labels(),
            "values": self.get_values(),
        }


if __name__ == "__main__":
    from portfolio import Portfolio

    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    chart_data = ChartData(portfolio)

    print(chart_data.get_chart_data())
