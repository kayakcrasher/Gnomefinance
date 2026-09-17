# api_client.py

import requests

from error_handler import (
    APIError,
    NetworkError,
)


class APIClient:
    """Reusable HTTP client for GNOMEfinance."""

    def __init__(
        self,
        base_url=None,
        timeout=10,
    ):
        self.base_url = base_url
        self.timeout = timeout

    def build_url(self, endpoint):
        """Build the complete API URL."""

        if self.base_url:
            return (
                f"{self.base_url.rstrip('/')}/"
                f"{endpoint.lstrip('/')}"
            )

        return endpoint

    def get(self, endpoint, params=None):
        """Send a GET request and return JSON data."""

        url = self.build_url(endpoint)

        try:

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout as error:

            raise NetworkError(
                "The API request timed out."
            ) from error

        except requests.exceptions.ConnectionError as error:

            raise NetworkError(
                "Could not connect to the API."
            ) from error

        except requests.exceptions.HTTPError as error:

            raise APIError(
                f"API returned an HTTP error: "
                f"{error}"
            ) from error

        except requests.exceptions.JSONDecodeError as error:

            raise APIError(
                "The API returned invalid JSON."
            ) from error

        except requests.exceptions.RequestException as error:

            raise APIError(
                f"API request failed: {error}"
            ) from error


if __name__ == "__main__":

    client = APIClient(
        "https://api.coingecko.com/api/v3"
    )

    try:

        data = client.get(
            "/simple/price",
            {
                "ids": "bitcoin,solana",
                "vs_currencies": "usd",
            },
        )

        print(
            "GNOMEfinance API Test"
        )

        print(
            "---------------------"
        )

        print(data)

    except (
        APIError,
        NetworkError,
    ) as error:

        print(
            "GNOMEfinance API error:",
            error,
        )
