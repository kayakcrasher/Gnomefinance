from test_networks import (
    test_address_validation,
    test_registry,
    test_solana_network_information,
    test_unknown_network,
)


def run_tests():
    print("GNOMEfinance Tests")
    print("==================")

    tests = [
        ("Network Registry", test_registry),
        ("Solana Network", test_solana_network_information),
        ("Address Validation", test_address_validation),
        ("Unknown Network Handling", test_unknown_network),
    ]

    passed = 0

    for name, test in tests:
        try:
            test()
            print(f"PASS: {name}")
            passed += 1
        except Exception as error:
            print(f"FAIL: {name}")
            print(f"      {error}")

    print("==================")
    print(f"{passed}/{len(tests)} tests passed")

    if passed != len(tests):
        raise SystemExit(1)

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    run_tests()
