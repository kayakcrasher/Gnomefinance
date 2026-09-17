import unittest
from unittest.mock import patch

from .prices import get_price, force_refresh
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


class TestPrices(unittest.TestCase):

    @patch("gnomefinance.prices.cache.get", return_value=123.45)
    def test_get_price_uses_cache(self, mock_cache):
        price = get_price("bitcoin")

        self.assertEqual(price, 123.45)
        mock_cache.assert_called_once_with("bitcoin")

    @patch("gnomefinance.prices.cache")
    @patch("gnomefinance.prices.urllib.request.urlopen")
    def test_get_price_reads_api(self, mock_urlopen, mock_cache):
        mock_cache.get.return_value = None

        mock_urlopen.return_value = FakeResponse(
            b'{"bitcoin":{"usd":65000.0}}'
        )

        price = get_price("bitcoin")

        self.assertEqual(price, 65000.0)
        mock_cache.save.assert_called_once_with(
            "bitcoin",
            65000.0,
        )

    @patch("gnomefinance.prices.cache")
    @patch("gnomefinance.prices.urllib.request.urlopen")
    def test_force_refresh_updates_price(
        self,
        mock_urlopen,
        mock_cache,
    ):
        mock_urlopen.return_value = FakeResponse(
            b'{"solana":{"usd":150.25}}'
        )

        price = force_refresh("solana")

        self.assertEqual(price, 150.25)

        mock_cache.save.assert_called_once_with(
            "solana",
            150.25,
        )

    @patch("gnomefinance.prices.cache")
    @patch("gnomefinance.prices.urllib.request.urlopen")
    def test_get_price_converts_api_failure_to_price_error(
        self,
        mock_urlopen,
        mock_cache,
    ):
        mock_cache.get.return_value = None

        mock_urlopen.side_effect = OSError(
            "network unavailable"
        )

        with self.assertRaises(PriceAPIError):
            get_price("bitcoin")


if __name__ == "__main__":
    unittest.main()
