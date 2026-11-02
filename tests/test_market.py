import pytest

from gnomefinance.errors import NetworkError, ValidationError
from gnomefinance.market import MarketData


def test_quotes_are_parsed_and_mapped(market_client):
    quotes = MarketData(client=market_client).get_quotes()
    assert quotes["bitcoin"]["price"] == 100000.0
    assert quotes["ethereum"]["change_24h"] == -1.0
    assert quotes["bitcoin"]["stale"] is False


def test_avalanche_uses_correct_coingecko_id(market_client):
    MarketData(client=market_client).get_quotes()
    ids = market_client.calls[0][2]["ids"].split(",")
    assert "avalanche-2" in ids


def test_quotes_are_cached(market_client):
    market = MarketData(client=market_client)
    market.get_quotes()
    market.get_quotes()
    assert len(market_client.calls) == 1
    market.get_quotes(force=True)
    assert len(market_client.calls) == 2


def test_falls_back_to_stale_quotes_when_offline(market_client):
    market = MarketData(client=market_client)
    market.get_quotes()
    market_client.error = NetworkError("offline")
    quotes = market.get_quotes(force=True)
    assert quotes["bitcoin"]["price"] == 100000.0
    assert quotes["bitcoin"]["stale"] is True


def test_raises_when_offline_with_no_data(market_client):
    market_client.error = NetworkError("offline")
    with pytest.raises(NetworkError):
        MarketData(client=market_client).get_quotes()


def test_history(market_client):
    points = MarketData(client=market_client).get_history("bitcoin", 7)
    assert points == [[1, 90000.0], [2, 95000.0], [3, 100000.0]]


@pytest.mark.parametrize("asset, days", [("dogecoin", 7), ("bitcoin", 3)])
def test_history_validates_input(market_client, asset, days):
    with pytest.raises(ValidationError):
        MarketData(client=market_client).get_history(asset, days)
