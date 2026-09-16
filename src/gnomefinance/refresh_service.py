from .coins import COINS
from .prices import force_refresh
from .price_data import Price
from .refresh import RefreshController
from .errors import PriceAPIError


class RefreshService:
    def __init__(self, cooldown=10):
        self.controller = RefreshController(cooldown)

    def refresh_all(self):
        if not self.controller.refresh():
            return []

        prices = []

        for coin_id, symbol in COINS.items():
            try:
                usd_price = force_refresh(coin_id)

                price = Price(
                    coin_id,
                    symbol,
                    usd_price
                )

                prices.append(price)

            except PriceAPIError as error:
                print(f"Warning: {error}")

        return prices
