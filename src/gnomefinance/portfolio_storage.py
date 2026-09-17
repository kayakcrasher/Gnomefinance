# portfolio_storage.py

import json
from pathlib import Path


class PortfolioStorage:
    """Save and load GNOMEfinance portfolio data."""

    def __init__(self, filename="portfolio.json"):
        self.filename = Path(filename)

    def save(self, portfolio):
        """Save the portfolio to a JSON file."""

        data = portfolio.get_all_assets()

        with self.filename.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )

    def load(self, portfolio):
        """Load portfolio data from a JSON file."""

        if not self.filename.exists():
            return False

        with self.filename.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        portfolio.clear()

        for network, amount in data.items():

            portfolio.add_asset(
                network,
                float(amount),
            )

        return True

    def exists(self):
        """Return True if saved portfolio exists."""

        return self.filename.exists()

    def delete(self):
        """Delete the saved portfolio."""

        if self.filename.exists():
            self.filename.unlink()


if __name__ == "__main__":

    from portfolio import Portfolio

    portfolio = Portfolio()

    portfolio.add_asset(
        "bitcoin",
        0.065,
    )

    portfolio.add_asset(
        "solana",
        5.4,
    )

    storage = PortfolioStorage()

    storage.save(portfolio)

    print(
        "Portfolio saved."
    )

    loaded = Portfolio()

    storage.load(loaded)

    print(
        "Loaded portfolio:"
    )

    loaded.display()
