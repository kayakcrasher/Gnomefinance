from .coins import COINS
from .prices import get_price
from .price_data import Price
from .display import show_header, show_price, show_footer


def main():
    show_header()

    for coin_id, symbol in COINS.items():
        usd_price = get_price(coin_id)

        price = Price(
            coin_id,
            symbol,
            usd_price
        )

        show_price(price)

    show_footer()


if __name__ == "__main__":
    main()
