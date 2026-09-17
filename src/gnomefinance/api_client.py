# api_client.py

import requests


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

        except requests.exceptions.Timeout:
            print(
                "GNOMEfinance API error: "
                "Request timed out."
            )

        except requests.exceptions.ConnectionError:
            print(
                "GNOMEfinance API error: "
                "Could not connect to the API."
            )

        except requests.exceptions.HTTPError as error:
            print(
                "GNOMEfinance API error: "
                f"HTTP error: {error}"
            )

        except requests.exceptions.RequestException as error:
            print(
                "GNOMEfinance API error: "
                f"{error}"
            )

        return {}


if __name__ == "__main__":

    client = APIClient(
        "https://api.coingecko.com/api/v3"
    )

    data = client.get(
        "/simple/price",
        {
            "ids": "bitcoin,solana",
            "vs_currencies": "usd",
        },
    )

    print("GNOMEfinance API Test")
    print("---------------------")
    print(data)
