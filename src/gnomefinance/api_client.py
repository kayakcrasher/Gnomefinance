"""Shared HTTP client.

All network traffic goes through here, so error handling lives in one place
and tests can swap in a fake client.
"""

import requests

from . import __version__
from .config import API_TIMEOUT
from .errors import APIError, NetworkError


class APIClient:
    def __init__(self, base_url="", timeout=API_TIMEOUT, headers=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": f"GNOMEfinance/{__version__}"}
        )
        if headers:
            self.session.headers.update(headers)

    def build_url(self, endpoint):
        if endpoint.startswith("http") or not self.base_url:
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None):
        """GET a URL and return the decoded JSON."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, payload):
        """POST JSON and return the decoded JSON."""
        return self._request("POST", endpoint, json=payload)

    def rpc(self, method, params=None):
        """Make a JSON-RPC 2.0 call (used by Solana and Ethereum)."""
        data = self.post(
            "",
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []},
        )

        if not isinstance(data, dict):
            raise APIError("RPC returned an unexpected response.")

        if data.get("error"):
            error = data["error"]
            message = error.get("message") if isinstance(error, dict) else error
            raise APIError(f"RPC error: {message}")

        return data.get("result")

    def _request(self, method, endpoint, **kwargs):
        url = self.build_url(endpoint)

        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
        except requests.exceptions.Timeout as error:
            raise NetworkError(f"Request to {url} timed out.") from error
        except requests.exceptions.ConnectionError as error:
            raise NetworkError(f"Could not connect to {url}.") from error
        except requests.exceptions.RequestException as error:
            raise NetworkError(f"Request failed: {error}") from error

        if response.status_code == 429:
            raise APIError("Rate limited by the API. Try again in a minute.")

        if response.status_code == 404:
            raise APIError("Not found.")

        if not response.ok:
            raise APIError(f"API returned HTTP {response.status_code}.")

        try:
            return response.json()
        except ValueError as error:
            raise APIError("API returned invalid JSON.") from error
