# api_client.py

import requests


class APIClient:
    """Reusable HTTP client for GNOMEfinance."""

    def __init__(self, base_url=None):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        """Send a GET request to an API endpoint."""

        if self.base_url:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        else:
            url = endpoint

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()


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

    print(data)
