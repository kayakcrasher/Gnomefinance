from .coins import COINS
from .prices import get_price
from .price_data import Price


def main():
    print("Welcome to GNOMEfinance!")
    print()

    for coin_id, symbol in COINS.items():
        usd_price = get_price(coin_id)

        price = Price(
            coin_id,
            symbol,
            usd_price
        )

        price.show()
        print()


if __name__ == "__main__":
    main()
