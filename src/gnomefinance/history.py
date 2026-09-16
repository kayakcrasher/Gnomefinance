import urllib.request
import json

from .config import API_URL, CURRENCY
from .errors import PriceAPIError


def get_history(coin_id, days=7):
    url = (
        f"{API_URL}/coins/{coin_id}/market_chart"
        f"?vs_currency={CURRENCY}"
        f"&days={days}"
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())

        return data["prices"]

    except Exception as error:
        raise PriceAPIError(
            f"Could not get history for {coin_id}: {error}"
        )
