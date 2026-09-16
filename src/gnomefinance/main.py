from .coins import COINS
from .prices import get_price
from .price_data import Price
from .display import show_header, show_price, show_footer
from .refresh import RefreshController
from .errors import PriceAPIError


def get_prices():
    prices = []

    for coin_id, symbol in COINS.items():
        try:
            usd_price = get_price(coin_id)

            price = Price(
                coin_id,
                symbol,
                usd_price
            )

            prices.append(price)

        except PriceAPIError as error:
            print(f"Warning: {error}")
            print()

    return prices


def main():
    refresh_controller = RefreshController(cooldown=10)

    show_header()

    if refresh_controller.refresh():
        prices = get_prices()

        for price in prices:
            show_price(price)

    show_footer()


if __name__ == "__main__":
    main()
