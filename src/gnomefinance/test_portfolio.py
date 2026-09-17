import unittest

from .portfolio import Portfolio


class TestPortfolio(unittest.TestCase):

    def test_new_portfolio_is_empty(self):
        portfolio = Portfolio()

        self.assertEqual(
            portfolio.get_all_assets(),
            {},
        )

    def test_add_asset(self):
        portfolio = Portfolio()

        portfolio.add_asset(
            "bitcoin",
            0.065,
        )

        self.assertEqual(
            portfolio.get_amount("bitcoin"),
            0.065,
        )

    def test_add_asset_accumulates_amount(self):
        portfolio = Portfolio()

        portfolio.add_asset(
            "bitcoin",
            0.065,
        )

        portfolio.add_asset(
            "bitcoin",
            0.035,
        )

        self.assertEqual(
            portfolio.get_amount("bitcoin"),
            0.1,
        )

    def test_multiple_assets(self):
        portfolio = Portfolio()

        portfolio.add_asset(
            "bitcoin",
            0.065,
        )

        portfolio.add_asset(
            "solana",
            5.4,
        )

        portfolio.add_asset(
            "cardano",
            1500,
        )

        self.assertEqual(
            portfolio.get_amount("bitcoin"),
            0.065,
        )

        self.assertEqual(
            portfolio.get_amount("solana"),
            5.4,
        )

        self.assertEqual(
            portfolio.get_amount("cardano"),
            1500,
        )

    def test_unknown_network_raises_error(self):
        portfolio = Portfolio()

        with self.assertRaises(ValueError):
            portfolio.add_asset(
                "not_a_real_network",
                100,
            )

    def test_negative_amount_raises_error(self):
        portfolio = Portfolio()

        with self.assertRaises(ValueError):
            portfolio.add_asset(
                "bitcoin",
                -1,
            )

    def test_unknown_asset_returns_zero(self):
        portfolio = Portfolio()

        self.assertEqual(
            portfolio.get_amount("bitcoin"),
            0,
        )

    def test_get_all_assets(self):
        portfolio = Portfolio()

        portfolio.add_asset(
            "bitcoin",
            0.065,
        )

        portfolio.add_asset(
            "solana",
            5.4,
        )

        self.assertEqual(
            portfolio.get_all_assets(),
            {
                "bitcoin": 0.065,
                "solana": 5.4,
            },
        )


if __name__ == "__main__":
    unittest.main()
