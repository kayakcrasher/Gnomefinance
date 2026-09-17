import unittest
from unittest.mock import patch

from .history import get_history
from .errors import PriceAPIError


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return self.data


class TestHistory(unittest.TestCase):

    @patch("gnomefinance.history.urllib.request.urlopen")
    def test_get_history_returns_prices(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(
            b'{"prices":[[1000,65000.0],[2000,65500.0]]}'
        )

        history = get_history("bitcoin", days=7)

        self.assertEqual(
            history,
            [
                [1000, 65000.0],
                [2000, 65500.0],
            ],
        )

    @patch("gnomefinance.history.urllib.request.urlopen")
    def test_get_history_uses_requested_days(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(
            b'{"prices":[]}'
        )

        get_history("solana", days=30)

        url = mock_urlopen.call_args.args[0]

        self.assertIn(
            "/coins/solana/market_chart",
            url,
        )

        self.assertIn(
            "vs_currency=usd",
            url,
        )

        self.assertIn(
            "days=30",
            url,
        )

    @patch("gnomefinance.history.urllib.request.urlopen")
    def test_get_history_converts_api_failure_to_price_error(
        self,
        mock_urlopen,
    ):
        mock_urlopen.side_effect = OSError(
            "network unavailable"
        )

        with self.assertRaises(PriceAPIError):
            get_history("bitcoin")


if __name__ == "__main__":
    unittest.main()
