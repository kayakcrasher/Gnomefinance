import pytest

from conftest import BTC_ADDRESS, ETH_ADDRESS, SOL_ADDRESS
from gnomefinance.chains import BitcoinChain, EthereumChain, SolanaChain, base58_decode
from gnomefinance.errors import ValidationError

VALID_BTC = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # genesis (legacy)
    "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",  # P2SH
    BTC_ADDRESS,  # SegWit
    "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0",  # Taproot
]
INVALID_BTC = [
    "",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNb",  # bad checksum
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdx",  # bad checksum
    "tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx",  # testnet
    "bc1QAR0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",  # mixed case
    "hello",
]


def test_base58_decode_keeps_leading_zeros():
    assert base58_decode("11111111111111111111111111111111") == bytes(32)


@pytest.mark.parametrize("address", VALID_BTC)
def test_valid_bitcoin_addresses(address):
    assert BitcoinChain(client=None).validate_address(address)


@pytest.mark.parametrize("address", INVALID_BTC)
def test_invalid_bitcoin_addresses(address):
    assert not BitcoinChain(client=None).validate_address(address)


def test_ethereum_validation():
    chain = EthereumChain(client=None)
    assert chain.validate_address(ETH_ADDRESS)
    assert not chain.validate_address(ETH_ADDRESS[:-1])
    assert not chain.validate_address("de0B295669a9FD93d5F28D9Ec85E40f4cb697BAe")


def test_solana_validation():
    chain = SolanaChain(client=None)
    assert chain.validate_address(SOL_ADDRESS)
    assert chain.validate_address("11111111111111111111111111111111")
    assert not chain.validate_address("0OIl" * 10)  # not Base58
    assert not chain.validate_address(SOL_ADDRESS[:20])


def test_balances_are_converted_to_whole_coins(chain_clients):
    assert BitcoinChain(chain_clients["bitcoin"]).get_balance(BTC_ADDRESS) == 1.0
    assert EthereumChain(chain_clients["ethereum"]).get_balance(ETH_ADDRESS) == 2.0
    assert SolanaChain(chain_clients["solana"]).get_balance(SOL_ADDRESS) == 3.0


def test_invalid_address_never_hits_the_network(chain_clients):
    client = chain_clients["solana"]
    with pytest.raises(ValidationError):
        SolanaChain(client).get_balance("nope")
    assert client.calls == []
