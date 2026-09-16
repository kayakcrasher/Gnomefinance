from .assets import Asset
from .prices import get_price


def main():
    bitcoin = Asset("Bitcoin", "BTC", get_price("bitcoin"))
    ethereum = Asset("Ethereum", "ETH", get_price("ethereum"))
    solana = Asset("Solana", "SOL", get_price("solana"))

    print("Welcome to GNOMEfinance!")
    print()

    bitcoin.show()
    print()

    ethereum.show()
    print()

    solana.show()


if __name__ == "__main__":
    main()
