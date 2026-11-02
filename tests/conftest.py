"""Shared test helpers. No test ever touches the real internet."""

import pytest

from gnomefinance.chains import BitcoinChain, EthereumChain, SolanaChain
from gnomefinance.market import MarketData
from gnomefinance.service import GnomeFinance
from gnomefinance.storage import Storage

BTC_ADDRESS = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
ETH_ADDRESS = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
SOL_ADDRESS = "So11111111111111111111111111111111111111112"

MARKETS = [
    {"id": "bitcoin", "current_price": 100000.0, "price_change_percentage_24h": 2.0,
     "market_cap": 1, "total_volume": 2},
    {"id": "ethereum", "current_price": 4000.0, "price_change_percentage_24h": -1.0,
     "market_cap": 1, "total_volume": 2},
    {"id": "solana", "current_price": 200.0, "price_change_percentage_24h": 0.0,
     "market_cap": 1, "total_volume": 2},
]


class FakeClient:
    """Stands in for APIClient: returns canned answers and records calls."""

    def __init__(self, get=None, rpc=None, error=None):
        self.get_responses = get or {}
        self.rpc_responses = rpc or {}
        self.error = error
        self.calls = []

    def get(self, endpoint, params=None):
        self.calls.append(("get", endpoint, params))
        if self.error:
            raise self.error
        return self.get_responses[endpoint]

    def rpc(self, method, params=None):
        self.calls.append(("rpc", method, params))
        if self.error:
            raise self.error
        return self.rpc_responses[method]


@pytest.fixture
def market_client():
    return FakeClient(get={
        "/coins/markets": MARKETS,
        "/coins/bitcoin/market_chart": {"prices": [[1, 90000.0], [2, 95000.0], [3, 100000.0]]},
    })


@pytest.fixture
def chain_clients():
    return {
        "bitcoin": FakeClient(get={f"/address/{BTC_ADDRESS}": {
            "chain_stats": {"funded_txo_sum": 150_000_000, "spent_txo_sum": 50_000_000},
            "mempool_stats": {"funded_txo_sum": 0, "spent_txo_sum": 0},
        }}),
        "ethereum": FakeClient(rpc={"eth_getBalance": hex(2 * 10**18)}),
        "solana": FakeClient(rpc={"getBalance": {"value": 3_000_000_000}}),
    }


@pytest.fixture
def make_service(tmp_path, market_client, chain_clients):
    def build(path=None):
        chains = {
            "bitcoin": BitcoinChain(chain_clients["bitcoin"]),
            "ethereum": EthereumChain(chain_clients["ethereum"]),
            "solana": SolanaChain(chain_clients["solana"]),
        }
        return GnomeFinance(
            storage=Storage(path or tmp_path / "portfolio.json"),
            market=MarketData(client=market_client),
            chains=chains,
        )
    return build


@pytest.fixture
def service(make_service):
    return make_service()
