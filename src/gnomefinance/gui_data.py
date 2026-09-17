# gui_data.py

from portfolio_service import PortfolioService
from portfolio_value import PortfolioValue


class GUIData:
    """Provide clean data for the GNOMEfinance GUI."""

    def __init__(self):
        self.portfolio_service = PortfolioService()

    def add_asset(self, network, amount):
        """Add an asset to the portfolio."""
        self.portfolio_service.add_asset(network, amount)

    def get_dashboard_data(self):
        """Return everything the dashboard needs."""

        portfolio = self.portfolio_service.portfolio

        value_service = PortfolioValue(portfolio)

        assets = portfolio.get_all_assets()
        values = value_service.get_values()

        dashboard = {
            "assets": {},
            "total_value": value_service.get_total(),
        }

        for network, amount in assets.items():
            dashboard["assets"][network] = {
                "amount": amount,
                "value_usd": values.get(network, 0),
            }

        return dashboard


if __name__ == "__main__":
    gui_data = GUIData()

    gui_data.add_asset("bitcoin", 0.065)
    gui_data.add_asset("solana", 5.4)
    gui_data.add_asset("cardano", 1500)
    gui_data.add_asset("avalanche", 25)

    data = gui_data.get_dashboard_data()

    print("GNOMEfinance Dashboard")
    print("----------------------")

    for network, asset in data["assets"].items():
        print(
            f"{network}: "
            f"{asset['amount']} "
            f"= ${asset['value_usd']:,.2f}"
        )

    print("----------------------")
    print(f"TOTAL: ${data['total_value']:,.2f}")
