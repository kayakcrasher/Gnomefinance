import urllib.request
import json


def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())

    return data["bitcoin"]["usd"]
