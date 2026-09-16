import urllib.request
import json

from .config import API_URL, CURRENCY
from .errors import PriceAPIError
from .cache import PriceCache


cache = PriceCache(duration=30)


def get_price(coin_id):
    cached_price = cache.get(coin_id)

    if cached_price is not None:
        return cached_price

    url = (
        f"{API_URL}/simple/price"
        f"?ids={coin_id}&vs_currencies={CURRENCY}"
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())

        price = data[coin_id][CURRENCY]

        cache.save(coin_id, price)

        return price

    except Exception as error:
        raise PriceAPIError(
            f"Could not get price for {coin_id}: {error}"
        )
