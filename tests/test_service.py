import pytest

from conftest import BTC_ADDRESS, SOL_ADDRESS
from gnomefinance.errors import NetworkError, ValidationError


def test_empty_summary(service):
    summary = service.summary()
    assert summary["assets"] == []
    assert summary["total_value"] == 0
    assert summary["errors"] == []


def test_summary_math(service):
    service.set_holding("bitcoin", 0.5)   # $50,000, +2% today
    service.set_holding("ethereum", 5)    # $20,000, -1% today
    summary = service.summary()

    assert summary["total_value"] == pytest.approx(70000)
    rows = {row["asset_id"]: row for row in summary["assets"]}
    assert rows["bitcoin"]["allocation"] == pytest.approx(50000 / 70000 * 100)
    # 24h USD move is computed from the value 24h ago, not value * pct.
    assert rows["bitcoin"]["value_change_24h"] == pytest.approx(50000 - 50000 / 1.02)
    assert rows["ethereum"]["value_change_24h"] == pytest.approx(20000 - 20000 / 0.99)
    assert summary["assets"][0]["asset_id"] == "bitcoin"  # sorted by value


def test_wallet_balances_are_added_to_holdings(service):
    service.set_holding("solana", 2)
    service.add_wallet("solana", SOL_ADDRESS, "Phantom")
    row = service.summary()["assets"][0]
    assert row["amount"] == 5  # 2 manual + 3 on-chain
    assert row["manual_amount"] == 2
    assert row["wallet_amount"] == 3
    assert row["value"] == 1000


def test_asset_without_price_shows_none(service):
    service.set_holding("cardano", 100)  # not in the fake market data
    row = service.summary()["assets"][0]
    assert row["price"] is None and row["value"] is None


def test_changes_persist(make_service, tmp_path):
    first = make_service()
    first.set_holding("bitcoin", 0.1)
    wallet = first.add_wallet("bitcoin", BTC_ADDRESS)

    second = make_service()
    assert second.portfolio.holdings == {"bitcoin": 0.1}
    assert second.wallets == [wallet]

    second.remove_wallet(wallet["id"])
    assert make_service().wallets == []


def test_duplicate_and_invalid_wallets_are_rejected(service):
    service.add_wallet("bitcoin", BTC_ADDRESS)
    with pytest.raises(ValidationError):
        service.add_wallet("bitcoin", BTC_ADDRESS)
    with pytest.raises(ValidationError):
        service.add_wallet("bitcoin", "not-an-address")
    with pytest.raises(ValidationError):
        service.add_wallet("dogecoin", BTC_ADDRESS)


def test_wallet_errors_are_reported_not_raised(service, chain_clients):
    service.add_wallet("solana", SOL_ADDRESS, "Phantom")
    chain_clients["solana"].error = NetworkError("RPC down")
    summary = service.summary(force=True)
    assert summary["wallets"][0]["balance"] is None
    assert any("RPC down" in e for e in summary["errors"])


def test_price_outage_is_reported(service, market_client):
    service.set_holding("bitcoin", 1)
    market_client.error = NetworkError("offline")
    summary = service.summary()
    assert summary["assets"][0]["value"] is None
    assert summary["errors"]
