import urllib.request
import json

from .config import API_URL, CURRENCY
from .errors import PriceAPIError


def get_price(coin_id):
    url = (
        f"{API_URL}/simple/price"
        f"?ids={coin_id}&vs_currencies={CURRENCY}"
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())

        return data[coin_id][CURRENCY]

    except Exception as error:
        raise PriceAPIError(
            f"Could not get price for {coin_id}: {error}"
        )
