
from .assets import Asset
from .prices import get_bitcoin_price


def main():
    bitcoin_price = get_bitcoin_price()

    bitcoin = Asset("Bitcoin", "BTC", bitcoin_price)

    print("Welcome to GNOMEfinance!")
    bitcoin.show()


if __name__ == "__main__":
    main()
