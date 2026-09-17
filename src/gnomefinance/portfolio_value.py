# portfolio_value.py

from portfolio import Portfolio
from price_service import get_prices


def calculate_values(portfolio):
    """Calculate the USD value of each portfolio asset."""

    prices = get_prices(portfolio.get_all_assets())

    values = {}

    for network, amount in portfolio.get_all_assets().items():
        price = prices.get(network, 0)
        values[network] = amount * price

    return values


def calculate_total(values):
    """Calculate total portfolio value."""

    return sum(values.values())


def display_values(portfolio):
    """Display portfolio values and total."""

    values = calculate_values(portfolio)
    total = calculate_total(values)

    print("GNOMEfinance Portfolio Value")
    print("----------------------------")

    for network, value in values.items():
        print(f"{network}: ${value:,.2f}")

    print("----------------------------")
    print(f"TOTAL: ${total:,.2f}")


if __name__ == "__main__":
    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    display_values(portfolio)
