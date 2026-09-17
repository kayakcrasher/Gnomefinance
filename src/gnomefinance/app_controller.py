# app_controller.py

from gui_data import GUIData
from market_data import MarketData
from portfolio_allocation import PortfolioAllocation
from portfolio_input import PortfolioInput
from portfolio_storage import PortfolioStorage


class AppController:
    """Coordinate GNOMEfinance application logic."""

    def __init__(self):
        self.data = GUIData()
        self.market = MarketData()
        self.storage = PortfolioStorage()

    def get_portfolio(self):
        """Return the current portfolio."""

        return (
            self.data
            .portfolio_service
            .portfolio
        )

    def get_portfolio_input(self):
        """Return the portfolio input handler."""

        return PortfolioInput(
            self.get_portfolio()
        )

    def set_holding(
        self,
        network,
        amount,
    ):
        """Set an exact asset holding."""

        inputs = self.get_portfolio_input()

        inputs.set_asset(
            network,
            amount,
        )

    def remove_holding(
        self,
        network,
    ):
        """Remove an asset."""

        inputs = self.get_portfolio_input()

        inputs.remove_asset(
            network
        )

    def clear_portfolio(self):
        """Remove all portfolio assets."""

        inputs = self.get_portfolio_input()

        inputs.clear()

    def save_portfolio(self):
        """Save the current portfolio."""

        self.storage.save(
            self.get_portfolio()
        )

    def load_portfolio(self):
        """Load the saved portfolio."""

        return self.storage.load(
            self.get_portfolio()
        )

    def get_dashboard_data(self):
        """Return portfolio dashboard data."""

        return (
            self.data
            .get_dashboard_data()
        )

    def get_market_data(self):
        """Return market data for portfolio assets."""

        portfolio = self.get_portfolio()

        networks = list(
            portfolio
            .get_all_assets()
            .keys()
        )

        return self.market.get_market_data(
            networks
        )

    def get_allocation_data(self):
        """Return portfolio allocation data."""

        allocation = PortfolioAllocation(
            self.get_portfolio()
        )

        return allocation.get_summary()

    def refresh_market_data(self):
        """Clear the market cache."""

        self.market.clear_cache()

    def get_complete_dashboard(self):
        """Return all data needed by the GUI."""

        return {
            "portfolio": self.get_dashboard_data(),
            "market": self.get_market_data(),
            "allocation": self.get_allocation_data(),
        }


if __name__ == "__main__":

    controller = AppController()

    controller.set_holding(
        "bitcoin",
        0.065,
    )

    controller.set_holding(
        "solana",
        5.4,
    )

    controller.save_portfolio()

    dashboard = (
        controller
        .get_complete_dashboard()
    )

    print(
        "GNOMEfinance Controller"
    )

    print(
        "----------------------"
    )

    print(
        dashboard
    )
