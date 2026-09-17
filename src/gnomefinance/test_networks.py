from network_registry import NetworkRegistry
from wallet_service import WalletService


def test_registry():
    print("Testing Network Registry...")
    registry = NetworkRegistry()

    networks = registry.list_registered()

    assert "solana" in networks

    print("PASS: Solana is registered.")


def test_solana_info():
    print("Testing Solana network information...")
    wallet_service = WalletService()

    info = wallet_service.get_network_info("solana")

    assert info["name"] == "Solana"
    assert info["symbol"] == "SOL"
    assert "connected" in info

    print("PASS: Solana network information is valid.")
    print(f"Network: {info['name']}")
    print(f"Symbol: {info['symbol']}")
    print(f"Connected: {info['connected']}")


def test_address_validation():
    print("Testing Solana address validation...")
    wallet_service = WalletService()

    network = wallet_service.get_network("solana")

    valid_length_address = "A" * 32
    invalid_address = "short"

    assert network.validate_address(valid_length_address)
    assert not network.validate_address(invalid_address)

    print("PASS: Basic address validation works.")


def run_tests():
    print("GNOMEfinance Network Tests")
    print("==========================")

    test_registry()
    test_solana_info()
    test_address_validation()

    print("==========================")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    run_tests()
