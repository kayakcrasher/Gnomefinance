from .assets import Asset
from .coins import COINS
from .prices import get_price


def main():
    print("Welcome to GNOMEfinance!")
    print()

    for coin_id, symbol in COINS.items():
        price = get_price(coin_id)
        asset = Asset(coin_id.title(), symbol, price)

        asset.show()
        print()


if __name__ == "__main__":
    main()
