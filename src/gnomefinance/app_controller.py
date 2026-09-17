from gui_data import GUIData
from market_data import MarketData
from portfolio_allocation import PortfolioAllocation
from portfolio_input import PortfolioInput
from portfolio_storage import PortfolioStorage
from wallet_service import WalletService


class AppController:
    """Coordinate GNOMEfinance application logic."""

    def __init__(self):
        self.data = GUIData()
        self.market = MarketData()
        self.storage = PortfolioStorage()
        self.wallet = WalletService()

    # ---------------------------------------------------------
    # Portfolio
    # ---------------------------------------------------------

    def get_portfolio(self):
        return self.data.portfolio_service.portfolio

    def get_portfolio_input(self):
        return PortfolioInput(self.get_portfolio())

    def set_holding(self, network, amount):
        inputs = self.get_portfolio_input()
        inputs.set_asset(network, amount)

    def remove_holding(self, network):
        inputs = self.get_portfolio_input()
        inputs.remove_asset(network)

    def clear_portfolio(self):
        inputs = self.get_portfolio_input()
        inputs.clear()

    # ---------------------------------------------------------
    # Portfolio Storage
    # ---------------------------------------------------------

    def save_portfolio(self):
        self.storage.save(self.get_portfolio())

    def load_portfolio(self):
        return self.storage.load(self.get_portfolio())

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------

    def get_dashboard_data(self):
        return self.data.get_dashboard_data()

    def get_market_data(self):
        portfolio = self.get_portfolio()

        networks = list(
            portfolio.get_all_assets().keys()
        )

        return self.market.get_market_data(networks)

    def get_allocation_data(self):
        allocation = PortfolioAllocation(
            self.get_portfolio()
        )

        return allocation.get_summary()

    def refresh_market_data(self):
        self.market.clear_cache()

    def get_complete_dashboard(self):
        return {
            "portfolio": self.get_dashboard_data(),
            "market": self.get_market_data(),
            "allocation": self.get_allocation_data(),
        }

    # ---------------------------------------------------------
    # Wallet / Blockchain
    # ---------------------------------------------------------

    def get_wallet_balance(self, network, address):
        """Get a live blockchain wallet balance."""

        return self.wallet.get_balance(
            network,
            address,
        )

    def get_wallet_transaction(
        self,
        network,
        transaction_id,
    ):
        """Get blockchain transaction information."""

        return self.wallet.get_transaction(
            network,
            transaction_id,
        )

    def check_network_connection(self, network):
        """Check whether a blockchain network is reachable."""

        return self.wallet.is_connected(network)

    def get_network_info(self, network):
        """Get basic information about a blockchain network."""

        return self.wallet.get_network_info(network)

    def get_network_status(self):
        """Get connection status for registered networks."""

        status = {}

        for network_id in self.wallet.registry.list_registered():
            status[network_id] = (
                self.wallet.get_network_info(network_id)
            )

        return status


if __name__ == "__main__":
    controller = AppController()

    print("GNOMEfinance Controller")
    print("-----------------------")

    status = controller.get_network_status()

    for network_id, info in status.items():
        print(
            f"{info['name']} "
            f"({info['symbol']}): "
            f"{'CONNECTED' if info['connected'] else 'OFFLINE'}"
        )
