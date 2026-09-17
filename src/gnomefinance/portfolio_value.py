# portfolio_value.py

from price_service import PriceService


class PortfolioValue:
    """Calculate the USD value of a portfolio."""

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.price_service = PriceService()

    def get_values(self):
        """Calculate the USD value of each asset."""

        assets = self.portfolio.get_all_assets()
        prices = self.price_service.get_prices(assets)

        values = {}

        for network, amount in assets.items():
            price = prices.get(network, 0)
            values[network] = amount * price

        return values

    def get_total(self):
        """Calculate the total portfolio value."""

        values = self.get_values()

        return sum(values.values())

    def display(self):
        """Display portfolio values."""

        values = self.get_values()

        print("GNOMEfinance Portfolio Value")
        print("----------------------------")

        for network, value in values.items():
            print(f"{network}: ${value:,.2f}")

        print("----------------------------")
        print(f"TOTAL: ${self.get_total():,.2f}")


if __name__ == "__main__":
    from portfolio import Portfolio

    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    portfolio_value = PortfolioValue(portfolio)

    portfolio_value.display()
