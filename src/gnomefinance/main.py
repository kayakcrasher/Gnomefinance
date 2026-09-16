from .assets import Asset


def main():
    bitcoin = Asset("Bitcoin", "BTC")

    print("Welcome to GNOMEfinance!")
    bitcoin.show()


if __name__ == "__main__":
    main()
