from wallet_service import WalletService


def test_solana_connection():
    wallet_service = WalletService()

    connected = wallet_service.is_connected("solana")

    assert connected is True
