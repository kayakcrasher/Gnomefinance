import unittest
from unittest.mock import patch

from .web_app import app


class TestWebApp(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            b"GNOMEfinance",
            response.data,
        )

    @patch("gnomefinance.web_app.get_price")
    def test_prices_endpoint(self, mock_get_price):
        mock_get_price.side_effect = [
            65000.0,
            3500.0,
            150.0,
        ]

        response = self.client.get(
            "/api/prices"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.get_json(),
            {
                "bitcoin": 65000.0,
                "ethereum": 3500.0,
                "solana": 150.0,
            },
        )

    @patch("gnomefinance.web_app.get_history")
    def test_history_endpoint(self, mock_get_history):
        mock_get_history.return_value = [
            [1000, 65000.0],
            [2000, 65500.0],
        ]

        response = self.client.get(
            "/api/history/bitcoin"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.get_json(),
            [
                [1000, 65000.0],
                [2000, 65500.0],
            ],
        )

        mock_get_history.assert_called_once_with(
            "bitcoin",
            days=7,
        )

    def test_portfolio_endpoint(self):
        response = self.client.get(
            "/api/portfolio"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.get_json(),
            {},
        )


if __name__ == "__main__":
    unittest.main()
