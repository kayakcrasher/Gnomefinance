import urllib.request
import json

from .config import API_URL, CURRENCY


def get_price(coin_id):
    url = (
        f"{API_URL}/simple/price"
        f"?ids={coin_id}&vs_currencies={CURRENCY}"
    )

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    return data[coin_id][CURRENCY]
