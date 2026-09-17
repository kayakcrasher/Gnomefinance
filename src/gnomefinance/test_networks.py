from network_registry import NetworkRegistry
from wallet_service import WalletService


def test_registry():
    registry = NetworkRegistry()

    networks = registry.list_registered()

    assert "solana" in networks


def test_solana_network_information():
    wallet_service = WalletService()

    network = wallet_service.get_network("solana")

    assert network.get_network_name() == "Solana"
    assert network.get_symbol() == "SOL"


def test_address_validation():
    wallet_service = WalletService()

    network = wallet_service.get_network("solana")

    valid_length_address = "A" * 32
    invalid_address = "short"

    assert network.validate_address(valid_length_address)
    assert not network.validate_address(invalid_address)


def test_unknown_network():
    wallet_service = WalletService()

    try:
        wallet_service.get_network("ethereum")
        assert False, "Expected ValueError"
    except ValueError:
        pass
