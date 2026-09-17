# portfolio_chart.py

import matplotlib.pyplot as plt


def create_portfolio_chart(values):
    """Create a portfolio allocation chart."""

    if not values:
        print("No portfolio data available.")
        return

    labels = list(values.keys())
    amounts = list(values.values())

    plt.figure(figsize=(8, 5))

    plt.bar(labels, amounts)

    plt.title("GNOMEfinance Portfolio")
    plt.xlabel("Asset")
    plt.ylabel("USD Value")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from portfolio import Portfolio
    from portfolio_value import PortfolioValue

    portfolio = Portfolio()

    portfolio.add_asset("bitcoin", 0.065)
    portfolio.add_asset("solana", 5.4)
    portfolio.add_asset("cardano", 1500)
    portfolio.add_asset("avalanche", 25)

    portfolio_value = PortfolioValue(portfolio)

    values = portfolio_value.get_values()

    create_portfolio_chart(values)
