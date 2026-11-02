"""The single list of assets GNOMEfinance knows about.

To support a new coin, add one entry here. ``coingecko_id`` is the id used
by CoinGecko's API; ``chain`` is set when we can read wallet balances for it.
"""

ASSETS = {
    "bitcoin": {
        "name": "Bitcoin",
        "symbol": "BTC",
        "icon": "₿",
        "coingecko_id": "bitcoin",
        "chain": "bitcoin",
    },
    "ethereum": {
        "name": "Ethereum",
        "symbol": "ETH",
        "icon": "Ξ",
        "coingecko_id": "ethereum",
        "chain": "ethereum",
    },
    "solana": {
        "name": "Solana",
        "symbol": "SOL",
        "icon": "◎",
        "coingecko_id": "solana",
        "chain": "solana",
    },
    "cardano": {
        "name": "Cardano",
        "symbol": "ADA",
        "icon": "₳",
        "coingecko_id": "cardano",
        "chain": None,
    },
    "avalanche": {
        "name": "Avalanche",
        "symbol": "AVAX",
        "icon": "▲",
        "coingecko_id": "avalanche-2",
        "chain": None,
    },
}


def get_asset(asset_id):
    """Return asset info, or raise KeyError for an unknown asset."""
    return ASSETS[asset_id]


def is_known(asset_id):
    return asset_id in ASSETS


def symbol(asset_id):
    return ASSETS[asset_id]["symbol"]


def find_by_symbol(text):
    """Accept either an id ("bitcoin") or a symbol ("BTC")."""
    text = text.strip().lower()

    if text in ASSETS:
        return text

    for asset_id, info in ASSETS.items():
        if info["symbol"].lower() == text:
            return asset_id

    return None
